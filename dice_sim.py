#!/usr/bin/python3

"""
Rough draft implementation of the corrupting dice - more for practice with
Python classes than for exploratory simulation purposes. But it may be more
useful than expected.

As in many games your (net modified) score in an ability is the number of dice
that you'll roll.

Unlike most other games, these dice are typed according to the "flavor" of
magic that's powering them.

An entity is perfectly safe whenever working with their native flavor of magic
but working with other flavors of magic carries multiple risks, including the
risk of corruption.

The magic native to the primary world of this game, the one the protagonists
are defending, is weak even while it's plentiful. To put this in D&D terms,
imagine if spell slots only went up to 2nd level, with higher-level slots
down-converted numerically, e.g. a 6th level slot would become three 2nd level
slots.

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
protection/containment for it so that it's reasonably safe to let them galavant
about and fight things that want to eat grandma for dinner.

One question that may be explored with this infrastructure is what difference
there is at the statistical and "feel" levels for different arrangements of the
dice, and possibly also the effects of Unintended Consequences. The general
success and failure mechanics may also be looked at.

For example, is there any difference between: a. a die with two warp and one
ward b. a die with one warp and no ward.

Some hand calculations of the two simple scenarios above show that it's much
less lively when you leave two faces blank rather than having one warp and one
ward.  For 4 dice you have <2% chance of more than 2 Warp with die a., while
you have >8% chance of more than 2 Warp with die b.  That's more than four
times the number of "interesting results" (unintended consequences) even with
two static Ward.

(a quick check of the math verified that it was correct and that the average is
the same for both dice; what's different is that the dice with the ward symbols
have a larger range opposing the warp - ranging from -N to N warp - and with the
same average that requires more results in the upper positive end of the range;
this works out beautifully from the evil GM perspective because excess ward is
wasted)

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

a. 1d{P, , ,L,N,G} = 1/6 1P, 5/6 0P
   2d{P, , ,L,N,G} = 1/36 2P, 10/36 1P, 25/36 0P
   3d{P, , ,L,N,G} = 1/216 3P, 15/216 2P, 75/216 1P, 125/216 0P
   4d{P, , ,L,N,G} = 1/1296 4P, 20/1296 3P, 150/1296 2P, 500/1296 1P, 625/1296 0P

b. 1d{P,P,D,L,N,G} = 2/6 1P, 3/6 0P, 1/6 1D
   2d{P,P,D,L,N,G} = 4/36 2P, 12/36 1P, 13/36 0P, 6/36 1D, 1/36 2D
   3d{P,P,D,L,N,G} = 8/216 3P, 36/216 2P, 66/216 1P, 63/216 0P, 33/216 1D, 9/216 2D, 1/216 3D
   4d{P,P,D,L,N,G} = 16/1296 4P, 96/1296 3P, 248/1296 2P, 360/1296 1P, 321/1296 0P, 180/1296 1D, 62/1296 2D, 12/1296 3D, 1/1296 4D

c. 1d{P,P,D,L+D,N,G+P} = 3/6 1P, 1/6 0P, 2/6 1D
   2d{P,P,D,L+D,N,G+P} = 9/36 2P, 6/36 1P, 13/36 0P, 4/36 1D, 4/36 2D
   3d{P,P,D,L+D,N,G+P} = 27/216 3P, 27/216 2P, 63/216 1P, 37/216 0P, 42/216 1D, 12/216 2D, 8/216 3D
   4d{P,P,D,L+D,N,G+P} = 81/1296 4P, 108/1296 3P, 270/1296 2P, 228/1296 1P, 289/1296 0P, 152/1296 1D, 120/1296 2D, 32/1296 3D, 16/1296 4D

Other options to explore
 a. one always warp and one maybe warp (condition TBD)
 b. three levels of warp - corresponding with the three levels of power for
    success/failure
 c. sides with multiple symbols?
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

