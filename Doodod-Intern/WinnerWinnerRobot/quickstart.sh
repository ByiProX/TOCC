#! /bin/bash
ps -ef |grep   WinnerWinnerRobot  | grep -v 'grep'  | awk  '{print  " kill  "  $2}' | sh
source /www/WinnerWinnerRobot/venv/bin/activate
cd  /www/WinnerWinnerRobot/
git pull
./start_app.sh