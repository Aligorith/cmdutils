#!python3
#
# Utility to copy all photos from the source directory (flat folder)
# to being grouped by date. By default, the grouping is done by
# the filenames (assuming the format used by Samsung Phones).
#
# Author: Joshua Leung (aligorith@gmail.com)
# Date: 15 March 2020

import sys
import os

import argparse
import datetime
import re
import shutil
import time

try:
	import pytest
except:
	print("PyTest not installed...")
	pass

#######################################
# "DateSpec" Handling

# Help text for the "datespec" property
DATESPEC_DESCRIPTION = """\
Defines the date ranges that are considered for copying.

 (1) "all" = All dates are considered
 
 (2) "yyyyMMdd" = All dates starting from that date
 
 (3) "[yyyyMMdd] = Only that date
"""
# TODO: More to come if needed

# Get datespec interpreter given the datespec specifier string
# NOTE: It is assumed that this is only execute once
#
# > returns: fn(date_string: str = "yyyyMMdd") -> bool
def get_datespec_handler(datespec_format):
	if re.match(r"^(\d{4}\d{2}\d{2})|(\d{4}\d{2})|(\d{4})$", datespec_format):
		# Only those after the given date will be included
		def compare_newer_only(date_string):
			# Assume that the string sorting will work
			# e.g. "2011"   < "20110222" == true,
			#      "201212" < "20121212" == true,
			#      "201711" > "20171011 == true"
			return date_string > datespec_format
			
		print("Using 'NEWER_ONLY' datespec")
		return compare_newer_only
	
	elif re.match(r"^\[\d{4}\d{2}\d{2}\]$", datespec_format):
		# Absolute date format
		def compare_absolute_date(date_string):
			# Full date string must match. Just chop off the brackets on either side...
			return date_string == datespec_format[1 : -1]
			
		print("Using 'ABSOLUTE_DATE' datespec")
		return compare_absolute_date
	
	else:
		# All - No filtering
		def compare_all(_date_string):
			return True
		
		print("Using 'ALL' files")
		return compare_all


#######################################
# Args/Config Handling

# Handle command-line arguments
def get_config():
	# FIXME: Use a custom formatter so that help texts with custom formatting will work
	# See https://stackoverflow.com/questions/3853722
	parser = argparse.ArgumentParser(
		description = 
			"Copy all photos from export of phone's DCIM/Camera folder "
			"into the main collection, grouped by date")
	
	parser.add_argument("datespec", type=str, default=".",
	                    help=DATESPEC_DESCRIPTION)
	
	parser.add_argument("-i", "--inputdir", type=str, default="./Camera",
	                    help='Folder where the source files are (e.g. "./Camera")')
	
	parser.add_argument("-o", "--outdir", type=str, default="D:\\photos",
	                    help='Folder where the main photos collection lives (e.g. "D:\\photos")')
	
	parser.add_argument('-u', "--unsorted", type=str, default="D:\\photos\\n9_photos",
	                    help="Output folder where photos that couldn't be grouped by date go.")
	
	parser.add_argument("-p", "--postfix", type=str, default="n9",
	                    help='Postfix to use when the directory in question already exists')
	
	parser.add_argument("-d", "--dry_run", type=bool, default=False,
	                    help="If true, don't actually perform any file copying. For testing that the path handling will be correct.")
	
	parser.add_argument("-v", "--verbose", type=bool, default=False)
	
	return parser.parse_args()
	
#######################################
# File Utilities

# Regular Expression for use in extract_dateinfo_from_filename - matches the date format
RE_DATEINFO_FROM_FILENAME = re.compile(r"^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})")

# Extract a datetime.date() from a given filename
# < fileN: (str) Just the filename (no path string should be included)
# > returns: (str, datetime.date) The date-string (yyyyMMdd), followed by a decomposed version of that date
# > throws "ValueError" if a date couldn't be extracted...
#
# Note: Filenames are expected to follow the following format - "20190519_105307.jpg"
def extract_dateinfo_from_filename(fileN):
	match = RE_DATEINFO_FROM_FILENAME.match(fileN)
	if match:
		full_string = match.group(0)
		
		# XXX: Perhaps we don't need to parse these, only to re-format in the next step?
		year = int(match.group('year'))
		month = int(match.group('month'))
		day = int(match.group('day'))
		
		return (full_string, datetime.date(year, month, day))
	else:
		raise ValueError(f"Expected timestamp in 'yyyyMMdd' format not found in filename: '{fileN}'")
	
# Unit tests for extract_dateinfo_from_filename()
def test_dateinfo_extraction():
	assert extract_dateinfo_from_filename("20190519_105307.jpg") == ("20190519", datetime.date(2019, 5, 19))
	assert extract_dateinfo_from_filename("20190520_091757_001.jpg") == ("20190520", datetime.date(2019, 5, 20))
	assert extract_dateinfo_from_filename("20191210_102207(0).jpg") == ("20191210", datetime.date(2019, 12, 10))
	assert extract_dateinfo_from_filename("20191211_164729.mp4") == ("20191211", datetime.date(2019, 12, 11))
	assert extract_dateinfo_from_filename("20191211_180009~2.mp4") == ("20191211", datetime.date(2019, 12, 11))

# -------------------------------------

