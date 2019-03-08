# Convert aRGB files to sRGB (for upload to web/GPhotos) 
# Based on http://stackoverflow.com/a/41524153/6531515
import sys
import os
import tempfile

try:
	# Py 3 only
	import pathlib
	ICC_DATA_DIR = pathlib.Path(__file__).parents[0]
except ImportError:
	# Py 2 - Hardcoded to work with the standard install location
	ICC_DATA_DIR = r"C:\Users\Joshua\cmdutils"

from PIL import Image
from PIL import ImageCms
#from PIL import ExifTags

def is_adobe_rgb(img):
	# Note: Canon JPG's don't usually have embedded icc_profile data set.
	#      Instead, they only set the "Color Space" EXIF tag, but only in MarkerNote
	#return 'Adobe RGB' in img.info.get('icc_profile', '')
	MAKERNOTE_TAG = 37500
	CANON_CS_TAG = 0x00b4 # Exif.Canon.ColorSpace
	
	exif = img._getexif()
	makernote = exif[MAKERNOTE_TAG]

	return makernote[CANON_CS_TAG] == "Adobe RGB"  # XXX: This still doesn't work!


# Colorspace conversion magic
def adobe_to_srgb(img):
	srgb = ImageCms.createProfile('sRGB')
	
	#icc = open('AdobeRGB.icc')
	#icc = open(r'C:\Users\Joshua\cmdutils\AdobeRGB.icc', 'rb')
	icc = open(os.path.join(ICC_DATA_DIR, 'AdobeRGB.icc'), 'rb')
	
	img = ImageCms.profileToProfile(img, icc, srgb)
	#img = ImageCms.profileToProfile(img, icc, srgb, renderingIntent = ImageCms.INTENT_SATURATION)
	
	return img


# Fetch profiles to use into a global cache
COLOR_PROFILES = {}

def init_color_profiles():
	global COLOR_PROFILES
	
	COLOR_PROFILES['srgb'] = ImageCms.createProfile('sRGB')
	
	#COLOR_PROFILES['argb'] = ImageCms.getOpenProfile(r'AdobeRGB.icc')
	COLOR_PROFILES['argb'] = ImageCms.getOpenProfile(os.path.join(ICC_DATA_DIR, 'AdobeRGB.icc'))
init_color_profiles()

# Colorspace conversion magic (using cached profiles)
def adobe_to_srgb__fast(img):
	global COLOR_PROFILES
	
	srgb = COLOR_PROFILES['srgb']
	icc = COLOR_PROFILES['argb']
	
	img = ImageCms.profileToProfile(img, icc, srgb)
	#img = ImageCms.profileToProfile(img, icc, srgb, renderingIntent = ImageCms.INTENT_SATURATION)
	
	return img


# Helper to find files...
def find_images(path):
	# Find raw camera exports and picasa exports
	# FIXME: The stored filenames break if path != curdir
	images = [f for f in os.listdir(path) 
			  if f.startswith("_MG_") and (f.endswith(".JPG") or f.endswith('.jpg'))]
	return images


if len(sys.argv) > 1:
	# Check on each path supplied...
	print("Checking supplied paths...")
	images = []
	
	for path in sys.argv[1:]:
		if os.path.isdir(path):
			# Directory - Find everything interesting there to convert
			# TODO: Make this recursive?
			images += find_images(path)
		elif path.isdigit():
			# Partial filename - just the digits, for convenience
			# TODO: Check that a corresponding file actually exists..
			path = "_MG_%s.JPG" % (path)
			if not os.path.exists(path):
				print("   ERROR: '%s' does not exist" % (path))
			else:
				images.append(path)
		elif not os.path.exists(path):
			# Invalid Filename
			print("  ERROR: '%s' is not a valid path" % (path))
		else:
			# Valid Filename - Assume that this is an image
			# TODO: Check that it is an image...
			images.append(path)
else:
	# Hunt for picasa exports / camera raw exports
	print("sys.argv = %s\n\n" % (sys.argv))
	
	print("Finding images...")
	images = find_images('.')

# Report how many were found
N = len(images)
print("\n\nFound %d Images" % (N))
PREVIEW_LIMIT = 30

if N == 0:
	# Silently exit if nothing found
	sys.exit(1)
elif N < PREVIEW_LIMIT:
	# Show what we found if there aren't too many
	# (Use this when debugging, to ensure we're culling the right ones)
	print("   %s\n\n" % (images))
else:
	# Don't print all of them (as then we miss the full count)
	# (Useful when doing production exports on datasets with 100-600 shots)
	print("   %s\n    + '[... %d more...]\n\n'" % (images[:50], N - 50))

# Process images
# TODO: Parallelise this to use more cores?
for i, fileN in enumerate(images):
	print("[%3d/%3d] Converting ==> '%s'" % (i, N, fileN))
	
	# Open the file for conversion
	img = Image.open(fileN)
	exif = img.info['exif']

	#if is_adobe_rgb(img):
	#img =  adobe_to_srgb(img)
	img =  adobe_to_srgb__fast(img)
	
	# Save file again, replacing the underscore for a "I"
	# FIXME: This breaks if we use a filename with path embedded
	new_fileN = "I%s" % (fileN[1:])
	img.save(new_fileN, exif=exif)
	
