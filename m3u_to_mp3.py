#!/usr/bin/python3

"""
m3u_to_mp3.py - Convert m3u playlist's contents to mp3's in the target folder

Usage:
$ m3u_to_mp3.py [IN_FILE.m3u] [OUT_DIR/]
"""

import sys
import os
import subprocess
import shutil

# Get input and output destinations
try:
	args = sys.argv[1:]
	
	IN_FILE = args[0]
	OUT_DIR = args[1]
except IndexError:
	print(__doc__)
	sys.exit(-1)

# List of all the new filenames (to be saved into the new m3u file)
newFilenames = []

# Create output directory
if not os.path.exists(OUT_DIR):
	print("Creating '%s'..." % (OUT_DIR))
	os.makedirs(OUT_DIR)
	print("  OutDir Exists?   %s" % os.path.exists(OUT_DIR))

# Process each file
with open(IN_FILE) as f:
	for line in f:
		line = line.strip()
		
		if len(line) == 0 or line[0] == "#":
			# Blank / Comment Line
			continue
		
		# XXX: This assumes that all the files are in the same directory as the playlist!
		if line.endswith(".mp3"):
			# Just Copy... Already in target format
			old_filename = new_filename = line
			new_filepath = os.path.join(OUT_DIR, line)
			
			print("Copying '%s' => '%s'" % (old_filename, new_filepath))
			shutil.copy2(old_filename, new_filepath)
		else:
			# Convert file formats
			old_filename = line
			new_filename = line.rsplit('.')[0] + '.mp3'
			new_filepath = os.path.join(OUT_DIR, new_filename)
			
			print("Converting '%s' => '%s'..." % (old_filename, new_filepath))
			result = subprocess.run(['ffmpeg', '-i', line, '-vn', new_filepath], stdout=subprocess.PIPE)
			print("   %s" % result)
		
		newFilenames.append(new_filename)

# Save out the new playlist
# XXX: All comments have been stripped!
with open(os.path.join(OUT_DIR, IN_FILE), 'w') as f:
	# Mandatory header
	f.write("#EXTM3U\n")
	
	# Write files
	for fileN in newFilenames:
		f.write("%s\n" % fileN)
	
