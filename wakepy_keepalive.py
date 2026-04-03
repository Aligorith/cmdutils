# Requirements:
# pip install wakepy

import time
import wakepy

with wakepy.keep.running():
	while True:
		print("sleeping for 30")
		time.sleep(30)
