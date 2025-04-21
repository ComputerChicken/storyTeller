# Dependencies
import sys
import pygame
from pygame.locals import *
import os
import math
from tkinter import Tk     # tkinter for file management
from tkinter.filedialog import askopenfilename

# Remove tk window
Tk().withdraw()

# Set icon
programIcon = pygame.image.load("icon.png")

pygame.display.set_icon(programIcon)

# Initialize pygame
pygame.init()

# Get width/height of screen and define the surface with those values
width, height = infoObject = pygame.display.Info().current_w/3*2, pygame.display.Info().current_h/3*2
screen = pygame.display.set_mode((width,height),pygame.RESIZABLE)

fps = 60
fpsClock = pygame.time.Clock()

# Initialize needed fonts
pygame.font.init()
fontSize = 40
pixelFont = pygame.font.Font("pixelFont.ttf",fontSize)
pixelFontSmall = pygame.font.Font("pixelFont.ttf",int(fontSize/3*2))
pixelFontBig = pygame.font.Font("pixelFont.ttf",int(fontSize/3*4))

time = 0

ended = False

# This class allows me to easily create multiple inputs for the level builder
class InputBox:

    def __init__(self, x, y, w, h, placeHolder = '', text='',width=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.placeHolder = placeHolder
        self.text = text
        self.txt_surface = pixelFontSmall.render(text, True, (0, 0, 0))
        self.holder_surface = pixelFontSmall.render(placeHolder, True, (100, 100, 100))
        self.width = width
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = (230, 230, 230) if self.active else (255, 255, 255)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = pixelFontSmall.render(self.text, True, (0, 0, 0))

    def draw(self, screen):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10 if self.text else self.holder_surface.get_width()+10+self.width)
        self.rect.w = width
        # Blit the rects.
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, self.width)
        # Blit the text.
        screen.blit(self.txt_surface if self.text else self.holder_surface, (self.rect.x+5+self.width, self.rect.y+5))

class CheckBox:

    def __init__(self, x, y, label = "", width=50, height=50, state=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.state = state

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the state variable.
                self.state = not self.state

    def draw(self, screen):
        # Blit the rects.
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 5)
        # Blit the text.
        tempText = pixelFont.render("x" if self.state else "",False,(0, 0, 0))
        blit_centered(tempText, (self.rect.x+self.rect.width/2+3, self.rect.y+self.rect.height/2-5))
        tempText = pixelFontSmall.render(self.label, False, (0, 0, 0))
        screen.blit(tempText, (self.rect.x+self.rect.width+10, self.rect.y+4))

# A function for blitting objects (specifically text) to a center position
def blit_centered(source,pos):
    # Will return the blit object for later use
    return screen.blit(source,(pos[0]-source.get_rect().width/2,pos[1]-source.get_rect().height/2))

# The following classes are the classes for the game elements
class location:
    def __init__(this, name, start=None, onTravel=None, itemRequired=None, interactRequire = None, cantReturn=False, isEnding=False):
        this.isEnding = isEnding
        this.cantReturn = cantReturn
        this.name = name
        this.start = start
        this.interactRequire = interactRequire
        this.itemRequired = itemRequired
        this.onTravel = onTravel

    def canTravel(this, current, locations):
        # Check if you are at the starting location or if you came from that location
        if(current == this.start or current == None or locations[current].start == this.name):
            return True
        else:
            return False
        
    # Check if player has required item to enter a location
    def hasItem(this, inventory):
        if(this.itemRequired in list(inventory.keys()) or this.itemRequired == None):
            if(this.itemRequired != None):
                if(inventory[this.itemRequired].destroyOnUse):
                    del inventory[this.itemRequired]
            return True
        else:
            return False
        
    def travel(this, locations, inventory, currentLoc, interacted):
        global ended
        rtrn = ["",currentLoc]
        if this.canTravel(currentLoc, locations):
            if(this.hasItem(inventory)):
                if(this.interactRequire in interacted or this.interactRequire == None or interacted == set(["*"])):
                    interacted.add(this.name)
                    rtrn[1] = this.name
                    if(this.onTravel != None):
                        rtrn[0] = this.onTravel
                    if(this.isEnding):
                        ended = True
                    if(this.cantReturn):
                        this.start = "NO START"
                else:
                    rtrn[0] = "Must have interacted with " + this.interactRequire + " to interact"
            else:
                rtrn[0] = "Missing item: " + this.itemRequired
        return rtrn[0], rtrn[1]
        
