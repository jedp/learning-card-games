# Skat: A Player's Guide

Skat is a three-player trick-taking card game for a 32-card deck. Each hand, one
player (the **declarer**) plays alone against the other two (the **defenders**),
who form a temporary team. The pairing changes every hand. This guide covers the
rules, scoring, bidding, play, and strategy.

---

## 1. Rules

### The cards

- **3 players**, **32 cards**: 7, 8, 9, 10, Jack, Queen, King, Ace in each of the
  four suits (♣ clubs, ♠ spades, ♥ hearts, ♦ diamonds). (A standard 52-card deck
  with the 2s–6s removed.)
- **Deal:** each player gets **10 cards**, plus **2 cards face-down** in the middle
  called the **Skat**. Cards are dealt in packets, in a fixed order (clockwise
  from Forehand): **3 to each player · 2 to the Skat · 4 to each player · 3 to
  each player** — i.e. **3 – Skat – 4 – 3** (3 + 4 + 3 = 10 apiece). By tradition
  the Skat is dealt right after the first round of threes — never the first or
  last cards off the deck — as an anti-cheating convention.

### Card point values

Winning tricks isn't the goal by itself — cards carry **card points**, and you
fight to capture them:

| Card | Points |
|------|-------:|
| Ace | 11 |
| Ten | 10 |
| King | 4 |
| Queen | 3 |
| Jack | 2 |
| 9, 8, 7 | 0 |

There are **120 points** in the deck. **Note the two quirks that trip up
newcomers:** the **Ten is the second-most valuable card** (it ranks in power just
below the Ace and *above* the King), and the **Jacks are worth only 2 but are the
most powerful cards** (see below).

### Trumps — the heart of the game

There are three kinds of game, differing only in what is trump:

**Suit game** — a chosen suit plus all four Jacks are trump. The Jacks are the
top trumps and always rank ♣ > ♠ > ♥ > ♦. Example, with **clubs** as trump, the
trump order from strongest to weakest is:

```
J♣  J♠  J♥  J♦  A♣  10♣  K♣  Q♣  9♣  8♣  7♣      (11 trumps)
```

The three non-trump suits rank normally: **A, 10, K, Q, 9, 8, 7** (7 cards each).

**Grand** — **only the four Jacks** are trump (J♣ J♠ J♥ J♦, 4 trumps). Every
other card is an ordinary member of its suit. Clubs, spades, hearts and diamonds
are all plain 7-card suits.

**Null** — **no trump at all**, not even the Jacks. The rank order also changes
to the natural **7, 8, 9, 10, J, Q, K, A** (Ace high; the Ten drops back to
between the 9 and the Jack; Jacks are ordinary cards of their suit). The
declarer's goal is to take **zero tricks**.

### The golden rule about Jacks

> **A Jack is never a member of its printed suit — it is always a trump.** Leading
> *any* Jack means **leading trump.**

So the J♠ is not a spade; in a club game it's a trump. Leading J♦ does not mean
"diamonds led," it means "trump led."

### Following suit

- You must **follow the group that was led** if you can; otherwise you may play
  anything (including a trump, to "ruff").
- In a **suit game**, the two ways to lead trump are: lead a card of the trump
  suit, **or** lead any Jack. To follow, you may play any trump (a Jack or a
  trump-suit card).
- In **Grand**, only a Jack leads trump; to follow trump you must play a Jack.
  Leading a club/spade/heart/diamond leads that plain suit.
- Because a Jack is trump, the Jack of a suit does **not** count toward following
  that suit. If clubs are led and your only "club" is the J♣, you are **void in
  clubs** and may play anything.

### Winning a trick

The **highest trump** played wins the trick. If no trump was played, the
**highest card of the suit that was led** wins. The trick's winner leads to the
next trick.

### Seating and turn order

Relative to the dealer:

- **Forehand** — to the dealer's left; **always leads the first trick.**
- **Middlehand** — next.
- **Rearhand** — the dealer (in the 3-player game).

The deal rotates one seat each hand.

---

## 2. Scoring

### Winning the hand

- The **declarer wins** by capturing **61 or more** of the 120 card points.
- The **defenders win** ("set" the contract) by capturing **60 or more** between
  them (their points are pooled).
