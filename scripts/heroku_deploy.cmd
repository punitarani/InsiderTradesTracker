:: .\scripts\heroku_monitor.cmd

REM Deploying to Heroku
git push heroku main

REM Opening Website
start cmd.exe /c heroku open

REM Opening Logs Stream
heroku logs --tail --app=insider-trades-tracker
