@echo off
@REM Convert given file to flac
ffmpeg -i %1 -vn %1.flac
