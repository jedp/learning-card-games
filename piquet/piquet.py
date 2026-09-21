"""A playable game of Piquet (Rubicon scoring) with injectable strategies.

Run it:      python3 piquet.py
             python3 piquet.py --opponent defensive
             python3 piquet.py --opponent random --deals 6 --seed 17

The design separates three things on purpose, the same way skat.py does:

  * The *rules engine*  -- cards, the three declaration categories and how they
    are compared, legal moves, who wins a trick, and every scoring rule
    including repique, pique, the cards, capot and the rubicon.  This layer is
    objective and never makes a choice.
  * The *table*         -- Deal runs one deal (carte blanche, the exchange, the
    declarations, twelve tricks, the score) and Partie runs the six deals and
    settles the rubicon.  It asks players to choose but never decides for them.
  * The *strategies*    -- each Player owns a Strategy answering three
    questions: what do you discard, how much of your hand do you admit to, and
    which card do you play.  Swap the Strategy and you swap the playing style.
    A human is just a Strategy that asks you at a prompt.

The bots share one brain (HeuristicStrategy) tuned by a Style into defensive,
balanced or aggressive play.  Optionally they finish the hand with an exact
endgame search (see piquet_dd.py), sampling opponent hands that are *consistent
with the declarations actually made* -- which is the reading exercise in
piquet-reading-declarations.md, done in code.

House rule settled here: a player who leaves cards in the talon may look at
them privately, and the opponent does not get to see them.  Change
LEFTOVERS_ARE_PUBLIC if your table plays the other way.
"""

from __future__ import annotations

import argparse
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from itertools import combinations
from typing import Optional

import piquet_dd

LEFTOVERS_ARE_PUBLIC = False


# --------------------------------------------------------------------------- #
#  Cards
# --------------------------------------------------------------------------- #

SUITS = ("s", "h", "d", "c")
SUIT_SYMBOL = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}
RANKS = ("A", "K", "Q", "J", "T", "9", "8", "7")     # high to low
RANK_ORDER = {r: i for i, r in enumerate(RANKS)}     # 0 = ace = highest
PIPS = {"A": 11, "K": 10, "Q": 10, "J": 10, "T": 10, "9": 9, "8": 8, "7": 7}
SETTABLE = frozenset("AKQJT")        # nines and below never form a trio
RANK_NAME = {"A": "ace", "K": "king", "Q": "queen", "J": "jack", "T": "ten",
             "9": "nine", "8": "eight", "7": "seven"}
PLURAL = {"A": "aces", "K": "kings", "Q": "queens", "J": "jacks", "T": "tens"}
NUMBER = {0: "none", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
          6: "six", 7: "seven", 8: "eight"}


@dataclass(frozen=True, order=False)
class Card:
    rank: str
    suit: str

    @property
    def order(self) -> int:
        """0 for an ace down to 7 for a seven.  Lower beats higher."""
        return RANK_ORDER[self.rank]

    @property
    def pips(self) -> int:
        return PIPS[self.rank]

    def beats(self, other: "Card") -> bool:
        """True if this card wins over `other` when `other` was led."""
        return self.suit == other.suit and self.order < other.order

    def __str__(self) -> str:
        return SUIT_SYMBOL[self.suit] + ("10" if self.rank == "T" else self.rank)

    def as_pair(self):
        return (self.rank, self.suit)


def make_deck() -> list[Card]:
    return [Card(r, s) for s in SUITS for r in RANKS]


def sort_hand(cards) -> list[Card]:
    return sorted(cards, key=lambda c: (SUITS.index(c.suit), c.order))


def show_cards(cards) -> str:
    """Group a hand by suit, in suit order, high card first."""
    out = []
    for suit in SUITS:
        in_suit = sorted((c for c in cards if c.suit == suit), key=lambda c: c.order)
        if in_suit:
            out.append(SUIT_SYMBOL[suit] + " " +
                       " ".join("10" if c.rank == "T" else c.rank for c in in_suit))
    return "   ".join(out)


# --------------------------------------------------------------------------- #
#  The three declaration categories
# --------------------------------------------------------------------------- #

SEQUENCE_VALUE = {3: 3, 4: 4, 5: 15, 6: 16, 7: 17, 8: 18}
SEQUENCE_NAME = {3: "tierce", 4: "quart", 5: "quint",
                 6: "sixième", 7: "septième", 8: "huitième"}


@dataclass(frozen=True)
class Point:
    length: int
    pips: int
    suit: Optional[str]

    @property
    def value(self) -> int:
        return self.length

    def key(self):
        return (self.length, self.pips)

    def __str__(self) -> str:
        return f"point of {NUMBER[self.length]}, making {self.pips}"


@dataclass(frozen=True)
class Sequence:
    length: int
    top: str            # rank character of the highest card
    suit: str

    @property
    def value(self) -> int:
        return SEQUENCE_VALUE[self.length]

    def key(self):
        return (self.length, -RANK_ORDER[self.top])

    def __str__(self) -> str:
        name = SEQUENCE_NAME[self.length]
        if self.top == "A":
            return f"{name} major"
        return f"{name} to the {RANK_NAME[self.top]}"


@dataclass(frozen=True)
class CardSet:
    count: int          # 3 = trio, 4 = quatorze
    rank: str

    @property
    def value(self) -> int:
        return 14 if self.count == 4 else 3

    def key(self):
        return (self.count, -RANK_ORDER[self.rank])

    def __str__(self) -> str:
        return f"{NUMBER[self.count]} {PLURAL[self.rank]}"


def best_point(hand) -> Point:
    best = Point(0, 0, None)
    for suit in SUITS:
        in_suit = [c for c in hand if c.suit == suit]
        if not in_suit:
            continue
        candidate = Point(len(in_suit), sum(c.pips for c in in_suit), suit)
        if candidate.key() > best.key():
            best = candidate
    return best


