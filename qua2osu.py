"""Command-line tool for map conversion"""

# ## Imports
import argparse  # parsing command line arguments
import os  # for paths and directories
import sys  # used only for sys.exit()
import time  # to measure execution time
import webbrowser  # to open the explorer cross-platform

from constants import *
from conversion import convertMapset

# ## Functions


def initArgParser() -> argparse.ArgumentParser:
    """Creates an argument parser with all of the arguments already added

    Uses `COMMAND_LINE_ARGS` from constants.py to generate each argument
    """

    argParser = argparse.ArgumentParser()

    for arg in COMMAND_LINE_ARGS:
        argument = COMMAND_LINE_ARGS[arg]

        if "list" in argument:
            argParser.add_argument(
                argument["shortFlag"],  # Example: "-i", "-od"
                argument["longFlag"],  # Example: "--help", "--sampleset"
                required=argument["required"],
                help=argument["description"],
                default=argument["default"],
                type=argument["type"],
                # This is literally the only line that was added
                # please tell me there's a better way
                choices=argument["list"]
            )

        else:
            argParser.add_argument(
                argument["shortFlag"],
                argument["longFlag"],
                required=argument["required"],
                help=argument["description"],
                default=argument["default"],
                type=argument["type"]
            )

    return argParser


def validateArgs(args) -> dict:
    """Validates all input arguments"""

    # Check if script was run without any arguments, enter
    # command window input mode if yes
    hasArguments = False
    for arg in args:
        if args[arg] is not None:
            hasArguments = True
            break

    if not hasArguments:
        args["input"] = input("Please enter your input folder: ")
        args["output"] = input("Please enter your output folder: ")

    # Validate each argument, set to default if bad
    # (only used for value in bounds checking at the moment)
    for arg in args:
        argumentObject = COMMAND_LINE_ARGS[arg]

        # Out of bounds check (only applies to OD and HP for now)
        valueTooLow = "min" in argumentObject and args[arg] < argumentObject["min"]
        valueTooHigh = "max" in argumentObject and args[arg] > argumentObject["max"]

        if valueTooLow:
            print(f"{arg} must be > {argumentObject['min']}")
            sys.exit(1)

        elif valueTooHigh:
            print(f"{arg} must be < {argumentObject['max']}")
            sys.exit(1)

    # Checks if the given input path exists, exits if not
    if not os.path.exists(args["input"]):
        print("Input folder does not exist")
        sys.exit(1)

    # Checks if output path exists, creates a new folder if not
    if not os.path.exists(args["output"]):
        os.mkdir(args["output"])
        print("New output folder was created")

    return args


# ### Main


def main():
    """Runs the map file conversions

    Run `py qua2osu.py --help` for help with command line arguments or just
    run `py qua2osu.py` by itself if you want to make do without the extra
    options
    """

    argParser = initArgParser()
    args = validateArgs(vars(argParser.parse_args()))

    qpFilesInInputDir = []

    # Filters for all files that end with .qp and puts the
    # complete path of the files into an array
    for file in os.listdir(args["input"]):
        path = os.path.join(args["input"], file)
        if (file.endswith('.qp') and os.path.isfile(path)):
            qpFilesInInputDir.append(file)

    numberOfQpFiles = len(qpFilesInInputDir)

    if numberOfQpFiles == 0:
        print("No mapsets found in " + args["input"])
        sys.exit(1)

    # Assigns the arguments to an options object to pass to
    # the `convertMapset()` function
    options = {
        "od": args["overall_difficulty"],
        "hp": args["hp_drain"],
        "hitSoundVolume": args["hitsound_volume"],
        "sampleSet": args["sampleset"]
    }

    # Starts the timer for the total execution time
    start = time.time()

    # Run the conversion for each .qp file
    for file in qpFilesInInputDir:
        filePath = os.path.join(args["input"], file)
        print(f"Converting {filePath}")
        convertMapset(filePath, args["output"], options)

    # Stops the timer for the total execution time
    end = time.time()
    timeElapsed = round(end - start, 2)

    print("Finished converting all mapsets, "
          f"total time elapsed: {timeElapsed} seconds")

    # Opens output folder in explorer
    absoluteOutputPath = os.path.realpath(args["output"])
    webbrowser.open("file:///" + absoluteOutputPath)


if __name__ == '__main__':
    main()
    sys.exit(0)
