# ## Imports
import os  # for paths and directories
import re
import zipfile  # to handle .zip files (.qua and .osz)

from reamber.quaver import QuaMap
from reamber.algorithms.convert import QuaToOsu
from reamber import osu

from constants import *

# ## Functions


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
