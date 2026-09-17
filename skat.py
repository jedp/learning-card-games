"""A playable game of Skat (Suit games + Grand) with injectable strategies.

Run it:      python3 skat.py

The design separates three things on purpose:

  * The *rules engine*  -- cards, trump logic, legal moves, who wins a trick,
    matador counting, and scoring.  This is objective and never makes choices.
  * The *table*         -- SkatRound orchestrates one deal: auction, the pickup
    and discard, ten tricks, and the score.  It asks players to choose but does
    not decide for them.
  * The *strategies*    -- each Player owns a Strategy that answers three
    questions: how high will you bid, what game do you declare, and which card
    do you play.  Swap the Strategy and you swap the playing style.  A human is
    just a Strategy that asks you at a prompt.

Only Suit games and Grand are implemented.  Null (declarer tries to take no
trick, no trump, different rank order) is the natural next extension -- see the
note at the bottom of the file.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import NamedTuple, Optional


# --------------------------------------------------------------------------- #
#  Cards
# --------------------------------------------------------------------------- #

class Suit(Enum):
    """The four suits.  `jack_ordering` ranks the Jacks: clubs beat spades beat
    hearts beat diamonds.  It doubles as a stable display order."""
    CLUBS = ("♣", 4)
    SPADES = ("♠", 3)
    HEARTS = ("♥", 2)
    DIAMONDS = ("♦", 1)

    def __init__(self, symbol: str, jack_ordering: int):
        self.symbol = symbol
        self.jack_ordering = jack_ordering


class Rank(Enum):
    """Ranks with three facts attached:
      * `plain_ordering` -- strength inside an ordinary suit in Suit/Grand games
        (Ace high, then Ten -- the Ten sits *above* the King).
      * `card_points`    -- what the card is worth when captured.
      * `null_ordering`  -- strength in a Null game, where the order is the
        natural 7-8-9-10-J-Q-K-A: the Ten drops back between the 9 and the Jack,
        and Jacks are ordinary cards of their suit, not trumps."""
    SEVEN = ("7", 0, 0, 0)
    EIGHT = ("8", 1, 0, 1)
    NINE = ("9", 2, 0, 2)
    QUEEN = ("Q", 3, 3, 5)
    KING = ("K", 4, 4, 6)
    TEN = ("10", 5, 10, 3)
    ACE = ("A", 6, 11, 7)
    JACK = ("J", 7, 2, 4)   # plain_ordering unused; in Null a Jack ranks here

    def __init__(self, label: str, plain_ordering: int, card_points: int,
                 null_ordering: int):
        self.label = label
        self.plain_ordering = plain_ordering
        self.card_points = card_points
        self.null_ordering = null_ordering


@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit

    @property
    def card_points(self) -> int:
        return self.rank.card_points

    def __str__(self) -> str:
        return f"{self.rank.label}{self.suit.symbol}"


def make_deck() -> list[Card]:
    """The 32-card Skat pack: 7 through Ace in every suit."""
    return [Card(rank, suit) for suit in Suit for rank in Rank]


# --------------------------------------------------------------------------- #
#  Contracts and trump logic
# --------------------------------------------------------------------------- #

class GameType(Enum):
    SUIT = "suit"     # a chosen suit + the four Jacks are trump
    GRAND = "grand"   # only the four Jacks are trump
    NULL = "null"     # no trump at all; declarer tries to take zero tricks


SUIT_BASE_VALUE = {Suit.DIAMONDS: 9, Suit.HEARTS: 10, Suit.SPADES: 11, Suit.CLUBS: 12}
GRAND_BASE_VALUE = 24
NULL_VALUE = 23
NULL_OUVERT_VALUE = 46   # declarer plays with the hand exposed

# A sentinel meaning "the trump family" when we ask what suit must be followed.
TRUMP_GROUP = "trump"


@dataclass
class Contract:
    game_type: GameType
    trump_suit: Optional[Suit] = None   # None for Grand/Null
    declarer: Optional["Player"] = None
    ouvert: bool = False                 # Null only: hand played face up


@dataclass
class Declaration:
    """What a strategy announces after winning the auction (before we attach the
    declarer and turn it into a live Contract)."""
    game_type: GameType
    trump_suit: Optional[Suit] = None
    ouvert: bool = False


def is_trump(card: Card, contract: Contract) -> bool:
    if contract.game_type is GameType.NULL:
        return False                     # Null has no trumps, not even Jacks
    if card.rank is Rank.JACK:
        return True
    if contract.game_type is GameType.GRAND:
        return False
    return card.suit is contract.trump_suit


def suit_rank(card: Card, contract: Contract) -> int:
    """Strength within a plain suit, respecting Null's different order."""
    if contract.game_type is GameType.NULL:
        return card.rank.null_ordering
    return card.rank.plain_ordering


def following_group(card: Card, contract: Contract):
    """Which 'suit' a card belongs to for the purpose of following suit.  All
    trumps (including the Jacks) belong to one group."""
    return TRUMP_GROUP if is_trump(card, contract) else card.suit


def trick_strength(card: Card, contract: Contract) -> tuple[int, int]:
    """A sortable strength.  Higher wins.  Only meaningful when comparing cards
    that are actually eligible to win the trick (same group, or trumps)."""
    if is_trump(card, contract):
        if card.rank is Rank.JACK:
            return (2, card.suit.jack_ordering)      # Jacks: the top tier
        return (1, card.rank.plain_ordering)         # trump-suit pip cards
    return (0, suit_rank(card, contract))            # plain-suit cards


