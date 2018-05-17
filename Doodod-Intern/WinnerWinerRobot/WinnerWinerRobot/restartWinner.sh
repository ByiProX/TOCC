#! /bin/bash
ps -ef |grep   WinnerWinnerRobot  | grep -v 'grep'  | awk  '{print  " kill  "  $2}' | sh
sleep 3s
source /www/WinnerWinnerRobot/venv/bin/activate
cd  /www/WinnerWinnerRobot/
./start_app.sh