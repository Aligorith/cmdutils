@echo off
@REM Use FFMPEG to boost volume of audio by 15db
ffmpeg -i %1 -vcodec copy -af "volume=15dB" v+15-%1