def card_outranks(challenger: Card, holder: Card, contract: Contract) -> bool:
    """Would `challenger` beat `holder` if both were live in the same trick?
    Used by counting players to reason about outstanding cards."""
    ch, ho = is_trump(challenger, contract), is_trump(holder, contract)
    if ch != ho:
        return ch                                    # a trump beats a non-trump
    if ch and ho:
        return trick_strength(challenger, contract) > trick_strength(holder, contract)
    return (challenger.suit is holder.suit
            and suit_rank(challenger, contract) > suit_rank(holder, contract))


def describe(contract: Contract) -> str:
    if contract.game_type is GameType.GRAND:
        return "Grand"
    if contract.game_type is GameType.NULL:
        return "Null Ouvert" if contract.ouvert else "Null"
    return contract.trump_suit.name.title()


def legal_moves(hand: list[Card], led: Optional[Card], contract: Contract) -> list[Card]:
    """You must follow the group that was led if you can; otherwise anything."""
    if led is None:
        return list(hand)
    led_group = following_group(led, contract)
    same = [c for c in hand if following_group(c, contract) == led_group]
    return same if same else list(hand)


def trick_winner(plays: list[tuple["Player", Card]], contract: Contract) -> "Player":
    """Highest trump wins; if no trump was played, the highest card of the led
    group wins.  Works on a partial trick too (useful for bots looking ahead)."""
    led_group = following_group(plays[0][1], contract)
    trumps = [(p, c) for p, c in plays if is_trump(c, contract)]
    if trumps:
        return max(trumps, key=lambda pc: trick_strength(pc[1], contract))[0]
    followers = [(p, c) for p, c in plays if following_group(c, contract) == led_group]
    return max(followers, key=lambda pc: suit_rank(pc[1], contract))[0]


# --------------------------------------------------------------------------- #
#  Matadors ("with / without") and the game value
# --------------------------------------------------------------------------- #

def matador_sequence(contract: Contract) -> list[Card]:
    """The chain of top trumps, from J-clubs downward, used to count matadors."""
    jacks = [Card(Rank.JACK, s) for s in Suit]  # clubs, spades, hearts, diamonds
    if contract.game_type is GameType.GRAND:
        return jacks
    pips = [Card(r, contract.trump_suit)
            for r in (Rank.ACE, Rank.TEN, Rank.KING, Rank.QUEEN,
                      Rank.NINE, Rank.EIGHT, Rank.SEVEN)]
    return jacks + pips


def count_matadors(cards, contract: Contract) -> int:
    """'With N' if you hold the top N trumps unbroken from J-clubs down;
    'without N' if you are missing the top N.  Either way we return N -- the
    multiplier only cares about the number."""
    sequence = matador_sequence(contract)
    held = set(cards)
    playing_with = sequence[0] in held
    count = 0
    for card in sequence:
        if (card in held) == playing_with:
            count += 1
        else:
            break
    return count


class Scoresheet(NamedTuple):
    declarer_points: int
    base_value: int
    matadors: int
    multiplier: int
    game_value: int
    made: bool
    schneider: bool
    schwarz: bool
    overbid: bool


def score_round(contract: Contract, declarer_cards, declarer_points: int,
                declarer_tricks: int, bid: int) -> Scoresheet:
    """Compute the game value and whether the declarer made the contract."""
    if contract.game_type is GameType.NULL:
        # No matadors, no card points, no Schneider: it is all-or-nothing on
        # whether the declarer took a single trick.
        value = NULL_OUVERT_VALUE if contract.ouvert else NULL_VALUE
        overbid = value < bid
        made = (declarer_tricks == 0) and not overbid
        return Scoresheet(declarer_points, value, 0, 1, value, made, False, False, overbid)

    base = (GRAND_BASE_VALUE if contract.game_type is GameType.GRAND
            else SUIT_BASE_VALUE[contract.trump_suit])
    matadors = count_matadors(declarer_cards, contract)

    opponents_points = 120 - declarer_points
    schneider = declarer_points >= 90 or opponents_points >= 90
    schwarz = declarer_tricks == 10 or declarer_tricks == 0

    multiplier = matadors + 1 + (1 if schneider else 0) + (1 if schwarz else 0)
    game_value = base * multiplier

    overbid = game_value < bid
    made = (declarer_points >= 61) and not overbid
    return Scoresheet(declarer_points, base, matadors, multiplier,
                      game_value, made, schneider, schwarz, overbid)


# --------------------------------------------------------------------------- #
#  Players and the Strategy interface
# --------------------------------------------------------------------------- #

class Player:
    def __init__(self, name: str, strategy: "Strategy"):
        self.name = name
        self.strategy = strategy
        self.hand: list[Card] = []
        self.won_cards: list[Card] = []   # cards captured in tricks this round
        self.tricks = 0
        self.match_score = 0

    @property
    def captured_points(self) -> int:
        return sum(c.card_points for c in self.won_cards)

    def __str__(self) -> str:
        return self.name


class GameEstimate(NamedTuple):
    """A bot's read on one possible contract from its own hand."""
    game_type: GameType
    trump_suit: Optional[Suit]
    matadors: int
    game_value: int
    strength: float


