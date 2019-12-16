# qua2osu
_converts quaver map files (.qp) to osu map files (.osz)_

---
### step by step instructions to build the app yourself
* install python if not done yet
* install pip if necessary (should ship with python)
* its best to set up a virtual environment for the project but not necessary if you dont know how
* open cmd, nagivate to your directory
* run `pip install -r requirements.txt` to install all package dependencies (mainly pyYaml (.qua parser), pyQT5 (gui) and some QOL stuff)
* run main.py either by double clicking or running `python3 main.py`
* gui should pop up, select a folder with your .qp files and select a folder to output your .osz files
* choose available options (currently od, hp, hs volume, hs sample set)
* click convert
* done

### notes

if you don't select any paths then it will choose .\samples as the default input path and .\output as the default output path

please report issues [here on github](https://github.com/IceDynamix/qua2osu/issues) thanks

i'll add an executable when i feel like it please be patient
