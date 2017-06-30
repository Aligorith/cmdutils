@echo Cropping End of Video (src cropTime out)
ffmpeg -t %2 -i %1 -acodec copy -vcodec copy %3