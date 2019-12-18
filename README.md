# qua2osu

> Converts quaver map files (.qp) to osu! map files (.osz)

## Screenshot

![Image of the GUI](https://i.imgur.com/LYwGaVj.png)

## Download

Download the lastest release from [here](https://github.com/IceDynamix/qua2osu/releases)

## Step by step instructions

* Download qua2osu, no python needed etc.
* GUI (Graphical User Interface) should pop up, select a folder with your .qp files and select a folder to output your .osz files
* Choose available options (currently od, hp, hs volume, hs sample set)
* Click convert
* Done

## Step by step instructions to build the project yourself

* Install [Git](https://git-scm.com/) and [Python](https://www.python.org/) if necessary
* Install [pip](https://pip.pypa.io/en/stable/installing/) if necessary (should ship with python)
* Clone this repo: `git clone https://github.com/IceDynamix/qua2osu.git`
* *It's best to set up a [virtual environment](https://docs.python.org/3/tutorial/venv.html) for the project, but not necessary if you don't know how to*
  * Activate your virtual environment by running the activate file in your virtual environment folder
* Run `pip install -r requirements.txt` in the directory to install all package dependencies (mainly PyYaml (.qua parser), PyQT5 (gui) and some QOL stuff)
* Run `py qua2osu.py` or `python3 qua2osu.py`
* Enjoy

## Documentation

This project uses [pycco](https://github.com/pycco-docs/pycco) to create documentation.
Regenerating the documentation after modifying or adding new files is done by `pycco yourpythonfile.py`.

* [Documentation of convert.py](https://icedynamix.github.io/qua2osu/convert.html)
* [Documentation of qua2osu.py](https://icedynamix.github.io/qua2osu/qua2osu.html)

## Contributing

In case you want to contribute to this project *(which I highly doubt to be perfectly honest)*, please keep following things in mind:

* This project uses [flake8](http://flake8.pycqa.org/en/latest/) as the primary linter. A `.flake8` is present in the root directory. Run `flake8 yourpythonfile.py` to lint your file.
* [QT Designer](https://build-system.fman.io/qt-designer-download) is used to work with the gui.ui file. Use `pyuic5 -x gui/gui.ui -o gui/gui.py` in the root directory to regenerate the gui.py file after editing the gui.ui file.
* Use [camelCase](https://en.wikipedia.org/wiki/Camel_case) for variable, function and method names.
* Use PascalCase (camelCase, but first letter capitalized) for class names.
* Use UPPER_SNAKE_CASE for constants.
* Please document your code. Refer to the Documentation section.

## Notes

The GUI will choose `.\samples` as the default input path and `.\output` as the default output path, in case you don't select any paths.

Please report issues [here on github](https://github.com/IceDynamix/qua2osu/issues).

## referenced games

* [**Quaver**](https://quavergame.com/)
* [**osu!**](https://osu.ppy.sh/)
