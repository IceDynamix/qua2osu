# ## Imports
import math  # for calculations
import os  # for paths and directories
import zipfile  # to handle .zip files (.qua and .osz)

import yaml  # to parse .yaml files (.qua)

from constants import *

# ## Functions


def loadQua(fileContent: str) -> object:
    """Parses the .qua (.yaml) difficulty file into an object using the PyYaml module"""

    qua = yaml.safe_load(fileContent)
    return qua


def cleanPath(path: str) -> str:
    """Cleans the path by removing illegal characters and replacing spaces with underscores *(currently unused)*"""

    path = REGEX_ILLEGAL_CHARACTERS.sub("", path)
    path = path.replace(" ", "_")
    return path


# ### General


def convertGeneral(qua: object, options: object) -> str:
    """Generates the [General] section of the .osu

    Currently generates following attributes:

    - AudioFilename
    - AudioLeadIn
    - PreviewTime
    - SampleSet
    - StackLeniency
    - Mode
    - LetterboxInBreaks
    - SpecialStyle
    - WidescreenStoryboard
    """

    lines = ["[General]"]
    generalRenames = RENAMES["general"]
    generalDefaultValues = DEFAULT_VALUES["general"]

    sampleSet = options["sampleSet"]
    lines.append(f"SampleSet: {sampleSet}")

    # Attributes that exist in both games but are named differently
    for element in RENAMES["general"]:
        lines.append(f"{generalRenames[element]}: {qua[element]}")

    for attribute in generalDefaultValues:
        lines.append(f"{attribute}: {generalDefaultValues[attribute]}")

    return "\n".join(lines)


# ### Editor


def convertEditor() -> str:
    """Generates the [Editor] section of the .osu

    Currently generates following attributes:

    - Bookmarks
    - DistanceSpacing
    - BeatDivisor
    - GridSize
    - TimelineZoom
    """

    lines = ["[Editor]"]
    editorDefaultValues = DEFAULT_VALUES["editor"]

    for attribute in editorDefaultValues:
        lines.append(f"{attribute}: {editorDefaultValues[attribute]}")

    return "\n".join(lines)


# ### Metadata


def convertMetadata(qua: object) -> str:
    """Generates the [Metadata] section of the .osu

    Currently generates following attributes:

    - AudioFile
    - Artist
    - ArtistUnicode
    - Title
    - TitleUnicode
    - Source
    - Creator
    - Tags
    - BeatmapID
    - BeatmapSetID
    """

    lines = ["[Metadata]"]
    metadataRenames = RENAMES["metadata"]
    metadataDefaultValues = DEFAULT_VALUES["metadata"]

    for element in qua:

        # Attributes that exist in both games and are named the same
        if element in ["Artist", "Title", "Source", "Creator"]:
            lines.append(f"{element}:{qua[element]}")

            # osu! uses ArtistUnicode and TitleUnicode attributes
            # to provide a romanized version of them. Since
            # Quaver doesn't really work with them, they can be set
            # to the same as the regular artist and title attribute
            if element in ["Artist", "Title"]:
                lines.append(f"{element}Unicode:{qua[element]}")

        # Attributes that exist in both games but are named differently
        elif element in metadataRenames:
            lines.append(f"{metadataRenames[element]}:{qua[element]}")

        # Adding Quaver to tags additionally to the already existing
        # tags in the .qua
        elif element == "Tags":
            tags = qua["Tags"]
            lines.append(f"Tags:Quaver {tags}")

    for attribute in metadataDefaultValues:
        lines.append(f"{attribute}:{metadataDefaultValues[attribute]}")

    return "\n".join(lines)


# ### Difficulty


def convertDifficulty(qua: object, options: object) -> str:
    """Generates the [Difficulty] section of the .osu

    Currently generates following attributes:

    - HPDrainRate
    - CircleSize
    - OverallDifficulty
    - ApproachRate
    - SliderMultiplier
    - SliderTickrate
    """

    lines = ["[Difficulty]"]
    difficultyDefaultValues = DEFAULT_VALUES["difficulty"]

    # Mode is provided either as "Keys4" or "Keys7", so this
    # extracts the number 4 or 7
    keyCount = qua["Mode"][-1:]
    od = options["od"]
    hp = options["hp"]

    # osu!mania uses Circle Size to save the key count
    lines.append(f"CircleSize: {keyCount}")
    lines.append(f"OverallDifficulty: {od}")
    lines.append(f"HPDrainRate: {hp}")

    for attribute in difficultyDefaultValues:
        lines.append(f"{attribute}: {difficultyDefaultValues[attribute]}")

    return "\n".join(lines)


