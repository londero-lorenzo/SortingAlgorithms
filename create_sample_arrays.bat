@echo off
cd /d "%~dp0"
start cmd /k ".\.labProjVenv\Scripts\activate.bat && echo Environment activated.&echo\Creating arrays... && py -m Utils.ArrayGenerator -f *.json -a -s Array && pause && exit