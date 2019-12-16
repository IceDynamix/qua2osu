import math
import os
import re
import time
import zipfile

import yaml


regexIllegalCharacters = re.compile(r"[<>:\"/\\|\?\*]")


def loadQua(fileContent):
    qua = yaml.safe_load(fileContent)
    return qua


def cleanPath(path):
    path = regexIllegalCharacters.sub("", path)
    path = path.replace(" ", "_")
    return path


generalRenames = {
    "AudioFile": "AudioFilename",
    "SongPreviewTime": "PreviewTime"
}

generalDefaultValues = {
    "AudioLeadIn": 0,
    "Countdown": 0,
    "StackLeniency": 0.7,
    "Mode": 3,
    "LetterboxInBreaks": 0,
    "SpecialStyle": 0,
    "WidescreenStoryboard": 0
}


def convertGeneral(qua, options):
    # AudioFilename, AudioLeadIn, AudioHash, PreviewTime, Countdown, SampleSet, StackLeniency, Mode, LetterboxInBreaks, StoryFireInFront, UseSkinSprites, AlwaysShowPlayfield, OverlayPosition, SkinPreference, EpilepsyWarning, CountdownOffset, SpecialStyle, WidescreenStoryboard, SamplesMatchPlaybackRate
    lines = ["[General]"]

    # TODO sampleset
    sampleSet = options["sampleSet"]
    lines.append(f"SampleSet: {sampleSet}")
    for element in generalRenames:
        lines.append(f"{generalRenames[element]}: {qua[element]}")
    for attribute in generalDefaultValues:
        lines.append(f"{attribute}: {generalDefaultValues[attribute]}")

    return "\n".join(lines)


editorDefaultValues = {
    "Bookmarks": "",  # if i set this to None then it will print "None" in the .osu, which is why i set this to ""
    "DistanceSpacing": 1.5,
    "BeatDivisor": 4,
    "GridSize": 4,
    "TimelineZoom": 2.5
}


def convertEditor(qua):
    # Bookmarks, DistanceSpacing, BeatDivisor, GridSize, TimelineZoom
    lines = ["[Editor]"]
    for attribute in editorDefaultValues:
        lines.append(f"{attribute}: {editorDefaultValues[attribute]}")
    return "\n".join(lines)


# qua attribute name -> osu attribute name
metadataRenames = {
    "DifficultyName": "Version",
    "SongPreviewTime": "PreviewTime"
}

metadataDefaultValues = {
    "BeatmapID": 0,
    "BeatmapSetID": -1
}


def convertMetadata(qua):
    lines = ["[Metadata]"]

    for element in qua:
        if element in ["AudioFile", "Artist", "Title", "Source", "Tags", "Creator"]:
            lines.append(f"{element}:{qua[element]}")
            if element in ["Artist", "Title"]:
                lines.append(f"{element}Unicode:{qua[element]}")
        elif element in metadataRenames:
            lines.append(f"{metadataRenames[element]}:{qua[element]}")

    for attribute in metadataDefaultValues:
        lines.append(f"{attribute}:{metadataDefaultValues[attribute]}")

    return "\n".join(lines)


difficultyDefaultValues = {
    "ApproachRate": 5,
    "SliderMultiplier": 1.4,
    "SliderTickRate": 1
}


def convertDifficulty(qua, options):
    # HPDrainRate, CircleSize, OverallDifficulty, ApproachRate, SliderMultiplier, SliderTickrate
    lines = ["[Difficulty]"]

    keyCount = qua["Mode"][-1:]
    od = options["od"]
    hp = options["hp"]

    lines.append(f"OverallDifficulty: {od}")
    lines.append(f"CircleSize: {keyCount}")
    lines.append(f"HPDrainRate: {hp}")

    for attribute in difficultyDefaultValues:
        lines.append(f"{attribute}: {difficultyDefaultValues[attribute]}")
    return "\n".join(lines)


