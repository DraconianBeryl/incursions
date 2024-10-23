#!/usr/bin/python3

import itertools
import random
import statistics

LOCATION_IDS = [chr(c) for c in range(ord("A"),ord("Z") + 1)]
CLUE_IDS = [chr(c) for c in range(ord("α"),ord("ω") + 1)]

def mapGenerator(nClueLocations: int, nLocationEncounters: int, nStarterClues: int):
    if nClueLocations > len(LOCATION_IDS):
        raise ValueError
    if (nClueLocations + nStarterClues) > len(CLUE_IDS):
        raise ValueError

    locs = LOCATION_IDS[0:nClueLocations]
    syms = CLUE_IDS[0:(nClueLocations+nStarterClues)]

    def _mapGenerator():
        locShuffle = random.sample(locs, len(locs));
        starterClues = locShuffle[:nStarterClues]
        targets = locShuffle[nStarterClues:]
        targets += syms[:nStarterClues]
        random.shuffle(targets)
        return {
            "starters": starterClues,
            "locations": { l: {"c":t, "d": random.randrange(nLocationEncounters)} for (t,l) in zip(targets,locs) }
        }

    return _mapGenerator

def mapAnalyzer(mapData: dict):
    starters = mapData["starters"]
    locs = mapData["locations"]

    depthsList = []
    encountersList = []
    locationsList = []

    for s in starters:
        at = s
        locations = 0
        encounters = 0
        while at in locs:
            depthsList.append(locs[at]["d"])
            encounters += 1 + locs[at]["d"]
            locations += 1
            at = locs[at]["c"]
        encountersList.append(encounters)
        locationsList.append(locations)

    return { "depth": depthsList, "encounters": encountersList, "locations": locationsList }

def calcMapMetrics(mapData: dict):
    return {
        v: { "min": min(mapData[v]), "max": max(mapData[v]), "mean": statistics.mean(mapData[v]) } for v in mapData
    }

def calcMapGroupMetrics(mapStats: dict):
    return {
        v: {
            "min": min(mapStats[v].keys()),
            "max": max(mapStats[v].keys()),
            "mean": statistics.fmean(mapStats[v].keys(),mapStats[v].values())
        } for v in mapStats
    }

def evalRuns(nRuns: int, generatorFunction):
    stats = { "depth": {}, "encounters": {}, "locations": {} }

    for i in range(nRuns):
        ms = mapAnalyzer(generatorFunction())
        for k in stats:
            kStats = stats[k]
            for v in ms[k]:
                if v not in kStats:
                    kStats[v] = 0
                kStats[v] += 1

    print(stats)
    return calcMapGroupMetrics(stats)

nClueLocations = 16
nLocationEncounters = 2
nTargets = 3

mapgen = mapGenerator(nClueLocations,nLocationEncounters,nTargets)

print(evalRuns(1000,mapgen))