- **Schneider:** the losing side is held to **30 or fewer** points (i.e. the
  winning side takes 90+). Worth a bonus.
- **Schwarz:** the losing side takes **no trick at all**. Worth a further bonus.

### The game value

The value of a suit or Grand game is:

```
game value = base value × multiplier
```

**Base values:**

| Game | Base |
|------|-----:|
| Diamonds | 9 |
| Hearts | 10 |
| Spades | 11 |
| Clubs | 12 |
| Grand | 24 |
| Null | 23 (Null) · 46 (Null Ouvert) — fixed, not multiplied |

**Multiplier** = *matadors* + 1 (for the game) + 1 per bonus achieved (Schneider,
Schwarz; plus, in full rules, Hand / Ouvert / announced bonuses).

### Matadors ("with" and "without")

Count the **unbroken run of top trumps starting at the J♣** (the highest trump):

- **Hold the J♣?** You are **"with"** — count how many top trumps you hold in an
  unbroken run from the top.
- **Don't hold the J♣?** You are **"without"** — count how many top trumps you are
  *missing* in an unbroken run from the top.

Either way, the *number* is what feeds the multiplier; "with N" and "without N"
give the **same** multiplier. The run is measured only from the top and stops at
the first card that breaks the pattern.

Examples for a **Clubs** game (trump run J♣ J♠ J♥ J♦ A♣ 10♣ K♣ Q♣ 9♣ 8♣ 7♣):

- Hold J♣ J♠ J♥, not J♦ → **with 3** → 12 × (3+1) = **48**.
- Hold J♣ only (missing J♠) → **with 1** → 12 × 2 = **24**.
- Missing J♣ (whatever you hold below) → **without 1** → 12 × 2 = **24**.
- Missing J♣ and J♠, holding J♥ → **without 2** → 12 × 3 = **36**.
- Hold every trump except the J♣ → **without 1** (only the top card is missing)
  → 12 × 2 = **24**, *even though you hold ten of the eleven trumps.*

For **Grand**, the run is only the four Jacks, so the count maxes at 4.

### Worked multiplier

A Clubs game, **with 3**, that also achieves Schneider:

```
12 × ( 3 matadors + 1 game + 1 Schneider ) = 12 × 5 = 60
```

### Schneider and Schwarz bonuses

**Schneider** and **Schwarz** are extra achievements, and each is worth **+1 to
the multiplier** — the same weight as one matador. They are defined by the
**losing** side's result:

- **Schneider** (+1): the losing side is held to **30 card points or fewer**
  (equivalently, the winning side takes **90 or more**).
- **Schwarz** (+1): the losing side takes **no trick at all** (0 tricks). A hand
  that is Schwarz is necessarily also Schneider, so the two bonuses **stack**
  (+2 together).

**How and when they are scored — two ways:**

1. **Achieved (unannounced).** If the threshold is simply reached *during play*,
   the extra multiplier is added **automatically at scoring** — a reward for
   outperforming. You don't have to call it in advance. *(This is the only form
   the accompanying `skat.py` uses.)*
2. **Announced (called before play).** In full Skat the declarer may *announce*
   "Schneider" or "Schwarz" before the first card is led, which raises the game's
   value by further multipliers — but then the declarer **must actually achieve
   what was announced or the game is lost**, even if the bid would otherwise have
   been made. Announcing is a deliberate grab for more points at higher risk (and
   in the full rules it requires a *Hand* game — playing without the Skat).

Either way, the bonus feeds the same formula, and the resulting value must still
cover the bid:

```
game value = base × ( matadors + 1 game + [Schneider] + [Schwarz] + … )
```

**Worked examples.** A Clubs game, **with 2**:

```
declarer takes 95 (Schneider, but defenders won a trick):
    12 × ( 2 + 1 game + 1 Schneider )            = 12 × 4 = 48

declarer takes all 120 (Schneider AND Schwarz):
    12 × ( 2 + 1 game + 1 Schneider + 1 Schwarz ) = 12 × 5 = 60
```

**Why it matters at the table:**

