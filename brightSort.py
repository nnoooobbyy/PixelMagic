'''
brightSort by Ryan Jokuti
https://github.com/ryanjokuti

this script looks at each pixel in an image and sorts them all in order of
brightness
'''

# imports
from PIL import Image
import os

# tunable variables
fileLocation = ""
resized = False
reverseSort = True
resizeMultiplier = 0.4

# opening images
selectedImage = Image.open(fileLocation).convert('RGB')
# splitting file directory and name for later
directoryName = os.path.dirname(fileLocation)
baseName = os.path.splitext(os.path.basename(fileLocation))[0]
print(directoryName)
print(baseName)

# resizing image
if (resized):
    baseWidth = int(selectedImage.size[0] * resizeMultiplier)
    print("resizing image to {}%...".format(int(resizeMultiplier * 100)))
    widthPercent = (selectedImage.size[1]/float(selectedImage.size[0]))
    baseHeight = int((float(baseWidth)*float(widthPercent)))
    selectedImage = selectedImage.resize((baseWidth,baseHeight), Image.ANTIALIAS)
    print("resize successful!")

# getting image size
columns = selectedImage.size[0]
rows = selectedImage.size[1]
print("columns: {}".format(columns))
print("rows: {}".format(rows))

# a function that gets pixels that fit certain conditions and puts them in a list of 'spots'
def brightSort():
    print("gathering all {} pixels...".format(columns * rows))
    sortList = []
    for row in range(rows):
        for column in range(columns):
            sortList.append(selectedImage.getpixel((column, row)))
    print("appended all pixels into a list, sorting list...")
    sortList.sort(key=sum, reverse=reverseSort)
    print("list sorted, placing pixels...")
    i = 0
    for row in range(rows):
        for column in range(columns):
            selectedImage.putpixel((column, row), sortList[i])
            i += 1
    print("displaying sorted image...")
    selectedImage.save("{}/{}BrightSorted.jpg".format(directoryName, baseName))
    selectedImage.show()

brightSort()