@echo off
@REM Convert given file to mp3
ffmpeg -i %1 -vn %1.mp3