- **As declarer**, a Schneider you didn't strictly need can still lift a marginal
  game over the line — but *bidding up to a level that requires* a Schneider is a
  bet you may not win (fall short and it's an overbid loss).
- **As a defender**, when the contract is unbeatable, fight to reach **31 points**
  (avoid being Schneidered) and to steal at least **one trick** (avoid Schwarz) —
  each denies the declarer a multiplier and shrinks your loss on the scoreboard.
  When you're instead crushing the declarer, push the other way: hold them to
  **≤ 30** for the Schneider and deny every trick for the Schwarz, to **enlarge**
  their loss (a losing declarer pays −2 × the value, bonuses included).

### The overbid rule (critical)

> Your **final game value must be at least as high as your bid.** If it isn't, you
> **lose automatically** — no matter how many card points you took.

Because the value depends on matadors and on bonuses you actually achieve, part
of it is uncertain when you bid. Two things can move it:

- **The Skat can change your matador count.** You bid before seeing it. Picking up
  a top trump you were missing can *raise* a "with" hand — but can *lower* a
  "without" hand, because holding the top trump collapses a long "without" run to
  "with 1."
- **Schneider/Schwarz are bonuses you either earn or don't.** Bidding up to a
  number that *requires* a Schneider is a bet that you'll get it.

### Match scoring

- **Declarer makes it:** **+ game value.**
- **Declarer loses it:** **− 2 × game value** (this includes overbids). Defenders
  don't score points directly; setting the declarer is its own reward on the
  scoreboard.

*(Tournament Skat has additional refinements — Bock rounds, announced games, etc.
— but the above is the core.)*

---

## 3. Bidding

### What the numbers mean

During the auction players call **numbers**, and each number is a possible **game
value** (18, 20, 22, 23, 24, 27, 30, 33, 36, 40, 44, 45, 46, 48, …). You are **not**
naming a suit — you commit to the actual game (a suit, Grand, or Null) only *after*
you win, at declaration. Bidding has **nothing to do with a number of tricks.**

### The auction sequence

1. **Middlehand bids to Forehand.** Middlehand calls ascending numbers; Forehand
   says *"yes"* (holds) or passes. This continues until one of them passes.
2. **Rearhand then bids to the survivor**, the same way.
3. The last player standing is the **declarer**, at the last number reached. (If
   everyone passes to Forehand, Forehand may still take the game at 18 or the
   hand is thrown in.)

**Tie-break falls out of the sequence:** the *caller* must always go one step
higher to stay in, so if two players are willing to the same number, the one who
merely *holds* it wins — the caller ran out of room above it. In effect,
**Forehand beats Middlehand, and the survivor beats Rearhand** on ties.

### How high can you bid?

Your ceiling is your game's value. Two ceilings matter:

- **Safe ceiling = base × (matadors + 1)** — the "just make it" value, guaranteed
  the moment you take 61. Bid freely up to here.
- **Higher, only if you're confident of a bonus.** With a dominant hand you can bid
  past the safe ceiling by banking on a Schneider (adds one multiplier). But if
  you don't earn it, that's an overbid loss.

You never have to bid to your ceiling — bid only as high as you need to outlast
the others.

### The with/without paradox — the most important bidding lesson

**A big "without" number is not a strong hand.** It means the top trumps are all
held *against* you. A hand with only the lowest trump of a suit can be "without
10" (a huge paper value) yet take almost no tricks — it is the *least* playable
game, not the most valuable. Conversely, a hand that will win a pile of tricks
can have a modest value if you hold the top trumps ("with N" is capped by how many
you hold in a row).

The consequence: **trick-taking power and game value are different things.** Value
sets your bid ceiling; trick power decides whether you make 61. Sometimes you hold
a hand that will *make easily* but whose value is too low to *win the auction* —
and the higher-value alternatives won't make. Recognizing when **not** to bid a
strong-looking hand is a real skill.

### A starter rule for when to bid

Open the bidding when your hand has, roughly:

- the **J♣ or J♠** (or, for Grand, several Jacks), **and**
- a **five-card trump suit** (or a strong Grand shape of Jacks + Aces), **and**
- at least **one side Ace** or a suit you can quickly make void.

**No Jacks = no trump control ≈ a pass.** That single tell filters most weak
hands.

---

## 4. Game play

### Order of play

Forehand leads to the first trick. Each player in turn must follow suit if able;
the winner of each trick leads the next. Ten tricks are played.

### Master cards — know when a card is a guaranteed winner

A card is a **master** only when every higher card of its group has already been
played. Because the **Ten outranks the King**, a King is *not* a master until
**both the Ace and the Ten** of that suit are gone. A Ten is not a master until
the Ace is gone. Leading a non-master into a suit where a higher card still lives
just hands that card the trick.

### Void detection

The moment a player **fails to follow suit** — they discard or ruff — they are
**void** in the led suit. Store that as a fact: it tells you they will ruff that
suit again, and that leading it to them donates a ruff. A handful of "who's void
where" facts is cheap to remember and hugely informative.

### Card counting — how to actually do it

Nobody counts all 32 cards. Count a few **categories**, count **down** from the
known total, and remember by **exception** (what's still missing, not everything
played). Update once per trick. Build the skill in layers — don't add a rung until
the one below is automatic:

1. **The Jacks.** Just four cards. Track which have appeared and who played them.
   This alone drives half your trump decisions. Start here.
2. **The trumps.** A suit game has **11** trumps, Grand has **4**, Null has none.
   Subtract your own, then tick down. The moment you're listening for is *"trumps
   all gone"* — then your side-suit Aces are safe to cash and your remaining
   trumps are masters. (Shortcut: count *rounds* — one full round of trump is 3
   gone.)
3. **Aces and Tens** — the "counters" (84 of the 120 points). Knowing which are
   gone tells you where the points are, and which of *your* Kings/Tens have become
   masters.
4. **The running point total** — toward 61 (declarer), 60 (defenders), and the
   Schneider lines (30 and 90).

Your biggest free advantage: **you see your own ten cards.** Subtract them from
the totals immediately and you've done a third of the work. As a defender,
remember two cards are unseen in the Skat/discard.

---

## 5. Sample hands

### 5a. A Suit game (Clubs)

**Declarer holds:** `J♣ J♠ J♥ · A♣ 10♣ K♣ 9♣ · A♠ 10♠ · 7♦`

- **Trump = clubs:** J♣ J♠ J♥ J♦ A♣ 10♣ K♣ Q♣ 9♣ 8♣ 7♣.
- **Matadors:** holds J♣ J♠ J♥, missing J♦ → **with 3** → 12 × 4 = **48**.
- **Shape:** seven trumps (three Jacks + four clubs) and both black Aces — a
  crushing hand.

**Plan and character of play:**
1. **Draw trumps first.** Lead the J♣, then J♠, then J♥ to strip the defenders'
   trumps. Any Jack you don't hold (here the J♦) will fall under your higher ones.
2. Once the defenders are out of trumps, **cash your top trumps** (A♣, 10♣) and
   your **side Aces** (A♠, then the 10♠, which is master once the A♠ is gone).
3. Defenders can only score by capturing what you're forced to concede — with a
   hand this strong, expect to reach Schneider.

This is the essence of a suit game: **use trump length to control the hand, then
harvest your winners.**

### 5b. A Grand

**Declarer holds:** `J♣ J♠ · A♣ 10♣ K♣ · A♠ 10♠ · A♥ · K♦`

- **Trump = the four Jacks only.**
- **Matadors:** holds J♣ J♠, missing J♥ → **with 2** → 24 × 3 = **72**.
- **Shape:** two top Jacks plus **three Aces and two Tens** spread across the
  suits — the classic Grand signature.

**Plan and character of play:**
1. There are only four trumps in the whole deck. **Lead a Jack to draw out the two
   held by the defenders.** One or two rounds usually clears them.
2. With trumps gone, **your Aces and Tens are unstoppable.** Cash A♣ (and the
   10♣ behind it), A♠ (then 10♠), A♥.
3. **Discard for value and voids:** into the Skat you'd bank a high card you can't
   protect (e.g. a spare Ten) and shed a lone card to create a void your Jacks can
   ruff.

Grand rewards **Jacks + Aces + Tens across suits.** Whoever wins the tiny trump
war controls the Aces, and the Aces are the game.

### 5c. A Null

**Declarer holds:** `7♣ 8♣ 9♣ · 7♠ 8♠ · 7♥ 8♥ · 7♦ 8♦ 9♦`

- **No trump. Rank order is 7-8-9-10-J-Q-K-A.** The declarer must take **zero
  tricks** to win; the game is worth **23** (or 46 played Ouvert / open).
- **Shape:** nothing but low cards, with a low card in every suit to **duck**
  under whatever is led. This is exactly what a Null hand wants.

**Plan and character of play:**
1. **Duck everything.** When a suit is led, play a card *lower* than the highest
   already on the table so you don't win. The rule of thumb: shed the **highest
   card you can that still loses the trick.**
2. **Danger cards are high cards and Aces** — anything that might be forced to win.
   That's why a Null hand wants 7s, 8s, 9s, short suits, and voids. (A hand's
   "Null risk" is low when it has low cards guarding everything and no stranded
   high cards.)
