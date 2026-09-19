# Piquet — A Worked Hand

*One deal, start to finish. Deliberately stacked so that every scoring rule
fires at least once — real hands are messier. See `piquet-cheatsheet.md` for the
rules and `piquet-card.html` for the printable table card.*

## The deal

You are **elder** (non-dealer).

```
ELDER (you)    ♠ A K 9 8     ♥ 9     ♦ J 10 9    ♣ 10 9 8 7
YOUNGER        ♠ 7           ♥ A K Q J 8 7      ♦ A K      ♣ A K Q
TALON          top five: ♠Q ♠J ♠10 ♦8 ♦7   ·   under: ♥10 ♦Q ♣J
```

## Elder's discard

Standing pat is worth about 11: point of four in spades (38), a tierce in
diamonds, a quart in clubs.

But the clubs are `10 9 8 7` — a quart worth **4**, and **dead in play**, since
♣A K Q J are all missing and every one of them loses to something. ♠A K and
♦J 10 9 are live fragments that only need feeding.

**Throw the quart.** Discard ♣10 9 8 7 + ♥9, take all five.
Draw **♠Q ♠J ♠10 ♦8 ♦7**.

```
ELDER    ♠ A K Q J 10 9 8      ♦ J 10 9 8 7
```

Seven spades in sequence, five diamonds in sequence, **void in hearts and
clubs**.

Younger discards ♠7, ♥8, ♥7 and takes the last three (♥10, ♦Q, ♣J):

```
YOUNGER  ♥ A K Q J 10     ♦ A K Q     ♣ A K Q J
```

## Declarations

> **E:** "Point of seven." **Y:** "Good." → **E 7**
> **E:** "Septième — ace to the eight." *(17)* "And a quint in diamonds, jack to
>   the seven." *(15)* **Y:** "Good." → **E 32**
> **E:** "Nothing else." **Y:** "Three aces — three kings — three queens."
>   → **Y 9**

**Elder 39 · Younger 9.**

### What younger forfeited
Younger held a **quint major in hearts (15)**, a **quart major in clubs (4)**,
and a **tierce major in diamonds (3)** — **22 points of sequences** — and scored
**zero**, because elder's septième outranked the lot.
*This is the "loser scores nothing" rule at full force.*

### The repique that wasn't
Elder reached **39** in declarations — past the 30 threshold. Repique is **60**,
which would have put elder on **99 before a card was played**.

It didn't happen: repique requires the opponent to score **nothing at all** in
declarations, and younger's three trios scored 9.

**Younger's 9 points were really worth 69.** Three queens look like a
consolation prize; they were the entire defence.

> **Younger's lesson:** when you're being crushed, you are not playing for
> points — you are playing to *score at all*.

## The play

Younger knows from the declarations that elder's hand is **exactly** seven
spades and five diamonds. Elder leads.

| # | lead | younger | won |
|---|------|---------|-----|
| 1 | ♠A | ♥10 | E |
| 2 | ♠K | ♥J | E |
| 3 | ♠Q | ♣J | E |
| 4 | ♠J | ♥Q | E |
| 5 | ♠10 | ♣Q | E |
| 6 | ♠9 | ♥K | E |
| 7 | ♠8 | ♣K | E |
| 8 | ♦7 | **♦Q** | **Y** |
| 9 | ♥A | ♦8 | Y |
| 10 | ♣A | ♦9 | Y |
| 11 | ♦A | ♦10 | Y |
| 12 | ♦K | ♦J | Y |

Younger threw ♥K Q J 10 and ♣K Q J — the heart quint major and the club honours
— to hold **♦A K Q**. It looks like vandalism. It is the only move on the board.

**Strip younger of every diamond and elder takes all twelve: capot, 40.** One
diamond above the ♦J stops it, because the moment younger wins a trick elder
never leads again — elder is void in both of younger's suits, so every heart and
club younger leads wins by default.

> **The guard lesson:** the cards younger had to save were the three that looked
> most worthless.

## The score

| | elder | younger |
|---|---|---|
| Declarations | **39** | **9** |
| Leading to tricks | 8 | 4 |
| Winning a trick not led | — | 1 |
| Last trick | — | 1 |
| The cards (7 tricks) | 10 | — |
| **Total** | **57** | **15** |

One deal of six. Younger sits on **15**, needing **100** across the partie to
avoid the rubicon — and will spend the next five deals fighting for scraps not
to win, but to reach three figures, because failing means their total gets
**added** to elder's instead of subtracted.

## Rules this hand demonstrates

1. **Discarding a scoring combination** (the club quart) to chase length.
2. **Point decided on length**, 7 cards over 5.
3. **Sequence rank by length** — septième (7) beats quint (5).
4. **Loser scores nothing in a category** — younger forfeits 22.
5. **Categories are independent** — younger is crushed in point and sequences
   and still wins the sets outright.
6. **Nines and below never form a set** — and the trios that do score decide the
   hand.
7. **Repique denied** by a single scoring declaration — worth 60.
8. **Counting the opponent's hand** from declarations alone.
9. **Guards** — one card stands between 5 tricks and capot.
10. **The cards** — 7 tricks to 5, worth 10.
