#!/usr/bin/python3

"""
Generating roll tables for Warping dice for the purposes of odds analysis and
tuning.

Reference effective attribute scores:
     4 - an average starting character without special training or tools
     8 - a well-suited starting character (6) with a basic tool (2)
    12 - a well-suited character (6) with bonuses (2) and a decent tool (4)
    16 - a well-suited endgame character (7) with bonuses (3) and a very good
         tool (6)

A test may specify a bonus or penalty to the roll, and may require more than
one success, but see below for caveats about penalties.

As in many games your net modified score in an ability is the number of dice
that you'll roll.

Unlike most other games these dice are typed according to the "flavor" of magic
that's powering them, with each character having a native flavor and
non-magical sources being treated as that native flavor.

An entity is perfectly safe whenever working with their native flavor of magic
but working with other flavors of magic carries multiple risks, including the
risk of corruption due to Warp.

The magic native to the primary world of this game, the one the protagonists
are defending, is weak even while it's plentiful. To put this in D&D terms,
imagine if spell slots only went up to 2nd level, and instead of gaining
higher-level slots through progression they instead gain the down-converted
numerical equivalent in 1st and 2nd level slots, e.g. a 6th level slot would
become three 2nd level slots.

Magic native to other worlds, such as the elemental planes or the lands of the
fae, can be much more powerful. But those other worlds are inhabited by beings
of varying levels of intelligence/sentience that share only one characteristic:
they find us tasty in both body and spirit. Corrupted beings gain this trait.

So the magic of the other worlds is very tempting to use due to its power,
while also being very dangerous due to the risk of corruption and attention
from the natives of that world.

The corrupting influence of these magics is known as "Warp", but it is possible
to protect against it, which is known as "Ward".

Unwarded Warp will generate Uninteded Consequences, which are intended to be
varied in their effects (the severity of which is related to the amount), but
one that is planned to be common is the possibility of altering an ability to
change the flavor of one of the dice from "Native" to that of the Warp.
Permanently.

Most, if not all, of the PCs in this game will already be partially corrupted
by some flavor of alien magic, though they will also have some level of
protection or containment for it so that it's reasonably safe to let them
galavant about and fight things that want to eat grandma for dinner.

shorthand:
    P = warP
    D = warD
      = blank
    L = Lesser success (only counts as success when empowered)
    N = Normal success (counts as success unless depowered)
    G = Greater success (always counts as success)
    O = Empowered (mnemonic = Over-powered)
    U = Depowered (mnemonic = Under-powered)
    S = Success
    F = Failure

When it comes to counting successes, the initial plan was to count everything
applicable based on the (em|de)powered status as one success. While looking at
the odds tables from this it felt like there wasn't enough tuning options
available for the difficulty of checks, particularly if penalties to the number
of dice are disallowed.

Current thinking is that it may be beneficial to tuning to sometimes count N
and G as more than one success, based on (em|de)powered state. Specifically,
{L,N,G} would be {0,1,2} successes (regular power), {0,0,1} (depowered), and
{1,2,3} {empowered}.

This is still subject to playtesting, but for the feel that I want for the game
I expect that I'll need to increase the amount of Warp/Ward on each die, though
maintaining the expected value of 1/6 P.

Strawman low Warp dice:
    {P, , ,L,N,G}
      EV(P) = +1/6 (  0,  0,  0,  0,  0, +1), [0,1]
      EV(US) = 1/6 (  0,  0,  0,  0,  0,  1), [0,1]
      EV(S)  = 3/6 (  0,  0,  0,  0,  1,  2), [0,2]
      EV(OS) = 6/6 (  0,  0,  0,  1,  2,  3), [0,3]

Original Warp dice (warpingDie):
    {P,P,D,L,N,G}
      EV(P) = +1/6 ( -1,  0,  0,  0, +1, +1), [-1,1]
      EV(US) = 1/6 (  0,  0,  0,  0,  0,  1), [0,1]
      EV(S)  = 3/6 (  0,  0,  0,  0,  1,  2), [0,2]
      EV(OS) = 6/6 (  0,  0,  0,  1,  2,  3), [0,3]

More Warp dice (midWarpingDie):
    {P,P,D,DL,N,PG}
      EV(P) = +1/6 ( -1, -1,  0, +1, +1, +1), [-1,1]
      EV(US) = 1/6 (  0,  0,  0,  0,  0,  1), [0,1]
      EV(S)  = 3/6 (  0,  0,  0,  0,  1,  2), [0,2]
      EV(OS) = 6/6 (  0,  0,  0,  1,  2,  3), [0,3]

Even More Warp dice (madWarpingDie):
    {PP,P,DD,DL,N,PG}
      EV(P) = +1/6 ( -2, -1,  0, +1, +1, +2), [-2,2]
      EV(US) = 1/6 (  0,  0,  0,  0,  0,  1), [0,1]
      EV(S)  = 3/6 (  0,  0,  0,  0,  1,  2), [0,2]
      EV(OS) = 6/6 (  0,  0,  0,  1,  2,  3), [0,3]

The higher variance dice are more punishing to the player because there's no
gameplay benefit to having excess Ward, with the mathematical balance only
manifesting as more dice are rolled.

If production costs, and player confusion, weren't considerations I'd probably
adopt using the original warpingDie when Depowered, the midWarpingDie when at
Normal power, and the madWarpingDie when Overpowered, but for a physical game
both of those considerations make that unlikely to be workable.

Therefore I've tentatively selected the madWarpingDie for use in the first
prototypes - I'd rather have a game about corruption need to dial back the
corruption for balance rather than feel like it's missing. The need to dial it
back will be more obvious than a feel that it's missing.

This Warping effect of alien flavors of magic affects the application of
penalties to checks - only native dice can be removed. This is beneficial to
the players in that it may give them an effective minimum that's greater than
1, and also being beneficial to the gameplay experience by forcing ongoing
corruption to be ongoing. The only real alternative to this rule that's true to
the intended experience of this game would be disallowing penalties completely,
which takes away one of the tuning dials for the difficulty of checks. It's up
for consideration that the minimum is "all alien dice and at least one native
die", as is using penalties sparingly.

"""