3. **Watch out even for a 7:** if you lead a low card and both opponents are void
   in that suit, they discard and your card wins — breaking the contract. So
   leading is delicate; prefer to let others lead and duck under them.

Null inverts every instinct: there is no trump, high cards are liabilities, and
winning a trick is losing.

---

## 6. Offensive strategies (playing as declarer)

1. **Bid within your value.** Know your safe ceiling — `base × (matadors + 1)` —
   before you hold a bid. Push past it only when a Schneider is a near-lock.
2. **Discard smartly into the Skat.** Two goals: **bank points** (a Ten or a card
   you can't protect goes safely into your pile) and **create a void** so your
   trumps can ruff that suit. Never discard trumps you need for control.
3. **Draw trumps first.** Pull the defenders' trumps before cashing your side
   Aces — otherwise a void defender ruffs your Ace. A neat technique: **lead your
   *lowest* high trump to flush out the enemy's higher one** (e.g. lead a Jack to
   make them spend a higher Jack cheaply).
4. **Then cash your winners** — side Aces, then Tens, then run a long suit. Once
   everyone is void in your long suit, its low cards win and scoop the defenders'
   discards.
5. **Count your trumps down** so you know the exact moment the defenders are
   stripped and your side suits are safe.

### Common declarer mistakes

- **Cashing a side Ace before drawing trumps** → a void defender ruffs it.
- **Overbidding** → taking 61 doesn't save you if your game value is below your
  bid. This is the #1 way strong hands lose.
