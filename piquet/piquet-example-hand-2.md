# Piquet — An Ordinary Hand

*A second worked deal. Unlike `piquet-example-hand.md`, this one was **dealt at
random**, not constructed — no quints, no quatorze, no voids. Both sides are
played double-dummy optimal, so the trick count is exact rather than merely
plausible.*

**The lesson: elder wins the declarations two to one and loses the deal.**

## The deal

```
ELDER (you)   ♠ A K Q 9 8    ♥ K 10 9    ♦ Q 8      ♣ J 10
YOUNGER       ♠ J 10         ♥ A Q J     ♦ A J 9 7  ♣ A Q 9
TALON         top five, in order: ♠7 ♣8 ♥8 ♦K ♥7  ·  under: ♣7 ♦10 ♣K
```

## The exchange

Elder takes all five. Two real candidates:

- **Keep six spades** — throw ♥9 ♦Q ♦8 ♣J ♣10 → `♠A K Q 9 8 7`, point of six.
- **Build a second suit** — throw ♠9 ♠8 ♦8 ♣J ♣10, keeping ♠A K Q and ♥K 10 9.

Elder takes the second, and the packet obliges with ♥8 and ♥7:

```
ELDER    ♠ A K Q 7    ♥ K 10 9 8 7    ♦ K Q    ♣ 8
YOUNGER  ♠ J          ♥ A Q J         ♦ A J 10 9    ♣ A K Q 7
```

Younger throws ♠10 ♦7 ♣9 and draws ♣7, ♦10, ♣K.

## Declarations

> **E:** "Point of five." **Y:** "Good." → **E 5**
> **E:** "A quart, ten high." **Y:** "Good." **E:** "And a tierce major." → **E 7**
> **E:** "Three kings." **Y:** "Not good."
> **Y:** "Three aces — three jacks." → **Y 6**

| | elder | younger | winner |
|---|---|---|---|
| Point | hearts, 5 cards / 44 | diamonds, 4 / 40 | **E** — 5 |
| Sequences | ♥10 9 8 7 quart (4) + ♠A K Q tierce major (3) | ♦J 10 9 (3) + ♣A K Q (3) | **E** — 7 |
| Sets | three kings | three aces + three jacks | **Y** — 6 |

**Elder 12, younger 6.** Younger forfeits two tierces; elder forfeits the kings
to the aces.

## The play

| # | lead | reply | won |
|---|------|-------|-----|
| 1 | **E** ♠A | ♠J | E |
| 2 | **E** ♠K | ♥Q | E |
| 3 | **E** ♠Q | ♦J | E |
| 4 | **E** ♠7 | ♦10 | E |
| 5 | **E** ♥K | **♥A** | **Y** |
| 6 | **Y** ♥J | ♥10 | Y |
| 7 | **Y** ♣A | ♣8 | Y |
| 8 | **Y** ♣K | ♥9 | Y |
| 9 | **Y** ♣Q | ♥8 | Y |
| 10 | **Y** ♣7 | ♥7 | Y |
| 11 | **Y** ♦9 | **♦K** | E |
| 12 | **E** ♦Q | **♦A** | Y |

**Tricks 5–7. Younger takes the cards.**

### Four things to take from it

1. **The quart took zero tricks.** `♥K 10 9 8 7` scored 4 and won nothing —
   younger holds ♥A Q J. Declaration value and trick-taking power are different
   currencies. A quart headed by a king, sitting under an ace-queen, is worth its
   4 points and *nothing else*.
2. **Trick 5 decided the hand.** Elder had to broach some suit, and every suit
   was headed by younger. Losing the lead once was enough.
3. **Trick 11 was a throw-in.** Younger led ♦9 *into* elder's ♦K on purpose,
   losing a trick so that elder had to lead ♦Q into the ♦A. Elder's ♦K Q was
   always worth exactly one trick — younger chose which one, and took the
   last-trick point with it.
4. **The ♣7 won trick 10.** Elder kept a singleton ♣8, spent it at trick 7, and
   was void. Younger's seven took a trick.

## The score

| | elder | younger |
|---|---|---|
| Declarations | **12** | **6** |
| Leading to tricks | 7 | 9 |
| Last trick | — | 1 |
| The cards (7 tricks) | — | 10 |
| **Total** | **19** | **25** |

The cards are worth 10 and the play distributes about twelve more. Together they
outweigh a normal hand's declarations.

> **Elder's advantage is an advantage, not a result.**

## The discard, revisited

The other line, through the solver:

| elder's discard | declarations | tricks | **deal** |
|---|---|---|---|
| Chase the heart quart | 12–6 | 5–7 | **19–25** |
| Keep six spades | 6–6 | 6–6 | **13–13** |

Keeping six spades halves elder's declarations — ♠A K Q and ♠9 8 7 are two
tierces, and younger's ♣A K Q is *also* a tierce headed by an ace, so the
category **ties and neither player scores a sequence**. But the extra spades are
tricks, the split goes 6–6, and nobody takes the cards.

Six fewer points, six points better off. It is genuinely close, though: in a
rubicon partie the raw total matters too, and 19 helps toward 100 in a way that
13 does not.

**Elder cannot see any of this at the time.** The discard is where you choose
between scoring and winning, blind — which is the whole game.

## Contrast with the first example

| | constructed hand | this hand |
|---|---|---|
| Elder declarations | 39 | 12 |
| Best sequence | septième (17) | quart (4) |
| Decided by | repique denial + capot threat | the cards, 7–5 |
| Real decisions | younger's guards only | both discards, and the whole play |

The first hand teaches the *rules*. This one teaches the *game*.
