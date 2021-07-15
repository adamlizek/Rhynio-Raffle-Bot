from PIL import Image
import sys
im = Image.open(sys.argv[1])
print(str(im.size))
print(str(im.getbbox()))
im2 = im.crop(im.getbbox())
im2.save(sys.argv[1])