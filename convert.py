# 
import math
import os
import re
import time
import zipfile

import yaml

regexIllegalCharacters = re.compile(r"[<>:\"/\\|\?\*]")


# For attributes that exist in both games but are named differently
# QuaverAttribute: osuAttribute

RENAMES = {

    "general": {
        "AudioFile": "AudioFilename",
        "SongPreviewTime": "PreviewTime"
    },

    "metadata": {
        "DifficultyName": "Version",
        "SongPreviewTime": "PreviewTime"
    },

}

# For attributes that should be left the way they are

DEFAULT_VALUES = {

    "general": {
        "AudioLeadIn": 0,
        "Countdown": 0,
        "StackLeniency": 0.7,
        "Mode": 3,
        "LetterboxInBreaks": 0,
        "SpecialStyle": 0,
        "WidescreenStoryboard": 0
    },

    "editor": {
        # If bookmarks were to be set to None,
        # it would print out "None" when casted to a string
        "Bookmarks": "",
        "DistanceSpacing": 1.5,
        "BeatDivisor": 4,
        "GridSize": 4,
        "TimelineZoom": 2.5
    },

    "metadata": {
        "BeatmapID": 0,
        "BeatmapSetID": -1
    },

    "difficulty": {
        "ApproachRate": 5,
        "SliderMultiplier": 1.4,
        "SliderTickRate": 1
    }
}


def loadQua(fileContent: str) -> object:
    """Parses the .qua (.yaml) file into an object using PyYaml"""

    qua = yaml.safe_load(fileContent)
    return qua


def cleanPath(path: str) -> str:
    """Cleans the path by removing illegal characters and replacing spaces with underscores"""

    # ! Currently unused
    path = regexIllegalCharacters.sub("", path)
    path = path.replace(" ", "_")
    return path


def convertGeneral(qua: object, options: object) -> str:
    """Generates the [General] section of the .osu

    Currently generates following attributes:
        AudioFilename, AudioLeadIn,
        PreviewTime, SampleSet,
        StackLeniency, Mode,
        LetterboxInBreaks, SpecialStyle,
        WidescreenStoryboard
    """

    lines = ["[General]"]
    generalRenames = RENAMES["general"]
    generalDefaultValues = DEFAULT_VALUES["general"]

    sampleSet = options["sampleSet"]
    lines.append(f"SampleSet: {sampleSet}")

    for element in RENAMES["general"]:
        lines.append(f"{generalRenames[element]}: {qua[element]}")

    for attribute in generalDefaultValues:
        lines.append(f"{attribute}: {generalDefaultValues[attribute]}")

    return "\n".join(lines)


def convertEditor() -> str:
    """Generates the [Editor] section of the .osu

    Currently generates following attributes:
        Bookmarks, DistanceSpacing,
        BeatDivisor, GridSize, TimelineZoom
    """

    lines = ["[Editor]"]
    editorDefaultValues = DEFAULT_VALUES["editor"]

    for attribute in editorDefaultValues:
        lines.append(f"{attribute}: {editorDefaultValues[attribute]}")

    return "\n".join(lines)


def convertMetadata(qua: object) -> str:
    """Generates the [Metadata] section of the .osu

    Currently generates following attributes:
        AudioFile, Artist, ArtistUnicode, Title,
        TitleUnicode, Source, Creator, Tags,
        BeatmapID, BeatmapSetID
    """

    lines = ["[Metadata]"]
    metadataRenames = RENAMES["metadata"]
    metadataDefaultValues = DEFAULT_VALUES["metadata"]

    for element in qua:

        if element in ["AudioFile", "Artist", "Title", "Source", "Creator"]:
            lines.append(f"{element}:{qua[element]}")

            if element in ["Artist", "Title"]:
                lines.append(f"{element}Unicode:{qua[element]}")

        elif element in metadataRenames:
            lines.append(f"{metadataRenames[element]}:{qua[element]}")

        elif element == "Tags":
            tags = qua["Tags"]
            lines.append(f"Tags:Quaver {tags}")

    for attribute in metadataDefaultValues:
        lines.append(f"{attribute}:{metadataDefaultValues[attribute]}")

    return "\n".join(lines)


