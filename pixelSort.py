'''
pixelSort by Ryan Jokuti
https://github.com/ryanjokuti

this script looks at each pixel in an image and sorts a row of them from 
brightest-darkest or vice-versa if they are within the defined brightness range

takes around 3-5 minutes to process an image with a resolution of 3000x4000 on a mid-range CPU
'''

# imports
from PIL import Image
import multiprocessing
import datetime
import time
import sys
import random
import os

# tunable variables
fileLocation = ""       # file path of the image you're pixel sorting
resized = False     # if you're resizing the image before pixel sorting it, set this to true
reverseSort = True      # false = darkest pixels at the top; true = darkest pixels on the bottom
resizeMultiplier = 0.5      # the multiplier for resizing the image
brightnessMinimum = 30       # the minimum brightness a pixel has to be to be sorted
brightnessMaximum = 170     # the maximum brightness a pixel can be to be sorted
getSpotsProcesses = 15      # MULTIPROCESSING - number of processes for the getSpots function
pixelSortProcesses = 20     # MULTIPROCESSING - number of processes for the pixelSort function

# USE THIS TO CHANGE THE SORT DIRECTION (currently can't use negative numbers)
# a function that returns the sort's direction
def sortDirection(x, y, i):
    return (x + int(i * 0), y + int(i * 1))

# a function that returns true if the pixel falls within the defined brightness range
def meetConditions(xy, image):
    try:
        # gets the brightness of the pixel by taking the sum of the RGB values and dividing it by 3
        pixelBrightness = int(sum(image.getpixel(xy)) / 3)
        if pixelBrightness >= brightnessMinimum and pixelBrightness <= brightnessMaximum:
            return True
        else:
            return False
    except:
        return False

# a function that determines if each pixel in the assigned rows are starting points for pixel sorts
def rowSpot(assignedRows, columns, spots, image):
    for row in range(assignedRows[0], assignedRows[-1]):
        for column in range(columns):
            # sets the xy position to behind our pixel
            newXY = sortDirection(column, row, -1)
            # checks if the pixel behind it is already within range, meaning that this pixel wouldn't be a starting spot
            # also checks if the pixel is at the top/side of the image
            if (meetConditions(newXY, image) == False) or (newXY[0] < 0) or (newXY[1] < 0):
                # sets the xy position to in front of our pixel
                newXY = sortDirection(column, row, 1)
                # checks if the pixel in front of it is within range, because if not it's only 1 pixel, meaning there is no reason to sort it
                if meetConditions(newXY, image):
                    # finally checks and sees if our pixel is within the range, and then adds it to the list of spots if it is
                    if meetConditions((column, row), image):
                        spots.append((column, row))

# a function that gets pixels that fit certain conditions and puts them in a list of 'spots'
def getSpots():
    print("getting spots...")
    startTimeL = time.time()
    processList = []
    rowsTBA = list(range(rows))
    print("assigning rows...")
    while len(rowsTBA) > 0:
        assignedRows = rowsTBA[:rowAmount]
        rowsTBA = rowsTBA[rowAmount:]
        process = multiprocessing.Process(target=rowSpot, args=(assignedRows, columns, spots, selectedImage))
        processList.append(process)
    print("launching processes...")
    for process in processList:
        process.start()
    print("waiting for processes...")
    for process in processList:
        process.join()
    endTimeL = time.time()
    duration = int(endTimeL - startTimeL)
    print("finished getSpots in {} seconds".format(duration))

# a function that marks all spots as red and opens image
def markRed():
    print("marking {} spots in red...".format(len(spots)))
    startTimeL = time.time()
    # makes a copy of the image as to not mark on our actual image
    redImage = selectedImage.copy()
    # just loops through all of the spots and places a red pixel where they are
    for xy in spots:
        redImage.putpixel(xy, (255, 0, 0))
    endTimeL = time.time()
    duration = int(endTimeL - startTimeL)
    print("finished markRed in {} seconds".format(duration))
    redImage.show()

