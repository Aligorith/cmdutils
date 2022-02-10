import sys
import os

from PIL import Image

PATH = "./"
OUTDIR = "./cropped_images"

def crop_all(base_path:str, 
             outdir_name:str,
             crop_rect: tuple,
             *,
             rename_as_seq=False):
	out_path = os.path.join(base_path, outdir_name)
	if not os.path.exists(out_path):
		os.mkdir(out_path)
	
	files_list = os.listdir(base_path)
	for i, fileN in enumerate(files_list):
		fullpath = os.path.join(base_path, fileN)
		if os.path.isfile(fullpath):
			print("[% 6d / % 6d]  Cropping '%s'..." % (i+1, len(files_list), fullpath))
			
			im = Image.open(fullpath)
			imCrop = im.crop(crop_rect)
			
			if rename_as_seq:
				_, extn = os.path.splitext(fileN)
				assert extn[0] == "."
				
				seq_filename = ("%06d" % (i)) + extn
				out_filename = os.path.join(out_path, seq_filename)
				print("    '%s' -> '%s'" % (fullpath, out_filename))
			else:
				out_filename = os.path.join(out_path, fileN)
				
			imCrop.save(out_filename)

if __name__ == "__main__":
	args = sys.argv[1:]
	
	# Check for options
	# -i = Re-enumerate
	if args[0:1] == ["-i"]:
		print("! Rename using sequence id's...")
		rename_as_seq = True
		args = args[1:]
	else:
		rename_as_seq = False
	
	# Get crop coordinates
	if len(args) == 4:
		crop_rect = [int(x) for x in args]
	elif len(args) == 2:
		crop_rect = [0, 0, int(args[0]), int(args[1])]
	else:
		print("Usage: crop_all_images.py [-i] X Y W H")
		sys.exit(-1)
	
	# Perform cropping
	crop_all(PATH, OUTDIR,
	         crop_rect,
	         rename_as_seq=rename_as_seq)
	