class item:
    def __init__(this, name, info, onUse=None, interactRequire = None, destroyOnUse=False, isEnding=False):
        this.isEnding = isEnding
        this.name = name
        this.info = info
        this.onUse = onUse
        this.interactRequire = interactRequire
        this.destroyOnUse = destroyOnUse

    # Use an item (displays use text)
    def use(this, inventory, interacted):
        global ended
        if(this.interactRequire in interacted or this.interactRequire == None or interacted == set(["*"])):
            if(this.isEnding):
                ended = True
            if(this.onUse == None):
                return "This item cannot be used"
            interacted.add(this.name)
            out = this.onUse
            if(this.destroyOnUse):
                del inventory[this.name]
            return out
        else:
            return "Must have interacted with " + this.interactRequire + " to interact"

# The character class
class character:
    def __init__(this, name, dialog, location, giveItem = None, itemRequired = None, interactRequire = None, interactOnce = False, isEnding = False):
        this.isEnding = isEnding
        this.name = name
        this.dialog = dialog
        this.giveItem = giveItem
        this.itemRequired = itemRequired
        this.interactRequire = interactRequire
        this.location = location
        this.interactOnce = interactOnce
    
    # Check if player in a location where they can interact with the character
    def canInteract(this, current):
        if(current == this.location):
            return True
        else:
            return False

    # The interaction function
    def interact(this, inventory, interacted, characters):

        # Check if the player has the required item to interact and has interacted with required objects
        if(this.itemRequired == None or this.itemRequired in list(inventory.keys())):
            if(this.interactRequire == None or this.interactRequire in interacted or interacted == set(["*"])):
                if(this.itemRequired in list(inventory.keys())):
                    if(inventory[this.itemRequired].destroyOnUse):
                        del inventory[this.itemRequired]
                global ended
                if(this.isEnding):
                    ended = True

                interacted.add(this.name)
                out = this.dialog

                # Give the player the give item if it is not None
                if(this.giveItem != None):
                    inventory[this.giveItem.name] = this.giveItem
                    out += "\n\nYou have recieved: " + this.giveItem.name

                # Check if only interactable once, if so delete
                if(this.interactOnce):
                    del characters[this.name]
            else:
                out = "Must have interacted with " + str(this.interactRequire) + " to interact"
        else:
            out = "Must have " + this.itemRequired + " to interact"
        return out

# The interactable class is very similar to the player class
class interactable:
    def __init__(this, name, dialog, location, giveItem = None, itemRequired = None, interactRequire = None, interactOnce = False, isEnding = False):
        this.isEnding = isEnding
        this.name = name
        this.dialog = dialog
        this.giveItem = giveItem
        this.itemRequired = itemRequired
        this.interactRequire = interactRequire
        this.location = location
        this.interactOnce = interactOnce
    
    def canInteract(this, current):
        if(current == this.location):
            return True
        else:
            return False

    def interact(this, inventory, interacted, interactables):
        # Check if the player has the required item to interact and has interacted with required objects
        if(this.itemRequired == None or this.itemRequired in list(inventory.keys())):
            if(this.interactRequire == None or this.interactRequire in interacted or interacted == set(["*"])):
                if(this.itemRequired in list(inventory.keys())):
                    if(inventory[this.itemRequired].destroyOnUse):
                        del inventory[this.itemRequired]
                global ended
                if(this.isEnding):
                    ended = True

                interacted.add(this.name)
                out = this.dialog
                if(this.giveItem != None):
                    inventory[this.giveItem.name] = this.giveItem
                    out += "\n\nYou have recieved: " + this.giveItem.name
                if(this.interactOnce):
                    del interactables[this.name]
            else:
                out = "Must have interacted with " + this.interactRequire + " to interact"
        else:
            out = "Must have " + this.itemRequired + " to interact"
        return out