def all_sequences(hand) -> list[Sequence]:
    found = []
    for suit in SUITS:
        in_suit = sorted((c for c in hand if c.suit == suit), key=lambda c: c.order)
        if not in_suit:
            continue
        run = [in_suit[0]]
        for previous, current in zip(in_suit, in_suit[1:]):
            if current.order == previous.order + 1:
                run.append(current)
            else:
                if len(run) >= 3:
                    found.append(Sequence(len(run), run[0].rank, suit))
                run = [current]
        if len(run) >= 3:
            found.append(Sequence(len(run), run[0].rank, suit))
    return found


def all_sets(hand) -> list[CardSet]:
    found = []
    for rank in SETTABLE:
        count = sum(1 for c in hand if c.rank == rank)
        if count >= 3:
            found.append(CardSet(count, rank))
    return sorted(found, key=lambda s: s.key(), reverse=True)


def _spoken(holdings) -> str:
    """Read a list of combinations aloud, best first, capitalised."""
    ordered = sorted(holdings, key=lambda h: h.key(), reverse=True)
    text = ", ".join(str(h) for h in ordered)
    return text[0].upper() + text[1:] if text else ""


def carte_blanche(hand) -> bool:
    return not any(c.rank in ("K", "Q", "J") for c in hand)


def declaration_total(hand) -> int:
    """Everything the hand *could* score if it won all three categories.  Used
    by the bots to compare candidate discards, not by the rules."""
    return (best_point(hand).value
            + sum(s.value for s in all_sequences(hand))
            + sum(s.value for s in all_sets(hand))
            + (10 if carte_blanche(hand) else 0))


# --------------------------------------------------------------------------- #
#  Resolving a category:  the winner scores everything, the loser scores nothing
# --------------------------------------------------------------------------- #

@dataclass
class CategoryResult:
    name: str
    elder_holding: object           # what elder declared (may be sunk)
    younger_holding: object
    winner: str                     # "E", "Y" or "-" for a tie
    elder_points: int
    younger_points: int
    detail: str = ""


def _resolve(name, elder_best, younger_best, elder_all, younger_all) -> CategoryResult:
    e_key = elder_best.key() if elder_best else (0, 0)
    y_key = younger_best.key() if younger_best else (0, 0)
    if e_key > y_key:
        return CategoryResult(name, elder_best, younger_best, "E",
                              sum(x.value for x in elder_all), 0)
    if y_key > e_key:
        return CategoryResult(name, elder_best, younger_best, "Y",
                              0, sum(x.value for x in younger_all))
    return CategoryResult(name, elder_best, younger_best, "-", 0, 0)


def resolve_point(elder_point: Point, younger_point: Point) -> CategoryResult:
    e, y = elder_point, younger_point
    if e.key() > y.key():
        return CategoryResult("point", e, y, "E", e.value, 0)
    if y.key() > e.key():
        return CategoryResult("point", e, y, "Y", 0, y.value)
    return CategoryResult("point", e, y, "-", 0, 0)


def resolve_sequences(elder_seqs, younger_seqs) -> CategoryResult:
    e_best = max(elder_seqs, key=lambda s: s.key()) if elder_seqs else None
    y_best = max(younger_seqs, key=lambda s: s.key()) if younger_seqs else None
    return _resolve("sequences", e_best, y_best, elder_seqs, younger_seqs)


def resolve_sets(elder_sets, younger_sets) -> CategoryResult:
    e_best = max(elder_sets, key=lambda s: s.key()) if elder_sets else None
    y_best = max(younger_sets, key=lambda s: s.key()) if younger_sets else None
    return _resolve("sets", e_best, y_best, elder_sets, younger_sets)


# --------------------------------------------------------------------------- #
#  Play rules
# --------------------------------------------------------------------------- #

def legal_moves(hand: list[Card], led: Optional[Card]) -> list[Card]:
    """Follow suit if you can; otherwise anything, and it loses."""
    if led is None:
        return list(hand)
    same_suit = [c for c in hand if c.suit == led.suit]
    return same_suit if same_suit else list(hand)


def trick_winner(lead: Card, reply: Card) -> str:
    """Returns "leader" or "follower"."""
    return "follower" if reply.beats(lead) else "leader"


def is_master(card: Card, hand, seen: set) -> bool:
    """True when every higher card of this suit is already played or in `hand`."""
    for rank in RANKS:
        if RANK_ORDER[rank] >= card.order:
            break
        higher = Card(rank, card.suit)
        if higher not in seen and higher not in hand:
            return False
    return True


# --------------------------------------------------------------------------- #
#  Players and strategies
# --------------------------------------------------------------------------- #

class Player:
    def __init__(self, name: str, strategy: "Strategy"):
        self.name = name
        self.strategy = strategy
        self.hand: list[Card] = []
        self.discards: list[Card] = []
        self.seen_talon: list[Card] = []     # cards I looked at but did not take
        self.tricks = 0
        self.deal_score = 0
        self.partie_score = 0
        self.is_elder = False
        self.seat_name = ""

    @property
    def seat(self) -> str:
        return "E" if self.is_elder else "Y"

    def verb(self, word: str) -> str:
        """"You exchange" but "Margot exchanges" -- the human seat is second
        person, the bots are third."""
        return word if self.strategy.is_human else word + "s"

    def __str__(self) -> str:
        return self.name


class Strategy(ABC):
    """The three decisions a piquet player makes."""

    is_human = False

    @abstractmethod
    def choose_exchange(self, me: Player, deal: "Deal",
                        low: int, high: int) -> list[Card]:
        """Return the cards to throw away.  Their number decides how many you
        draw, so it must be between `low` and `high` inclusive."""

    @abstractmethod
    def choose_card(self, me: Player, deal: "Deal", legal: list[Card]) -> Card:
        """Pick one card from `legal` to play into the current trick."""

    def declared_point(self, me: Player, deal: "Deal", actual: Point) -> Point:
        """Return the point you *announce*.

        Declaring **less** than you hold is legal and is called sinking: you
        score only what you declare, you must be able to show it, and in return
        your opponent's reconstruction of your hand is wrong.  You may also name
        a different suit entirely -- the suit is never stated aloud, only the
        count -- which misdirects rather than merely conceals.

        Declaring **more** than you hold is a false declaration and forfeits the
        category.  Returning Point(0, 0, None) declines it outright, which hands
        the opponent every combination they hold in it.

        Younger may consult `deal.elder_declared_point`: hearing elder's claim
        first means younger can shave to exactly one better and risk nothing.
        The default is to tell the truth."""
        return actual


