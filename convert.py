import yaml
import time
import math
import os
import re
import zipfile

# global variables
inputFolder = "input"
outputFolder = "output"
regexIllegalCharacters = re.compile(r"[<>:\"/\\|\?\*]", re.IGNORECASE)

start = time.time()

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)


def loadQua(fileContent):
    qua = yaml.safe_load(fileContent)
    return qua


def cleanPath(path):
    path = regexIllegalCharacters.sub("", path)
    path = path.replace(" ", "_")
    return path


generalDictionary = {
    "AudioFile": "AudioFilename",
    "SongPreviewTime": "PreviewTime"
}

defaultGeneral = """AudioLeadIn: 0
Countdown: 0
SampleSet: Soft
StackLeniency: 0.7
Mode: 3
LetterboxInBreaks: 0
SpecialStyle: 0
WidescreenStoryboard: 0"""


def convertGeneral(qua):
    # AudioFilename, AudioLeadIn, AudioHash, PreviewTime, Countdown, SampleSet, StackLeniency, Mode, LetterboxInBreaks, StoryFireInFront, UseSkinSprites, AlwaysShowPlayfield, OverlayPosition, SkinPreference, EpilepsyWarning, CountdownOffset, SpecialStyle, WidescreenStoryboard, SamplesMatchPlaybackRate
    lines = ["[General]"]
    for element in generalDictionary:
        lines.append(generalDictionary[element] +
                     ": " + str(qua[element]))
    lines.append(defaultGeneral)
    return "\n".join(lines)


defaultEditor = """Bookmarks:
DistanceSpacing: 1.5
BeatDivisor: 4
GridSize: 4
TimelineZoom: 2.5"""


def convertEditor(qua):
    # Bookmarks, DistanceSpacing, BeatDivisor, GridSize, TimelineZoom
    lines = ["[Editor]"]
    lines.append(defaultEditor)
    return "\n".join(lines)


# qua attribute name -> osu attribute name
metadataDictionary = {
    "DifficultyName": "Version",
    "SongPreviewTime": "PreviewTime"
}

defaultMetadata = """BeatmapID:0
BeatmapSetID:-1"""


def convertMetadata(qua):
    lines = ["[Metadata]"]

    for element in qua:
        if element in ["AudioFile", "Artist", "Title", "Source", "Tags", "Creator"]:
            lines.append(element + ":" + qua[element])
            if element in ["Artist", "Title"]:
                lines.append(element + "Unicode:" + qua[element])
        elif element in metadataDictionary:
            lines.append(metadataDictionary[element] +
                         ":" + str(qua[element]))

    lines.append(defaultMetadata)
    return "\n".join(lines)


defaultDifficulty = """HPDrainRate:8
OverallDifficulty:8
ApproachRate:5
SliderMultiplier:1.4
SliderTickRate:1"""


def convertDifficulty(qua):
    # HPDrainRate, CircleSize, OverallDifficulty, ApproachRate, SliderMultiplier, SliderTickrate
    lines = ["[Difficulty]"]
    lines.append("CircleSize:" + qua["Mode"][-1:])
    lines.append(defaultDifficulty)
    return "\n".join(lines)


def convertEvents(qua):
    # Background syntax: 0,0,filename,0,0
    lines = ["[Events]"]
    lines.append('0,0,"' + qua["BackgroundFile"] + '",0,0')
    return "\n".join(lines)


def convertTimingPoints(qua):
    # time,beatLength,meter,sampleSet,sampleIndex,volume,uninherited,effects
    lines = ["[TimingPoints]"]
    for timingPoint in qua["TimingPoints"]:
        startTime = timingPoint["StartTime"]
        bpm = timingPoint["Bpm"]
        msPerBeat = 60000/bpm
        array = [startTime, msPerBeat, 4, 0, 0, 0, 1, 0]
        lines.append(",".join([str(element) for element in array]))

    for sv in qua["SliderVelocities"]:
        startTime = sv["StartTime"]
        multiplier = -100/sv["Multiplier"]
        array = [startTime, multiplier, 0, 0, 0, 0, 0]
        lines.append(",".join([str(element) for element in array]))

    return "\n".join(lines)


def convertHitObjects(qua):
    lines = ["[HitObjects]"]
    columns = int(qua["Mode"][-1:])  # 4 for 4k, 7 for 7k

    for hitObject in qua["HitObjects"]:

        # x,y,time,type,hitSound,objectParams,hitSample
        # default to 0 when start time is not there
        time = hitObject.get("StartTime", 0)
        lane = hitObject["Lane"]
        x = math.floor((lane / columns) * 512) - 64
        y = 192

        if not "EndTime" in hitObject:  # normal note
            array = [x, y, time, 1, 0, "0:0:0:0:"]

        else:  # long note
            # x,y,time,type,hitSound,endTime,hitSample
            endTime = hitObject["EndTime"]
            array = [x, y, time, 128, 0, str(endTime) + ":0:0:0:0:"]

        lines.append(",".join([str(element) for element in array]))

    return "\n".join(lines)


def convertQua2Osu(fileContent):
    qua = loadQua(fileContent)

    osu = "\n\n".join(
        [
            "// This map was converted using qua2osu",
            "osu file format v14",
            convertGeneral(qua),
            convertEditor(qua),
            convertMetadata(qua),
            convertDifficulty(qua),
            convertEvents(qua),
            convertTimingPoints(qua),
            convertHitObjects(qua)
        ]
    )

    return osu


def convertMapset(path):
    folderName = os.path.basename(path).split(".")[0]
    outputPath = outputFolder + "/" + folderName

    with zipfile.ZipFile(path, "r") as oldDir:
        oldDir.extractall(outputPath)

    for file in os.listdir(outputPath):
        filePath = outputPath + "/" + file
        if file.endswith(".qua"):
            with open(filePath, "r") as openedFile:
                fileContent = openedFile.read()
                osu = convertQua2Osu(fileContent)
                with open(filePath.replace(".qua", ".osu"), "w+") as newFile:
                    newFile.write(osu)
            os.remove(filePath)

    with zipfile.ZipFile(outputPath + ".osz", "w") as newDir:
        for root, dirs, files in os.walk(outputPath):
            for file in files:
                newDir.write(os.path.join(root, file), file)

    print("Finished converting " + path)


for file in os.listdir(inputFolder):
    if file.endswith(".qp"):
        convertMapset(inputFolder + "/" + file)

end = time.time()
print("Execution Time: " + str(end-start) + " seconds")
