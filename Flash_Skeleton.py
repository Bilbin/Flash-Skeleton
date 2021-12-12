from PIL import ImageGrab, Image
import cv2
from pynput import keyboard
from threading import Thread
import numpy as np
import os
import pyautogui

print("Save button template as \"button-template.png\" in directory")
print("Save input template as \"input-template.png\" in directory")
print("When asked for asset names, do not add the file extension")
directory = input("Enter directory of web content: ")
print("Press \"[\" to begin")
print("Press \"]\" to stop")

# Change per project
assetsDirectory = "../../../../src/assets/[app-name]"
imagePrefix = "[your prefix]"
buttonRGB = [0, 0, 0]
inputRGB = [0, 0, 0]
backgroundDimensions = (0, 0)
# Add one to the second set of coordinates you get from your image editor
backgroundCoordinates = (0, 0, 0, 0)

scssName = f"{directory}.scss"
htmlName = f"{directory}.html"
cssName = f"{directory}.css"

backgroundName = f"{directory}-background"
backgroundFileName = f"{imagePrefix}{backgroundName}"

# Divide targeted dimension by initial dimensions
xSizingScaleFactor = backgroundDimensions[0] / (backgroundCoordinates[2] - backgroundCoordinates[0] + 1)
ySizingScaleFactor = backgroundDimensions[1] / (backgroundCoordinates[3] - backgroundCoordinates[1] + 1)

htmlPath = f"{directory}/{directory}.html"
scssPath = f"{directory}/{directory}.scss"
cssPath = f"{directory}/{directory}.css"

htmlMaster = ('<head>\n'
              f'\t<link rel="stylesheet" href="{directory}.css">\n'
              '\t<link rel="stylesheet" href="reset.css">\n'
              '</head>\n')
scssMaster = ""
cssMaster = ""

try:
    os.mkdir(directory)
except FileExistsError:
    pass

try:
    os.makedirs(f"{directory}/{assetsDirectory}")
except FileExistsError:
    pass


def on_press(key):
    try:
        if key.char == '[':
            thread = Thread(target=main)
            thread.daemon = True
            thread.start()

        if key.char == ']':
            return False
    except:
        pass


def main():
    print("Retrieving background")
    print(f"xScaleFactor: {xSizingScaleFactor}")
    print(f"yScaleFactor: {ySizingScaleFactor}")
    getBackground()
    print("\nPreparing Markup")
    elements = prepareMarkup()
    print("Writing Markup")
    writeMarkup(elements)
    print("\nDone")


def writeMarkup(elements):
    global htmlMaster
    global scssMaster
    global cssMaster

    for element in elements:
        htmlMaster += element.html
        scssMaster += element.scss
        cssMaster += element.css

    htmlMaster += "</div>"
    scssMaster += "}"

    removeFile(htmlPath)
    removeFile(scssPath)
    removeFile(cssPath)

    with open(htmlPath, 'w') as f:
        f.write(htmlMaster)

    with open(scssPath, 'w') as f:
        f.write(scssMaster)

    with open(cssPath, 'w') as f:
        f.write(cssMaster)


def removeFile(path):
    if os.path.isfile(path):
        os.remove(path)


def prepareMarkup():
    buttons = prepareElements(f"{directory}/button-template.png", buttonRGB, Button)
    duplicates = {}
    if buttons is not None:
        for button in buttons:
            duplicates = button.changeName(duplicates)
    print("\nImage naming completed\n")

    inputs = prepareElements(f"{directory}/input-template.png", inputRGB, Input)

    elements = (buttons if buttons is not None else []) + (inputs if inputs is not None else [])
    for element in elements:
        element.writeHtml()
        element.writeScss()
        element.writeCss()

    return elements


def prepareElements(file, rgb, elementClass):
    contours = getContours(file, rgb)

    if contours == [] or contours is None:
        return

    elements = []
    for ind, contour in enumerate(contours):
        topLeft = contour[0][0]
        bottomRight = contour[2][0]
        # Adjust to get last row and column of pixels
        element = elementClass(topLeft, bottomRight, ind)
        elements.append(element)

    return elements


def getFullAssetPath(fileName):
    assetsDirectoryWithBackslashes = assetsDirectory.replace('/', '\\')
    return f"{os.getcwd()}\\{directory}\\{assetsDirectoryWithBackslashes}\\{fileName}"


# Saves background image as [backgroundName].png
def getBackground():
    # Pixels: add 1 to the last two coords
    background = ImageGrab.grab(bbox=backgroundCoordinates)

    backgroundResized = background.resize(backgroundDimensions)
    backgroundResized.save(getFullAssetPath(f"{backgroundFileName}.png"))

    global htmlMaster
    global scssMaster
    global cssMaster
    htmlMaster += f'<div class="{backgroundName} frame">\n'
    scssMaster += (f'.{backgroundName} {{\n'
                   f'\tbackground: url({assetsDirectory}/{backgroundFileName}.png) no-repeat;\n'
                   f'\twidth: {backgroundDimensions[0]}px;\n'
                   f'\theight: {backgroundDimensions[1]}px;\n'
                   '\tposition: relative;\n\n')
    cssMaster += (f'.{backgroundName} {{\n'
                  f'\tbackground: url({assetsDirectory}/{backgroundFileName}.png) no-repeat;\n'
                  f'\twidth: {backgroundDimensions[0]}px;\n'
                  f'\theight: {backgroundDimensions[1]}px;\n'
                  '\tposition: relative;\n'
                  '}\n\n')


