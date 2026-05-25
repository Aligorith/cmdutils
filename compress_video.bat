@REM echo off

@REM This just does basic compression with FFMPEG. Got a 40mb camera video down to < 5mb
@REM The following flag is skipped from the audio "-b:a 128k" part (going after the "aac" bit)
ffmpeg -i %1 -c:v libx264 -crf 23 -preset medium -c:a aac %2