from dataclasses import dataclass
import enum
import numpy as np
import random
import statistics
import typing

class RollContext(enum.StrEnum):
    STANDARD  = enum.auto()
    DEPOWERED = enum.auto()
    EMPOWERED = enum.auto()

class DieSymbol(enum.StrEnum):
    WARP         = enum.auto()
    WARD         = enum.auto()
    WEAK_POWER   = enum.auto()
    POWER        = enum.auto()
    STRONG_POWER = enum.auto()

def symbolWarpValue(sym: DieSymbol, context: RollContext = RollContext.STANDARD):
    match sym:
        case DieSymbol.WARP:
            return 1
        case DieSymbol.WARD:
            return -1
        case _:
            return 0

def symbolSuccessValue(sym: DieSymbol, context: RollContext = RollContext.STANDARD):
    successValue = None;

    match sym:
        case DieSymbol.STRONG_POWER:
            successValue = 2
        case DieSymbol.POWER:
            successValue = 1
        case DieSymbol.WEAK_POWER:
            successValue = 0

    if successValue is None:
        return 0

    match context:
        case RollContext.EMPOWERED:
            successValue += 1
        case RollContext.DEPOWERED:
            successValue -= 1

    if successValue < 0:
        return 0

    return successValue

class DieFace():
    faceNames = {}

    def __init__(self, /, name: str, symbols: dict):
        if name in DieFace.faceNames:
            raise ValueError("Duplicate DieFace name")
        for symbol, qty in symbols.items():
            if symbol not in DieSymbol and not isinstance(symbol, int):
                raise ValueError("Unknown symbol '{}' on DieFace '{}'".format(symbol, name))
            if not isinstance(qty, int):
                raise ValueError("Unusable quantity '{}' of symbol '{}' on DieFace '{}'".format(qty, symbol, name))
        self.name = name
        self.symbols = symbols

    def warpValue(self, context: RollContext = RollContext.STANDARD):
        return sum(symbolWarpValue(s, context) * self.symbols[s] for s in self.symbols)

    def successValue(self, context: RollContext = RollContext.STANDARD):
        return sum(symbolSuccessValue(s, context) * self.symbols[s] for s in self.symbols)