# --------------------------------------------------------------------------- #
#  One brain, three personalities
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class Style:
    """Tuning knobs.  These are the whole difference between the bots."""
    name: str
    declaration_weight: float    # how much declaration points sway the discard
    trick_weight: float          # how much raw trick power sways it
    guard_weight: float          # how much low cards that stop a suit are worth
    max_draw: bool               # always take the largest legal exchange
    lead_long: bool              # lead your longest suit to establish it
    duck: bool                   # decline cheap wins to keep a stopper back
    sink_point: bool             # understate the point to hide your shape
    solver_from: int             # solve exactly once this many cards remain


DEFENSIVE = Style("defensive", declaration_weight=0.7, trick_weight=1.4,
                  guard_weight=1.5, max_draw=False, lead_long=False,
                  duck=True, sink_point=True, solver_from=6)
BALANCED = Style("balanced", declaration_weight=1.0, trick_weight=1.1,
                 guard_weight=0.8, max_draw=True, lead_long=True,
                 duck=False, sink_point=False, solver_from=6)
AGGRESSIVE = Style("aggressive", declaration_weight=1.6, trick_weight=0.9,
                   guard_weight=0.2, max_draw=True, lead_long=True,
                   duck=False, sink_point=False, solver_from=5)

STYLES = {"defensive": DEFENSIVE, "balanced": BALANCED, "aggressive": AGGRESSIVE}

# rough trick-taking worth of a card held in a suit
_CARD_POWER = {"A": 4.0, "K": 2.6, "Q": 1.5, "J": 0.8, "T": 0.4,
               "9": 0.1, "8": 0.0, "7": 0.0}


def trick_power(hand) -> float:
    """A crude estimate of how many tricks a hand will take on its own."""
    total = 0.0
    for suit in SUITS:
        in_suit = sorted((c for c in hand if c.suit == suit), key=lambda c: c.order)
        if not in_suit:
            continue
        total += sum(_CARD_POWER[c.rank] for c in in_suit)
        total += 0.4 * max(0, len(in_suit) - 3)          # long suits run
        if in_suit[0].rank == "K" and len(in_suit) == 1:
            total -= 1.2                                  # a bare king is a loser
        elif in_suit[0].rank == "Q" and len(in_suit) <= 2:
            total -= 0.5
    return total


def guard_value(hand) -> float:
    """Reward holding a low card in a suit -- the thing that stops the opponent
    running it.  Being void in a suit is what lets a seven win a trick."""
    total = 0.0
    for suit in SUITS:
        in_suit = [c for c in hand if c.suit == suit]
        if not in_suit:
            total -= 1.0                                  # a void is a leak
            continue
        length = len(in_suit)
        total += min(length, 3) * 0.35
        if length >= 2 and any(c.order >= RANK_ORDER["T"] for c in in_suit):
            total += 0.4                                  # a genuine low guard
    return total