- **Leading a bare Ten** (no small card behind it) → an Ace drops on it for 10
  points. Keep Tens guarded.
- **A wasteful Skat discard** → throwing away trump control or keeping unsupported
  honors instead of banking points and making a void.

---

## 7. Defensive strategies (playing as a defender)

The two defenders are **one team with one shared point-pile**, aiming for **60**.
The whole art is cooperation without being able to talk.

1. **Position is everything.** The defender who plays **after** the declarer is in
   the power seat — they act with full information and can capture. The defender
   who plays **before** the declarer should play cautiously and set up their
   partner. The proverb: **"lead through strength, up to weakness"** — lead a low
   card *through* the declarer so your partner behind them can pounce.
2. **Smear on your partner's tricks.** When your partner is winning a trick the
   declarer can't beat, **pile your Aces and Tens onto it.** Points captured by
   either defender go in the same pile. Don't hoard a Ten — dump it on partner's
   winning Ace.
3. **Starve the declarer's tricks.** When the declarer is winning and you can't
   stop it, play your **cheapest** card (a 7, 8, 9). *Never* feed an Ace or Ten —
   or even a King when a lower card is available — into a trick the declarer takes.
   This applies to **discards** too, not just to following suit.
4. **Don't lead into the declarer's Aces or voids.** He chose a trump suit, so
   assume he's short somewhere. Leading your side Ace into a void gets it ruffed;
   leading a low card into his master Ace hands him the trick. **Make the declarer
   lead his own long suits** — then your side plays after the Ace and can duck low.
5. **Lead trumps when *you* are trump-strong.** Holding high trumps (especially
   Jacks) as a defender, lead them to strip the declarer and win outright — don't
   feed side-suit losers into his cards or voids. (When you're trump-weak, the
   opposite: don't lead trump and do the declarer's work for him.)
6. **Cash your masters once trumps are gone.** The instant the declarer is out of
   trumps, switch from disrupting to harvesting: run your established winners and
   deny him the lead. Hang on to a card until it has *become* a master, then take
   the trick with it.
7. **Use void detection.** Once a suit is a known void for the declarer, stop
   leading it — you're only donating ruffs (and often your partner's card with it).