class Strategy(ABC):
    """The three decisions a player makes.  Implement these and you have a new
    style of play."""

    @abstractmethod
    def decide_bid_limit(self, me: Player, table: "SkatRound") -> int:
        """The highest game value this player is willing to be committed to.
        Return 0 to pass."""

    @abstractmethod
    def declare_contract(self, me: Player, table: "SkatRound"):
        """After winning the auction and picking up the Skat (so `me.hand` has
        12 cards), return (GameType, trump_suit or None, [two cards to discard])."""

    @abstractmethod
    def choose_card(self, me: Player, table: "SkatRound", legal: list[Card]) -> Card:
        """Pick one card from `legal` to play into the current trick."""


# --------------------------------------------------------------------------- #
#  A heuristic bot, tunable into different styles
# --------------------------------------------------------------------------- #

def _strength_index(card: Card, contract: Contract) -> int:
    """Flatten trick_strength into one number for sorting a hand nicely."""
    tier, sub = trick_strength(card, contract)
    return tier * 100 + sub


class HeuristicStrategy(Strategy):
    """One brain, several personalities.  `bid_threshold` sets how strong a hand
    it insists on before committing; `aggression` sets how eagerly it draws
    trumps and fights for tricks; `plays_grand` lets it consider Grand."""

    def __init__(self, bid_threshold: float, aggression: float,
                 plays_grand: bool = True, plays_null: bool = True):
        self.bid_threshold = bid_threshold
        self.aggression = aggression
        self.plays_grand = plays_grand
        self.plays_null = plays_null

    # -- bidding ---------------------------------------------------------- #
    def _best_game(self, hand) -> Optional[GameEstimate]:
        viable = [g for g in evaluate_games(hand, self.plays_grand, self.plays_null)
                  if g.strength >= self.bid_threshold]
        return max(viable, key=lambda g: g.game_value) if viable else None

    def decide_bid_limit(self, me: Player, table: "SkatRound") -> int:
        best = self._best_game(me.hand)
        return best.game_value if best else 0

    # -- declaring & discarding ------------------------------------------ #
    def declare_contract(self, me: Player, table: "SkatRound"):
        # Re-evaluate on the fuller 12-card hand.  Take the highest-value game
        # the hand can actually support; only fall back to raw value if nothing
        # clears the confidence bar.
        options = evaluate_games(me.hand, self.plays_grand, self.plays_null)
        supported = [g for g in options if g.strength >= self.bid_threshold]
        chosen = (max(supported, key=lambda g: g.game_value) if supported
                  else max(options, key=lambda g: g.strength))
        contract = Contract(chosen.game_type, chosen.trump_suit, me)
        discards = self._pick_discards(me.hand, contract)
        return Declaration(chosen.game_type, chosen.trump_suit), discards

    def _pick_discards(self, twelve, contract: Contract) -> list[Card]:
        if contract.game_type is GameType.NULL:
            # Shed the two most dangerous (highest) cards -- Aces first.
            return sorted(twelve, key=lambda c: -c.rank.null_ordering)[:2]
        # Otherwise keep trumps and Aces; shed the lowest 'keep value' cards.
        def keep_value(card: Card) -> int:
            if is_trump(card, contract):
                return 100 + _strength_index(card, contract)
            if card.rank is Rank.ACE:
                return 60
            if card.rank is Rank.TEN:
                return 25
            return card.card_points
        return sorted(twelve, key=keep_value)[:2]

    # -- playing ---------------------------------------------------------- #
    def choose_card(self, me: Player, table: "SkatRound", legal: list[Card]) -> Card:
        if table.contract.game_type is GameType.NULL:
            return play_to_lose(me, table, legal)   # nobody wants a trick... mostly
        if not table.current_trick:
            return self._lead(me, table, legal)
        return self._follow(me, table, legal)

    def _lead(self, me: Player, table: "SkatRound", legal) -> Card:
        contract = table.contract
        if table.is_declarer(me):
            my_trumps = [c for c in legal if is_trump(c, contract)]
            if my_trumps and table.opponents_hold_trump(me) and self.aggression > 0.3:
                return max(my_trumps, key=lambda c: _strength_index(c, contract))
        # Defender or a declarer with trumps already drawn: cash an Ace, else
        # get out cheaply with a low side card.
        side_aces = [c for c in legal if c.rank is Rank.ACE and not is_trump(c, contract)]
        if side_aces:
            return side_aces[0]
        side = [c for c in legal if not is_trump(c, contract)] or legal
        return min(side, key=lambda c: c.card_points)

    def _follow(self, me: Player, table: "SkatRound", legal) -> Card:
        contract = table.contract
        leader = table.current_winner()
        winning = [c for c in legal if table.would_win(me, c)]

        if table.same_side(me, leader):
            # Our side is winning this trick -> smear points onto it without
            # needlessly overtaking a partner.
            keep_it_ours = [c for c in legal if c not in winning] or legal
            return max(keep_it_ours, key=lambda c: c.card_points)

        # The other side is winning.
        pot = sum(c.card_points for _, c in table.current_trick)
        worth_taking = pot > 0 or table.is_declarer(me) or self.aggression > 0.6
        if winning and worth_taking:
            return min(winning, key=lambda c: (c.card_points, _strength_index(c, contract)))
        # Can't or won't win: starve the trick with our cheapest card.
        return min(legal, key=lambda c: c.card_points)


def CautiousStrategy() -> HeuristicStrategy:
    """Bids only strong hands, plays it safe."""
    return HeuristicStrategy(bid_threshold=8.0, aggression=0.2)


