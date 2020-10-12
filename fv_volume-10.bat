@echo off
@REM Use FFMPEG to reduce volume of audio by 10db
ffmpeg -i %1 -vcodec copy -af "volume=-10dB" EDITED-%1