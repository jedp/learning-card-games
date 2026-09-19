# Reading the Declarations

*How to turn the call-and-response into a picture of the opposing hand — and
where that picture stops. Worked from the deal in `piquet-example-hand-2.md`.
Every count below is computed, not estimated; see the end for how to reproduce
them.*

## The governing rule

**You reveal exactly what you score.**

Win a category and you must announce it and show it on demand. Lose one and you
say "Good" and stay silent — your quart, your tierce, your three queens go
unmentioned. The rule that makes losing a category expensive is the same rule
that makes losing it **opaque**.

Two consequences follow, and they run in opposite directions:

- **Winning the declarations costs you information.** The player who sweeps the
  categories has described their hand out loud.
- **"Good" is an upper bound, not a fact.** It tells you only what the opponent
  *lacks*. "Not good" is a lower bound, and is usually the more valuable answer.

## The position

Elder's hand and discards, which is all elder legitimately knows:

```
ELDER holds     ♠ A K Q 7    ♥ K 10 9 8 7    ♦ K Q    ♣ 8
ELDER threw     ♠9 ♠8 ♦8 ♣J ♣10
```

That is 17 known cards. The other 15 are younger's twelve plus younger's three
discards:

```
UNKNOWN POOL    ♠ J 10    ♥ A Q J    ♦ A J 10 9 7    ♣ A K Q 9 7
```

Younger's hand is "which three of those fifteen went into the discard."

> **455 possible younger hands** before either player says a word.

## Step 1 — the point

> **E:** "Point of five." **Y:** "Good."

Elder's five hearts make 44. "Good" means younger's best point is **worse than
(5 cards, 44 pips)**.

Only two suits in the pool could even reach five cards:

| | | pips |
|---|---|---|
| ♦ A J 10 9 7 | five diamonds | **47** |
| ♣ A K Q 9 7 | five clubs | **47** |

Both beat 44. Younger said "Good", so younger holds **neither five**. Therefore
**at least one diamond and at least one club are in younger's discards** — two
of the three, located, from a single word.

## Step 2 — the sequences

> **E:** "A quart, ten high. And a tierce major." **Y:** "Good."

Younger has no quart. Now check whether that was ever possible:

- Diamonds: `A-K-Q-J` needs ♦K and ♦Q — both in elder's hand.
  `J-10-9-8` needs ♦8 — in elder's discards.
- Clubs: `A-K-Q-J` needs ♣J — in elder's discards.

A quart was **unavailable to younger from the start**. The verdict cost younger
6 points in forfeited tierces and told elder *nothing elder did not already
know*. A cheap "Good" is often an empty one — check before you bank on it.

## Step 3 — the sets

> **E:** "Three kings." **Y:** "Not good." **Y:** "Three aces — three jacks."

This is where the hand opens up, because younger **won** and therefore had to
speak.

- **Three aces.** Elder holds ♠A, so younger's three are **♥A ♦A ♣A**. Exact.
- **Three jacks.** The pool contains only ♠J ♥J ♦J — ♣J is in elder's own
  discards. So younger holds **♠J ♥J ♦J**. Exact.

**Six cards pinned precisely**, from one losing verdict and one winning
declaration.

## Where that leaves elder

> **54 possible younger hands** remain — down 88%.

```
CERTAIN in younger's hand:   ♠J   ♥A ♥J   ♦A ♦J   ♣A
STILL OPEN (6 of these 9):   ♠10  ♥Q  ♦10 ♦9 ♦7  ♣K ♣Q ♣9 ♣7
CONSTRAINT:                  at least one ♦ and at least one ♣ were discarded
```

Elder can now conclude, **before leading a card**:

- **♥A and ♥J are both offside.** The five-card heart suit — the quart that just
  scored 4 — will take **zero tricks**. Leading a heart surrenders the lead.
- **♦A and ♣A are offside.** ♦K Q is worth at most one trick; the singleton ♣8
  is worth nothing.
- **The only certain tricks are ♠A K Q.**

That is a complete and correct read of the hand's shape, available at trick one.

## Where the picture stops

Younger's clubs were **♣A K Q 7** — a tierce major, and the suit that took
tricks 7, 8 and 9.

Elder knew younger held ♣A and at most four clubs. Elder did **not** know the
king and queen were there:

> **♣K appears in only 36 of the 54 surviving hands. So does ♣Q.**

Two-thirds likely, never certain. And the reason is the governing rule: younger's
club tierce lost the sequences category to elder's quart, so **younger never
announced it**. The combination that decided the deal stayed invisible precisely
because it scored nothing.

This is the part declarations are structurally silent about. They describe
**length, honours and shape**. They say nothing about **guards, low cards, or
entries** — and the play is decided by those.

## The asymmetry, counted

Run the same reconstruction from younger's chair. Elder announced a point of
five making 44, a quart ten-high, a tierce major, and three kings — every one
of them a *winning* declaration, so every one of them spoken aloud.

- "Quart to the ten" in a five-card heart suit pins **♥10 9 8 7**.
- 44 − 34 = 10, so the fifth heart is worth 10 pips. The ten is used; younger
  holds ♥Q and ♥J. It must be **♥K**.
- "Tierce major" is headed by an ace. Younger holds ♥A ♦A ♣A, so elder's ace is
  ♠A, and the tierce is **♠A K Q**.
- "Three kings": ♠K and ♥K are pinned; younger holds ♣K, so the third is **♦K**.

> **Nine of elder's twelve cards, exposed before a card is led.**

| | knows | candidate hands before | after |
|---|---|---|---|
| **Elder** | 17 cards | 455 | **54** |
| **Younger** | 15 cards | 6,188 | **40** |

Elder discards five and so starts knowing more — elder's uncertainty is an
order of magnitude smaller before anyone speaks. Elder pays for it by **having
to declare first**, and ends the exchange slightly *worse* informed than
younger.

> **The declaration ritual is elder trading information for points, from a
> position of knowing more to begin with.**

## The habit to build

Before you lead to trick one:

1. **List your own 17 (or 15).** Hand plus discards. The rest is the pool.
2. **Convert each verdict into an inequality**, not a fact. "Good" caps them;
   "Not good" floors them.
3. **Pin what was announced.** A winning declaration is exact information —
   cross-reference it against the cards you hold to name the actual cards.
4. **Ask what a "Good" could not have been.** If the opponent could never have
   beaten you in that category, the verdict was free and told you nothing.
5. **Then ask what is still dark.** It will be low cards, guards, and any
   combination that *lost*. That is where the tricks are.

## Reproducing the counts

`piquet_dd.py` and `piquet.py` are in this directory. The bots in `piquet.py`
do exactly this reasoning in `Deal._consistent_with_declarations` — they sample
opponent hands and reject any that would not have produced the verdicts actually
heard, then solve the survivors exactly. To redo the counts above:

```python
from itertools import combinations
import piquet as P
# build the two hands and both discard piles, take the complement of what one
# seat knows, and filter combinations() by the verdicts that were given
```

The full script used to verify this document is short enough to rewrite from the
five steps above — and writing it is a better way to learn the deductions than
reading them.