def AggressiveStrategy() -> HeuristicStrategy:
    """Bids thin, hunts trumps and tricks."""
    return HeuristicStrategy(bid_threshold=5.5, aggression=0.9)


def play_to_lose(me: Player, table: "SkatRound", legal: list[Card]) -> Card:
    """Null play, generic version: shed the highest card you can without taking
    the trick; if every legal card would win, surrender the cheapest."""
    non_winning = [c for c in legal if not table.would_win(me, c)]
    if non_winning:
        return max(non_winning, key=lambda c: c.rank.null_ordering)
    return min(legal, key=lambda c: c.rank.null_ordering)


class CardCountingDefender(HeuristicStrategy):
    """A defender that remembers what has been played and reasons from it.

    It uses the table's public history (`played_cards`, `completed_tricks`) to:
      * know when the declarer can no longer ruff (all trumps accounted for),
        so side-suit Aces are safe to cash;
      * avoid leading a suit the declarer has shown void in (which would just
        donate a ruff);
      * smear onto a partner's trick only when no outstanding card can overtake
        it, and never waste a high card the last opponent could beat;
      * defend Null by trying to force a trick onto the declarer.

    When it happens to be the declarer, it just plays the inherited heuristic.
    """

    # -- defence: leading ------------------------------------------------- #
    def _lead_defender(self, me, table, legal):
        contract = table.contract
        declarer_void = table.declarer_void_suits()
        # A side Ace wins outright unless the declarer can ruff it -- i.e. unless
        # the declarer is (known) void in that suit.
        aces = [c for c in legal if c.rank is Rank.ACE
                and not is_trump(c, contract) and c.suit not in declarer_void]
        if aces:
            return max(aces, key=lambda c: sum(1 for x in me.hand if x.suit is c.suit))
        # Otherwise get out low, through the declarer, not into a known void.
        safe = [c for c in legal if not is_trump(c, contract) and c.suit not in declarer_void]
        pool = safe or [c for c in legal if not is_trump(c, contract)] or legal
        return min(pool, key=lambda c: c.card_points)

    # -- defence: following ----------------------------------------------- #
    def _follow_defender(self, me, table, legal):
        contract = table.contract
        leader = table.current_winner()
        winning_card = dict(table.current_trick)[leader]
        unseen = table.unseen_cards(me)
        last_to_play = table.is_last_to_play()

        if table.same_side(me, leader):
            # Partner is winning: pile on points, but stay under partner so we
            # don't hand the lead back, and don't burn an Ace if the last hand
            # could still overtake.
            keep_ours = [c for c in legal if not table.would_win(me, c)] or legal
            overtakeable = any(card_outranks(x, winning_card, contract) for x in unseen)
            if last_to_play or not overtakeable:
                return max(keep_ours, key=lambda c: c.card_points)   # safe smear
            safe = [c for c in keep_ours if c.rank is not Rank.ACE] or keep_ours
            return max(safe, key=lambda c: c.card_points)

        # Declarer is winning.  Take the trick if we safely can; else starve.
        winners = [c for c in legal if table.would_win(me, c)]
        if winners:
            take = min(winners, key=lambda c: (c.card_points, _strength_index(c, contract)))
            beatable = any(card_outranks(x, take, contract) for x in unseen)
            if last_to_play or not beatable:
                return take
        return min(legal, key=lambda c: c.card_points)              # starve

    # -- defence against a Null contract ---------------------------------- #
    def _defend_null(self, me, table, legal):
        # The declarer is trying to take zero tricks; our job is to force one on
        # them.  If the declarer has already played and is currently winning,
        # keep it that way and dump our highest card under theirs.  Otherwise,
        # avoid winning ourselves and unload high cards.
        if not table.current_trick:
            # Lead low from our longest suit to squeeze the declarer.
            by_len = {}
            for c in legal:
                by_len.setdefault(c.suit, []).append(c)
            longest = max(by_len.values(), key=len)
            return min(longest, key=lambda c: c.rank.null_ordering)

        leader = table.current_winner()
        declarer_leads_trick = any(p is table.declarer for p, _ in table.current_trick)
        if declarer_leads_trick and table.is_declarer(leader):
            # Declarer is winning -- let them keep it; shed our biggest card under.
            under = [c for c in legal if not table.would_win(me, c)]
            pool = under or legal
            return max(pool, key=lambda c: c.rank.null_ordering)
        return play_to_lose(me, table, legal)

    def choose_card(self, me, table, legal):
        if table.is_declarer(me):
            return super().choose_card(me, table, legal)     # declare? play normally
        if table.contract.game_type is GameType.NULL:
            return self._defend_null(me, table, legal)
        if not table.current_trick:
            return self._lead_defender(me, table, legal)
        return self._follow_defender(me, table, legal)


def CountingDefenderStrategy() -> CardCountingDefender:
    """A solid, card-counting opponent (plays a normal game when it declares)."""
    return CardCountingDefender(bid_threshold=7.0, aggression=0.5)


class RandomStrategy(Strategy):
    """A baseline that always passes and plays a legal card at random."""

    def decide_bid_limit(self, me, table):
        return 0

    def declare_contract(self, me, table):
        best = max(evaluate_games(me.hand, True), key=lambda g: g.game_value)
        return Declaration(best.game_type, best.trump_suit), me.hand[:2]

    def choose_card(self, me, table, legal):
        return random.choice(legal)


