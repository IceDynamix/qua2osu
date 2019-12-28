# ## Imports
import argparse  # parsing command line arguments
import os  # for paths and directories
import sys
import time  # to measure execution time

from constants import *
from conversion import convertMapset

# ## Functions


def initArgParser() -> argparse.ArgumentParser:

    argParser = argparse.ArgumentParser()

    argParser.add_argument("-i", "--input",
                           required=False,
                           help="path of the input folder, defaults to ./input")

    argParser.add_argument("-o", "--output",
                           required=False,
                           help="path of the output folder, defaults to ./output")

    argParser.add_argument("-od", "--overall-difficulty",
                           required=False,
                           help="overall difficulty as an integer between 0 and 10, defaults to 8")

    argParser.add_argument("-hp", "--hp-drain",
                           required=False,
                           help="HP drain as an integer between 0 and 10, defaults to 8")

    argParser.add_argument("-hs", "--sampleset",
                           required=False,
                           help="hitsound sample set as either 'Soft', 'Normal' or 'Drum', defaults to Soft")

    argParser.add_argument("-hv", "--hitsound-volume",
                           required=False,
                           help="hitsound volume as an integer between 0 and 100, defaults to 20")

    return argParser


def validateArgs(args):
    """Validates all input arguments"""

    # Check if script was run without any arguments, enter
    # command window input mode if yes
    hasArguments = False
    for arg in args:
        if args[arg] is not None:
            hasArguments = True
            break

    # Make the sampleset title case so we can compare to our samplesets constant
    # without having to worry about capitalization
    args["sampleset"] = str.title(args["sampleset"])

    # Validate each argument, set to default if bad
    for arg in args:
        invalid = False
        argumentObject = COMMAND_LINE_ARGS[arg]
        defaultValue = argumentObject["default"]

        if args[arg] is None:
            args[arg] = defaultValue
            continue

        else:
            try:
                args[arg] = argumentObject["format"](args[arg])
            except (ValueError, TypeError):
                invalid = True

        if not invalid:
            if "min" in argumentObject and \
                    args[arg] < argumentObject["min"]:
                invalid = True

            elif "max" in argumentObject and \
                    args[arg] > argumentObject["max"]:
                invalid = True

            elif "list" in argumentObject and \
                    str.title(args[arg]) not in argumentObject["list"]:
                invalid = True

        if invalid:
            print(f"Argument {arg} was invalid, using default value {defaultValue}")
            args[arg] = defaultValue

    if not hasArguments:
        args["input"] = input("Please enter your input folder: ")
        args["output"] = input("Please enter your output folder: ")

    # Checks if the given input path exists
    try:
        os.path.exists(args["input"])
    except OSError:
        print("Input path was invalid")
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
    run `py qua2osu.py` by itself if you want to do without the extra options
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


if __name__ == '__main__':
    main()
