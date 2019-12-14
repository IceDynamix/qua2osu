import yaml
import time
import math
import os
import re

start = time.time()

outputFolder = "output"
regexIllegalCharacters = re.compile(r"[<>:\"/\\|\?\*]", re.IGNORECASE)

if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

def loadQua(path):
    with open(path, "r") as file:
        qua = yaml.safe_load(file)
    return qua


def cleanPath(path):
    path = regexIllegalCharacters.sub("", path)
    path = path.replace(" ", "_")
    return path


metadataDictionary = {
    "DifficultyName": "Version",
    "SongPreviewTime": "PreviewTime"
}


def convertGeneral(qua):
    # AudioFilename, AudioLeadIn, AudioHash, PreviewTime, Countdown, SampleSet, StackLeniency, Mode, LetterboxInBreaks, StoryFireInFront, UseSkinSprites, AlwaysShowPlayfield, OverlayPosition, SkinPreference, EpilepsyWarning, CountdownOffset, SpecialStyle, WidescreenStoryboard, SamplesMatchPlaybackRate
    return ""


def convertEditor(qua):
    # Bookmarks, DistanceSpacing, BeatDivisor, GridSize, TimelineZoom
    return ""


def convertMetadata(qua):
    # quaver
    # 'AudioFile': 'audio.mp3', 'SongPreviewTime': 85943, 'BackgroundFile': 'Ether_strike.jpg', 'MapId': 1631, 'MapSetId': 542, 'Mode': 'Keys4', 'Title': 'Ether Strike', 'Artist': 'Akira Complex', 'Source': 'Arcaea', 'Tags': 'dump sv ln jacks speed', 'Creator': 'IceDynamix', 'DifficultyName': 'celestial cry'

    # osu
    # Title, TitleUnicode, Artist, ArtistUnicode, Creator, version, Source, Tags, BeatmapID, BeatmapsetID
    resultString = "[Metadata]\n"

    for element in qua:
        if element in ["AudioFile", "Artist", "Title", "Source", "Tags", "Creator"]:
            resultString += element + ":" + qua[element] + "\n"
            if element in ["Artist", "Title"]:
                resultString += element + "Unicode:" + qua[element] + "\n"
        elif element in metadataDictionary:
            resultString += metadataDictionary[element] + \
                ":" + str(qua[element]) + "\n"

    return resultString


def convertDifficulty(qua):
    # HPDrainRate, CircleSize, OverallDifficulty, ApproachRate, SliderMultiplier, SliderTickrate
    return ""


def convertEvents(qua):
    # im basically only doing backgrounds dont judge me
    # Background syntax: 0,0,filename
    returnString = "[Events]\n"
    returnString += "0,0," + qua["BackgroundFile"]
    return returnString


def convertTimingPoints(qua):
    # time,beatLength,meter,sampleSet,sampleIndex,volume,uninherited,effects
    resultString = "[TimingPoints]\n"
    for timingPoint in qua["TimingPoints"]:
        startTime = timingPoint["StartTime"]
        bpm = timingPoint["Bpm"]
        msPerBeat = 60000/bpm
        array = [startTime, msPerBeat, 4, 0, 0, 0, 0, 0]
        timingPointString = ",".join([str(element) for element in array])
        resultString += timingPointString + "\n"

    for sv in qua["SliderVelocities"]:
        startTime = sv["StartTime"]
        multiplier = -100/sv["Multiplier"]
        array = [startTime, multiplier, 0, 0, 0, 0, 0]
        svString = ",".join([str(element) for element in array])
        resultString += svString + "\n"

    return resultString


def convertHitObjects(qua):
    resultString = "[HitObjects]\n"
    columns = int(qua["Mode"][-1:])  # 4 for 4k, 7 for 7k

    for hitObject in qua["HitObjects"]:

        # x,y,time,type,hitSound,objectParams,hitSample
        time = hitObject["StartTime"]
        lane = hitObject["Lane"]
        x = math.floor((lane / columns) * 512)
        y = 192

        if not hasattr(hitObject, "EndTime"):  # normal note
            objectType = 0
            array = [x, y, time, objectType, 0, 0, 0]

        else:  # long note
            # x,y,time,type,hitSound,endTime,hitSample
            objectType = 7
            endTime = hitObject["EndTime"]
            array = [x, y, time, objectType, endTime, 0]

        resultString += ",".join([str(element) for element in array]) + "\n"

    return resultString

def convertQua2Osu(path):
    print("Loading Qua...")
    qua = loadQua(path)
    general = convertGeneral(qua)
    editor = convertEditor(qua)
    metadata = convertMetadata(qua)
    difficulty = convertDifficulty(qua)
    events = convertEvents(qua)
    timingPoints = convertTimingPoints(qua)
    # leaving out colors :)
    hitObjects = convertHitObjects(qua)

    osu = "\n\n".join([general, editor, metadata, difficulty, events, timingPoints, hitObjects])

    folderName = qua["Artist"] + " - " + qua["Title"]
    fileName = folderName + " (" + qua["DifficultyName"] + ").osu"
    folderPath = cleanPath(outputFolder) + "/" + cleanPath(folderName)
    filePath = folderPath + "/" + cleanPath(fileName)

    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    with open(filePath, "w") as file:
        file.write(osu)
        print(" ----- Finished converting " + fileName)


for map in ["samples/620/3928.qua", "samples/542/1631.qua", "samples/636/4269.qua", "samples/473/1050.qua"]:
    convertQua2Osu(map)

end = time.time()
print("Execution Time: " + str(end-start) + " seconds")