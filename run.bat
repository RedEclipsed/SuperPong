@echo off

REM Try to install all the requirements for SuperPong
py -m pip install -r requirements.txt

REM Run SuperPong
python3 ./main.py
py ./main.py
