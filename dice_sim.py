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
ward b. a die with one warp and no ward

Other options to explore
 a. one always warp and one maybe warp (condition TBD)
 b. three levels of warp - corresponding with the three levels of power for
    success/failure
 c. sides with multiple symbols?
"""

from dataclasses import dataclass
import enum
import random
import statistics
import typing

class DieFace(enum.StrEnum):
    WARP         = enum.auto()
    WARD         = enum.auto()
    WEAK_POWER   = enum.auto()
    POWER        = enum.auto()
    STRONG_POWER = enum.auto()

ABILITY_DIE = (DieFace.WARP, DieFace.WARP, DieFace.WARD, DieFace.WEAK_POWER, DieFace.POWER, DieFace.STRONG_POWER)
ABILITY_DIE_SIDES = len(ABILITY_DIE)

class Aspect(enum.StrEnum):
    NATIVE = enum.auto()
    FIRE   = enum.auto()
    AIR    = enum.auto()
    WATER  = enum.auto()
    EARTH  = enum.auto()

class RollContext(enum.StrEnum):
    STANDARD  = enum.auto()
    DEPOWERED = enum.auto()
    EMPOWERED = enum.auto()

@dataclass(frozen=True)
class DieRoll:
    aspect: Aspect
    face: DieFace

    def __str__(self):
        return self.face + "(" + self.aspect + ")"

class TestRollResults:
    def __init__(self, powerContext: RollContext = RollContext.STANDARD):
        self.powerContext = powerContext
        self.dice = []

    def addResult(self, result: DieRoll):
        self.dice.append(result)

    def successes(self) -> int:
        nSuccesses = 0
        for d in self.dice:
            if d.face == DieFace.WEAK_POWER and self.powerContext == RollContext.EMPOWERED:
                nSuccesses += 1
            if d.face == DieFace.POWER and self.powerContext != RollContext.DEPOWERED:
                nSuccesses += 1
            if d.face == DieFace.STRONG_POWER:
                nSuccesses += 1
        return nSuccesses

    def netWarp(self) -> int:
        aspectedWarp = {}
        for d in self.dice:
            if d.aspect != Aspect.NATIVE:
                if d.aspect not in aspectedWarp:
                    aspectedWarp[d.aspect] = 0
                if d.face == DieFace.WARP:
                    aspectedWarp[d.aspect] += 1
                if d.face == DieFace.WARD:
                    aspectedWarp[d.aspect] -= 1
        for a in aspectedWarp:
            if aspectedWarp[a] < 0:
                aspectedWarp[a] = 0
        return aspectedWarp

    def __str__(self):
        return '[' + ','.join(str(d) for d in self.dice) + ']@' + self.powerContext

class Ability:
    def __init__(self, name: str, score: int, baseType: Aspect = Aspect.NATIVE, specials: dict = None):
        if score <= 0:
            raise ValueError

        self.name     = name
        self.score    = score
        self.baseType = baseType
        self.pool = {}

        scoreBalance = score

        if specials is not None:
            for specialKey in specials.keys():
                if specialKey not in Aspect:
                    raise ValueError
                if specials[specialKey] <= 0:
                    raise ValueError
                if specials[specialKey] > scoreBalance:
                    raise ValueError
                self.pool[specialKey] = specials[specialKey]
                scoreBalance -= specials[specialKey]

        self.pool[baseType] = scoreBalance

    def __str__(self):
        representation = self.name + "(" + self.baseType + ": " + str(self.pool[self.baseType])

        for specialType in self.pool:
            if specialType != self.baseType:
                representation += ", " + specialType + ": " + str(self.pool[specialType])

        representation += ")"

        return representation

    def roll(self, powerContext: RollContext = RollContext.STANDARD):
        result = TestRollResults(powerContext)

        for a,n in self.pool.items():
            for i in range(n):
                result.addResult( DieRoll(aspect=a, face=random.choice(ABILITY_DIE)) )

        return result


strength = Ability("Strength", 3)
speed    = Ability("Speed", 5, Aspect.AIR)
health   = Ability("Health", 5, Aspect.NATIVE, { Aspect.EARTH: 2 })
wisdom   = Ability("Wisdom", 4, Aspect.NATIVE, { Aspect.WATER: 1, Aspect.FIRE: 3 })

for ability in (strength, speed, health, wisdom):
    for powerContext in RollContext:
        for i in range(10):
            tr = ability.roll(powerContext)
            print((str(tr),tr.successes(),tr.netWarp()))