# Figure out folder that a given file should go to
# <> date_to_folder_map: ({ str : str }) Map from date_string's to full folder paths
# < date_string: (str) The "yyyyMMdd" string that the filename starts with.
#                      Used as a "key" in date_to_folder_map for faster lookups for subsequent files.
# < date_info: (datetime.date) A parsed version of this for easier manipulation
# < out_dir: (str) Path to the root folder for the photo collection
# < conflict_postfix: (str) Postfix to add to the folder name if the standard name is used already (e.g. from other cameras)
# < is_dry_run: (bool) If True, the necessary output folders won't be created...
#
# > returns: (str) The folder path for this file. If it doesn't exist in date_to_folder_map, it will be added
def folder_path_for_file(date_to_folder_map, date_string, date_info, out_dir, conflict_postfix, is_dry_run):
	# Use a previously resolved path (if one is in place)
	if date_string in date_to_folder_map:
		return date_to_folder_map[date_string]
	
	# Construct a basic folder name for this file from its timestamp
	folder_name = "%02d/%02d_%02d_%02d" % (date_info.year, date_info.year, date_info.month, date_info.day)
	folder_name = os.path.join(out_dir, folder_name)
	
	# Check if this folder exists already
	if os.path.exists(folder_name):
		# Use the post-fix version
		folder_name += f"-{conflict_postfix}"
	
	# Try to create this folder
	if not os.path.exists(folder_name):
		print("    Creating directory: '%s'" % (folder_name))
		if not is_dry_run:
			os.makedirs(folder_name) # NOTE: This will create the intermediate paths
			print("   Folder Created? %s" % os.path.exists(folder_name))
		else:
			print("    Not creating folder...")
	else:
		print("    NOTE: Directory '%s' already exists!" % (folder_name))
	
	# Register this folder against this date_string
	date_to_folder_map[date_string] = folder_name
	return folder_name


#######################################
# Main App

def main():
	config = get_config()
	print("Photo Copying Settings = %s" % (config))
	
	# Sanity checks
	input_dir = config.inputdir
	if not os.path.exists(input_dir):
		print(f"ERROR: Input Directory '{input_dir}' does not exist", file=sys.stderr)
		sys.exit(1)
	
	out_dir = config.outdir
	if not os.path.exists(out_dir):
		print(f"ERROR: Output Directory '{out_dir}' does not exist", file=sys.stderr)
		sys.exit(2)
	
	is_dry_run = config.dry_run
	is_verbose = config.verbose
	
	conflict_postfix = config.postfix
	# TODO: Verify that there's nothing offensive here
	
	# Parse datespec
	datespec = config.datespec
	
	can_use_file_fn = get_datespec_handler(datespec)
	assert (can_use_file_fn is not None)
	
	# Process each file
	# NOTE: Assumes that these are all files - there are no nested folders here
	source_files = sorted(os.listdir(input_dir))
	N = len(source_files)
	
	date_to_folder_map = {}  # Map from date-strings (yyyyMMdd) to folder names for those images
	unsorted_files = []      # Files that were not handled the standard way
	
	processed_count = 0      # Number of files that have been processed
	skipped_count = 0        # Number of files that have been skipped
	
	last_processed = ""      # Filename of the last processed file
	
	print(f"\nProcessing {N} files:")
	for i, fileN in enumerate(source_files):
		# Check if processing or skipping this file
		if can_use_file_fn(fileN):
			print(f"  [{i}/{N}] Processing ==> '{fileN}'...")
		else:
			if is_verbose: print(f"  [{i}/{N}] Skip ==> '{fileN}'...")
			skipped_count += 1
			continue
		
		# Get date info from filename
		try:
			date_string, date_info = extract_dateinfo_from_filename(fileN)
		except ValueError as e:
			print(f"    ERROR: {e}", file=sys.stderr)
			unsorted_files.append(fileN)
			continue;
		
		# Figure out folder that this file will get added to
		folder_name = folder_path_for_file(date_to_folder_map, date_string, date_info, out_dir, conflict_postfix, is_dry_run)
		out_fileN = os.path.join(folder_name, fileN)
		print(f"    Copying to '{out_fileN}...")
		
		# Perform copying...
		if not is_dry_run:
			full_source_fileN = os.path.join(input_dir, fileN)
			shutil.copyfile(full_source_fileN, out_fileN)
		
		# Note that this was the most recent file processed...
		last_processed = fileN
		processed_count += 1
	
	# Handle the unsorted files
	U = len(unsorted_files)
	
	print("\n\n%d files copied + sorted (to %d folders). Skipped %d files. Adding %d files to 'unsorted' directory" 
	      % (processed_count, len(date_to_folder_map), skipped_count, U))
	if U:
		# Create directory for unsorted files
		unsorted_dir = config['unsorted']
		
		# Perform the copying
		for fileN in unsorted_files:
			pass
	
	# Log the last processed file (assuming they're all in order)
	# XXX: This only works best when just processing the whole dump
	if not is_dry_run:
		print("Updating processing history log...")
		log_filename = "%s.processing_history_log.txt" % (sys.argv[0]) # Should be in current directory...
		with open(log_filename, 'a') as f:
			now = datetime.datetime.now().strftime("%Y%m%d %H:%M")
			
			f.write("[[%s]] %s\n" % (now, ' '.join(sys.argv)))
			f.write("\tF: %d (D: %d) + U: %d\t%s\n" % (processed_count, len(date_to_folder_map), U, last_processed))
			f.flush()
			
			print("History Updated in '%s'" % (f.name))
	
	print("\nDone!")

if __name__ == '__main__':
	main()

