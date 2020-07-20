@echo off
@REM Download video with subtitles (manual ones. For auto, substitute "write-sub" for "write-auto-sub"

dv --write-sub --sub-lang=en %*