class HeuristicStrategy(Strategy):
    """One brain.  The Style decides what it cares about."""

    def __init__(self, style: Style, rng: Optional[random.Random] = None):
        self.style = style
        self.rng = rng or random.Random()

    # -- the exchange ------------------------------------------------------ #

    def _score_hand(self, hand) -> float:
        s = self.style
        return (s.declaration_weight * declaration_total(hand)
                + s.trick_weight * trick_power(hand)
                + s.guard_weight * guard_value(hand))

    def choose_exchange(self, me, deal, low, high) -> list[Card]:
        sizes = [high] if self.style.max_draw else list(range(max(low, high - 2), high + 1))
        best, best_discard = None, None
        for size in sizes:
            drawn = deal.peek_talon(me, size)
            for discard in combinations(sort_hand(me.hand), size):
                if any(c.rank == "A" for c in discard):
                    continue                  # never throw an ace
                kept = [c for c in me.hand if c not in discard]
                score = self._score_hand(kept + drawn)
                if best is None or score > best:
                    best, best_discard = score, list(discard)
        if best_discard is None:              # degenerate: hand is all aces
            best_discard = sort_hand(me.hand)[-low:]
        return best_discard

    # -- declaring --------------------------------------------------------- #

    def _shavings(self, me, actual: Point):
        """Progressively shorter honest declarations from the same suit, keeping
        the highest cards so the pip count stays as large as it can."""
        in_suit = sorted((c for c in me.hand if c.suit == actual.suit),
                         key=lambda c: c.order)
        for drop in range(1, len(in_suit)):
            kept = in_suit[:-drop]
            yield Point(len(kept), sum(c.pips for c in kept), actual.suit)

    def declared_point(self, me, deal, actual: Point) -> Point:
        """Sink the point to conceal the shape, at 1 point per card given up."""
        if not self.style.sink_point or actual.length < 4:
            return actual

        heard = deal.elder_declared_point
        if not me.is_elder and heard is not None:
            # Younger knows what has to be beaten: shave as far as is still safe.
            best = actual
            for shorter in self._shavings(me, actual):
                if shorter.key() > heard.key():
                    best = shorter
                else:
                    break
            return best

        # Elder declares blind, and measurement says that is a losing game:
        # over 200 bot deals a blind elder sink lost the point outright 76 times
        # in 130 (58%), for a net swing of -436 declaration points.  No length
        # threshold rescued it.  So the bots only sink from the younger chair,
        # where the information makes it free.
        return actual

    # -- the play ---------------------------------------------------------- #

    def choose_card(self, me, deal, legal) -> Card:
        if len(me.hand) <= self.style.solver_from:
            exact = self._solve_endgame(me, deal, legal)
            if exact is not None:
                return exact
        if deal.led_card is None:
            return self._lead(me, deal, legal)
        return self._follow(me, deal, legal, deal.led_card)

    def _lead(self, me, deal, legal) -> Card:
        seen = deal.seen_by(me)
        masters = [c for c in legal if is_master(c, me.hand, seen)]
        if masters:
            # cash the master in the suit where we have the most behind it
            return max(masters, key=lambda c: (len([x for x in me.hand
                                                    if x.suit == c.suit]), -c.order))
        if self.style.lead_long:
            lengths = {s: len([c for c in me.hand if c.suit == s]) for s in SUITS}
            suit = max(SUITS, key=lambda s: (lengths[s], -min(
                (c.order for c in me.hand if c.suit == s), default=99)))
            in_suit = sorted((c for c in legal if c.suit == suit), key=lambda c: c.order)
            if in_suit:
                return in_suit[0]
        # defensive: lead the cheapest card from the suit we least want to keep
        return min(legal, key=lambda c: (_CARD_POWER[c.rank],
                                         len([x for x in me.hand if x.suit == c.suit])))

    def _follow(self, me, deal, legal, led: Card) -> Card:
        winners = [c for c in legal if c.beats(led)]
        following = [c for c in legal if c.suit == led.suit]

        if following:
            if not winners:
                return max(following, key=lambda c: c.order)      # cheapest loser
            if self.style.duck and len(following) > len(winners) \
                    and led.order >= RANK_ORDER["T"]:
                # they led rubbish; keep the big card for something worth having
                return max(following, key=lambda c: c.order)
            return max(winners, key=lambda c: c.order)            # cheapest winner

        return self._discard(me, deal, legal)

    def _discard(self, me, deal, legal) -> Card:
        """Void in the led suit: throw the card we can most afford to lose."""
        seen = deal.seen_by(me)

        def cost(card: Card) -> tuple:
            in_suit = [c for c in me.hand if c.suit == card.suit]
            master = is_master(card, me.hand, seen)
            guarded = len(in_suit) > 1
            return (master,                       # never pitch a winner
                    _CARD_POWER[card.rank] * (1.0 if guarded else 1.6),
                    -len(in_suit))                # prefer our longest suit
        return min(legal, key=cost)

    # -- exact endgame ------------------------------------------------------ #

    def _solve_endgame(self, me, deal, legal) -> Optional[Card]:
        """Sample opponent hands that are consistent with the declarations that
        were actually made, solve each one exactly, and vote.

        This is the only place the bot uses piquet_dd, and it never peeks: the
        samples are built from what this seat legitimately knows."""
        worlds = deal.sample_opponent_hands(me, limit=16, rng=self.rng)
        if not worlds:
            return None

        votes: dict[Card, float] = {c: 0.0 for c in legal}
        # piquet_dd always reports the differential from elder's point of view,
        # so a younger-seat bot wants to minimise it.
        sign = 1 if me.is_elder else -1

        for opponent_hand in worlds:
            if deal.led_card is None:
                votes_this = self._vote_on_lead(me, deal, legal, opponent_hand)
            else:
                votes_this = self._vote_on_reply(me, deal, legal, opponent_hand)
            for card, value in votes_this.items():
                votes[card] += sign * value

        return max(votes, key=lambda c: votes[c])

    def _vote_on_lead(self, me, deal, legal, opponent_hand) -> dict:
        """On lead we can hand the whole position to the solver and take the
        card it chooses."""
        mine = [c.as_pair() for c in me.hand]
        theirs = [c.as_pair() for c in opponent_hand]
        elder_cards, younger_cards = (mine, theirs) if me.is_elder else (theirs, mine)
        value, line = piquet_dd.solve(elder_cards, younger_cards,
                                      elder_leads=me.is_elder,
                                      elder_tricks=deal.tricks_won["E"])
        chosen = Card(*line[0][1])
        return {chosen: value} if chosen in legal else {}

    def _vote_on_reply(self, me, deal, legal, opponent_hand) -> dict:
        """Mid-trick the solver cannot resume, so try each legal reply, settle
        this trick by hand, and let the solver take over from the next one."""
        led = deal.led_card
        out = {}
        for reply in legal:
            follower_wins = reply.beats(led)
            elder_wins = follower_wins if me.is_elder else not follower_wins
            e_tricks = deal.tricks_won["E"] + (1 if elder_wins else 0)

            # The lead point is already awarded; what this choice decides is the
            # capture point, the last-trick point, and everything after.
            capture = (1 if elder_wins else -1) if follower_wins else 0

            my_rest = [c for c in me.hand if c != reply]
            opp_rest = [c for c in opponent_hand if c != led]
            if not my_rest:                                  # this was trick 12
                cards = (10 if e_tricks > 6 else -10 if 12 - e_tricks > 6 else 0)
                if e_tricks == 12:
                    cards = 40
                elif e_tricks == 0:
                    cards = -40
                last = 1 if elder_wins else -1
                out[reply] = capture + last + cards
                continue

            e_rest, y_rest = ((my_rest, opp_rest) if me.is_elder
                              else (opp_rest, my_rest))
            value, _ = piquet_dd.solve([c.as_pair() for c in e_rest],
                                       [c.as_pair() for c in y_rest],
                                       elder_leads=elder_wins,
                                       elder_tricks=e_tricks)
            out[reply] = capture + value
        return out


def DefensiveStrategy(rng=None) -> HeuristicStrategy:
    return HeuristicStrategy(DEFENSIVE, rng)


def BalancedStrategy(rng=None) -> HeuristicStrategy:
    return HeuristicStrategy(BALANCED, rng)


def AggressiveStrategy(rng=None) -> HeuristicStrategy:
    return HeuristicStrategy(AGGRESSIVE, rng)


class RandomStrategy(Strategy):
    """A sparring partner with no plan at all.  Useful as a baseline."""

    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng or random.Random()

    def choose_exchange(self, me, deal, low, high) -> list[Card]:
        size = self.rng.randint(low, high)
        return self.rng.sample(sort_hand(me.hand), size)

    def choose_card(self, me, deal, legal) -> Card:
        return self.rng.choice(sorted(legal, key=lambda c: (c.suit, c.order)))


# --------------------------------------------------------------------------- #
#  The human seat
# --------------------------------------------------------------------------- #

def _ask_int(prompt: str, low: int, high: int) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
        except ValueError:
            print("  (please type a number)")
            continue
        if low <= value <= high:
            return value
        print(f"  (choose between {low} and {high})")