# Returns contours in order of left to right, up to down
def getContours(file, rgb):
    if not os.path.isfile(file):
        print(f"{file} not found.")
        return None

    im = cv2.imread(file)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    bounds = np.array(rgb)
    mask = cv2.inRange(im, bounds, bounds)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        print(f"No contours found in {file}.")
        return None

    contoursSorted = sortContours(contours)

    return contoursSorted


# Sorts contours left to right, up to down
def sortContours(contours):
    # First sort by y-coords
    contoursTmp = sorted(contours, key=lambda contour: contour[0][0][1])
    # Then sort by x-coords (sort groups of same y-coord)
    contoursSorted = []
    groupTmp = []
    groupNum = contoursTmp[0][0][0][1]

    for i in range(len(contoursTmp)):
        if contoursTmp[i][0][0][1] == groupNum:
            groupTmp.append(contoursTmp[i])

            if i == len(contoursTmp) - 1:
                contoursSorted += sorted(groupTmp, key=lambda coord: coord[0][0][0])

        else:
            contoursSorted += sorted(groupTmp, key=lambda coord: coord[0][0][0])
            groupTmp = [contoursTmp[i]]
            groupNum = contoursTmp[i][0][0][1]

            if i == len(contoursTmp) - 1:
                contoursSorted.append(contoursTmp[i])

    return contoursSorted


def xScaleFactor(pixels):
    return round(pixels * xSizingScaleFactor)


def yScaleFactor(pixels):
    return round(pixels * ySizingScaleFactor)


class Element():
    def __init__(self, topLeft, bottomRight, num):
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.adjustedBottomRight = list(map(lambda coord: coord + 1, self.bottomRight))
        self.num = num
        self.width = None
        self.scaledWidth = None
        self.height = None
        self.scaledHeight = None
        self.leftMargin = None
        self.scaledLeftMargin = None
        self.topMargin = None
        self.scaledTopMargin = None
        self.html = None
        self.scss = None
        self.css = None
        self.getDimensions()
        self.getMargins()

    def getDimensions(self):
        self.width = self.adjustedBottomRight[0] - self.topLeft[0]
        self.height = self.adjustedBottomRight[1] - self.topLeft[1]
        self.scaledWidth = xScaleFactor(self.width)
        self.scaledHeight = yScaleFactor(self.height)

    def getMargins(self):
        self.leftMargin = self.topLeft[0] - backgroundCoordinates[0]
        self.topMargin = self.topLeft[1] - backgroundCoordinates[1]
        self.scaledLeftMargin = xScaleFactor(self.leftMargin)
        self.scaledTopMargin = yScaleFactor(self.topMargin)


class Input(Element):
    def __init__(self, topLeft, bottomRight, num):
        super().__init__(topLeft, bottomRight, num)
        self.name = input(f"What new name do you want for input number {self.num + 1}?: ")
        self.inputType = self.getType()

    def getType(self):
        valid = False

        while not valid:
            inputType = input("Is it an input (i) or textarea (t)?:")
            valid = inputType in ["i", "t"]
        print()

        return inputType

    def writeHtml(self):
        if self.inputType == "i":
            self.html = f'\t<input class="{self.name}">\n'

        elif self.inputType == "t":
            self.html = f'\t<textarea class="{self.name}"></textarea>\n'

    def writeScss(self):
        self.scss = (f'\t.{self.name} {{\n'
                     '\t\tposition: absolute;\n'
                     f'\t\tmargin-top: {self.scaledTopMargin}px;\n'
                     f'\t\tmargin-left: {self.scaledLeftMargin}px;\n'
                     f'\t\twidth: {self.scaledWidth}px;\n'
                     f'\t\theight: {self.scaledHeight}px;\n'
                     '\t}\n\n')

    def writeCss(self):
        self.css = (f'.{self.name} {{\n'
                    '\tposition: absolute;\n'
                    f'\tmargin-top: {self.scaledTopMargin}px;\n'
                    f'\tmargin-left: {self.scaledLeftMargin}px;\n'
                    f'\twidth: {self.scaledWidth}px;\n'
                    f'\theight: {self.scaledHeight}px;\n'
                    '}\n\n')


