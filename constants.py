# ## Imports
import re  # for regular expressions

# ## Constants

REGEX_ILLEGAL_CHARACTERS = re.compile(r"[<>:\"/\\|\?\*]")


HIT_SOUNDS = {
    "Normal": 1,
    "Whistle": 2,
    "Finish": 4,
    "Clap": 8
}


SAMPLESETS = [
    "Soft",
    "Normal",
    "Drum"
]


# For attributes that exist in both games but are named differently.

# Format: QuaverAttribute -> osuAttribute

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

# Format: QuaverAttribute -> osuAttribute

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
    },

}


COMMAND_LINE_ARGS = {

    "input": {
        "default": "input",
        "format": [str]
    },

    "output": {
        "default": "output",
        "format": str
    },

    "overall_difficulty": {
        "default": 8,
        "format": float,
        "min": 0,
        "max": 10
    },

    "hp_drain": {
        "default": 8,
        "format": float,
        "min": 0,
        "max": 10
    },

    "hitsound_volume": {
        "default": 20,
        "format": int,
        "min": 0,
        "max": 100
    },

    "sampleset": {
        "default": "Soft",
        "format": str,
        "list": SAMPLESETS
    }


}