class HumanStrategy(Strategy):
    is_human = True

    def _yes_no(self, prompt: str) -> bool:
        while True:
            reply = input(prompt).strip().lower()
            if reply in ("y", "yes"):
                return True
            if reply in ("n", "no", ""):
                return False
            print("  (please answer y or n)")

    def declared_point(self, me, deal, actual: Point) -> Point:
        heard = deal.elder_declared_point
        if heard is not None and not me.is_elder:
            print(f'\n  Elder declared: "Point of {NUMBER[heard.length]}."'
                  f"   (making {heard.pips})")
        print(f"\n  Your best point is {actual} in "
              f"{SUIT_SYMBOL[actual.suit]}.")
        if not self._yes_no("  Sink it -- declare less, to hide your shape? "
                            "(y/N) "):
            return actual

        print("  You score only what you declare, and must be able to show it.")
        print("  The suit is never stated aloud, so you may name a different one.")
        options = []
        for suit in SUITS:
            in_suit = sorted((c for c in me.hand if c.suit == suit),
                             key=lambda c: c.order)
            if in_suit:
                options.append((suit, in_suit))
        for i, (suit, cards) in enumerate(options):
            listing = " ".join("10" if c.rank == "T" else c.rank for c in cards)
            print(f"    [{i}] {SUIT_SYMBOL[suit]} {listing:<16} "
                  f"{len(cards)} cards, {sum(c.pips for c in cards)} pips")
        index = _ask_int("  Declare from which suit? ", 0, len(options) - 1)
        suit, cards = options[index]
        count = _ask_int(f"  Declare how many cards?  "
                         f"(0 = no point at all, max {len(cards)}) ",
                         0, len(cards))
        if count == 0:
            print("  Declaring no point -- your opponent takes the category.")
            return Point(0, 0, None)
        kept = cards[:count]
        declared = Point(count, sum(c.pips for c in kept), suit)
        forfeit = actual.length - count if suit == actual.suit else actual.length
        print(f"  Declaring {declared}, showing "
              f"{' '.join(str(c) for c in kept)}.")
        if forfeit > 0:
            print(f"  (giving up {forfeit} point(s) against your best holding)")
        return declared

    def choose_exchange(self, me, deal, low, high) -> list[Card]:
        cards = sort_hand(me.hand)
        print(f"\n  Your hand:  {show_cards(cards)}")
        print(f"  {me.seat_name} -- you may exchange {low} to {high} cards.")
        self._describe_holding(cards)
        count = _ask_int(f"  How many will you throw? ({low}-{high}) ", low, high)
        chosen: list[Card] = []
        while len(chosen) < count:
            remaining = [c for c in cards if c not in chosen]
            listing = "  ".join(f"[{i}] {c}" for i, c in enumerate(remaining))
            print(f"    {listing}")
            index = _ask_int(f"    throw #{len(chosen) + 1} of {count}: ",
                             0, len(remaining) - 1)
            chosen.append(remaining[index])
        print(f"  Throwing: {' '.join(str(c) for c in chosen)}")
        return chosen

    def _describe_holding(self, cards):
        point = best_point(cards)
        seqs = all_sequences(cards)
        sets_ = all_sets(cards)
        print(f"    point:      {point}")
        print(f"    sequences:  {', '.join(str(s) for s in seqs) or 'none'}")
        print(f"    sets:       {', '.join(str(s) for s in sets_) or 'none'}")

    def choose_card(self, me, deal, legal) -> Card:
        print(f"\n  Trick {deal.trick_number}.  "
              f"Tricks so far -- you {deal.tricks_won[me.seat]}, "
              f"opponent {deal.tricks_won['Y' if me.is_elder else 'E']}.")
        if deal.led_card is not None:
            print(f"  Opponent led {deal.led_card}.")
        else:
            print("  Your lead.")
        print(f"  Your hand:  {show_cards(me.hand)}")
        ordered = sort_hand(legal)
        listing = "  ".join(f"[{i}] {c}" for i, c in enumerate(ordered))
        print(f"  Legal:  {listing}")
        return ordered[_ask_int("  Play which card? ", 0, len(ordered) - 1)]


# --------------------------------------------------------------------------- #
#  Transcript
# --------------------------------------------------------------------------- #

