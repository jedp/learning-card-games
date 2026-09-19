# Piquet — Dos and Don'ts

*Strategy (what to aim at) and tactics (what to do about it), split by phase.
Cross-references: `piquet-cheatsheet.md` for the rules, `piquet-card.html` to
print, the two worked hands for where these come from.*

---

## The discard — where the deal is decided

### Do

- **Take the maximum.** Elder should take all five almost always: you will never
  see more of the talon, and the cards you leave behind go to your opponent.
- **Count the hand the talon might build, not the one you hold.** You discard
  *before* you see what you draw, so what you are judging is what your fragments
  could become. With 12 in hand, 20 cards are unseen:

  | you need… | **elder** (draws 5) | **younger** (draws 3) |
  |---|---|---|
  | one specific card | **25%** | 15% |
  | any of two | **45%** | 28% |
  | any of three | **60%** | 40% |
  | any of four | **72%** | 51% |

  *Elder's rule of thumb: any one card you need is a one-in-four shot.*

- **Prefer fragments with several ways to improve.** `♥10 9` becomes a tierce if
  either the jack or the eight turns up — two chances, 45%. `A K` needing
  precisely the queen is 25%. Keep the flexible fragment.

- **Ask the trick question too, not just the scoring one.** You are building
  toward the hand you will *play*, not only the one you will declare. In
  `piquet-example-hand-2.md` elder's heart quart arrived exactly as planned,
  scored its 4 points, and took **zero tricks**.
- **Throw a scoring combination when it is dead in play.** A quart of `10 9 8 7`
  is worth 4 points and wins nothing. Trading it for length in a live suit is
  normal good play, not a gamble.
- **Know which job every card is doing.** A holding in a suit is one of three
  things, and the third is the one that costs you:

  1. **A stopper** — it will *win* a round and hand you back the lead. Needs an
     ace, or an honour with enough small cards under it to outlast the cards
     above it.
  2. **Fodder** — it will never win, but spending it beats discarding from a
     suit you care about. *Rank is irrelevant here; cheaper is strictly better.*
  3. **Neither** — the waste.

- **Never leave an honour bare.** A lone `K` dies under the ace and wins
  nothing. `K x` survives: you drop the small card under the ace and the king
  wins the next round. *The small card is an escort, not a stopper* — it never
  takes a trick itself, it keeps the big card alive until it can.

  Verified on hand 2: swapping elder's ♦Q for a second club leaves all three
  declaration categories identical (12–6) and **costs a trick**. With the
  escort, ♦K wins trick 11; bare, it dies under the ace at trick 6.

- **In a suit you can only afford one card, keep the LOWEST.** A lone high card
  is the trap — too valuable to spend as fodder, too weak to stop anything.
  You have paid a king's price for a job the seven does identically.

- **Length without an honour stops nothing.** `♣10 8` under `♣A K Q 7` takes
  the same zero tricks as `♣8` alone. Extra low cards change only which of your
  cards you spend, never who wins the suit.
- **Respect the cliff.** Quart → quint is **+11**. Never break a possible quint
  to save a trio.
- **Count your 30 before you throw.** If the discard puts you within reach of a
  repique, that is 60 points, more than most whole deals.

### Don't

- **Don't throw an ace.** Almost never right, and the exceptions need you to see
  the other hand.
- **Don't chase declarations with your whole hand.** Declaration points and
  trick-taking power are different currencies. In `piquet-example-hand-2.md`
  elder's heart quart scored 4 and took **zero tricks**; the discard that
  scored 6 fewer points finished 6 points better off.
- **Don't throw away all your cheap fodder.** A void does not lose you tricks
  in that suit — low cards were never going to win any. It costs you because
  every lead into it forces a discard from a suit you *do* care about. That is
  what stripped younger of a quint major in hand 1. Keep a worthless low card or
  two as a shield, but only when holding it is genuinely cheap.
- **Don't expect low cards to hold off length.** To stop the fourth card of a
  four-card suit you need four yourself. You usually cannot afford that, and two
  low cards buy you nothing but a delay.
- **Don't keep a bare king or an unescorted queen.** They lose to the ace *and*
  cost you a card elsewhere — category 3 above. A queen earns its place with two
  escorts, not with none.