def convertDifficulty(qua: object, options: object) -> str:
    """Generates the [Difficulty] section of the .osu

    Currently generates following attributes:
        HPDrainRate, CircleSize,
        OverallDifficulty, ApproachRate,
        SliderMultiplier, SliderTickrate
    """

    lines = ["[Difficulty]"]
    difficultyDefaultValues = DEFAULT_VALUES["difficulty"]

    keyCount = qua["Mode"][-1:]
    od = options["od"]
    hp = options["hp"]

    lines.append(f"OverallDifficulty: {od}")
    lines.append(f"CircleSize: {keyCount}")
    lines.append(f"HPDrainRate: {hp}")

    for attribute in difficultyDefaultValues:
        lines.append(f"{attribute}: {difficultyDefaultValues[attribute]}")
    return "\n".join(lines)


def convertEvents(qua: object) -> str:
    """Generates the [Events] section of the .osu (only background)"""

    # Background syntax: 0,0,filename,0,0
    lines = ["[Events]"]
    lines.append(f'0,0,"{qua["BackgroundFile"]}",0,0')
    return "\n".join(lines)


def convertTimingPoints(qua: object, options: object) -> str:
    """Generates the [TimingPoints] section of the .osu

    Structure of a timing point:
        [time,beatLength,meter,sampleSet,sampleIndex,volume,uninherited,effects]

        time : int
            Start time of the timing section, in milliseconds from the
            beginning of the beatmap's audio. The end of the timing section
            is the next timing point's time (or never, if this is the
            last timing point).

        beatLength : float
            - For uninherited timing points, the duration of a beat, in
                milliseconds.
            - For inherited timing points, a negative inverse slider
                velocity multiplier, as a percentage. For example, -50 would
                make all sliders in this timing section twice
                as fast as SliderMultiplier.

        meter : int
            Amount of beats in a measure. Inherited timing points ignore
            this property.

        sampleSet : int
            Default sample set for hit objects (0 = beatmap default,
            1 = normal, 2 = soft, 3 = drum).

        sampleIndex : int
            Custom sample index for hit objects. 0 indicates osu!'s default
            hit sounds.

        volume : int
            Volume percentage for hit objects.

        uninherited : 0 or 1
            Whether or not the timing point is uninherited.

        effects : int:int:...
            Bit flags that give the timing point extra effects.
    """

    lines = ["[TimingPoints]"]
    hitSoundVolume = options["hitSoundVolume"]

    for timingPoint in qua["TimingPoints"]:
        # if any value is 0 then quaver doesnt print it in the qua
        startTime = timingPoint.get("StartTime", 0)
        bpm = timingPoint.get("Bpm", 0)

        if bpm <= 0:  # 0.0x bpm or negative bpm
            msPerBeat = -10e10  # substituting with very low bpm value
        else:
            msPerBeat = 60000 / bpm

        lines.append(
            f"{startTime},{msPerBeat},4,0,0,{hitSoundVolume},1,0")

    for sv in qua["SliderVelocities"]:
        startTime = sv.get("StartTime", 0)
        multiplier = sv.get("Multiplier", 0)

        if multiplier <= 0:  # 0.0x sv or negative sv
            svValue = -10e10  # substituting with very low sv value
        else:
            svValue = -100 / multiplier

        lines.append(f"{startTime},{svValue},0,0,0,{hitSoundVolume},0")

    # osu doesnt care if the section is sorted
    # chronologically or not so im not doing it

    return "\n".join(lines)


hitSoundsDict = {
    "Normal": 1,
    "Whistle": 2,
    "Finish": 4,
    "Clap": 8
}


