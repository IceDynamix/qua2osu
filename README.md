# qua2osu

> Converts quaver map files (.qp) to osu! map files (.osz)

## Screenshot

![Image of the GUI](https://i.imgur.com/LYwGaVj.png)

## Download

Download the lastest release from
[here](https://github.com/IceDynamix/qua2osu/releases)

## Step by step instructions

- Download qua2osu, no installation needed etc.
- You can decide to use the command-line tool or the GUI (Graphical User
  Interface)
- Command-line:
    - Execute the qua2osu.exe file with the --help flag in the console by
      running `qua2osu.exe --help` (double-clicking doesn't work)
    - Set options with some flags to spice things up (Example:
      `qua2osu.exe -i myfolder/subfolder -od 8.5 -hp 9 -hv 0` which would
      convert all .qp files in "myfolder/subfolder", set OD to 8.5, HP to 9 and
      hitsound volume to 0)
- GUI:
    - Execute the qua2osu-gui.exe file, either by double-clicking or by running
      it in the console
    - GUI should pop up, select a folder with your .qp files and select a folder
      to output your .osz files
    - Set some settings and click on convert

## Step by step instructions to build the project yourself

- Install [Git](https://git-scm.com/) and [Python](https://www.python.org/) if
  necessary
- Install [pip](https://pip.pypa.io/en/stable/installing/) if necessary (should
  ship with python)
- Clone this repo: `git clone https://github.com/IceDynamix/qua2osu.git`
- *It's best to set up a
  [virtual environment](https://docs.python.org/3/tutorial/venv.html) for the
  project, but not necessary if you don't know how to*
    - *Activate your virtual environment by running the activate file in your
      virtual environment folder*
- Run `pip install -r requirements.txt` in the directory to install all package
  dependencies (mainly reamber (conversion), PyQT5 (gui) and some QOL stuff)
- Run `py qua2osu.py` or `py qua2osu-gui.py`

## Documentation

This project uses [pycco](https://github.com/pycco-docs/pycco) to create
documentation. Regenerating the documentation after modifying or adding new
files is done by `pycco ./*.py`. Having a git hook that generates it pre-commit
and adds it to the staged files is recommended.

[Documentation](https://icedynamix.github.io/qua2osu/index.html)

## Contributing

In case you want to contribute to this project, please keep following things in
mind:

- This project uses [flake8](http://flake8.pycqa.org/en/latest/) as the primary
  linter. A `.flake8` is present in the root directory. Run
  `flake8 yourpythonfile.py` to lint your file.
- [QT Designer](https://build-system.fman.io/qt-designer-download) is used to
  work with the gui.ui file. Use `pyuic5 -x gui/gui.ui -o gui/gui.py` in the
  root directory to regenerate the gui.py file after editing the gui.ui file.
- Use [camelCase](https://en.wikipedia.org/wiki/Camel_case) for variable,
  function and method names.
- Use PascalCase (camelCase, but first letter capitalized) for class names.
- Use UPPER_SNAKE_CASE for constants.
- Please document your code. Refer to the Documentation section.

Please report issues [here on github](https://github.com/IceDynamix/qua2osu/issues).

## Referenced games

- [**Quaver**](https://quavergame.com/)
- [**osu!**](https://osu.ppy.sh/)