class GameLogger:
    def __init__(self, path: str):
        self.path = path
        self.lines: list[str] = []

    def write(self, text: str = ""):
        self.lines.append(text)

    def flush(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("\n".join(self.lines) + "\n")


# --------------------------------------------------------------------------- #
#  One deal
# --------------------------------------------------------------------------- #

class Deal:
    def __init__(self, elder: Player, younger: Player, rng: random.Random,
                 logger: Optional[GameLogger] = None, number: int = 1,
                 quiet: bool = False):
        self.elder, self.younger = elder, younger
        self.rng, self.logger, self.number, self.quiet = rng, logger, number, quiet

        elder.is_elder, younger.is_elder = True, False
        elder.seat_name, younger.seat_name = "Elder (non-dealer)", "Younger (dealer)"
        for p in (elder, younger):
            p.hand, p.discards, p.seen_talon = [], [], []
            p.tricks, p.deal_score = 0, 0

        deck = make_deck()
        rng.shuffle(deck)
        elder.hand = sort_hand(deck[:12])
        younger.hand = sort_hand(deck[12:24])
        self.talon = deck[24:]
        self.talon_taken = 0

        self.played: list[Card] = []
        self._play_record: list[tuple[str, Card]] = []
        self.led_card: Optional[Card] = None
        self.trick_number = 0
        self.tricks_won = {"E": 0, "Y": 0}
        self.score = {"E": 0, "Y": 0}
        self.declaration_score = {"E": 0, "Y": 0}
        self.category_results: list[CategoryResult] = []
        self.announcements: list[str] = []      # what each seat said out loud
        self.elder_declared_point: Optional[Point] = None
        self.pique_awarded = False

    # -- narration --------------------------------------------------------- #

    def say(self, message: str = ""):
        if not self.quiet:
            print(message)
        if self.logger:
            self.logger.write(message)

    def player(self, seat: str) -> Player:
        return self.elder if seat == "E" else self.younger

    def opponent_of(self, me: Player) -> Player:
        return self.younger if me.is_elder else self.elder

    # -- information available to a seat ----------------------------------- #

    def peek_talon(self, me: Player, size: int) -> list[Card]:
        """The cards this seat would draw by exchanging `size`."""
        start = self.talon_taken
        return self.talon[start:start + size]

    def seen_by(self, me: Player) -> set:
        """Cards this seat knows are out of play: everything played, plus its
        own discards and anything it legitimately looked at in the talon."""
        return set(self.played) | set(me.discards) | set(me.seen_talon)

    def sample_opponent_hands(self, me: Player, limit: int,
                              rng: random.Random) -> list[list[Card]]:
        """Deals for the opponent's remaining cards that are consistent with
        every declaration actually made.  This is the only 'reading' the bot
        does, and it is exactly what a human could do at the table."""
        opponent = self.opponent_of(me)
        need = len(opponent.hand)
        known = set(me.hand) | set(me.discards) | set(self.played) | set(me.seen_talon)
        pool = [c for c in make_deck() if c not in known]
        if len(pool) < need:
            return []

        # Their played cards are public, so any sample of what is left in their
        # hand reconstructs the full twelve they declared from.
        opponent_played = self._cards_played_by(opponent)

        worlds, attempts = [], 0
        while len(worlds) < limit and attempts < limit * 40:
            attempts += 1
            sample = rng.sample(pool, need)
            if self._consistent_with_declarations(opponent, sample + opponent_played):
                worlds.append(sample)
        if not worlds:               # constraints too tight for this budget
            worlds = [rng.sample(pool, need) for _ in range(min(limit, 4))]
        return worlds

    def _cards_played_by(self, who: Player) -> list[Card]:
        return [c for seat, c in self._play_record if seat == who.seat]

    BEST_OF = {"point": lambda h: best_point(h),
               "sequences": lambda h: max(all_sequences(h),
                                          key=lambda s: s.key(), default=None),
               "sets": lambda h: max(all_sets(h),
                                     key=lambda s: s.key(), default=None)}

    def _consistent_with_declarations(self, opponent: Player, hand) -> bool:
        """Would this hypothetical hand have produced the verdicts we actually
        heard?  Rejection sampling -- the reading exercise, done automatically.

        Note how one-sided the information is.  "Good" only tells us their
        holding is *worse* than ours; it is an upper bound, never a fact.
        """
        if len(hand) != 12:
            return True

        for result in self.category_results:
            holding = self.BEST_OF[result.name](hand)
            theirs = holding.key() if holding is not None else (0, 0)

            mine_holding = (result.younger_holding if opponent.is_elder
                            else result.elder_holding)
            mine = mine_holding.key() if mine_holding is not None else (0, 0)

            if result.winner == opponent.seat:
                if not theirs > mine:
                    return False
            elif result.winner == "-":
                if theirs != mine:
                    return False
            else:                                  # we won, so they are worse
                if theirs >= mine:
                    return False
        return True

    # -- scoring helpers ---------------------------------------------------- #

    def award(self, seat: str, points: int, label: str):
        if points == 0:
            return
        self.score[seat] += points
        who = self.player(seat)
        self.say(f"    {who.name} {who.verb('score')} {points:>3}  ({label})"
                 f"   [{self.score['E']} - {self.score['Y']}]")

    # -- the deal ----------------------------------------------------------- #

    def play(self) -> tuple[int, int]:
        self.say("")
        self.say("=" * 66)
        self.say(f"DEAL {self.number}   elder: {self.elder.name}   "
                 f"younger: {self.younger.name}")
        self.say("=" * 66)
        if self.logger:
            self.logger.write(f"  (dealt) elder   {show_cards(self.elder.hand)}")
            self.logger.write(f"  (dealt) younger {show_cards(self.younger.hand)}")
            self.logger.write(f"  (dealt) talon   "
                              f"{' '.join(str(c) for c in self.talon)}")

        self._carte_blanche()
        self._exchange()
        self._declarations()
        self._play_tricks()
        self._settle()
        return self.score["E"], self.score["Y"]

    def _carte_blanche(self):
        for player in (self.elder, self.younger):
            if carte_blanche(player.hand):
                self.say(f"  {player.name} declares carte blanche "
                         f"(no king, queen or jack).")
                self.award(player.seat, 10, "carte blanche")
                self.declaration_score[player.seat] += 10

    def _exchange(self):
        self.say("\n  -- the exchange --")

        # Elder: at least one, at most five, from the top of the talon.
        high = min(5, len(self.talon))
        discard = self._ask_exchange(self.elder, 1, high)
        self._apply_exchange(self.elder, discard)

        # Younger: up to whatever is left.
        remaining = len(self.talon) - self.talon_taken
        if remaining > 0:
            discard = self._ask_exchange(self.younger, 1, remaining)
            self._apply_exchange(self.younger, discard)
        else:
            self.say(f"  {self.younger.name} "
                     f"{self.younger.verb('have') if not self.younger.strategy.is_human else 'have'}"
                     f" nothing left to exchange.")

    def _ask_exchange(self, player: Player, low: int, high: int) -> list[Card]:
        while True:
            discard = player.strategy.choose_exchange(player, self, low, high)
            discard = list(discard)
            if (low <= len(discard) <= high
                    and len(set(discard)) == len(discard)
                    and all(c in player.hand for c in discard)):
                return discard
            print(f"  (illegal exchange from {player.name}; retrying)")

    def _apply_exchange(self, player: Player, discard: list[Card]):
        size = len(discard)
        drawn = self.talon[self.talon_taken:self.talon_taken + size]
        self.talon_taken += size
        for card in discard:
            player.hand.remove(card)
        player.discards.extend(discard)
        player.hand.extend(drawn)
        player.hand = sort_hand(player.hand)

        self.say(f"  {player.name} {player.verb('exchange')} {size}.")
        if self.logger:
            self.logger.write(f"    throws {' '.join(str(c) for c in discard)}"
                              f"   draws {' '.join(str(c) for c in drawn)}")

        # Whatever this seat left behind, it may look at privately.
        if player.is_elder:
            leftovers = self.talon[self.talon_taken:5]
        else:
            leftovers = self.talon[self.talon_taken:]
        if leftovers:
            player.seen_talon.extend(leftovers)
            self.say(f"  {player.name} {player.verb('look')} at the "
                     f"{len(leftovers)} card(s) left behind.")
            if LEFTOVERS_ARE_PUBLIC:
                self.opponent_of(player).seen_talon.extend(leftovers)

    # -- declarations ------------------------------------------------------- #

    def _declarations(self):
        self.say("\n  -- declarations --")
        elder_point = self.elder.strategy.declared_point(
            self.elder, self, best_point(self.elder.hand))
        # Younger hears elder's claim before answering, and may therefore shave
        # a declaration down to exactly what still beats it.  Elder declares
        # blind.  This asymmetry is why elder sinking is a gamble and younger
        # sinking is nearly free.
        self.elder_declared_point = elder_point
        younger_point = self.younger.strategy.declared_point(
            self.younger, self, best_point(self.younger.hand))

        actual_elder = best_point(self.elder.hand)
        if elder_point.key() < actual_elder.key():
            if self.logger:
                self.logger.write(f"    ({self.elder.name} sinks the point: "
                                  f"holds {actual_elder}, declares {elder_point})")

        point = resolve_point(elder_point, younger_point)
        self._announce_point(point)

        sequences = resolve_sequences(all_sequences(self.elder.hand),
                                      all_sequences(self.younger.hand))
        self._announce_combination(sequences, all_sequences(self.elder.hand),
                                   all_sequences(self.younger.hand), "sequence")

        sets_ = resolve_sets(all_sets(self.elder.hand), all_sets(self.younger.hand))
        self._announce_combination(sets_, all_sets(self.elder.hand),
                                   all_sets(self.younger.hand), "set")

        for result in (point, sequences, sets_):
            self.category_results.append(result)
            self.award("E", result.elder_points, result.name)
            self.award("Y", result.younger_points, result.name)
            self.declaration_score["E"] += result.elder_points
            self.declaration_score["Y"] += result.younger_points

        self._check_repique()

    def _announce_point(self, result: CategoryResult):
        elder_point = result.elder_holding
        if elder_point.length == 0:
            self.say(f"    {self.elder.name}: \"No point.\"")
        else:
            self.say(f'    {self.elder.name}: "Point of '
                     f'{NUMBER[elder_point.length]}."')
            verdict = {"E": "Good.", "Y": "Not good.", "-": "Equal."}[result.winner]
            if result.winner == "-":
                self.say(f"    {self.younger.name}: \"Equal.\"   "
                         f"{self.elder.name}: \"Making {elder_point.pips}.\"  "
                         f"{self.younger.name}: \"Equal -- neither scores.\"")
            else:
                self.say(f"    {self.younger.name}: \"{verdict}\"")
        if result.winner == "Y":
            said = str(result.younger_holding)
            self.say(f'    {self.younger.name}: "{said[0].upper()}{said[1:]}."')

    def _announce_combination(self, result, elder_all, younger_all, noun):
        if elder_all:
            self.say(f'    {self.elder.name}: "{_spoken(elder_all)}."')
        else:
            self.say(f'    {self.elder.name}: "No {noun}."')
        verdict = {"E": "Good.", "Y": "Not good.", "-": "Equal."}[result.winner]
        self.say(f"    {self.younger.name}: \"{verdict}\"")
        if result.winner == "Y" and younger_all:
            self.say(f'    {self.younger.name}: "{_spoken(younger_all)}."')

    def _check_repique(self):
        for seat in ("E", "Y"):
            other = "Y" if seat == "E" else "E"
            if self.declaration_score[seat] >= 30 and self.declaration_score[other] == 0:
                self.say(f"    REPIQUE for {self.player(seat).name} "
                         f"-- 30 in declarations before the opponent scored at all.")
                self.award(seat, 60, "repique")
                self.pique_awarded = True       # repique excludes pique

    # -- the play ----------------------------------------------------------- #

    def _play_tricks(self):
        self.say("\n  -- the play --")
        leader, follower = self.elder, self.younger

        for trick in range(1, 13):
            self.trick_number = trick
            self.led_card = None

            lead = self._ask_card(leader)
            self.led_card = lead
            self.award(leader.seat, 1, f"led to trick {trick}")
            self._check_pique()

            reply = self._ask_card(follower)
            self.led_card = None

            if trick_winner(lead, reply) == "follower":
                winner = follower
                self.award(winner.seat, 1, f"took trick {trick} without leading")
                self._check_pique()
            else:
                winner = leader

            self.tricks_won[winner.seat] += 1
            winner.tricks += 1
            elder_card = lead if leader.is_elder else reply
            younger_card = reply if leader.is_elder else lead
            self.say(f"    {trick:>2}.  elder {str(elder_card):<5} "
                     f"younger {str(younger_card):<5}  -> {winner.name}")

            if trick == 12:
                self.award(winner.seat, 1, "last trick")
                self._check_pique()

            leader = winner                     # the winner leads the next trick
            follower = self.opponent_of(leader)

        self._score_the_cards()

    def _ask_card(self, player: Player) -> Card:
        legal = legal_moves(player.hand, self.led_card)
        while True:
            card = player.strategy.choose_card(player, self, legal)
            if card in legal:
                break
            print(f"  (illegal card from {player.name}; retrying)")
        player.hand.remove(card)
        self.played.append(card)
        self._play_record.append((player.seat, card))
        return card

    def _check_pique(self):
        """Elder only: 30 in declarations and play combined before younger has
        scored anything at all.  Repique, if it happened, excludes it."""
        if self.pique_awarded:
            return
        if self.score["Y"] == 0 and self.score["E"] >= 30:
            self.say(f"    PIQUE for {self.elder.name} -- 30 reached in hand "
                     f"and play before younger scored.")
            self.award("E", 30, "pique")
            self.pique_awarded = True

    def _score_the_cards(self):
        e, y = self.tricks_won["E"], self.tricks_won["Y"]
        self.say(f"\n    tricks: elder {e}, younger {y}")
        if e == 12:
            self.award("E", 40, "capot -- all twelve tricks")
        elif y == 12:
            self.award("Y", 40, "capot -- all twelve tricks")
        elif e > 6:
            self.award("E", 10, "the cards")
        elif y > 6:
            self.award("Y", 10, "the cards")
        else:
            self.say("    six all -- neither scores the cards.")

    def _settle(self):
        self.elder.deal_score = self.score["E"]
        self.younger.deal_score = self.score["Y"]
        self.say(f"\n  DEAL {self.number}:  {self.elder.name} {self.score['E']}   "
                 f"{self.younger.name} {self.score['Y']}")


# --------------------------------------------------------------------------- #
#  A partie: six deals and the rubicon
# --------------------------------------------------------------------------- #

class Partie:
    """Six deals, each player elder three times, then rubicon scoring:

        loser reached 100  ->  winner scores (difference) + 100
        loser under 100    ->  winner scores (both totals added) + 100
    """

    def __init__(self, players: tuple[Player, Player], rng: random.Random,
                 deals: int = 6, logger: Optional[GameLogger] = None,
                 quiet: bool = False):
        self.players = players
        self.rng = rng
        self.deals = deals
        self.logger = logger
        self.quiet = quiet
        self.totals = {players[0].name: 0, players[1].name: 0}

    def play(self):
        for index in range(self.deals):
            elder = self.players[index % 2]
            younger = self.players[(index + 1) % 2]
            deal = Deal(elder, younger, self.rng, self.logger,
                        number=index + 1, quiet=self.quiet)
            e_score, y_score = deal.play()
            self.totals[elder.name] += e_score
            self.totals[younger.name] += y_score
            self._report(f"  running totals: "
                         + "   ".join(f"{n} {v}" for n, v in self.totals.items()))
        return self._settle()

    def _report(self, message: str):
        if not self.quiet:
            print(message)
        if self.logger:
            self.logger.write(message)

    def _settle(self):
        (a, b) = self.players
        a_total, b_total = self.totals[a.name], self.totals[b.name]
        self._report("")
        self._report("#" * 66)
        self._report(f"PARTIE OVER   {a.name} {a_total}   {b.name} {b_total}")

        if a_total == b_total:
            self._report("A tie -- no game points.")
            return None

        winner, loser = ((a, b) if a_total > b_total else (b, a))
        win_total = max(a_total, b_total)
        lose_total = min(a_total, b_total)

        if lose_total >= 100:
            game_points = (win_total - lose_total) + 100
            self._report(f"{loser.name} reached 100, so {winner.name} "
                         f"{winner.verb('score')} the difference plus 100.")
        else:
            game_points = (win_total + lose_total) + 100
            self._report(f"RUBICON -- {loser.name} failed to reach 100, so "
                         f"{winner.name} {winner.verb('score')} both totals "
                         f"added, plus 100.")
        winner.partie_score += game_points
        self._report(f"{winner.name} {winner.verb('win')} the partie: "
                     f"{game_points} points.")
        self._report("#" * 66)
        return winner, game_points


# --------------------------------------------------------------------------- #
#  Entry point
# --------------------------------------------------------------------------- #

def build_opponent(choice: str, rng: random.Random) -> tuple[str, Strategy]:
    if choice == "random-style":
        choice = rng.choice(["defensive", "balanced", "aggressive"])
    names = {"defensive": "Colette", "balanced": "Margot",
             "aggressive": "Gaston", "random": "Pierrot"}
    if choice == "random":
        return names["random"], RandomStrategy(rng)
    return names[choice], HeuristicStrategy(STYLES[choice], rng)


def main():
    parser = argparse.ArgumentParser(
        description="Play piquet against a robot opponent.")
    parser.add_argument("--opponent", default="random-style",
                        choices=["defensive", "balanced", "aggressive",
                                 "random", "random-style"],
                        help="opponent style; 'random-style' picks one per "
                             "partie and tells you which afterwards")
    parser.add_argument("--deals", type=int, default=6,
                        help="deals in the partie (6 is standard)")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--watch", action="store_true",
                        help="bot against bot -- no prompts")
    parser.add_argument("--hide-style", action="store_true",
                        help="do not reveal the opponent's style at the end")
    parser.add_argument("--log", default=None, help="transcript path")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    style_name, strategy = build_opponent(args.opponent, rng)

    if args.watch:
        you = Player("Margot", HeuristicStrategy(BALANCED, rng))
    else:
        you = Player("You", HumanStrategy())
    them = Player(style_name, strategy)

    from pathlib import Path
    log_path = args.log or str(Path(__file__).with_name(
        f"piquet_log_{datetime.now():%Y%m%d_%H%M%S}.txt"))
    logger = GameLogger(log_path)
    logger.write("Piquet game transcript (Rubicon scoring)")
    logger.write(f"Generated {datetime.now():%Y-%m-%d %H:%M:%S}")
    logger.write(f"Opponent: {them.name}")
    logger.write("Contains both hands and the talon so the play can be reviewed.")
    logger.write("")

    print(f"\nPiquet -- a partie of {args.deals} deals against {them.name}.")
    print("32 cards, no trumps.  Elder alternates each deal.")
    if not args.hide_style and args.opponent != "random-style":
        article = "an" if args.opponent[0] in "aeiou" else "a"
        print(f"{them.name} plays {article} {args.opponent} game.")

    partie = Partie((you, them), rng, deals=args.deals,
                    logger=logger, quiet=False)
    partie.play()

    if args.opponent == "random-style" and not args.hide_style:
        revealed = (strategy.style.name if isinstance(strategy, HeuristicStrategy)
                    else "random")
        article = "an" if revealed[0] in "aeiou" else "a"
        print(f"\n({them.name} was playing {article} {revealed} game.)")

    logger.flush()
    print(f"\nTranscript written to: {logger.path}")
    print("Hand that file to Claude for a critique of your discards and play.")


if __name__ == "__main__":
    main()
