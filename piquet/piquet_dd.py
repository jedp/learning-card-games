"""Double-dummy solver for the piquet play phase.

Given both twelve-card hands laid face up, this plays the twelve tricks out
perfectly for both sides and reports the exact result.  "Double dummy" means
perfect information: it is the answer to *what was actually available*, not to
*what you could have known*.  Use it to settle an argument after a deal, never
as a model of correct play at the table.

    from piquet_dd import solve, score_line
    value, line = solve(elder_hand, younger_hand)
    elder_pts, younger_pts, elder_tricks, younger_tricks = score_line(line)

A hand is any iterable of (rank, suit) pairs using the characters
"AKQJT987" and "shdc" -- for example ("A", "s") is the ace of spades.

Play scoring implemented here:
    +1  to whoever leads a trick
    +1  to whoever wins a trick they did not lead
    +1  extra for winning the last trick
    +10 for taking 7..11 tricks ("the cards"), or +40 for all 12 ("capot")

Declarations are *not* included -- they are settled before a card is led, so
they do not interact with the play.  Add them afterwards.

Run it directly for a demonstration:   python3 piquet_dd.py
"""

from __future__ import annotations

RANKS = "AKQJT987"          # high to low
SUITS = "shdc"
ORDER = {r: i for i, r in enumerate(RANKS)}     # 0 = ace = highest
SUIT_NAME = {"s": "♠", "h": "♥", "d": "♦", "c": "♣"}

# Cards live in a 32-bit int: bit (suit_index * 8 + rank_index).
# Within a suit a LOWER bit index means a HIGHER card.
SUIT_MASK = [0xFF << (8 * k) for k in range(4)]


def cid(card) -> int:
    rank, suit = card
    return SUITS.index(suit) * 8 + ORDER[rank]


