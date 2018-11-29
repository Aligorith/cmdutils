@echo AVI to H264 (src out)
ffmpeg -i %1 -vcodec libx264 -crf 22 %2