8. **Change goals when the contract is unbeatable.** If you can't reach 60, fight
   to reach **30** so you at least avoid being Schneidered (which denies the
   declarer a fat bonus). When you're crushing him, push the other way — hold him
   under 31 to Schneider *him*.

### The two-question lead check

Before every lead, ask:

1. **Do I hold a master here?** (Every higher card gone — for a King, the Ace
   *and* the Ten.) If yes, cash it.
2. **If not, has the Ace of the suit I'm about to lead appeared?** If no, someone
   holds it — don't lead into it.

### Common defender mistakes

- **Feeding the declarer** — playing an Ace/Ten/King into a trick he wins instead
  of your cheapest card.
- **Failing to smear** — keeping a Ten "safe" instead of banking it on your
  partner's winning trick.
- **Cashing into a void** — leading a side Ace into a suit the declarer can ruff.
- **Leading trumps for the declarer** when you're trump-weak — doing his job of
  drawing trumps for him.
- **Leading a King (or a Ten) into a suit where a higher card still lives.**

---

## 8. Glossary

- **Skat** — (1) the game itself; (2) the two face-down cards dealt to the middle.
  The declarer picks them up and discards two; those discards count as card points
  for the declarer.
- **Declarer** — the player who wins the auction and plays alone.
- **Defenders** — the other two players, a temporary team against the declarer.
- **Forehand / Middlehand / Rearhand** — the three seats. Forehand (left of the
  dealer) always leads the first trick; Rearhand is the dealer.
- **Trump** — a card that beats all non-trump suits. The four Jacks are always
  trump; a suit game adds a whole suit; Grand has only the Jacks; Null has none.
- **Matadors (Spitzen)** — the unbroken run of top trumps from the J♣ downward.
  You are **"with"** N if you hold them, **"without"** N if they're held against
  you. Sets the multiplier.
- **Base value** — the per-game number multiplied by the multiplier (♦9 ♥10 ♠11
  ♣12, Grand 24).
- **Game value** — base value × multiplier; must be ≥ your bid or you lose.
- **Follow suit** — play a card of the led group if you can; Jacks count as trump,
  not their face suit.
- **Ruff** — to play a trump on a suit you're void in, to win the trick.
- **Void** — holding no cards of a suit; lets you ruff or discard when it's led.
- **Counter / counters** — the point-carrying cards (A, 10, K, Q, J). The 9, 8, 7
  are worthless "blanks."
- **Smear (schmieren)** — to dump a high-point card onto a trick your partner is
  winning, banking the points for the defense.
- **Starve** — to play your cheapest card onto a trick the declarer is winning, so
  you feed him as few points as possible.
- **Master** — a card that will win because every higher card of its group is gone.
- **Schneider** — holding the losing side to 30 points or fewer (a bonus
  multiplier). Can also be *announced* before play for extra value.
- **Schwarz** — the losing side takes no trick at all (a further bonus).
- **Overbid** — bidding higher than your game's final value; an automatic loss
  regardless of card points taken.
- **Hand game** — declaring without picking up the Skat, for an extra multiplier.
- **Ouvert (open)** — declaring with your hand face-up on the table (common in
  Null), for extra value.
- **Grand** — the game where only the four Jacks are trump (base 24).
- **Null** — the game with no trump where the declarer tries to take zero tricks;
  the rank order becomes 7-8-9-10-J-Q-K-A.

## Quick reference

| Fact | Value |
|------|-------|
| Cards / players | 32 / 3 |
| Deal | 10 · 10 · 10 + 2 Skat |
| Total card points | 120 |
| Declarer needs | 61 |
| Defenders need | 60 |
| Schneider (bonus) | loser ≤ 30 |
| Schwarz (bonus) | loser takes no trick |
| Jack order (always) | ♣ > ♠ > ♥ > ♦ |
| Trumps in a suit game | 11 (4 Jacks + 7 of suit) |
| Trumps in Grand | 4 (the Jacks) |
| Trumps in Null | none |
| Base values | ♦9 ♥10 ♠11 ♣12 · Grand 24 · Null 23/46 |
| Multiplier | matadors + 1 (game) + bonuses |
| Golden rule | A Jack is always trump, never its face suit |
| Overbid | game value below your bid = automatic loss |
