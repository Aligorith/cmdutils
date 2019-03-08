#!/usr/bin/python3 $@

# Strip excess "vlc:node" playlist NOP's from XSPF playlists.
# These can sometimes build up when saving over an existing
# playlist with "tree mode" enabled for playlist display.
# On one hand, we want to keep tree mode enabled (to avoid
# saving over the wrong playlist), but don't also don't want
# to end up with multiple NOP's building up (as new items
# don't end up in the right places, and the whole thing tends
# to say collapsed until the last possible minute).
#
# Date: 8 March 2019

import sys
import os
import shutil

if len(sys.argv) == 1:
	print("Usage: $ %s <filenames>" % (os.path.basename(__file__)))
else:
	for fileN in sys.argv[1:]:
		print("Processing ==> '%s'" % (fileN))
		
		# Read in entire file
		with open(fileN) as f:
			lines = f.readlines()
		
		# Remove offending lines
		def filter_vlc_playlist_nops(line):
			line = line.strip()
			return not (line.startswith("<vlc:node ") or line.startswith("</vlc:node "))
		lines = list(filter(filter_vlc_playlist_nops, lines))
		
		# Backup the old file in case this goes wrong (or it gets cancelled mid-write)
		backup_fileN = fileN + ".old"
		shutil.copy(fileN, backup_fileN)
		print("    Original file backed up to '%s'" % (backup_fileN))
		
		# Write out to a new file
		with open(fileN, 'w') as f:
			for line in lines:
				f.write(line)