def null_risk(hand) -> float:
    """How dangerous a hand is for a Null game -- lower is safer.  You lose Null
    the moment you are forced to win a trick, so Aces are poison, high cards want
    low cards beneath them to duck under, and voids are pure safety."""
    risk = 0.0
    for suit in Suit:
        cards = sorted((c for c in hand if c.suit is suit),
                       key=lambda c: c.rank.null_ordering)
        if not cards:
            continue                                 # a void suit is perfectly safe
        risk += cards[0].rank.null_ordering * 0.5    # a high *lowest* card can't duck
        risk += sum(2.5 for c in cards if c.rank is Rank.ACE)
        risk += sum(1.0 for c in cards if c.rank is Rank.KING)
        lows = sum(1 for c in cards if c.rank.null_ordering <= 2)   # 7, 8, 9
        highs = sum(1 for c in cards if c.rank.null_ordering >= 4)  # J, Q, K, A
        risk += max(0, highs - lows)                 # unguarded high cards
    return risk


def evaluate_games(hand, allow_grand: bool, allow_null: bool = False) -> list[GameEstimate]:
    """Score every contract this hand could declare.  `strength` is a rough
    trick-taking estimate (for Null, a safety estimate); `game_value` is the real
    base x (matadors + 1), or the fixed Null value."""
    def strength(contract: Contract) -> float:
        trumps = sum(1 for c in hand if is_trump(c, contract))
        aces = sum(1 for c in hand if c.rank is Rank.ACE)
        tens = sum(1 for c in hand if c.rank is Rank.TEN)
        return 1.3 * trumps + 1.6 * aces + 0.6 * tens

    estimates = []
    for suit in Suit:
        contract = Contract(GameType.SUIT, suit)
        m = count_matadors(hand, contract)
        estimates.append(GameEstimate(GameType.SUIT, suit, m,
                                      SUIT_BASE_VALUE[suit] * (m + 1), strength(contract)))
    if allow_grand:
        contract = Contract(GameType.GRAND)
        m = count_matadors(hand, contract)
        estimates.append(GameEstimate(GameType.GRAND, None, m,
                                      GRAND_BASE_VALUE * (m + 1), strength(contract)))
    if allow_null:
        # Map "low risk" onto the same strength scale the bots gate on: only a
        # genuinely safe hand clears a normal bidding threshold.
        estimates.append(GameEstimate(GameType.NULL, None, 0,
                                      NULL_VALUE, max(0.0, 12.0 - null_risk(hand))))
    return estimates


# --------------------------------------------------------------------------- #
#  The human at the keyboard -- also just a Strategy
# --------------------------------------------------------------------------- #

def display_sort_key(card: Card, contract: Optional[Contract]):
    """Order a hand for display: trumps first (strongest first), then suits with
    the highest rank first.  Respects Null's rank order when a Null is in play."""
    if contract and is_trump(card, contract):
        return (0, -_strength_index(card, contract))
    rank_value = suit_rank(card, contract) if contract else card.rank.plain_ordering
    return (1, -card.suit.jack_ordering, -rank_value)


def show_cards(cards, contract: Optional[Contract] = None) -> str:
    ordered = sorted(cards, key=lambda c: display_sort_key(c, contract))
    return "  ".join(f"[{i}] {c}" for i, c in enumerate(ordered))


def fmt_cards(cards, contract: Optional[Contract] = None) -> str:
    """A clean, index-free card list for the transcript."""
    ordered = sorted(cards, key=lambda c: display_sort_key(c, contract))
    return " ".join(str(c) for c in ordered)


def _ask_int(prompt: str, low: int, high: int) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
        except (ValueError, EOFError):
            print("  (please type a number)")
            continue
        if low <= value <= high:
            return value
        print(f"  (choose between {low} and {high})")


class HumanStrategy(Strategy):

    def decide_bid_limit(self, me: Player, table: "SkatRound") -> int:
        print(f"\nYour hand: {show_cards(me.hand)}")
        best = max(evaluate_games(me.hand, True, True), key=lambda g: g.game_value)
        if best.game_type is GameType.GRAND:
            label, detail = "Grand", f"with/without {best.matadors}"
        elif best.game_type is GameType.NULL:
            label, detail = "Null", "no trumps, take no trick"
        else:
            label, detail = best.trump_suit.name.title(), f"with/without {best.matadors}"
        print(f"  Your strongest game looks like {label}: {detail}, worth {best.game_value}.")
        print(f"  (Null risk score {null_risk(me.hand):.1f} - lower is safer for Null.)")
        return _ask_int("  Your maximum bid (0 to pass): ", 0, 300)

    def declare_contract(self, me: Player, table: "SkatRound"):
        print(f"\nYou won the auction at {table.winning_bid}.  Your 12 cards:")
        print(f"  {show_cards(me.hand)}")
        print("  Games:  [C]lubs [S]pades [H]earts [D]iamonds "
              "[G]rand [N]ull [O]=Null Ouvert")
        letter_to_suit = {"C": Suit.CLUBS, "S": Suit.SPADES,
                          "H": Suit.HEARTS, "D": Suit.DIAMONDS}
        while True:
            choice = input("  Declare which game? ").strip().upper()[:1]
            if choice == "G":
                declaration = Declaration(GameType.GRAND)
            elif choice == "N":
                declaration = Declaration(GameType.NULL)
            elif choice == "O":
                declaration = Declaration(GameType.NULL, ouvert=True)
            elif choice in letter_to_suit:
                declaration = Declaration(GameType.SUIT, letter_to_suit[choice])
            else:
                print("  (type C, S, H, D, G, N or O)")
                continue
            break
        contract = Contract(declaration.game_type, declaration.trump_suit,
                            me, declaration.ouvert)
        if declaration.game_type is GameType.NULL:
            print("  Null: order is 7-8-9-10-J-Q-K-A, no trumps. "
                  "Discard your most dangerous high cards.")
        else:
            print(f"  Trumps are: "
                  f"{show_cards([c for c in me.hand if is_trump(c, contract)], contract)}")
        discards = []
        for n in ("first", "second"):
            remaining = [c for c in me.hand if c not in discards]
            print(f"  {show_cards(remaining, contract)}")
            idx = _ask_int(f"  Discard your {n} card into the Skat [index]: ",
                           0, len(remaining) - 1)
            ordered = sorted(remaining, key=lambda c: display_sort_key(c, contract))
            discards.append(ordered[idx])
        return declaration, discards

    def choose_card(self, me: Player, table: "SkatRound", legal: list[Card]) -> Card:
        contract = table.contract
        if table.current_trick:
            played = "   ".join(f"{p.name}: {c}" for p, c in table.current_trick)
            print(f"\n  Trick so far -> {played}")
        else:
            print("\n  Your lead.")
        role = "declarer" if table.is_declarer(me) else "defender"
        if contract.game_type is GameType.NULL and not table.is_declarer(me):
            role = "defender (try to force a trick onto the declarer!)"
        print(f"  You ({role}).  Legal: {show_cards(legal, contract)}")
        ordered = sorted(legal, key=lambda c: display_sort_key(c, contract))
        idx = _ask_int("  Play which card [index]? ", 0, len(ordered) - 1)
        return ordered[idx]


