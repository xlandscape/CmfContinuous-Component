@echo off
set python=D:/WP3720/python-3.7.2.amd64/python.exe
set script=%cd%/bin/main.py
call %python% %script% --folder D:/LandscapeModel2019/projects --runlist landscapeyieldCatchment key --None
pause