def convertEvents(qua):
    # Background syntax: 0,0,filename,0,0
    lines = ["[Events]"]
    lines.append(f'0,0,"{qua["BackgroundFile"]}",0,0')
    return "\n".join(lines)


def convertTimingPoints(qua, options):
    # time, beatLength, meter, sampleSet, sampleIndex, volume, uninherited, effects
    lines = ["[TimingPoints]"]
    hitSoundVolume = options["hitSoundVolume"]

    for timingPoint in qua["TimingPoints"]:
        # if any value is 0 then quaver doesnt print it in the qua
        startTime = timingPoint.get("StartTime", 0)
        bpm = timingPoint.get("Bpm", 0)
        if bpm <= 0:  # 0.0x bpm or negative bpm
            msPerBeat = -10e10  # substituting with very low bpm value
        else:
            msPerBeat = 60000/bpm
        lines.append(
            f"{startTime},{msPerBeat},4,0,0,{hitSoundVolume},1,0")

    for sv in qua["SliderVelocities"]:
        startTime = sv.get("StartTime", 0)
        multiplier = sv.get("Multiplier", 0)
        if multiplier <= 0:  # 0.0x sv or negative sv
            svValue = -10e10  # substituting with very low sv value
        else:
            svValue = -100/multiplier
        lines.append(f"{startTime},{svValue},0,0,0,{hitSoundVolume},0")

    # osu doesnt care if the section is sorted chronologically or not so im not doing it

    return "\n".join(lines)


hitSoundsDict = {
    "Normal": 1,
    "Whistle": 2,
    "Finish": 4,
    "Clap": 8
}


def convertHitObjects(qua):
    lines = ["[HitObjects]"]
    columns = int(qua["Mode"][-1:])  # 4 for 4k, 7 for 7k

    for hitObject in qua["HitObjects"]:

        # x, y, time, type, hitSound, objectParams, hitSample
        time = hitObject.get("StartTime", 0)
        lane = hitObject.get("Lane", 0)
        x = math.floor((lane / columns) * 512) - 64
        y = 192
        hsBits = 0

        if "HitSound" in hitObject and not isinstance(hitObject["HitSound"], int):
            hitSounds = hitObject["HitSound"].split(", ")
            for hs in hitSounds:
                hsBits += hitSoundsDict[hs]

        if "EndTime" not in hitObject:  # normal note
            line = f"{x},{y},{time},1,{hsBits},0:0:0:0:"
        else:  # long note
            # x,y,time,type,hitSound,endTime,hitSample
            endTime = hitObject["EndTime"]
            line = f"{x},{y},{time},128,{hsBits},{endTime}:0:0:0:0:"

        lines.append(line)

    return "\n".join(lines)


def convertQua2Osu(fileContent, options):
    qua = loadQua(fileContent)
    osu = "\n\n".join([
        "// This map was converted using qua2osu",
        "osu file format v14",
        convertGeneral(qua, options),
        convertEditor(qua),
        convertMetadata(qua),
        convertDifficulty(qua, options),
        convertEvents(qua),
        convertTimingPoints(qua, options),
        convertHitObjects(qua)
    ])

    return osu


def convertMapset(path, outputFolder, options):
    # prefixing with q to prevent osu from showing the wrong preview backgrounds
    folderName = "q" + os.path.basename(path).split(".")[0]
    outputPath = os.path.join(outputFolder, folderName)

    with zipfile.ZipFile(path, "r") as oldDir:
        oldDir.extractall(outputPath)

    for file in os.listdir(outputPath):
        filePath = os.path.join(outputPath, file)
        if file.endswith(".qua"):
            with open(filePath, "r") as openedFile:
                fileContent = openedFile.read()
                osu = convertQua2Osu(fileContent, options)
                with open(filePath.replace(".qua", ".osu"), "w+") as newFile:
                    newFile.write(osu)
            os.remove(filePath)

    with zipfile.ZipFile(outputPath + ".osz", "w") as newDir:
        for root, dirs, files in os.walk(outputPath):
            for file in files:
                newDir.write(os.path.join(root, file), file)

    return