def card_of(index: int):
    return (RANKS[index % 8], SUITS[index // 8])


def mask(cards) -> int:
    m = 0
    for c in cards:
        m |= 1 << cid(c)
    return m


def show(card) -> str:
    rank, suit = card
    return SUIT_NAME[suit] + (rank if rank != "T" else "10")


def _bits(m: int):
    while m:
        low = m & -m
        yield low.bit_length() - 1
        m ^= low


def candidates(hand: int, unplayed: int, suit: int | None = None) -> list[int]:
    """Legal plays with strategically equivalent cards collapsed to one.

    Two cards of the same suit in the same hand are interchangeable when every
    card between them has already been played, so only the lower of each such
    block is worth searching.  This is what makes the search fast enough to be
    instant on a twelve-trick hand.
    """
    if suit is not None:
        follow = hand & SUIT_MASK[suit]
        pool = follow if follow else hand
    else:
        pool = hand

    out = []
    for i in _bits(pool):
        base = (i // 8) * 8
        j = i - 1
        while j >= base and not (unplayed >> j) & 1:
            j -= 1
        if j >= base and (hand >> j) & 1:
            continue                    # same as the higher card we also hold
        out.append(i)
    return out


def solve(elder, younger, elder_leads: bool = True, elder_tricks: int = 0):
    """Play the hand out optimally for both sides.

    Returns (value, line) where `value` is elder's play score minus younger's
    under best play by both, and `line` is one optimal sequence of tricks as
    (leader, lead_card, reply_card, winner) with leader/winner in {"E", "Y"}.

    `elder_leads` and `elder_tricks` let you resume from a partly played hand;
    the totals still assume a twelve-trick deal.
    """
    E0, Y0 = mask(elder), mask(younger)
    remaining = len(list(elder))
    TOTAL = 12
    memo: dict[tuple, int] = {}

    def rec(E: int, Y: int, e_leads: bool, e_tricks: int, n_left: int) -> int:
        if n_left == 0:
            y_tricks = TOTAL - e_tricks
            if e_tricks == TOTAL:
                return 40
            if y_tricks == TOTAL:
                return -40
            if e_tricks > 6:
                return 10
            if y_tricks > 6:
                return -10
            return 0

        key = (E, Y, e_leads, e_tricks)
        cached = memo.get(key)
        if cached is not None:
            return cached

        unplayed = E | Y
        last = n_left == 1

        # NOTE: no alpha-beta here.  Pruned values are bounds, not exact scores,
        # and caching a bound as if it were exact silently returns wrong lines.
        # The equivalence reduction above is what buys the speed instead.
        if e_leads:
            best = -999
            for li in candidates(E, unplayed):
                suit = li // 8
                worst = 999                    # younger picks the reply
                for ri in candidates(Y, unplayed, suit):
                    y_wins = (ri // 8 == suit) and (ri % 8) < (li % 8)
                    gain = 0 if y_wins else 1
                    if last:
                        gain += -1 if y_wins else 1
                    v = gain + rec(E ^ (1 << li), Y ^ (1 << ri),
                                   not y_wins, e_tricks + (0 if y_wins else 1),
                                   n_left - 1)
                    worst = min(worst, v)
                best = max(best, worst)
        else:
            best = 999
            for li in candidates(Y, unplayed):
                suit = li // 8
                top = -999                     # elder picks the reply
                for ri in candidates(E, unplayed, suit):
                    e_wins = (ri // 8 == suit) and (ri % 8) < (li % 8)
                    gain = 0 if e_wins else -1
                    if last:
                        gain += 1 if e_wins else -1
                    v = gain + rec(E ^ (1 << ri), Y ^ (1 << li),
                                   e_wins, e_tricks + (1 if e_wins else 0),
                                   n_left - 1)
                    top = max(top, v)
                best = min(best, top)

        memo[key] = best
        return best

    value = rec(E0, Y0, elder_leads, elder_tricks, remaining)

    # Walk the tree once more, taking an optimal choice at every turn, to
    # recover a concrete line of play.  The memo is still warm, so this is free.
    line = []
    E, Y, e_leads, e_tricks = E0, Y0, elder_leads, elder_tricks
    for n_left in range(remaining, 0, -1):
        unplayed = E | Y
        last = n_left == 1
        chosen = None

        if e_leads:
            best = -999
            for li in candidates(E, unplayed):
                suit = li // 8
                worst, worst_reply = 999, None
                for ri in candidates(Y, unplayed, suit):
                    y_wins = (ri // 8 == suit) and (ri % 8) < (li % 8)
                    gain = 0 if y_wins else 1
                    if last:
                        gain += -1 if y_wins else 1
                    v = gain + rec(E ^ (1 << li), Y ^ (1 << ri), not y_wins,
                                   e_tricks + (0 if y_wins else 1), n_left - 1)
                    if v < worst:
                        worst, worst_reply = v, ri
                if worst > best:
                    best, chosen = worst, (li, worst_reply)
            li, ri = chosen
            y_wins = (ri // 8 == li // 8) and (ri % 8) < (li % 8)
            line.append(("E", card_of(li), card_of(ri), "Y" if y_wins else "E"))
            E ^= 1 << li
            Y ^= 1 << ri
            e_leads = not y_wins
            e_tricks += 0 if y_wins else 1
        else:
            best = 999
            for li in candidates(Y, unplayed):
                suit = li // 8
                top, top_reply = -999, None
                for ri in candidates(E, unplayed, suit):
                    e_wins = (ri // 8 == suit) and (ri % 8) < (li % 8)
                    gain = 0 if e_wins else -1
                    if last:
                        gain += 1 if e_wins else -1
                    v = gain + rec(E ^ (1 << ri), Y ^ (1 << li), e_wins,
                                   e_tricks + (1 if e_wins else 0), n_left - 1)
                    if v > top:
                        top, top_reply = v, ri
                if top < best:
                    best, chosen = top, (li, top_reply)
            li, ri = chosen
            e_wins = (ri // 8 == li // 8) and (ri % 8) < (li % 8)
            line.append(("Y", card_of(li), card_of(ri), "E" if e_wins else "Y"))
            Y ^= 1 << li
            E ^= 1 << ri
            e_leads = e_wins
            e_tricks += 1 if e_wins else 0

    return value, line


def score_line(line):
    """(elder_points, younger_points, elder_tricks, younger_tricks) for a full
    twelve-trick line, including the last-trick point and the cards/capot bonus."""
    e = y = e_tricks = y_tricks = 0
    for leader, _lead, _reply, winner in line:
        if leader == "E":
            e += 1
        else:
            y += 1
        if winner != leader:                 # took a trick they did not lead
            if winner == "E":
                e += 1
            else:
                y += 1
        if winner == "E":
            e_tricks += 1
        else:
            y_tricks += 1

    if line[-1][3] == "E":                   # last trick
        e += 1
    else:
        y += 1

    if e_tricks == 12:
        e += 40
    elif y_tricks == 12:
        y += 40
    elif e_tricks > 6:
        e += 10
    elif y_tricks > 6:
        y += 10
    return e, y, e_tricks, y_tricks


def format_line(line) -> str:
    rows = ["  #   leader   elder   younger   won"]
    for i, (leader, lead, reply, winner) in enumerate(line, 1):
        elder_card, younger_card = (lead, reply) if leader == "E" else (reply, lead)
        rows.append(f" {i:>2}      {leader}      {show(elder_card):<6}  "
                    f"{show(younger_card):<8}  {winner}")
    return "\n".join(rows)


def parse_hand(text: str):
    """Parse "sAKQ7 hK10987 dKQ c8" into a list of (rank, suit) pairs."""
    cards = []
    for group in text.split():
        suit, body = group[0].lower(), group[1:].upper().replace("10", "T")
        if suit not in SUITS:
            raise ValueError(f"unknown suit {group[0]!r}")
        for rank in body:
            if rank not in RANKS:
                raise ValueError(f"unknown rank {rank!r} in {group!r}")
            cards.append((rank, suit))
    return cards


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        elder, younger = parse_hand(sys.argv[1]), parse_hand(sys.argv[2])
    else:
        print("Usage: python3 piquet_dd.py 'sAKQ7 hK10987 dKQ c8' "
              "'sJ hAQJ dAJ109 cAKQ7'")
        print("No hands given -- solving the worked example from "
              "piquet-example-hand-2.md instead.\n")
        elder = parse_hand("sAKQ7 hK10987 dKQ c8")
        younger = parse_hand("sJ hAQJ dAJ109 cAKQ7")

    if len(elder) != 12 or len(younger) != 12:
        raise SystemExit(f"need 12 cards each, got {len(elder)} and {len(younger)}")
    if set(elder) & set(younger):
        raise SystemExit("the two hands share a card")

    value, line = solve(elder, younger)
    e, y, et, yt = score_line(line)
    print(format_line(line))
    print(f"\ntricks   elder {et}   younger {yt}")
    print(f"play     elder {e}   younger {y}   (differential {value:+d})")
