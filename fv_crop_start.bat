@echo Cropping Start of Video (src cropTime out)
ffmpeg -ss %2 -i %1 -acodec copy -vcodec copy %3