# ### Events


def convertEvents(qua: object) -> str:
    """Generates the [Events] section of the .osu (only background)

    Background syntax: `0,0,filename,0,0`
    """

    lines = ["[Events]"]
    lines.append(f'0,0,"{qua["BackgroundFile"]}",0,0')

    return "\n".join(lines)


# ### Timing Points


def convertTimingPoints(qua: object, options: object) -> str:
    """Generates the [TimingPoints] section of the .osu

    Structure of a timing point:
    [time,beatLength,meter,sampleSet,sampleIndex,volume,uninherited,effects]

    - time (int)
        - Start time of the timing section, in milliseconds from the
        beginning of the beatmap's audio. The end of the timing section
        is the next timing point's time (or never, if this is the
        last timing point).

    - beatLength : float
        - For uninherited timing points, the duration of a beat, in
            milliseconds.
        - For inherited timing points, a negative inverse slider
            velocity multiplier, as a percentage. For example, -50 would
            make all sliders in this timing section twice
            as fast as SliderMultiplier.

    - meter (int)
        - Amount of beats in a measure. Inherited timing points ignore
        this property.

    - sampleSet (int)
        - Default sample set for hit objects (0 = beatmap default,
        1 = normal, 2 = soft, 3 = drum).

    - sampleIndex (int)
        - Custom sample index for hit objects. 0 indicates osu!'s default
        hit sounds.

    - volume (int)
        - Volume percentage for hit objects.

    - uninherited (0 or 1)
        - Whether or not the timing point is uninherited.

    - effects (int:int:...)
        - Bit flags that give the timing point extra effects.
    """

    lines = ["[TimingPoints]"]
    hitSoundVolume = options["hitSoundVolume"]

    # Converts each timing point
    for timingPoint in qua["TimingPoints"]:

        # If any value is 0 then Quaver doesn't print it in the qua
        startTime = timingPoint.get("StartTime", 0)
        bpm = timingPoint.get("Bpm", 0)

        if bpm <= 0:  # 0.0x BPM or negative BPM
            # osu! can't really work with negative BPM and working with 0
            # BPM is a pain by itself, so I'm substituting the value
            # with very low bpm value (0.000006 BPM) instead. It still shows as
            # 0 BPM in song select though, because of rounding.
            msPerBeat = -10e10
        else:
            msPerBeat = 60000 / bpm

        lines.append(f"{startTime},{msPerBeat},4,0,0,{hitSoundVolume},1,0")

    # Converts each SV point
    for sv in qua["SliderVelocities"]:
        startTime = sv.get("StartTime", 0)
        multiplier = sv.get("Multiplier", 0)

        if multiplier <= 0:  # 0.0x SV or negative SV
            # Similar to BPM, osu! can't handle 0x or negative SV values, which is why
            # I'm substituting it with a very low value (0.00000001‬x). osu! clamps
            # all SV values between 0.01x-10x, so putting -10e10 instead of -10e4
            # doesn't *really* make a difference. That could change with lazer though
            # so I'm keeping it in.
            svValue = -10e10

        else:
            svValue = -100 / multiplier

        lines.append(f"{startTime},{svValue},0,0,0,{hitSoundVolume},0,0")

    # I'm running through all uninherited points, then all inherited points,
    # which means that the lines aren't chronologically sorted.
    # osu! doesnt care about the order of the timing points though, so
    # I'm not sorting it.

    return "\n".join(lines)


# ### Hit Objects


