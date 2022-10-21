@echo off

@REM Downloads playlist info as JSON file.
dv -J --flat-playlist %* > playlist.json && json_pprint.py playlist.json