# a function that takes all of the pixels that are within the brightness range, sorts them, then places them in a list to be pasted later
def spotsSort(assignedSpots, pasteList, image):
    for xy in assignedSpots:
        x = xy[0]
        y = xy[1]
        newXY = (x, y)
        sortList = []
        i = 0
        # while the pixel falls within the range, it adds each one to the sort list
        while meetConditions(newXY, image):
            sortList.append(image.getpixel(newXY))
            i += 1
            newXY = sortDirection(x, y, i)
        # once it hits a pixel that isn't within the range, it then sorts all of the pixels
        sortList.sort(key=sum, reverse=reverseSort)
        # gets the length of the sort
        endXY = sortDirection(x, y, len(sortList))
        # finds the bounds of our sort
        imageBox = (endXY[0] - xy[0] + 1, endXY[1] - xy[1] + 1)
        # creates an image which we will add our sorted pixels to
        pasteImage = Image.new('RGB', imageBox)
        # creates an image that will be our paste mask
        maskImage = Image.new('L', imageBox)
        # adds each pixel back, sorted
        for i in range(len(sortList)):
            newXY = sortDirection(0, 0, i)
            try:
                pasteImage.putpixel(newXY, sortList[i])
                maskImage.putpixel(newXY, 255)
            except:
                None
        # adds our image with the pixels sorted, the mask, and our starting position to the paste list
        pasteList.append((pasteImage, xy, maskImage))

# function that sorts starts all of the pixel sorting processes and then pastes their results into the original image
def pixelSort():
    print("pixel sorting {} spots...".format(len(spots)))
    startTimeL = time.time()
    processList = []
    spotsTBA = spots
    print("assigning spots...")
    while len(spotsTBA) > 0:
        assignedSpots = spotsTBA[:spotsAssigned]
        spotsTBA = spotsTBA[spotsAssigned:]
        process = multiprocessing.Process(target=spotsSort, args=(assignedSpots, pasteList, selectedImage))
        processList.append(process)
    print("launching processes...")
    for process in processList:
        process.start()
    print("waiting for processes...")
    for process in processList:
        process.join()
    print("pasting {} sorts...".format(len(pasteList)))
    # takes all of the pastes from the paste list and adds them to the original image
    for paste in pasteList:
        selectedImage.paste(paste[0], paste[1], paste[2])
    endTimeL = time.time()
    duration = int(endTimeL - startTimeL)
    print("finished pixelSort in {} seconds".format(duration))

# makes sure only the main thread runs these to avoid accidental iteration
if __name__ == '__main__':
    # variable setup
    manager = multiprocessing.Manager()     # manager allows for lists to be shared through multiple processes
    spots = manager.list()
    pasteList = manager.list()

    # getting starting time
    startTime = datetime.datetime.now()
    print("start time: {}".format(startTime))

    # opening image
    selectedImage = Image.open(fileLocation).convert('RGB')

    # splitting file directory and name for later
    directoryName = os.path.dirname(fileLocation)
    baseName = os.path.splitext(os.path.basename(fileLocation))[0]
    print(directoryName)
    print(baseName)

    # resizing image if the user said to
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

    # function execution
    # determining how many rows each process should be assigned
    rowAmount = int(rows / getSpotsProcesses)
    print("rows assigned per process: {}".format(rowAmount))
    getSpots()
    markRed()
    # determining how many spots each process should be assigned
    spotsAssigned = int(len(spots) / pixelSortProcesses)
    print("spots assigned per process: {}".format(spotsAssigned))
    pixelSort()

    # saving and then showing the sorted image
    selectedImage.save("{}/{}Sorted.jpg".format(directoryName, baseName))
    selectedImage.show()

    # getting ending time
    endTime = datetime.datetime.now()
    print("start time: {}".format(startTime))
    print("end time: {}".format(endTime))