def format(file):
    out = ""
    with open(file,"r") as f:
        out = f.read()
        strings = list(set([string.replace("#-#","'") for string in "\n".join(out.split("\n")[:-3]).replace("\\'","#-#").split("'")[1::2]]))
    for i, string in enumerate(strings):
        out = out.replace("'" + string + "'", "'" + string.split(" || ID: ")[0] + " || ID: ^^^" + f"{i:05d}" + "'")
    with open(file,"w") as f:
        f.write(out)

# i'm sorry for this code :(
def export(name, locations, characters, interactables, inventory, interacted, objective):

    # uhhh yeah idek where to begin to describe what is going on ¯\_(ツ)_/¯
    file = """begin_story(
    ["""
    for loc in locations:
        file += "\n        location(#-#" + loc + "#-#,#-#" + str(locations[loc].start) + "#-#,#-#" + str(locations[loc].onTravel) + "#-#,#-#" + str(locations[loc].itemRequired) + "#-#,#-#" + str(locations[loc].interactRequire) + "#-#,#-#" + str(locations[loc].cantReturn) + "#-#,#-#" + str(locations[loc].isEnding) + "#-#),"
    file += "\n    ],"
    
    file += "\n    ["
    for chr in characters:
        if characters[chr].giveItem:
            giveItem = "item(#-#" + characters[chr].giveItem.name + "#-#,#-#" + str(characters[chr].giveItem.info) + "#-#,#-#" + str(characters[chr].giveItem.onUse) + "#-#,#-#" + str(characters[chr].giveItem.interactRequire) + "#-#,#-#" + str(characters[chr].giveItem.destroyOnUse) + "#-#,#-#" + str(characters[chr].giveItem.isEnding) + "#-#)"
        else: giveItem = "None"
        file += "\n        character(#-#" + chr + "#-#,#-#" + str(characters[chr].dialog) + "#-#,#-#" + str(characters[chr].location) + "#-#," + giveItem + ",#-#" + str(characters[chr].itemRequired) + "#-#,#-#" + str(characters[chr].interactRequire) + "#-#,#-#" + str(characters[chr].interactOnce) + "#-#,#-#" + str(characters[chr].isEnding) + "#-#),"
    file += "\n    ],"

    file += "\n    ["
    for intr in interactables:
        if interactables[intr].giveItem:
            giveItem = "item(#-#" + interactables[intr].giveItem.name + "#-#,#-#" + str(interactables[intr].giveItem.info) + "#-#,#-#" + str(interactables[intr].giveItem.onUse) + "#-#,#-#" + str(interactables[intr].giveItem.interactRequire) + "#-#,#-#" + str(interactables[intr].giveItem.destroyOnUse) + "#-#,#-#" + str(interactables[intr].giveItem.isEnding) + "#-#)"
        else: giveItem = "None"
        file += "\n        interactable(#-#" + intr + "#-#,#-#" + str(interactables[intr].dialog) + "#-#,#-#" + str(interactables[intr].location) + "#-#," + giveItem + ",#-#" + str(interactables[intr].itemRequired) + "#-#,#-#" + str(interactables[intr].interactRequire) + "#-#,#-#" + str(interactables[intr].interactOnce) + "#-#,#-#" + str(interactables[intr].isEnding) + "#-#),"
    file += "\n    ],"

    file += "\n    ["
    for itm in inventory:
        file += "\n        item(#-#" + itm + "#-#,#-#" + str(inventory[itm].info) + "#-#,#-#" + str(inventory[itm].onUse) + "#-#,#-#" + str(inventory[itm].interactRequire) + "#-#,#-#" + str(inventory[itm].destroyOnUse) + "#-#,#-#" + str(inventory[itm].isEnding) + "#-#),"
    file += "\n    ],"

    file += "\n    set(["+("#-#"+"#-#,#-#".join(list(interacted))+"#-#")+"]),"

    file += "\n    #-#"+objective+"#-#"

    file += "\n)"

    file = file.replace("#-#None#-#","None")
    file = file.replace("#-#True#-#","True")
    file = file.replace("#-#False#-#","False")

    file = file.replace("'","\\'")

    file = file.replace("#-#","'")

    # Write the file (•_•)👍
    with open(name + ".story","w") as f:
        f.write(file)

    # Format the file with IDs
    format(name + ".story")

