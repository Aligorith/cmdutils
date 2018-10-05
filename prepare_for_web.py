# Convert aRGB files to sRGB (for upload to web/GPhotos) 
# Based on http://stackoverflow.com/a/41524153/6531515
import sys
import os
import tempfile

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
	
	icc = open(r'C:\Users\Joshua\cmdutils\AdobeRGB.icc', 'rb')
	#icc = open('AdobeRGB.icc')
	 	
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
	print("Finding images...")
	images = find_images('.')
	
print("\n\nFound %d Images:\n   %s\n\n" % (len(images), images))
if len(images) == 0:  sys.exit(1)

for fileN in images:
	print("Converting ==> '%s'" % (fileN))
	
	# Open the file for conversion
	img = Image.open(fileN)
	exif = img.info['exif']

	#if is_adobe_rgb(img):
	img =  adobe_to_srgb(img)
	
	# Save file again, replacing the underscore for a "I"
	# FIXME: This breaks if we use a filename with path embedded
	new_fileN = "I%s" % (fileN[1:])
	img.save(new_fileN, exif=exif)
	
