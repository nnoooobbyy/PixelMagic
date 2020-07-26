'''
ImageToText by Ryan Jokuti
https://github.com/ryanjokuti

this script looks at each pixel in an image and turns them into a character based on their brightness
*images are always required to be resized
'''

# imports
from PIL import Image
import os
import time

# modifiable variables
fileLocation = ""
# brightness characters
tenPercent = "█" # brightest
twentyfivePercent = "▓"
fiftyPercent = "▒"
seventyfivePercent = "░"
onehundredPercent = "░" # darkest

# canvas variables
columns = 0
rows = 0
canvas = []

# image initialization
selectedImage = Image.open(fileLocation).convert('L')
print(os.path.dirname(fileLocation))
print(os.path.basename(fileLocation))
directoryName = os.path.dirname(fileLocation)
baseName = os.path.basename(fileLocation)

# resizing image
baseWidth = int(input("what do you want the width to be? "))
print("resizing image...")
widthPercent = (selectedImage.size[1]/float(selectedImage.size[0])) * 0.45
baseHeight = int((float(baseWidth)*float(widthPercent)))
selectedImage = selectedImage.resize((baseWidth,baseHeight), Image.ANTIALIAS)
print("resize successful!")

# getting size
columns = selectedImage.size[0]
rows = selectedImage.size[1]  
print("columns: " + str(columns))
print("rows: " + str(rows))

# converts the image's pixels into text
def textConversion():
    print("converting into text...")
    for row in range(rows):
        # adds the row number before each row for easy reference in code
        canvas.append(row)
        print("    (" + str(int((row/rows) * 100)) +"%)", end="\r")
        for column in range(columns):
            # appends the pixel as text to the canvas
            pixelValue = selectedImage.getpixel((column, row))
            print(pixelValue, end="\r")
            if pixelValue <= 26:
                canvas.append(tenPercent)
            elif pixelValue <= 64:
                canvas.append(twentyfivePercent)
            elif pixelValue <= 128:
                canvas.append(fiftyPercent)
            elif pixelValue <= 191:
                 canvas.append(seventyfivePercent)
            else:
                canvas.append(onehundredPercent)
    print("conversion successful!")

# prints the board in a formatted fashion
def viewCanvas():
    global rows
    global columns

    resultFileName = baseName + ".txt"
    resultFileLocation = os.path.join(directoryName + "/" + resultFileName)
    resultFile = open(resultFileLocation,"w+")
    print("opened file " + resultFileLocation)
    # prints each row separately, using a for loop
    for row in range(rows):
        # finds the start of the row by adding 1 from the row #'s index
        rowLocation = canvas.index(row) + 1
        # finds the end of the row by adding the amount of columns
        rowEnd = rowLocation + columns
        # creates a new list with only the slice from that row
        rowSegment = canvas[rowLocation:rowEnd]
        # prints the list in a nice format
        print(''.join(map(str, rowSegment)))
        # tries to write to file
        try:
            resultFile.write(''.join(map(str, rowSegment)))
            resultFile.write("\n")
        except UnicodeEncodeError:
            pass
    # prints three empty lines for formatting
    print("")
    print("")
    print("")
    resultFile.close()

textConversion()
viewCanvas()
time.sleep(10)