# Primary function of library used to initalize the story
def begin_story(name, locations, characters = [], interactables = [], inventory = [], interacted = set([]), objective = ""):
    # Global variables
    global width, height, ended

    ended = False

    # Make each list of classes into a dict for easier access
    locationsTemp = {}
    for loc in locations:
        locationsTemp[loc.name] = loc
    locations = locationsTemp.copy()

    inventoryTemp = {}
    for itm in inventory:
        inventoryTemp[itm.name] = itm
    inventory = inventoryTemp.copy()

    charactersTemp = {}
    for chr in characters:
        charactersTemp[chr.name] = chr
    characters = charactersTemp.copy()

    interactablesTemp = {}
    for intr in interactables:
        interactablesTemp[intr.name] = intr
    interactables = interactablesTemp.copy()

    # This will define the current dialog/message that is shown to the user
    userDisplay = objective

    # Get the current location from the back of the locations list, we use the back because it's easy to put any key at the back of a dict, this is helpful when exporting stories
    currentLoc = list(locations.keys())[-1]

    while True:
        # Get mouse pos
        menuText = pixelFont.render("MENU", False, (0, 0, 0))
        if ended:
            mouseX, mouseY = width-menuText.get_rect().width/2-20,height-menuText.get_rect().height/2-20
        else:
            mouseX, mouseY = pygame.mouse.get_pos()
        click = False

        # Reset screen
        screen.fill((255, 255, 255))

        # Check for exit and click events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h

        # Show the user display text

        # Split the text into lines if the text is to big or contains and escape character (escape characters cannot be proccessed by the text renderer)
        idSplit = userDisplay.split(" || ID: ")
        for i in range(len(idSplit)):
            if "^^^" in idSplit[i]:
                idSplit[i] = idSplit[i][8:]
        lines = "".join(idSplit).split("\n")
        for i, line in enumerate(lines):
            userDisplayText = pixelFont.render(line, False, (0, 0, 0))
            if(userDisplayText.get_rect().width > width):
                lines.remove(line)
                line = line.split()
                lines.insert(i," ".join(line[int(len(line)/2):]))
                lines.insert(i," ".join(line[:int(len(line)/2)]))
        
        # For each line, render it then offset it down for the next line
        for line in lines:
            userDisplayText = pixelFont.render(line, False, (0, 0, 0))
            blit_centered(userDisplayText,(width/2,height-userDisplayText.get_rect().height-fontSize-(len(lines)-lines.index(line)-1)*userDisplayText.get_rect().height))

        # Show the top text
        inventoryText = pixelFont.render("Inventory", False, (0, 0, 0))
        blit_centered(inventoryText,(width/4-width/8,fontSize))
        
        locationsText = pixelFont.render("Locations", False, (0, 0, 0))
        blit_centered(locationsText,((width/4)*2-width/8,fontSize))

        charactersText = pixelFont.render("Characters", False, (0, 0, 0))
        blit_centered(charactersText,((width/4)*3-width/8,fontSize))

        interactablesText = pixelFont.render("Interactables", False, (0, 0, 0))
        blit_centered(interactablesText,((width/4)*4-width/8,fontSize))

        # Get the visitable locations to display
        vistableLocations = list(locations.keys())
        for loc in locations:
            if not locations[loc].canTravel(currentLoc, locations):
                vistableLocations.pop(vistableLocations.index(loc))

        for loc in vistableLocations:
            tempText = pixelFont.render(loc.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*2-width/8,tempText.get_rect().height*(vistableLocations.index(loc)+2)))
            # Check if hovering if so display a box around text
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                # If the user clicks, then we will use logic to determine if the player should travel to the location
                if(click):
                    userDisplay, currentLoc = locations[loc].travel(locations, inventory, currentLoc, interacted)
        
        # List all items in inventory
        for itm in list(inventory.keys()):
            tempText = pixelFont.render(itm.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4-width/8,tempText.get_rect().height*(list(inventory.keys()).index(itm)+2)))
            # Check if the user is hovering, if so display a box around text and then show the tooltip thing
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)

                tempText = pixelFontSmall.render(inventory[itm].info.split(" || ID: ")[0], False, (0, 0, 0))
                tempBlit = screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))

                pygame.draw.rect(screen,(255, 255, 255),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height))
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height),3)

                screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))

                # If the user is clicking, use the item
                if(click):
                    userDisplay = inventory[itm].use(inventory, interacted)
        
        interactableCharacters = list(characters.keys())
        for chr in characters:
            if not characters[chr].canInteract(currentLoc):
                interactableCharacters.pop(interactableCharacters.index(chr))

        for chr in interactableCharacters:
            tempText = pixelFont.render(chr.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*3-width/8,tempText.get_rect().height*(interactableCharacters.index(chr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click and characters[chr].canInteract(currentLoc)):
                    userDisplay = characters[chr].interact(inventory, interacted, characters)

        interactableInteractables = list(interactables.keys())
        for intr in interactables:
            if not interactables[intr].canInteract(currentLoc):
                interactableInteractables.pop(interactableInteractables.index(intr))

        for intr in interactableInteractables:
            tempText = pixelFont.render(intr.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width-width/8,tempText.get_rect().height*(interactableInteractables.index(intr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    userDisplay = interactables[intr].interact(inventory, interacted, interactables)
        
        menuText = pixelFont.render("MENU", False, (0, 0, 0))

        tempBlit = screen.blit(menuText,(width-menuText.get_rect().width-20,height-menuText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                break

        saveText = pixelFont.render("SAVE", False, (0, 0, 0))

        tempBlit = screen.blit(saveText,(width-menuText.get_rect().width-saveText.get_rect().width-50,height-saveText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                locations[currentLoc] = locations.pop(currentLoc)
                export(name + " - SAVE", locations,characters,interactables,inventory,interacted,"")

        pygame.display.flip()
        fpsClock.tick(fps)

def level_select():
    global width, height
    global time
    while True:
        # Get mouse pos
        mouseX, mouseY = pygame.mouse.get_pos()
        click = False

        # Reset screen
        screen.fill((255, 255, 255))

        # Check for exit and click events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
                
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(".story")]
        for file in files:
            fileText = pixelFont.render(file[:-6], False, (0, 0, 0))
            tempBlit = blit_centered(fileText,(width/2,files.index(file)*fileText.get_rect().height+fontSize*3+15))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0), pygame.Rect(tempBlit.left-9,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    with open(file) as f:
                        exec(f.read().replace("begin_story(","begin_story('"+file[:-6]+"',"))
        
        playText = pixelFontBig.render("PLAY", False, (0, 0, 0))
        blit_centered(playText,(width/2,fontSize/3*4+math.sin(time)*5))

        backText = pixelFont.render("BACK", False, (0, 0, 0))

        tempBlit = screen.blit(backText,(width-backText.get_rect().width-20,height-backText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                break

        uploadText = pixelFont.render("UPLOAD", False, (0, 0, 0))
        tempBlit = blit_centered(uploadText,(width/2,height-fontSize))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                file = askopenfilename(filetypes=[("Story files",".story")])
                if file:
                    contents = ""
                    with open(file) as f:
                        contents = f.read()
                    with open(file.split("/")[-1],"w") as f:
                        f.write(contents)

        pygame.display.flip()
        fpsClock.tick(fps)

        time += 0.07

def build_select():
    global width, height
    global time

    newInput = InputBox(0,0,200,50,"Name",width=5)

    while True:
        # Get mouse pos
        mouseX, mouseY = pygame.mouse.get_pos()
        click = False

        # Reset screen
        screen.fill((255, 255, 255))

        # Check for exit and click events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
            newInput.handle_event(event)
                
        files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith(".story")]
        for file in files:
            fileText = pixelFont.render(file[:-6], False, (0, 0, 0))
            tempBlit = blit_centered(fileText,(width/3,files.index(file)*fileText.get_rect().height+fontSize*3+15))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0), pygame.Rect(tempBlit.left-9,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    with open(file) as f:
                        exec(f.read().replace("begin_story(","story_builder(\'"+file[:-6]+"\',"))
        
        editText = pixelFontBig.render("EDIT", False, (0, 0, 0))
        blit_centered(editText,(width/3,fontSize/3*4+math.sin(time)*5))

        newText = pixelFontBig.render("NEW", False, (0, 0, 0))
        blit_centered(newText,(width/3*2,fontSize/3*4+math.sin(time)*5))

        tempText = pixelFont.render("+", False, (0, 0, 0))
        tempBlit = blit_centered(tempText,(width/3*2-98,fontSize/3*4+99))
        pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-12,tempBlit.top+6,50,50),5)

        if(click and tempBlit.collidepoint(mouseX,mouseY)):
            story_builder(newInput.text)

        newInput.rect.x = width/3*2-80
        newInput.rect.y = fontSize/3*4+75
        newInput.draw(screen)

        backText = pixelFont.render("BACK", False, (0, 0, 0))

        tempBlit = screen.blit(backText,(width-backText.get_rect().width-20,height-backText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                break

        uploadText = pixelFont.render("UPLOAD", False, (0, 0, 0))
        tempBlit = blit_centered(uploadText,(width/2,height-fontSize))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                file = askopenfilename(filetypes=[("Story files",".story")])
                if file:
                    contents = ""
                    with open(file) as f:
                        contents = f.read()
                    with open(file.split("/")[-1],"w") as f:
                        f.write(contents)

        pygame.display.flip()
        fpsClock.tick(fps)

        time += 0.07
    
def story_builder(name, locations = [location("default","NO START")], characters = [], interactables = [], inventory = [], interacted = set([]), objective = ""):
    global width, height, ended
    locationsTemp = {}
    for loc in locations:
        locationsTemp[loc.name] = loc
    locations = locationsTemp.copy()

    inventoryTemp = {}
    for itm in inventory:
        inventoryTemp[itm.name] = itm
    inventory = inventoryTemp.copy()

    charactersTemp = {}
    for chr in characters:
        charactersTemp[chr.name] = chr
    characters = charactersTemp.copy()

    interactablesTemp = {}
    for intr in interactables:
        interactablesTemp[intr.name] = intr
    interactables = interactablesTemp.copy()

    # This will define the current dialog/message that is shown to the user
    userDisplay = ""

    currentLoc = list(locations.keys())[-1]

    inputs = []
    itemInputs = []
    selection = 0

    while True:
        # Get mouse pos
        mouseX, mouseY = pygame.mouse.get_pos()
        click = False
        rightClick = False

        # Reset screen
        screen.fill((255, 255, 255))

        # Check for exit and click events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                if event.button == 3:
                    rightClick = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
            for inputObj in inputs:
                inputObj.handle_event(event)
            if len(itemInputs) != 0:
                for inputObj in itemInputs:
                    inputObj.handle_event(event)

        selections = [pixelFontSmall.render("Location",False,(0,0,0)),pixelFontSmall.render("Item",False,(0,0,0)),pixelFontSmall.render("Character",False,(0,0,0)),pixelFontSmall.render("Interactable",False,(0,0,0))]
        tempBlit = screen.blit(selections[selection],(0,height-selections[selection].get_rect().height))
        if(tempBlit.collidepoint(mouseX,mouseY)):
            pygame.draw.rect(screen,(0,0,0),tempBlit,2)
            if(click):
                selection = (selection+1) % (len(selections))
                # 0 - Location
                # 1 - Item
                # 2/3 - Character / Interactable
                match selection:
                    case 0:
                        inputs = [InputBox(0,0,200,50,"Name"),InputBox(0,0,200,50,"Dialog"),InputBox(0,0,200,50,"Item Required"),InputBox(0,0,200,50,"Interaction Required"),CheckBox(0,0,"Cant Return"),CheckBox(0,0,"Is Ending")]
                    case 1:
                        inputs = [InputBox(0,0,200,50,"Name"),InputBox(0,0,200,50,"Info"),InputBox(0,0,200,50,"On Use"),InputBox(0,0,200,50,"Interaction Required"),CheckBox(0,0,"Use Once"),CheckBox(0,0,"Is Ending")]
                    case 2 | 3:
                        inputs = [InputBox(0,0,200,50,"Name"),InputBox(0,0,200,50,"Dialog"),InputBox(0,0,200,50,"Item Required"),InputBox(0,0,200,50,"Interaction Required"),CheckBox(0,0,"Interact Once"),CheckBox(0,0,"Give Item"),CheckBox(0,0,"Is Ending")]
                        itemInputs = [InputBox(0,0,200,50,"Name"),InputBox(0,0,200,50,"Info"),InputBox(0,0,200,50,"On Use"),InputBox(0,0,200,50,"Interaction Required"),CheckBox(0,0,"Use Once"),CheckBox(0,0,"Is Ending")]

        offset = -tempBlit.height

        match selection:
            case 2 | 3:
                if(inputs[5].state):
                    for index, inputObj in enumerate(itemInputs):
                        inputObj.rect.y = height-(len(itemInputs)-index)*inputObj.rect.h-tempBlit.height
                        inputObj.draw(screen)
                        tempText = pixelFontSmall.render("Item",False,(0,0,0))
                        tempBlit = screen.blit(tempText,(0,height-tempBlit.height*(len(itemInputs)+3.7)))
                        offset = -len(itemInputs)*inputObj.rect.h-tempBlit.height*2
        for index, inputObj in enumerate(inputs):
            inputObj.rect.y = height-(len(inputs)-index)*inputObj.rect.h+offset
            inputObj.draw(screen)
            
        tempText = pixelFont.render("+", False, (0, 0, 0))
        tempBlit = blit_centered(tempText,(tempText.get_rect().width+3,height-len(inputs)*50-tempText.get_rect().height/2+offset))
        pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-18,tempBlit.top,tempBlit.height,tempBlit.height),5)

        if(tempBlit.collidepoint(mouseX,mouseY) and click):
            match selection:
                case 0:
                    locations[inputs[0].text] = location(
                        inputs[0].text,
                        currentLoc,
                        inputs[1].text if inputs[1].text else None,
                        inputs[2].text if inputs[2].text else None,
                        inputs[3].text if inputs[3].text else None,
                        inputs[4].state,
                        inputs[5].state
                    )
                case 1:
                    inventory[inputs[0].text] = item(
                        inputs[0].text,
                        inputs[1].text,
                        inputs[2].text if inputs[2].text else None,
                        inputs[3].text if inputs[3].text else None,
                        inputs[4].state,
                        inputs[5].state,
                    )
                case 2:
                    characters[inputs[0].text] = character(
                        inputs[0].text,
                        inputs[1].text,
                        currentLoc,
                        item(
                            itemInputs[0].text,
                            itemInputs[1].text,
                            itemInputs[2].text if itemInputs[2].text else None,
                            itemInputs[3].text if itemInputs[3].text else None,
                            itemInputs[4].state,
                            itemInputs[5].state
                        ) if inputs[5].state else None,
                        inputs[2].text if inputs[2].text else None,
                        inputs[3].text if inputs[3].text else None,
                        inputs[4].state,
                        inputs[6].state
                    )
                case 3:
                    interactables[inputs[0].text] = interactable(
                        inputs[0].text,
                        inputs[1].text,
                        currentLoc,
                        item(
                            itemInputs[0].text,
                            itemInputs[1].text,
                            itemInputs[2].text if itemInputs[2].text else None,
                            itemInputs[3].text if itemInputs[3].text else None,
                            itemInputs[4].state,
                            itemInputs[5].state
                        ) if inputs[5].state else None,
                        inputs[2].text if inputs[2].text else None,
                        inputs[3].text if inputs[3].text else None,
                        inputs[4].state,
                        inputs[6].state
                    )

        # Show the user display text
        idSplit = userDisplay.split(" || ID: ")
        for i in range(len(idSplit)):
            if "^^^" in idSplit[i]:
                idSplit[i] = idSplit[i][8:]
        lines = "".join(idSplit).split("\n")
        for i, line in enumerate(lines):
            userDisplayText = pixelFont.render(line, False, (0, 0, 0))
            if(userDisplayText.get_rect().width > width):
                lines.remove(line)
                line = line.split()
                lines.insert(i," ".join(line[int(len(line)/2):]))
                lines.insert(i," ".join(line[:int(len(line)/2)]))
        
        for line in lines:
            userDisplayText = pixelFont.render(line, False, (0, 0, 0))
            blit_centered(userDisplayText,(width/2,height-userDisplayText.get_rect().height-fontSize-(len(lines)-lines.index(line)-1)*userDisplayText.get_rect().height))

        # Show the top text
        inventoryText = pixelFont.render("Inventory", False, (0, 0, 0))
        blit_centered(inventoryText,(width/4-width/8,fontSize))
        
        locationsText = pixelFont.render("Locations", False, (0, 0, 0))
        blit_centered(locationsText,((width/4)*2-width/8,fontSize))

        charactersText = pixelFont.render("Characters", False, (0, 0, 0))
        blit_centered(charactersText,((width/4)*3-width/8,fontSize))

        interactablesText = pixelFont.render("Interactables", False, (0, 0, 0))
        blit_centered(interactablesText,((width/4)*4-width/8,fontSize))

        vistableLocations = list(locations.keys())
        for loc in locations:
            if not locations[loc].canTravel(currentLoc, locations):
                vistableLocations.pop(vistableLocations.index(loc))

        for loc in vistableLocations:
            tempText = pixelFont.render(loc.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*2-width/8,tempText.get_rect().height*(vistableLocations.index(loc)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    userDisplay, currentLoc = locations[loc].travel(locations, inventory, currentLoc, set(["*"]))
                if(rightClick):
                    del locations[loc]
                    rightClick = False

        for itm in list(inventory.keys()):
            tempText = pixelFont.render(itm.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4-width/8,tempText.get_rect().height*(list(inventory.keys()).index(itm)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                tempText = pixelFontSmall.render(inventory[itm].info.split(" || ID: ")[0], False, (0, 0, 0))
                tempBlit = screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))
                pygame.draw.rect(screen,(255, 255, 255),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height))
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height),3)
                screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))
                if(click):
                    userDisplay = inventory[itm].use(inventory, set(["*"]))
                if(rightClick):
                    del inventory[itm]
                    rightClick = False
        
        interactableCharacters = list(characters.keys())
        for chr in characters:
            if not characters[chr].canInteract(currentLoc):
                interactableCharacters.pop(interactableCharacters.index(chr))

        for chr in interactableCharacters:
            tempText = pixelFont.render(chr.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*3-width/8,tempText.get_rect().height*(interactableCharacters.index(chr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    userDisplay = characters[chr].interact(inventory, set(["*"]), characters)
                if(rightClick):
                    del characters[chr]
                    rightClick = False

        interactableInteractables = list(interactables.keys())
        for intr in interactables:
            if not interactables[intr].canInteract(currentLoc):
                interactableInteractables.pop(interactableInteractables.index(intr))

        for intr in interactableInteractables:
            tempText = pixelFont.render(intr.split(" || ID: ")[0], False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width-width/8,tempText.get_rect().height*(interactableInteractables.index(intr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    userDisplay = interactables[intr].interact(inventory, set(["*"]), interactables)
                if(rightClick):
                    del interactables[intr]
                    rightClick = False

        menuText = pixelFont.render("MENU", False, (0, 0, 0))

        tempBlit = screen.blit(menuText,(width-menuText.get_rect().width-20,height-menuText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                break

        saveText = pixelFont.render("SAVE", False, (0, 0, 0))

        tempBlit = screen.blit(saveText,(width-menuText.get_rect().width-saveText.get_rect().width-50,height-saveText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                locations[currentLoc] = locations.pop(currentLoc)
                export(name, locations,characters,interactables,inventory,set([]),"")

        pygame.display.flip()
        fpsClock.tick(fps)

def main_menu():
    global width, height
    global time
    while True:
        # Get mouse pos
        mouseX, mouseY = pygame.mouse.get_pos()
        click = False

        # Reset screen
        screen.fill((255, 255, 255))

        # Check for exit and click events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
        
        menuTextLine1 = pixelFontBig.render("STORY", False, (0, 0, 0))
        menuTextLine2 = pixelFontBig.render("BUILDER", False, (0, 0, 0))

        blit_centered(menuTextLine1, (width/2, height/6+math.sin(time)*5))
        blit_centered(menuTextLine2, (width/2, height/6+menuTextLine1.get_rect().height+math.sin(time)*5))

        playText = pixelFont.render("PLAY", False, (0, 0, 0))

        tempBlit = blit_centered(playText,(int(width/2),height/6+fontSize*5))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                level_select()
        
        storyBuilderText = pixelFont.render("BUILD", False, (0, 0, 0))

        tempBlit = blit_centered(storyBuilderText,(int(width/2),height/3+fontSize*5))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                build_select()

        pygame.display.flip()
        fpsClock.tick(fps)

        time += 0.07
main_menu()
