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
    -P = weak warP (only counts when empowered)
    +P = warP (counts unless depowered)
    *P = strong warP (always counts)
    -D = weak warD (only counts when empowered)
    +D = warD (counts unless depowered)
    *D = strong warD (always counts)
    -S = weak Success (only counts when empowered)
    +S = Success (counts unless depowered)
    *S = strong Success (always counts)
    O = Empowered (mnemonic = Over-powered)
    U = Depowered (mnemonic = Under-powered)

This is still subject to playtesting, but I think it gives a good range of both
Warp/Ward and successes.

Variable Warp dice (warpingDie):
    {
        (*P|-P),
        (*P),
        (*D|-D),
        (-S,+D),
        (+S,-S),
        (*S,+S,-S,+P)
    }

Resulting values:
    Depowered:
        Warp:      { +1, +1, -1,  0,  0,  0 } = EV(P) = +1/6 [-1,+1]
        Successes: {  0,  0,  0,  0,  0, +1 } = EV(S) = +1/6 [ 0,+1]
    Normal:
        Warp:      { +1, +1, -1, -1,  0, +1 } = EV(P) = +1/6 [-1,+1]
        Successes: {  0,  0,  0,  0, +1, +2 } = EV(S) = +3/6 [ 0,+2]
    Empowered:
        Warp:      { +2, +1, -2, -1,  0, +1 } = EV(P) = +1/6 [-2,+2]
        Successes: {  0,  0,  0, +1, +2, +3 } = EV(S) = +6/6 [ 0,+3]

