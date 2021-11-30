@echo off
@REM Use FFMPEG to reduce volume of audio by 3db
ffmpeg -i %1 -vcodec copy -af "volume=-3dB" EDITED-%1