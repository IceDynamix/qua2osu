"""General constants that are needed in most places"""

# Hitsounds enum
HIT_SOUNDS = {
    "Normal": 1,
    "Whistle": 2,
    "Finish": 4,
    "Clap": 8
}

# Samplesets list
SAMPLESETS = [
    "Soft",
    "Normal",
    "Drum"
]


# Dictionary for attributes that exist in both games, but are named differently

# quaverAttribute -> osuAttribute

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

# For attributes that should be left the way they are.

# attribute -> default value

DEFAULT_VALUES = {

    "general": {
        "AudioLeadIn": 0,
        "Countdown": 0,
        "StackLeniency": 0.7,
        "Mode": 3,  # mania
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
        "BeatmapID": 0,  # unsubmitted
        "BeatmapSetID": -1
    },

    "difficulty": {
        "ApproachRate": 5,
        "SliderMultiplier": 1.4,
        "SliderTickRate": 1
    },

}

# Attributes of the command line arguments

# No documentation is really needed because there's already a description
# for every argument

COMMAND_LINE_ARGS = {

    "input": {
        "shortFlag": "-i",
        "longFlag": "--input",
        "required": False,
        "description": "Path of the input folder, defaults to ./input",
        "default": "input",
        "type": str
    },

    "output": {
        "shortFlag": "-o",
        "longFlag": "--output",
        "required": False,
        "description": "Path of the output folder, defaults to ./output",
        "default": "output",
        "type": str
    },

    "overall_difficulty": {
        "shortFlag": "-od",
        "longFlag": "--overall-difficulty",
        "required": False,
        "description": "Overall difficulty as an integer between 0 and 10, defaults to 8",
        "default": 8,
        "type": float,
        "min": 0,
        "max": 10
    },

    "hp_drain": {
        "shortFlag": "-hp",
        "longFlag": "--hp-drain",
        "required": False,
        "description": "HP drain as an integer between 0 and 10, defaults to 8",
        "default": 8,
        "type": float,
        "min": 0,
        "max": 10
    },

    "hitsound_volume": {
        "shortFlag": "-hv",
        "longFlag": "--hitsound-volume",
        "required": False,
        "description": "Hitsound volume as an integer between 0 and 100, defaults to 20",
        "default": 20,
        "type": int,
        "min": 0,
        "max": 100
    },

    "sampleset": {
        "shortFlag": "-hs",
        "longFlag": "--sampleset",
        "required": False,
        "description": "Hitsound sample set as either 'Soft', 'Normal' or 'Drum', defaults to Soft",
        "default": "Soft",
        "type": str,
        "list": SAMPLESETS
    }


}
