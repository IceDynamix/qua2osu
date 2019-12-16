# qua2osu

> converts quaver map files (.qp) to osu! map files (.osz)

## screenshot

![image of the gui](https://i.imgur.com/LYwGaVj.png)

## download

download the lastest release from [here](https://github.com/IceDynamix/qua2osu/releases)

## step by step instructions

* download qua2osu, no python needed etc.
* gui should pop up, select a folder with your .qp files and select a folder to output your .osz files
* choose available options (currently od, hp, hs volume, hs sample set)
* click convert
* done

## step by step instructions to build the app yourself

* install git, python if necessary
* install pip if necessary (should ship with python)
* clone this repo `git clone https://github.com/IceDynamix/qua2osu.git`
* its best to set up a virtual environment for the project but not necessary if you dont know how
* run `pip install -r requirements.txt` in the directory to install all package dependencies (mainly pyYaml (.qua parser), pyQT5 (gui) and some QOL stuff)
* run main.py either by double clicking or running `py main.py`
* enjoy

## notes

if you don't select any paths then it will choose `.\samples` as the default input path and `.\output` as the default output path
please report issues [here on github](https://github.com/IceDynamix/qua2osu/issues) thanks

## referenced games

[**Quaver**](https://quavergame.com/)
[**osu!**](https://osu.ppy.sh/)