class Die():
    dieNames = {}

    def __init__(self, /, name: str, faces: list[DieFace]):
        if name in Die.dieNames:
            raise ValueError("Duplicate Die name")

        self.name = name
        self.faces = faces
        self.sides = len(faces)

    def allResults(self, context: RollContext = RollContext.STANDARD, terseKeys: bool = False):
        results = {}

        for face in self.faces:
            successKey = face.successValue(context)
            warpKey = face.warpValue(context)

            if terseKeys:
                results[(successKey,warpKey)] = results.get((successKey,warpKey),0) + 1
            else:
                successKey = "Successes:" + str(successKey)
                warpKey = "Warp:" + str(warpKey)

                if successKey not in results:
                    results[successKey] = {}

                successSubset = results[successKey]

                successSubset[warpKey] = successSubset.get(warpKey, 0) + 1

        return results

class DiePool():
    def __init__(self, /, name: str, dice: list[Die]):
        self.name = name
        self.dice = dice
        self.nDice = len(dice)

    def allResults(self, context: RollContext = RollContext.STANDARD, terseKeys: bool = False):
        results = { (0,0): 1 }

        for die in self.dice:
            nextResults = {}

            dieResults = die.allResults(context, terseKeys=True)

            for dieResult in dieResults:
                for prevResult in results:
                    newResult = (prevResult[0]+dieResult[0],prevResult[1]+dieResult[1])

                    nextResults[newResult] = nextResults.get(newResult,0) + dieResults[dieResult] * results[prevResult]

            results = nextResults

        if terseKeys:
            return results

        longResults = {}

        for successWarpPair, count in results.items():
            successKey = "Successes:" + str(successWarpPair[0])
            warpKey = "Warp:" + str(successWarpPair[1])

            if successKey not in longResults:
                longResults[successKey] = {}

            longResults[successKey][warpKey] = count

        return longResults

def printFormattedResults(results: dict):
    minSuccesses = 0
    maxSuccesses = 0
    minWarp = 0
    maxWarp = 0

    for successWarpPair in results:
        if successWarpPair[0] < minSuccesses:
            minSuccesses = successWarpPair[0]
        if successWarpPair[0] > maxSuccesses:
            maxSuccesses = successWarpPair[0]
        if successWarpPair[1] < minWarp:
            minWarp = successWarpPair[1]
        if successWarpPair[1] > maxWarp:
            maxWarp = successWarpPair[1]

    successRange = (maxSuccesses - minSuccesses + 1)
    warpRange = (maxWarp - minWarp + 1)

    successTotals = [0] * successRange
    warpTotals = [0] * warpRange

    gridTotals = []

    n = 0

    for nSuccesses in range(minSuccesses, maxSuccesses + 1):
        gridTotals.append([0] * warpRange)

    for successWarpPair,count in results.items():
        successTotals[successWarpPair[0] - minSuccesses] += count
        warpTotals[successWarpPair[1] - minWarp] += count
        n += count
        gridTotals[successWarpPair[0] - minSuccesses][successWarpPair[1] - minWarp] += count

    print("n=" + str(n))

    successWidth = 1 + max(len(str(minSuccesses)),len(str(maxSuccesses)))
    warpWidth = 1 + max(len(str(minWarp)),len(str(maxWarp)),len("{:%}".format(1)))

    successLeaderFormat = " {:+" + str(successWidth) + "d}"
    warpHeaderFormat = " {:^+" + str(warpWidth) + "d}"
    cellFormat = " {:" + str(warpWidth) + "%}"
    emptyCellFormat = " {:^" + str(warpWidth) + "}"
    emptyCellText = emptyCellFormat.format("-")

    print(" " * (successWidth + 2), end='')
    for nWarp in range(minWarp,maxWarp + 1):
        print(warpHeaderFormat.format(nWarp), end='')
    print()

    for nSuccess in range(minSuccesses,maxSuccesses + 1):
        successIndex = nSuccess - minSuccesses
        print(successLeaderFormat.format(nSuccess), end='')
        warpRow = gridTotals[successIndex]
        for warpIndex in range(maxWarp - minWarp + 1):
            if warpRow[warpIndex]:
                print(cellFormat.format(warpRow[warpIndex] / n), end='')
            else:
                print(emptyCellText, end='')
        print(" = ", end='')
        print(cellFormat.format(successTotals[nSuccess] / n), end='')
        print(" ({})".format(successTotals[nSuccess]))

    print(" " * (successWidth + 2), *list(["=" * warpWidth] * warpRange) )
    print(" " * (successWidth + 2), end='')
    for warpIndex in range(maxWarp - minWarp + 1):
        print(cellFormat.format(warpTotals[warpIndex] / n), end='')
    print()