def convertHitObjects(qua: object) -> str:
    """Generates the [HitObjects] section of the .osu

    - Types:
        - 1 << 0 : Hit circle (normal note in osu!mania)
        - 1 << 1 : Slider (unused in osu!mania)
        - 1 << 3 : Spinner (unused in osu!mania)
        - 1 << 7 : osu!mania hold (commonly referred to as long note or LN)

    - Structure of a normal hit object:
        - [x,y,time,type,hitSound,objectParams,hitSample]
        - x (int)
            - Determines the index of the column that the note will be in.
            It is computed by floor(x * columnCount / 512) and
            clamped between 0 and columnCount - 1.
        - y (int)
            - Unused in osu!mania, defaults to 192
        - time (int)
            - Time when the object is to be hit, in milliseconds from
            the beginning of the beatmap's audio.
        - type (int)
            - Bit flags indicating the type of the object.
       - hitSound (int,int,...)
            - Extra parameters specific to the object's type.
        - objectParams
            - Extra parameters specific to the object's type.
        - hitSample (int)
            - bitwise flag

    - Structure of a LN:
        - [x,y,time,type,hitSound,endTime:hitSample]
        - endTime (int)
            - End time of the hold, in milliseconds from the
            beginning of the beatmap's audio.
    """

    lines = ["[HitObjects]"]

    # Mode is provided either as "Keys4" or "Keys7", so this
    # extracts the number 4 or 7
    numberOfCcolumns = int(qua["Mode"][-1:])

    for hitObject in qua["HitObjects"]:

        startTime = hitObject.get("StartTime", 0)
        lane = hitObject.get("Lane", 0)

        # osu! uses the x-coordinate to determine the
        # column, the max width of the osu playfield is 512
        xPos = math.floor((lane / numberOfCcolumns) * 512) - 64

        # y-coordinate is unused so default is set to 192, half of
        # osu!s max height
        yPos = 192

        # Bitwise enum
        hsBits = 0

        # Don't ask me how, but I've had hitsound values of -15 already, even though
        # anything other than a comma-seperated string shouldn't even be possible
        if "HitSound" in hitObject and not isinstance(hitObject["HitSound"], int):
            hitSounds = hitObject["HitSound"].split(", ")

            for hitSound in hitSounds:
                hsBits += HIT_SOUNDS[hitSound]

        # Is Normal note
        if "EndTime" not in hitObject:
            line = f"{xPos},{yPos},{startTime},1,{hsBits},0:0:0:0:"

        # LN
        else:
            endTime = hitObject["EndTime"]
            line = f"{xPos},{yPos},{startTime},128,{hsBits},{endTime}:0:0:0:0:"

        lines.append(line)

    return "\n".join(lines)


# ### Mapset


def convertQua2Osu(fileContent: str, options: object) -> str:
    """Converts a .qua beatmap file to a .osu beatmap file

    All parts are split into different sections, defined by the .osu structure:

    - General
        - Contains general settings
    - Editor
        - Contains editor related settings
    - Metadata
        - Contains the metadata of the beatmap
    - Difficulty
        - Contains difficulty related settings
    - Events
        - Contains the background file name
    - TimingPoints
        - Contains the timing
    - HitObjects
        - Contains the hit objects (notes)
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

    # Extra empty line at the bottom to help some tools
    # who expect one (like the R programming language)
    return osu + "\n"


def convertMapset(path: str, outputFolder: str, options) -> None:
    """Converts a whole .qp mapset to a .osz mapset

    Moves all files to a new directory and converts all .qua files to .osu files

    This function is called in the GUI.

    Options parameter is built up as following:

        options = {
            "od": int,
            "hp": int,
            "hitSoundVolume": int,
            "sampleSet": ["Soft","Normal","Drum"]
        }
    """

    # Prefixing with "q_" to prevent osu from showing the wrong preview
    # backgrounds, because it takes the folder number to
    # choose the background for whatever reason
    folderName = "q_" + os.path.basename(path).replace(".qp", "")
    outputPath = os.path.join(outputFolder, folderName)

    # Opens the .qp (.zip) mapset file and extracts it into a folder in the same directory
    with zipfile.ZipFile(path, "r") as oldDir:
        oldDir.extractall(outputPath)

    # Converts each .qua difficulty file
    for file in os.listdir(outputPath):
        filePath = os.path.join(outputPath, file)

        # Replaces each .qua file with the converted .osu file
        if file.endswith(".qua"):

            with open(filePath, "r") as openedFile:
                fileContent = openedFile.read()
                osu = convertQua2Osu(fileContent, options)

                with open(filePath.replace(".qua", ".osu"), "w+") as newFile:
                    newFile.write(osu)

            os.remove(filePath)

    # Creates a new .osz (.zip) mapset file
    with zipfile.ZipFile(outputPath + ".osz", "w") as newDir:
        for root, dirs, files in os.walk(outputPath):
            for file in files:
                newDir.write(os.path.join(root, file), file)