def convertHitObjects(qua: object) -> str:
    """Generates the [TimingPoints] section of the .osu

    Types:
        1 << 0 : Hit circle (normal note in osu!mania)
        1 << 1 : Slider (unused in osu!mania)
        1 << 3 : Spinner (unused in osu!mania)
        1 << 7 : osu!mania hold (commonly referred to as long note or LN)

    Structure of a normal hit object:
        [x,y,time,type,hitSound,objectParams,hitSample]

        x : int
            Determines the index of the column that the note will be in.
            It is computed by floor(x * columnCount / 512) and
            clamped between 0 and columnCount - 1.

        y : int
            Unused in osu!mania, defaults to 192

        time : int
            Time when the object is to be hit, in milliseconds from
            the beginning of the beatmap's audio.

        type : int
            Bit flags indicating the type of the object.

        hitSound : int,int,...
            Extra parameters specific to the object's type.

        objectParams :
            Extra parameters specific to the object's type.

        hitSample :

    Structure of a LN:
        [x,y,time,type,hitSound,endTime:hitSample]

        endTime : int
            End time of the hold, in milliseconds from the
            beginning of the beatmap's audio.
    """
    # TODO finish docs

    lines = ["[HitObjects]"]
    # Mode is provided either as "Keys4" or "Keys7"
    numberOfCcolumns = int(qua["Mode"][-1:])

    for hitObject in qua["HitObjects"]:

        # x, y, time, type, hitSound, objectParams, hitSample
        startTime = hitObject.get("StartTime", 0)
        lane = hitObject.get("Lane", 0)
        xPos = math.floor((lane / numberOfCcolumns) * 512) - 64
        yPos = 192
        hsBits = 0

        if "HitSound" in hitObject and not isinstance(hitObject["HitSound"], int):
            hitSounds = hitObject["HitSound"].split(", ")

            for hitSound in hitSounds:
                hsBits += hitSoundsDict[hitSound]

        if "EndTime" not in hitObject:  # normal note
            line = f"{xPos},{yPos},{startTime},1,{hsBits},0:0:0:0:"
        else:  # long note
            # x,y,time,type,hitSound,endTime,hitSample
            endTime = hitObject["EndTime"]
            line = f"{xPos},{yPos},{startTime},128,{hsBits},{endTime}:0:0:0:0:"

        lines.append(line)

    return "\n".join(lines)


def convertQua2Osu(fileContent: str, options: object) -> str:
    """Converts a .qua beatmap file to a .osu beatmap file

    All parts are split into different sections, defined by the .osu structure
         [General] : Contains general settings
          [Editor] : Contains editor related settings
        [Metadata] : Contains the metadata of the beatmap
      [Difficulty] : Contains difficulty related settings
          [Events] : Contains the background file name
    [TimingPoints] : Contains the timing
      [HitObjects] : Contains the hit objects (notes)
    """

    qua = loadQua(fileContent)

    osu = "\n\n".join([
        "// This map was converted using qua2osu",
        "osu file format v14",
        convertGeneral(qua, options),
        convertEditor(),
        convertMetadata(qua),
        convertDifficulty(qua, options),
        convertEvents(qua),
        convertTimingPoints(qua, options),
        convertHitObjects(qua)
    ])

    return osu


def convertMapset(path: str, outputFolder: str, options=None) -> None:
    """Converts a whole .qp mapset to a .osz mapset

    Moves all files to a new directory and converts
    all .qua files to .osu files
    """

    # prefixing with q_ to prevent osu
    # from showing the wrong preview backgrounds
    folderName = "q_" + os.path.basename(path).split(".")[0]
    outputPath = os.path.join(outputFolder, folderName)

    if options is None:
        options = {
            "od": 8,
            "hp": 8,
            "hitSoundVolume": 20,
            "sampleSet": "Soft"
        }

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


def main():
    inputPath = "samples"
    outputPath = "output"
    qpFilesInInputDir = []

    for file in os.listdir(inputPath):
        path = os.path.join(inputPath, file)
        if (file.endswith('.qp') and os.path.isfile(path)):
            qpFilesInInputDir.append(file)

    numberOfQpFiles = len(qpFilesInInputDir)

    if numberOfQpFiles == 0:
        print("No mapsets found in " + inputPath)

    else:
        start = time.time()
        for file in qpFilesInInputDir:
            filePath = os.path.join(inputPath, file)
            print(f"Converting {filePath}")
            convertMapset(filePath, outputPath, None)

        end = time.time()
        timeElapsed = round(end - start, 2)
        print(
            f"Finished converting all mapsets, total time elapsed: {timeElapsed} seconds")


if __name__ == '__main__':
    main()