def printSpreadsheetSuccessResults(results: dict):
    minSuccesses = 0
    maxSuccesses = 0

    for successWarpPair in results:
        if successWarpPair[0] < minSuccesses:
            minSuccesses = successWarpPair[0]
        if successWarpPair[0] > maxSuccesses:
            maxSuccesses = successWarpPair[0]

    successRange = (maxSuccesses - minSuccesses + 1)

    successTotals = [0] * successRange

    n = 0

    for successWarpPair,count in results.items():
        successTotals[successWarpPair[0] - minSuccesses] += count
        n += count

    print("{:d}".format(n), end='')

    for nSuccess in range(minSuccesses,maxSuccesses + 1):
        print("\t{:d}".format(successTotals[nSuccess]), end='')

    print()

warpFace = DieFace(name="Warp", symbols={ DieSymbol.WARP: 1 })
wardFace = DieFace(name="Ward", symbols={ DieSymbol.WARD: 1 })
wsFace = DieFace(name="Weak Success", symbols={ DieSymbol.WEAK_POWER: 1 })
sFace = DieFace(name="Normal Success", symbols={ DieSymbol.POWER: 1 })
ssFace = DieFace(name="Strong Success", symbols={ DieSymbol.STRONG_POWER: 1 })

warpingDie = Die(name="Warping Die", faces=[warpFace, warpFace, wardFace, wsFace, sFace, ssFace])

wsdFace = DieFace(name="Weak Success + Ward", symbols={ DieSymbol.WEAK_POWER: 1, DieSymbol.WARD: 1 })
sspFace = DieFace(name="Strong Success + Warp", symbols={ DieSymbol.STRONG_POWER: 1, DieSymbol.WARP: 1 })

midWarpingDie = Die(name="Mid Warping Die", faces=[warpFace, warpFace, wardFace, wsdFace, sFace, sspFace])

warp2Face = DieFace(name="Warp", symbols={ DieSymbol.WARP: 2 })
ward2Face = DieFace(name="Ward", symbols={ DieSymbol.WARD: 2 })

madWarpingDie = Die(name="Mad Warping Die", faces=[warp2Face, warpFace, ward2Face, wsdFace, sFace, sspFace])

#for nDice in range(8 + 1):
for nDice in (1,4):
    for die in (warpingDie, midWarpingDie, madWarpingDie):
        pool = DiePool(str(nDice)+"dW", [die]*nDice)

        for context in (RollContext.DEPOWERED, RollContext.STANDARD, RollContext.EMPOWERED):
            printFormattedResults(pool.allResults(context,terseKeys=True))
            print()

