# Piquet

Two players, 32 cards, no trumps, six deals to a partie. Rubicon scoring.

## Learn it

| file | what it is |
|---|---|
| `piquet-cheatsheet.md` | the rules, one page, house style |
| `piquet-card.html` | the same thing print-ready — open in a browser, prints to one page |
| `piquet-example-hand.md` | a **constructed** deal that fires every scoring rule once |
| `piquet-example-hand-2.md` | a **random** deal, played double-dummy optimal — elder leads the declarations 12–6 and loses 19–25 |
| `piquet-reading-declarations.md` | turning the call-and-response into a read on the opposing hand, with the counts |
| `piquet-dos-and-donts.md` | strategy and tactics by phase |

Suggested order: cheatsheet → example hand → example hand 2 → reading the
declarations → dos and don'ts.

## Play it

```
python3 piquet.py                          # opponent style chosen at random
python3 piquet.py --opponent defensive     # or balanced / aggressive / random
python3 piquet.py --deals 6 --seed 17      # reproducible
python3 piquet.py --watch                  # bot vs bot, no prompts
```

Every partie writes a timestamped transcript containing **both hands and the
talon**, so the play can be reviewed afterwards — hand it to Claude for a
critique of your discards.

### The opponents

One brain (`HeuristicStrategy`) tuned by a `Style`. The knobs are the whole
difference between them:

| | discard favours | play |
|---|---|---|
| **Colette** (defensive) | guards and stoppers | ducks, keeps low cards back, sinks the point |
| **Margot** (balanced) | an even mix | cashes winners, leads its long suit |
| **Gaston** (aggressive) | declarations, sequences | leads long suits hard, plays for the cards and capot |
| **Pierrot** (random) | nothing at all | a baseline, not an opponent |

`--opponent random-style` picks one per partie and tells you which afterwards.

All three finish the hand with an **exact endgame search**: once few enough
cards remain they sample opponent hands that are consistent with the
declarations actually made, solve each exactly, and vote. They never look at
your cards — the samples are built only from what that seat legitimately knows.
That is the reading exercise from `piquet-reading-declarations.md`, in code, in
`Deal._consistent_with_declarations`.

## Analyse it

```
python3 piquet_dd.py                                  # solves the worked example
python3 piquet_dd.py 'sAKQ7 hK10987 dKQ c8' 'sJ hAQJ dAJ109 cAKQ7'
```

`piquet_dd.py` plays both hands out perfectly with full information. Use it to
settle "should I have kept the guard" after a deal — never as a model of correct
play at the table, since it sees cards you cannot.

## Known rough edges

- **The bots are mediocre in the middle game.** The exchange heuristic and the
  endgame search are decent; the tricks in between are plain heuristics. Elder
  averages roughly 30 to younger's 25 in balanced self-play, which is about the
  right shape but the absolute standard is club-beginner at best.
- **Sinking is implemented for the point only.** Sinking a sequence is legal and
  sometimes right; no bot does it.
- **The talon-leftovers house rule** is set by `LEFTOVERS_ARE_PUBLIC` at the top
  of `piquet.py`. It ships as *private* — a player who leaves cards may look at
  them and the opponent may not. Sources differ; flip it if your table does.