Because the higher-variance versions of the Warp/Ward distributions remain
centered around the same midpoint it leads to some interesting results when
combined with static Ward (such as the PC's starting protective gear).

Specifically, the chances of having excess Warp don't rise dramatically as the
number of dice increases, though the severity of that excess Warp does increase.

To give a concrete example:
  + At Normal power if you have 1 static Ward and roll 2 Warping dice you have
    a 75% chance to have no excess Warp and a 25% chance of having one excess
    Warp.
  + At Normal power if you have 1 static Ward and roll 3 Warping dice you still
    have a 75% chance to have no excess Warp, but now you only have a 12.5%
    chance of one excess Warp and you've gained a 12.5% chance of two excess
    Warp.
  + At Normal power if you have 1 static Ward you have to roll 9 Warping dice
    before you drop below a 50% chance to have no excess Warp, and that's
    barely below 50% at 49.4%, but you can have as much as 8 excess Warp and
    you have more than a 13.5% chance of having 4 or more excess Warp.

This Warping effect of alien flavors of magic affects the application of
penalties to checks - only native dice can be removed. This is beneficial to
the players in that it may give them an effective minimum that's greater than
1, and also being beneficial to the gameplay experience by forcing ongoing
corruption to be ongoing. The only real alternative to this rule that's true to
the intended experience of this game would be disallowing penalties completely,
which takes away one of the tuning dials for the difficulty of checks. It's up
for consideration that the minimum is "all alien dice and at least one native
die", as is using penalties sparingly.


production/usability thoughts relative to symbology

tentatively, each of Warp, Ward, and Power will be represented by the outline
of a symbol with an inset '-', '+', or '*' (specifically six-pointed)
indicating in which contexts that symbol is counted and each side having up to
four symbols.

tentative symbol associations:
    Warp
        Diamond (a "warped" square)
    Ward
        Shield (a (mostly?) flat top and sides that curve to a bottom point,
        see the "rosa shield" icon on game-icons.net for a possible outline)
    Power/Success
        Circle (not ideal from an association perspective, but easy to read)

On colors and magical flavor symbology

The acrylic dice available through the game crafter come in:
    Black
    Blue
    Green
    Orange
    Pink
    Red
    White
    Pale Yellow

Possible associations, color and symbol (for cards, etc)
    Red
      * Native - the color of our blood
        A blood drop
        A heart
    Pale Yellow
      + Fire - the color of summer's sun
        A sun with rays
    Orange
      + Earth - the color of autumn's bounty
        A gourd or pumpkin
    White
      + Water - the color of winter's snow
        A snowflake (probably just lines)
    Green
      + Air - the color of spring's growth
        A leaf or blades of grass

    Black
        Shadow (not in base game)
    Blue
    Pink

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
    WEAK_WARP    = enum.auto()
    WARP         = enum.auto()
    STRONG_WARP  = enum.auto()
    WEAK_WARD    = enum.auto()
    WARD         = enum.auto()
    STRONG_WARD  = enum.auto()
    WEAK_POWER   = enum.auto()
    POWER        = enum.auto()
    STRONG_POWER = enum.auto()

def symbolWarpValue(sym: DieSymbol, context: RollContext = RollContext.STANDARD):
    match sym:
        case DieSymbol.STRONG_WARP:
            return 1
        case DieSymbol.STRONG_WARD:
            return -1
        case DieSymbol.WARP:
            if context != RollContext.DEPOWERED:
                return 1
            return 0
        case DieSymbol.WARD:
            if context != RollContext.DEPOWERED:
                return -1
            return 0
        case DieSymbol.WEAK_WARP:
            if context == RollContext.EMPOWERED:
                return 1
            return 0
        case DieSymbol.WEAK_WARD:
            if context == RollContext.EMPOWERED:
                return -1
            return 0
        case _:
            return 0

def symbolSuccessValue(sym: DieSymbol, context: RollContext = RollContext.STANDARD):
    match sym:
        case DieSymbol.STRONG_POWER:
            return 1
        case DieSymbol.POWER:
            if context != RollContext.DEPOWERED:
                return 1
            return 0
        case DieSymbol.WEAK_POWER:
            if context == RollContext.EMPOWERED:
                return 1
            return 0
        case _:
            return 0

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

    def allResults(self, context: RollContext = RollContext.STANDARD, terseKeys: bool = False, disregardExcessWard: bool = False, nStaticWard: int = 0):
        results = { (0,0): 1 }

        for die in self.dice:
            nextResults = {}

            dieResults = die.allResults(context, terseKeys=True)

            for dieResult in dieResults:
                for prevResult in results:
                    newResult = (prevResult[0]+dieResult[0],prevResult[1]+dieResult[1])

                    nextResults[newResult] = nextResults.get(newResult,0) + dieResults[dieResult] * results[prevResult]

            results = nextResults

        if disregardExcessWard:
            newResults = {}

            for successWarpPair, count in results.items():
                effectiveKey = successWarpPair

                if successWarpPair[1] < nStaticWard:
                    effectiveKey = (successWarpPair[0],0)
                else:
                    effectiveKey = (successWarpPair[0],successWarpPair[1] - nStaticWard)

                if effectiveKey not in newResults:
                    newResults[effectiveKey] = 0

                newResults[effectiveKey] += count

            results = newResults

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

p2Face = DieFace(name="Warp2", symbols={ DieSymbol.STRONG_WARP: 1, DieSymbol.WEAK_WARP: 1 })
p1Face = DieFace(name="Warp", symbols={ DieSymbol.STRONG_WARP: 1 })
d2Face = DieFace(name="Ward2", symbols={ DieSymbol.STRONG_WARD: 1, DieSymbol.WEAK_WARD: 1 })
wsdFace = DieFace(name="Weak Power", symbols={ DieSymbol.WEAK_POWER: 1, DieSymbol.WARD: 1 })
sFace = DieFace(name="Normal Power", symbols={ DieSymbol.POWER: 1, DieSymbol.WEAK_POWER: 1 })
sspFace = DieFace(name="Strong Power", symbols={ DieSymbol.STRONG_POWER: 1, DieSymbol.POWER: 1, DieSymbol.WEAK_POWER: 1, DieSymbol.WARP: 1 })

warpingDie = Die(name="Warping Die", faces=[p2Face, p1Face, d2Face, wsdFace, sFace, sspFace])

bFace = DieFace(name="Blank", symbols={})
wsFace = DieFace(name="Weak Power", symbols={ DieSymbol.WEAK_POWER: 1 })
ssFace = DieFace(name="Strong Power", symbols={ DieSymbol.STRONG_POWER: 1, DieSymbol.POWER: 1, DieSymbol.WEAK_POWER: 1 })

nativeDie = Die(name="Native Die", faces=[bFace, bFace, bFace, wsFace, sFace, ssFace])

for nStaticWard in range(0,4):
    for nWarpingDice in range(0,10):
        for nNativeDice in range(2,3):
            pool = DiePool(str(nNativeDice) + "dN + " + str(nWarpingDice) + "dW", ([nativeDie] * nNativeDice) + ([warpingDie] * nWarpingDice))

            for context in (RollContext.DEPOWERED, RollContext.STANDARD, RollContext.EMPOWERED):
                # for manual review use these two lines
                print(pool.name + " plus " + str(nStaticWard) + " Ward, " + context)
                printFormattedResults(pool.allResults(context,terseKeys=True,disregardExcessWard=True,nStaticWard=nStaticWard))
                print()

                # for copy/paste into a spreadsheet use this line
                #printSpreadsheetSuccessResults(pool.allResults(context,terseKeys=True))