class Button(Element):
    def __init__(self, topLeft, bottomRight, num):
        super().__init__(topLeft, bottomRight, num)
        self.image = None
        self.scaledImage = None
        self.hoverImage = None
        self.scaledHoverImage = None
        self.name = None
        self.hoverName = None
        self.imageName = None
        self.hoverImageName = None
        self.getImage()
        self.getHoverImage()

    def getImage(self):
        self.name = f"b-{self.num}"
        self.imageName = f"{imagePrefix}{self.name}"
        self.image = ImageGrab.grab(bbox=tuple(self.topLeft) + tuple(self.adjustedBottomRight))
        self.scaledImage = self.image.resize((self.scaledWidth, self.scaledHeight))
        self.scaledImage.save(getFullAssetPath(f"{self.imageName}.png"))

    def getHoverImage(self):
        self.hoverName = f"b-{self.num}-hover"
        self.hoverImageName = f"{imagePrefix}{self.hoverName}"
        pyautogui.moveTo(round(self.topLeft[0] + (self.width / 2)), round(self.topLeft[1] + (self.height / 2)), 0.3)
        self.hoverImage = ImageGrab.grab(bbox=tuple(self.topLeft) + tuple(self.adjustedBottomRight))
        self.scaledHoverImage = self.hoverImage.resize((self.scaledWidth, self.scaledHeight))
        self.scaledHoverImage.save(getFullAssetPath(f"{self.hoverImageName}.png"))

    def changeName(self, duplicates):
        self.image.show()
        newName = input(f"What new name do you want for button number {self.num + 1}?: ")

        # useExisting is for images that have to be modified and can't be made on the fly
        # i.e. down-button images that have specific backgrounds (backgrounds have to be removed manually)
        useExisting = False
        if "use-existing" in newName:
            newName = newName.replace(" use-existing", "")
            useExisting = True

        newImageName = f"{imagePrefix}{newName}"

        if newName in duplicates.keys():
            duplicates[newName] += 1
        else:
            duplicates[newName] = 1

        if duplicates[newName] != 1 or useExisting:
            print("Image already exists. Removing Duplicate.")
            os.remove(f"{directory}/{assetsDirectory}/{self.imageName}.png")
            os.remove(f"{directory}/{assetsDirectory}/{self.hoverImageName}.png")

        else:
            if os.path.isfile(f"{directory}/{assetsDirectory}/{newImageName}.png"):
                os.remove(f"{directory}/{assetsDirectory}/{newImageName}.png")
                os.remove(f"{directory}/{assetsDirectory}/{newImageName}-hover.png")

            os.rename(f"{directory}/{assetsDirectory}/{self.imageName}.png",
                      f"{directory}/{assetsDirectory}/{newImageName}.png")
            os.rename(f"{directory}/{assetsDirectory}/{self.hoverImageName}.png",
                      f"{directory}/{assetsDirectory}/{newImageName}-hover.png")

        self.imageName = newImageName
        self.hoverImageName = f"{newImageName}-hover"

        if duplicates[newName] == 1:
            self.name = newName
            self.hoverName = f"{newName}-hover"
        else:
            self.name = f"{newName}-{duplicates[newName]}"
            self.hoverName = f"{self.name}-hover"

        return duplicates

    def writeHtml(self):
        self.html = f'\t<button class="{self.name}"></button>\n'

    def writeScss(self):
        self.scss = (f'\t.{self.name} {{\n'
                     f'\t\tbackground: url({assetsDirectory}/{self.imageName}.png) no-repeat;\n'
                     '\t\tposition: absolute;\n'
                     f'\t\tmargin-top: {self.scaledTopMargin}px;\n'
                     f'\t\tmargin-left: {self.scaledLeftMargin}px;\n'
                     f'\t\twidth: {self.scaledWidth}px;\n'
                     f'\t\theight: {self.scaledHeight}px;\n'
                     '\t}\n\n'
                     f'\t.{self.name}:hover {{\n'
                     f'\t\tbackground: url({assetsDirectory}/{self.hoverImageName}.png) no-repeat;\n'
                     '\t\tposition: absolute;\n'
                     f'\t\tmargin-top: {self.scaledTopMargin}px;\n'
                     f'\t\tmargin-left: {self.scaledLeftMargin}px;\n'
                     f'\t\twidth: {self.scaledWidth}px;\n'
                     f'\t\theight: {self.scaledHeight}px;\n'
                     '\t}\n\n')

    def writeCss(self):
        self.css = (f'.{self.name} {{\n'
                    f'\tbackground: url({assetsDirectory}/{self.imageName}.png) no-repeat;\n'
                    '\tposition: absolute;\n'
                    f'\tmargin-top: {self.scaledTopMargin}px;\n'
                    f'\tmargin-left: {self.scaledLeftMargin}px;\n'
                    f'\twidth: {self.scaledWidth}px;\n'
                    f'\theight: {self.scaledHeight}px;\n'
                    '}\n\n'
                    f'.{self.name}:hover {{\n'
                    f'\tbackground: url({assetsDirectory}/{self.hoverImageName}.png) no-repeat;\n'
                    '\tposition: absolute;\n'
                    f'\tmargin-top: {self.scaledTopMargin}px;\n'
                    f'\tmargin-left: {self.scaledLeftMargin}px;\n'
                    f'\twidth: {self.scaledWidth}px;\n'
                    f'\theight: {self.scaledHeight}px;\n'
                    '}\n\n')


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
