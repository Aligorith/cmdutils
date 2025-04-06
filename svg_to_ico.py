#!/usr/bin/python3

# Utility to render a Windows ICO file from a given SVG file
#
# Uses Python-Qt bindings for rendering the SVG, and Pillow for saving
# an ICO archive from that image data
#
# TODO: Try to use inkscape for rendering if "-inkscape" arg is given instead

import sys

import importlib.util
import os
import pathlib

# FIXME: Find a way to NOT have to fully repeat these like this.
#        Unfortunately, cannot get Py3.12 / PySide6 to accept "from QtCore import QSize"
if importlib.util.find_spec("PySide6") is not None:
	import PySide6
	from PySide6.QtCore import QSize
	from PySide6.QtWidgets import QApplication

	from PySide6.QtGui import (
		QIcon,
		QImage,
		QPixmap,
	)
elif importlib.util.find_spec("PyQt5") is not None:
	import PyQt5
	from PyQt5.QtCore import QSize
	from PyQt5.QtWidgets import QApplication

	from PyQt5.QtGui import (
		QIcon,
		QImage,
		QPixmap,
	)
else:
	print("ERROR: Could not import PySide6 or PyQt5 (as checked using importlib.util.find_spec())")
	sys.exit(-1)

from PIL import Image

###############################################
# SVG to ICO file conversion logic

# Convert the given SVG file to an ICO equivalent
# < src_path: (str | pathlib.Path) Input SVG filename
# < dst_path: (str | pathlib.Path) Output SVG filename
def convert_svg_to_ico(src_path, dst_path):
	# Sanity checks about the extensions involved
	assert os.path.splitext(src_path)[-1].lower() == ".svg"
	assert os.path.splitext(dst_path)[-1].lower() == ".ico"
	
	print("Converting '%s' => '%s'..." % (src_path, dst_path))
	
	# Load the source image with PyQt's image renderer
	qt_image = QImage(src_path)
	
	# Render/save this to a raster image on disk
	# Note: This is easier than trying to do it with NumPy buffer conversions
	# TODO: Render this to a higher resolution so the downsampling can work nicer
	TMP_FILENAME = "svg2ico_tmp_render.png"
	
	qt_image.save(TMP_FILENAME)
	
	# Load tempfile using PIL
	py_image = Image.open(TMP_FILENAME)
	
	# Save to ICO
	py_image.save(dst_path)
	
	# Remove the tempfile
	os.remove(TMP_FILENAME)

###############################################


if __name__ == '__main__':
	# QApplication so QPixmap works
	app = QApplication(sys.argv)
	
	# Get files to operate on
	# TODO: Filter out any arguments first, then the rest are files
	files = sys.argv[1:]
	
	if len(files) == 0:
		print("Usage: svg_to_ico.py <path_to_svg_1.svg> <...>")
		sys.exit()
	
	# Main application icon
	for fileN in files:
		# Validate that we have an SVG
		svg_filename = pathlib.Path(fileN)
		if not svg_filename.suffix.lower() == '.svg':
			print(f"ERROR: '{fileN}' is not a valid svg file for processing. Skipping...")
			continue;
		
		# Convert filename to the output .ico one
		ico_filename = svg_filename.with_suffix('.ico')
		
		# Perform the conversion
		convert_svg_to_ico(svg_filename, ico_filename)

