@echo off
@REM Use FFMPEG to boost volume of audio by 7db
ffmpeg -i %1 -vcodec copy -af "volume=7dB" v+7_%1