- **Don't take fewer than five to hold one card back** without a concrete
  reason. In hand 2 the fifth card of the packet was the ♠Q that made the
  quart — a hand can turn on the card you decline.

---

## The declarations

### Do

- **Declare in strict order**: point → sequences → sets. Score every combination
  in a category you win.
- **Let a single card work three times.** ♠A can serve the point, the quart and
  four aces at once.
- **Remember the loser scores nothing** — and therefore reveals nothing. If you
  are being crushed, your silence is worth something.
- **Fight to score *at all* when you are behind.** One scoring declaration kills
  a repique. In the first worked hand, younger's three trios were worth 9 points
  and denied elder 60 — so they were really worth **69**.
- **Consider sinking when you are far ahead in a category.** Declaring a point
  of five while holding six costs 1 point and hides a suit length. Cheap, and
  the opponent's reconstruction is now wrong in a specific way.

### Don't

- **Don't read "Good" as "my opponent has nothing."** It means only that their
  holding in *that category* is worse than yours. They may hold a quatorze.
- **Don't forget nines and below never form a set.** Three nines are worth
  nothing; three tens are worth 3.
- **Don't sink a sequence.** Understating a quint as a quart costs 11. Sinking
  is for the point, where it costs 1.
- **Don't assume a tie is impossible.** Equal length *and* equal pips in the
  point, or two tierces both headed by an ace, means **neither player scores**.
  It is the cheapest way to lose 15 points there is.

---

## The play

### Do

- **Count the opposing hand before you lead.** See
  `piquet-reading-declarations.md`. In a typical deal the declarations cut the
  possibilities by around 90%.
- **Cash certain winners early** when you have a long solid suit — the lead
  point plus the discards you force are both real.
- **Keep your stoppers even when it hurts.** In the first worked hand younger threw a
  quint major in hearts and three club honours to hold ♦A K Q, because losing
  the last diamond meant capot: 40 points.
- **Remember a winner you cannot reach is not a winner.** You can only cash on a
  trick you lead. If you can never regain the lead, your aces are decoration.
- **Use a throw-in.** Deliberately losing a trick to force the opponent to lead
  into your tenace is a real technique — it won tricks 11 and 12 in hand 2.
- **Watch the 6–6 line.** Seven tricks is worth 10; six is worth nothing.
  Turning 5–7 into 6–6 is a ten-point swing and often easier than winning.

### Don't

- **Don't broach a suit you cannot afford to lose the lead in.** Once you are
  out, every remaining winner you hold may be stranded.
- **Don't lead a second-best suit hoping to establish it.** `K 10 9 8 7` behind
  `A Q J` takes nothing at all.
- **Don't pitch a master.** When forced to discard, throw from your longest suit
  and keep anything that is now top of its suit.
- **Don't strand your own length.** If you hold four of a suit and the opponent
  is void, the fourth card only wins if you still have the lead when you get to
  it.
- **Don't take a trick you do not need.** Ducking cheaply keeps a stopper for
  the round that matters.

---

## The partie

### Do

- **Play for your own total, not just the margin.** Rubicon scoring pays
  *difference + 100* if the loser reached 100, but *both totals added + 100* if
  they did not. Crossing 100 is worth fighting for even in a hand you have lost.
- **Fight for scraps when you are being beaten.** Every point you scrape toward
  100 subtracts *twice* from the eventual settlement.
- **Remember elder alternates.** Six deals, three in each chair. A bad elder
  hand is half the story.

### Don't

- **Don't concede a deal early.** There is no such thing as a dead hand when the
  rubicon is in play.
- **Don't treat elder's advantage as a result.** It is a real edge — the
  five-card exchange and the first lead — but in `piquet-example-hand-2.md`
  elder led the declarations 12–6 and lost the deal 19–25.

---

## The five things that actually cost beginners points

1. **Leading a suit headed by the opponent**, losing the lead at trick 4 or 5
   and never getting it back.
2. **Discarding stoppers, or stripping an honour of its escort**, to chase one
   more declaration point.
3. **Letting a repique happen** by failing to scrape a single scoring
   declaration.
4. **Missing the 6–6 line** and conceding the cards by one trick.
5. **Treating "Good" as good news.**