# --------------------------------------------------------------------------- #
#  One deal, start to finish
# --------------------------------------------------------------------------- #

class GameLogger:
    """Accumulates a full, analysis-ready transcript -- including every hand and
    the Skat -- and writes it to a file at the end of the match."""

    def __init__(self, path: str):
        self.path = path
        self.lines: list[str] = []

    def write(self, line: str = ""):
        self.lines.append(line)

    def flush(self):
        with open(self.path, "w") as fh:
            fh.write("\n".join(self.lines) + "\n")


class SkatRound:
    def __init__(self, players: list[Player], dealer_index: int,
                 logger: Optional[GameLogger] = None, hand_number: int = 1):
        self.players = players
        self.dealer_index = dealer_index
        self.logger = logger
        self.hand_number = hand_number
        # Seats: forehand leads, then middlehand, then rearhand (the dealer).
        self.forehand = players[(dealer_index + 1) % 3]
        self.middlehand = players[(dealer_index + 2) % 3]
        self.rearhand = players[dealer_index]
        self.order = [self.forehand, self.middlehand, self.rearhand]

        self.skat: list[Card] = []
        self.skat_discards: list[Card] = []
        self.contract: Optional[Contract] = None
        self.declarer: Optional[Player] = None
        self.declarer_twelve: list[Card] = []   # snapshot for matador counting
        self.winning_bid = 0
        self.current_trick: list[tuple[Player, Card]] = []
        self.played_cards: list[Card] = []
        self.completed_tricks: list[list[tuple[Player, Card]]] = []
        self.dealt: dict[Player, list[Card]] = {}     # snapshot for the transcript
        self.declarer_hand10: list[Card] = []

    # -- transcript ------------------------------------------------------- #
    def log(self, line: str = ""):
        if self.logger is not None:
            self.logger.write(line)

    def _tag(self, p: Player) -> str:
        human = isinstance(p.strategy, HumanStrategy)
        seat = ("forehand" if p is self.forehand else
                "middlehand" if p is self.middlehand else "rearhand")
        return f"{p.name} ({seat}{', human' if human else ''})"

    # -- small helpers the strategies lean on ----------------------------- #
    def is_declarer(self, p: Player) -> bool:
        return p is self.declarer

    def same_side(self, a: Player, b: Player) -> bool:
        return self.is_declarer(a) == self.is_declarer(b)

    def defenders(self) -> list[Player]:
        return [p for p in self.order if p is not self.declarer]

    def current_winner(self) -> Player:
        return trick_winner(self.current_trick, self.contract)

    def would_win(self, me: Player, card: Card) -> bool:
        hypothetical = self.current_trick + [(me, card)]
        return trick_winner(hypothetical, self.contract) is me

    def opponents_hold_trump(self, me: Player) -> bool:
        seen = set(self.played_cards) | set(me.hand)
        return any(is_trump(c, self.contract) and c not in seen for c in make_deck())

    # -- history the card-counting players read --------------------------- #
    def unseen_cards(self, me: Player) -> list[Card]:
        """Cards `me` cannot account for: still in other hands or the Skat."""
        seen = set(self.played_cards) | set(me.hand)
        return [c for c in make_deck() if c not in seen]

    def is_last_to_play(self) -> bool:
        """True if the player about to act is the third (final) card this trick."""
        return len(self.current_trick) == 2

    def declarer_void_suits(self) -> set:
        """Suits the declarer has *shown* void in by failing to follow them."""
        voids = set()
        for trick in self.completed_tricks:
            led_group = following_group(trick[0][1], self.contract)
            if led_group is TRUMP_GROUP:
                continue
            for player, card in trick:
                if player is self.declarer and following_group(card, self.contract) != led_group:
                    voids.add(led_group)
        return voids

    def legal_for(self, p: Player) -> list[Card]:
        led = self.current_trick[0][1] if self.current_trick else None
        return legal_moves(p.hand, led, self.contract)

    def next_player(self, p: Player) -> Player:
        return self.order[(self.order.index(p) + 1) % 3]

    # -- phases ----------------------------------------------------------- #
    def deal(self):
        deck = make_deck()
        random.shuffle(deck)
        for i, seat in enumerate(self.order):
            seat.hand = deck[i * 10:(i + 1) * 10]
        self.skat = deck[30:32]
        self.dealt = {p: list(p.hand) for p in self.order}

        self.log("=" * 70)
        self.log(f"HAND {self.hand_number}   (dealer: {self.rearhand.name})")
        self.log("=" * 70)
        self.log("Dealt hands (hidden info, for analysis):")
        for seat in self.order:
            self.log(f"  {self._tag(seat):<28} {fmt_cards(seat.hand)}")
        self.log(f"  Skat (face down):            {fmt_cards(self.skat)}")

    def run_auction(self) -> Optional[Player]:
        limits = {p: p.strategy.decide_bid_limit(p, self) for p in self.order}
        self.log("")
        self.log("Auction:")
        for p in self.order:
            self.log(f"  {self._tag(p):<28} willing up to {limits[p]}")
        if max(limits.values()) < 18:
            self.log("  -> all passed; hand thrown in.")
            return None  # everyone passed -> the hand is thrown in
        # Highest limit wins; ties go to the earlier seat (they held first).
        winner = max(self.order, key=lambda p: (limits[p], -self.order.index(p)))
        contest = max(limits[p] for p in self.order if p is not winner)
        ladder = valid_bids()
        playable = [v for v in ladder if v <= contest]
        self.winning_bid = max(playable) if playable else 18
        self.declarer = winner
        self.contract = None
        self.log(f"  -> {self._tag(winner)} wins at {self.winning_bid}.")
        print(f"\n{winner.name} wins the auction at {self.winning_bid}.")
        return winner

    def declaration_phase(self):
        d = self.declarer
        d.hand = d.hand + self.skat  # pick up the Skat -> 12 cards
        declaration, discards = d.strategy.declare_contract(d, self)
        self.contract = Contract(declaration.game_type, declaration.trump_suit,
                                 d, declaration.ouvert)
        self.skat_discards = list(discards)
        for c in discards:
            d.hand.remove(c)
        self.declarer_twelve = d.hand + self.skat_discards  # the 12 held
        self.declarer_hand10 = list(d.hand)
        print(f"{d.name} declares {describe(self.contract)}.")
        if self.contract.ouvert:
            print(f"  (open hand) {show_cards(d.hand, self.contract)}")

        self.log("")
        self.log(f"Declaration: {self._tag(d)} declares {describe(self.contract)}.")
        self.log(f"  Picked up Skat {fmt_cards(self.skat)}; "
                 f"discarded {fmt_cards(self.skat_discards)} "
                 f"({sum(c.card_points for c in self.skat_discards)} pts banked).")
        self.log(f"  Declarer's 10: {fmt_cards(self.declarer_hand10, self.contract)}")
        if self.contract.game_type is not GameType.NULL:
            trumps = [c for c in self.declarer_hand10 if is_trump(c, self.contract)]
            self.log(f"  Declarer's trumps: {fmt_cards(trumps, self.contract)}")

    def play_tricks(self):
        is_null = self.contract.game_type is GameType.NULL
        self.log("")
        self.log(f"Play (declarer = {self.declarer.name}, "
                 f"defenders = {', '.join(p.name for p in self.defenders())}):")
        declarer_running = 0
        leader = self.forehand
        for trick_no in range(1, 11):
            self.current_trick = []
            turn = leader
            for _ in range(3):
                legal = self.legal_for(turn)
                card = turn.strategy.choose_card(turn, self, legal)
                turn.hand.remove(card)
                self.current_trick.append((turn, card))
                self.played_cards.append(card)
                turn = self.next_player(turn)
            winner = self.current_winner()
            gained = [c for _, c in self.current_trick]
            winner.won_cards.extend(gained)
            winner.tricks += 1
            self.completed_tricks.append(list(self.current_trick))
            summary = "  ".join(f"{p.name}:{c}" for p, c in self.current_trick)
            role = "declarer" if winner is self.declarer else "defender"
            if is_null:
                note = " <- declarer takes it, Null is broken!" if winner is self.declarer else ""
                print(f"  Trick {trick_no:>2}: {summary}   -> {winner.name}{note}")
                self.log(f"  T{trick_no:>2}  {summary:<34} -> {winner.name}{note}")
                if winner is self.declarer:
                    self.current_trick = []
                    return   # contract already lost; no need to play on
            else:
                pts = sum(c.card_points for c in gained)
                if winner is self.declarer:
                    declarer_running += pts
                print(f"  Trick {trick_no:>2}: {summary}   -> {winner.name} (+{pts})")
                self.log(f"  T{trick_no:>2}  {summary:<34} -> {winner.name} "
                         f"({role}, +{pts})  [declarer has {declarer_running}]")
            leader = winner

    def settle(self):
        d = self.declarer
        declarer_points = d.captured_points + sum(c.card_points for c in self.skat_discards)
        sheet = score_round(self.contract, self.declarer_twelve,
                            declarer_points, d.tricks, self.winning_bid)

        print("\n" + "-" * 60)
        if self.contract.game_type is GameType.NULL:
            print(f"Null: {d.name} took {d.tricks} trick(s); needed 0.")
            print(f"Game value {sheet.game_value}.")
        else:
            print(f"Declarer {d.name}: {declarer_points} card points "
                  f"(defenders {120 - declarer_points}).")
            extras = []
            if sheet.schneider:
                extras.append("Schneider")
            if sheet.schwarz:
                extras.append("Schwarz")
            extra = f"  [{', '.join(extras)}]" if extras else ""
            print(f"Base {sheet.base_value} x multiplier {sheet.multiplier} "
                  f"(with/without {sheet.matadors}){extra} = game value {sheet.game_value}.")
        if sheet.overbid:
            print(f"OVERBID: game value {sheet.game_value} < bid {self.winning_bid}. "
                  f"{d.name} loses regardless of points.")
        if sheet.made:
            d.match_score += sheet.game_value
            print(f"{d.name} MAKES it.  +{sheet.game_value}")
        else:
            penalty = 2 * sheet.game_value
            d.match_score -= penalty
            print(f"{d.name} LOSES it.  -{penalty}")
        print("-" * 60)

        # Transcript summary of the outcome.
        self.log("")
        if self.contract.game_type is GameType.NULL:
            self.log(f"Result: Null -- {d.name} took {d.tricks} trick(s), needed 0. "
                     f"Value {sheet.game_value}.")
        else:
            flags = [name for name, on in
                     (("Schneider", sheet.schneider), ("Schwarz", sheet.schwarz)) if on]
            extra = f" [{', '.join(flags)}]" if flags else ""
            self.log(f"Result: {describe(self.contract)}, with/without {sheet.matadors}, "
                     f"base {sheet.base_value} x {sheet.multiplier}{extra} = {sheet.game_value}. "
                     f"Declarer {declarer_points} pts (defenders {120 - declarer_points}).")
        if sheet.overbid:
            self.log(f"  OVERBID: value {sheet.game_value} < bid {self.winning_bid}.")
        self.log(f"  {d.name} {'MAKES' if sheet.made else 'LOSES'} it "
                 f"({'+' if sheet.made else '-'}"
                 f"{sheet.game_value if sheet.made else 2 * sheet.game_value}).")
        self.log("")

    def play(self):
        self.deal()
        if self.run_auction() is None:
            print("\nEverybody passed -- the hand is thrown in.")
            return
        self.declaration_phase()
        self.play_tricks()
        self.settle()


