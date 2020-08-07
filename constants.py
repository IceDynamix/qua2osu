"""General constants that are needed in most places"""

# Samplesets list
SAMPLESETS = [
    "Soft",
    "Normal",
    "Drum"
]

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
