# Skat Cheat Sheet

*A one-page reference. See `skat.md` for the full guide.*

## Setup
3 players · 32 cards (7-8-9-10-J-Q-K-A × 4 suits) · **10 each + 2 Skat**.
Deal in packets, clockwise from Forehand: **3 each – 2 to Skat – 4 each – 3 each**.
Declarer plays alone vs. two defenders. **120 card points** total.

## Card points
**A = 11 · 10 = 10 · K = 4 · Q = 3 · J = 2 · 9/8/7 = 0.**
Quirks: the **10 beats the K**; the **Jacks are the top trumps** (worth only 2).

## Trumps & rank
- **Jacks are ALWAYS trump**, order **♣ > ♠ > ♥ > ♦** (a Jack is never its face suit).
- **Suit game** (e.g. ♣): `J♣ J♠ J♥ J♦ · A 10 K Q 9 8 7 of ♣` = **11 trumps**;
  other suits rank `A 10 K Q 9 8 7`.
- **Grand**: only the **4 Jacks** are trump.
- **Null**: **no trump**; rank flips to `7 8 9 10 J Q K A` (declarer takes **0 tricks**).

## Winning
Declarer needs **61**; defenders need **60**.
**Schneider** = loser ≤ 30 · **Schwarz** = loser takes no trick (each a bonus).

## Value & matadors
`game value = base × multiplier`
**Base:** ♦9 ♥10 ♠11 ♣12 · **Grand 24** · **Null 23 / Ouvert 46** (fixed).
**Multiplier = matadors + 1 (game) + 1 per bonus (Schneider, Schwarz).**

**Matadors** = unbroken run of top trumps from **J♣** down:
- Hold J♣ → **"with N"** (how many you hold in a row).
- Miss J♣ → **"without N"** (how many missing in a row).
- Same multiplier either way. *A big "without" = the top trumps are AGAINST you =
  a weak hand with a high paper value.*

Examples (Clubs): with J♣J♠J♥ = **with 3** → 48 · miss J♣ = **without 1** → 24.

## Bidding
- Numbers = game values (18, 20, 22, 23, 24, 27, 30, 33, 36, 40, …). You name a
  **game** only after winning.
- **Middlehand bids to Forehand; survivor bids to Rearhand.** Ties: the **holder**
  wins (Forehand > Middlehand > Rearhand).
- **Safe ceiling = base × (matadors + 1)** — bid up to here freely; go higher only
  if a Schneider is a lock.
- **⚠ Overbid = automatic loss.** If your final game value < your bid, you lose no
  matter how many points you took. (The Skat can raise or *lower* your matadors.)
- **Open the bidding when:** you hold the J♣ or J♠ **+** a 5-card trump suit
  (or Jacks + Aces for Grand) **+** a side Ace. **No Jacks ≈ pass.**

## Play basics
- **Follow suit** if you can; else play anything (a Jack counts as trump, not its
  suit). Highest trump wins; else highest card of the led suit.
- **Forehand leads first;** the trick's winner leads next.
- **Master card** = every higher card is gone. A **King is not a master until the
  Ace AND the Ten** have appeared.

## Declarer (offense)
1. **Discard** into the Skat to **bank points** and **make a void**.
2. **Draw trumps first** (lead a low Jack to flush a higher one), *then* cash Aces.
3. **Run your winners**; count trumps down so you know when side suits are safe.
4. **Never overbid**; don't cash a side Ace while a defender can still ruff.

## Defenders (defense) — one team, target 60
1. **Smear** high cards onto your **partner's** winning tricks.
2. **Starve** — play your **cheapest** card onto the **declarer's** winning tricks
   (never feed an A/10/K when a 7/8/9 will do). Applies to discards too.
3. **Don't lead into his Aces or voids** — make the declarer lead his long suits.
4. **Lead trumps when you're trump-strong;** don't when you're weak.
5. **Cash your masters** the moment the declarer is out of trumps.
6. **Track voids** — once he ruffs a suit, stop leading it.

## Two-question lead check
1. **Do I hold a master here?** (all higher cards gone) → cash it.
2. **If not, has the Ace of this suit appeared?** If no → don't lead into it.

## Count in layers (build one at a time)
**Jacks (4) → trumps (11 / 4 / 0) → Aces & Tens → running points.**
Count *down*, remember *voids*, update once per trick. You already see your 10
cards — subtract them first.
