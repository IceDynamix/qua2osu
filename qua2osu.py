"""Command-line tool for map conversion"""


# ## Imports


import argparse  # parsing command line arguments
import os  # for paths and directories
import re
import sys  # used only for sys.exit()
import time  # to measure execution time
import webbrowser  # to open the explorer cross-platform
import zipfile  # to handle .zip files (.qua and .osz)

from reamber.algorithms.convert import QuaToOsu
from reamber.quaver import QuaMap

# ## Constants


SAMPLESETS = [
    "Soft",
    "Normal",
    "Drum"
]


# ## Functions


def initArgParser() -> argparse.ArgumentParser:
    """Creates an argument parser with all of the arguments already added"""

    argParser = argparse.ArgumentParser("Converts .qp files to .osz files")

    def qpOrDirPath(inputPath):
        if (inputPath.endswith(".qp") and os.path.isFile(inputPath)) or os.path.isdir(inputPath):
            return inputPath
        else:
            raise argparse.ArgumentTypeError("Path is not a directory or not a .qp file")

    argParser.add_argument(
        "input",
        help="Paths of directories containing .qp files, or direct paths to .qp files. Both are possible.",
        nargs="*",
        type=qpOrDirPath
    )

    def directory(path):
        if os.path.isdir(path):
            return path
        raise argparse.ArgumentTypeError("Not a valid path")

    argParser.add_argument(
        "-o",
        "--output",
        required=False,
        help="Path of the output folder, defaults to ./output",
        default="./output",
        type=directory
    )

    def diffValue(x):
        x = float(x)
        if x >= 0 and x <= 10:
            return x
        else:
            raise argparse.ArgumentTypeError("Value must be larger between 0 and 10")

    argParser.add_argument(
        "-od",
        "--overall-difficulty",
        required=False,
        help="Overall difficulty as an integer between 0 and 10, defaults to 8",
        default=8,
        type=diffValue
    )

    argParser.add_argument(
        "-hp",
        "--hp-drain",
        required=False,
        help="HP drain as an integer between 0 and 10, defaults to 8",
        default=8,
        type=diffValue
    )

    def hsVolume(n):
        n = int(n)
        if n >= 0 and n <= 100:
            return n
        else:
            raise argparse.ArgumentTypeError("Value must be between 0 and 100")

    argParser.add_argument(
        "-hv",
        "--hitsound-volume",
        required=False,
        help="Hitsound volume as an integer between 0 and 100, defaults to 20",
        default=20,
        type=hsVolume
    )

    argParser.add_argument(
        "-hs",
        "--sampleset",
        required=False,
        help="Hitsound sample set as either 'Soft', 'Normal' or 'Drum', defaults to Soft",
        default="Soft",
        type=str,
        choices=SAMPLESETS
    )

    argParser.add_argument(
        "-p",
        "--preserve-folder-structure",
        required=False,
        help="Outputs in original directory structure if specified",
        action="store_true"
    )

    argParser.add_argument(
        "-r",
        "--recursive-search",
        required=False,
        help="Looks for .qp in all subdirectories of given directories if specified",
        action="store_true"
    )

    return argParser


def searchForQpFiles(directory: str, qpList: list, recursive: bool) -> list:
    for path in os.listdir(directory):
        fullRelativePath = os.path.join(directory, path)
        if os.path.isfile(fullRelativePath) and fullRelativePath.endswith(".qp"):
            qpList.append(os.path.normpath(fullRelativePath))
        elif os.path.isdir(fullRelativePath) and recursive:
            searchForQpFiles(fullRelativePath, qpList, recursive)


def convertDifficulties(path: str, outputFolder: str, options) -> None:
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

        # Replaces each .qua file with the converted .osu file, uses Evening's reamber package
        if file.endswith(".qua"):
            qua = QuaMap.readFile(filePath)
            convertedOsu = QuaToOsu.convert(qua)

            if options["od"]:
                convertedOsu.overallDifficulty = options["od"]
            if options["hp"]:
                convertedOsu.hpDrainRate = options["hp"]

            if options["hitSoundVolume"] or options["sampleset"]:
                for list in [convertedOsu.bpms.data(), convertedOsu.svs.data()]:
                    for element in list:
                        if options["hitSoundVolume"]:
                            element.volume = options["hitSoundVolume"]
                        if options["sampleSet"]:
                            element.sampleSet = SAMPLESETS.index(options["sampleSet"])

            newFileName = re.sub(r"\.qua$", ".osu", filePath, 1, re.MULTILINE)
            convertedOsu.writeFile(newFileName)
            os.remove(filePath)

    # Creates a new .osz (.zip) mapset file
    with zipfile.ZipFile(outputPath + ".osz", "w") as newDir:
        for root, dirs, files in os.walk(outputPath):
            for file in files:
                newDir.write(os.path.join(root, file), file)

    for root, dirs, files in os.walk(outputPath, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))

    os.rmdir(outputPath)


# ### Main


def main():
    """Runs the map file conversions

    Run `py qua2osu.py --help` for help with command line arguments
    """

    argParser = initArgParser()
    args = vars(argParser.parse_args())

    if len(args["input"]) == 0:
        print("Please specify an input! (Paths to directories containing .qp files or .qp files directly)")
        sys.exit(1)

    qpFilesInInputDir = []

    # Filters for all files that end with .qp and puts the
    # complete path of the files into an array

    for path in args["input"]:
        if os.path.isfile(path) and path.endswith(".qp"):
            qpFilesInInputDir.append(path)
        elif os.path.isdir(path):
            searchForQpFiles(path, qpFilesInInputDir, args["recursive_search"])

    print(qpFilesInInputDir)

    if len(qpFilesInInputDir) == 0:
        print("No mapsets found")
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
        basePath = os.path.dirname(file) if args["preserve_folder_structure"] else ""

        outputPath = os.path.join(args["output"], basePath)
        if not os.path.exists(outputPath):
            os.mkdir(outputPath)

        print(f"Converting {file}")
        convertDifficulties(file, outputPath, options)

    # Stops the timer for the total execution time
    end = time.time()
    timeElapsed = round(end - start, 2)

    print(f"Finished converting all mapsets, total time elapsed: {timeElapsed} seconds")

    # Opens output folder in explorer
    absoluteOutputPath = os.path.realpath(args["output"])
    webbrowser.open("file:///" + absoluteOutputPath)


if __name__ == '__main__':
    main()
    sys.exit(0)