def valid_bids() -> list[int]:
    """The bid ladder for the games we implement: every base x multiplier, plus
    the fixed Null values."""
    bases = list(SUIT_BASE_VALUE.values()) + [GRAND_BASE_VALUE]
    values = {b * m for b in bases for m in range(2, 19)}  # multiplier >= 2 (>=18)
    values |= {NULL_VALUE, NULL_OUVERT_VALUE}
    return sorted(values)


# --------------------------------------------------------------------------- #
#  A match: rotate the deal, keep score
# --------------------------------------------------------------------------- #

def play_match(rounds: int = 3, seed: Optional[int] = None,
               log_path: Optional[str] = None):
    if seed is not None:
        random.seed(seed)
    players = [
        Player("You", HumanStrategy()),
        Player("Nadia", CountingDefenderStrategy()),   # counts cards on defence
        Player("Bruno", AggressiveStrategy()),
    ]
    if log_path is None:
        log_path = f"skat_log_{datetime.now():%Y%m%d_%H%M%S}.txt"
    logger = GameLogger(log_path)
    logger.write("Skat game transcript")
    logger.write(f"Generated {datetime.now():%Y-%m-%d %H:%M:%S}")
    logger.write("Contains every hand and the Skat so play can be reviewed. "
                 "The human seat is marked '(human)'.")
    logger.write("")

    for r in range(rounds):
        print("\n" + "=" * 60)
        print(f"HAND {r + 1} of {rounds}   (dealer: {players[r % 3].name})")
        print("=" * 60)
        for p in players:      # reset per-hand state
            p.won_cards, p.tricks = [], 0
        SkatRound(players, dealer_index=r % 3, logger=logger, hand_number=r + 1).play()

    print("\n" + "#" * 60)
    print("FINAL SCORES")
    logger.write("#" * 70)
    logger.write("FINAL SCORES")
    for p in sorted(players, key=lambda p: -p.match_score):
        print(f"  {p.name:<8} {p.match_score:+d}")
        logger.write(f"  {p.name:<8} {p.match_score:+d}")
    print("#" * 60)
    logger.flush()
    print(f"\nGame log written to: {logger.path}")
    print("Hand that file to Claude for a critique of your play.")


# --------------------------------------------------------------------------- #
#  Extending this: to add Null, give it its own rank order (7-8-9-10-J-Q-K-A,
#  no trump at all), a trick_winner that never sees trump, a fixed game value
#  (23 / 35 / 46 / 59), and a winner test of "declarer took zero tricks".
#  Because rules, table, and strategy are separate, only the engine layer and a
#  new Strategy method (or reused choose_card) need to know about it.
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    from pathlib import Path
    # Write the transcript next to this script with a timestamped name, so it is
    # easy to find no matter which directory you launch from.
    default_log = Path(__file__).with_name(f"skat_log_{datetime.now():%Y%m%d_%H%M%S}.txt")
    play_match(rounds=3, log_path=str(default_log))
