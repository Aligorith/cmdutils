#!/usr/bin/python

# Reformat all JSON files given on the command-line
# to be human-readable.
#
# NOTE: This may mangle any values, as we have to
# first parse to Python, then write them out again.

import sys
import json
import traceback

if len(sys.argv) <= 1:
	print("USAGE:")
	print("$ json_pprint.py <file_1.json> ... <file_N.json>")
	sys.exit(0)

else:
	for fileN in sys.argv[1:]:
		try:
			print("Reformatting JSON File => '%s'..." % fileN)
			with open(fileN) as f:
				data = json.load(f)
			with open(fileN, 'w') as f:
				json.dump(data, f, indent='\t')
		except Exception as err:
			print("! Error processing %s" % (fileN), file=sys.stderr)
			print(repr(err), file=sys.stderr)
			traceback.print_tb(err.__traceback__, file=sys.stderr)

