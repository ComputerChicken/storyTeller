# Dependencies
import sys
import pygame
from pygame.locals import *
import os
import math
import random
from tkinter import Tk     # tkinter for file management
from tkinter.filedialog import askopenfilename

Tk().withdraw()


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

# This class allows me to easily create multiple inputs for the level builder
class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = (255, 255, 255)
        self.text = text
        self.txt_surface = pixelFontSmall.render(text, True, (0, 0, 0))
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

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the rects.
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 2)
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))

# A function for blitting objects (specifically text) to a center position
def blit_centered(source,pos):
    # Will return the blit object for later use
    return screen.blit(source,(pos[0]-source.get_rect().width/2,pos[1]-source.get_rect().height/2))

# The following classes are the classes for the game elements
class location:
    def __init__(this, name, start=None, onTravel=None, itemRequired=None):
        this.name = name
        this.start = start
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
        
class item:
    def __init__(this, name, info, onUse=None, destroyOnUse=False):
        this.name = name
        this.info = info
        this.onUse = onUse
        this.destroyOnUse = destroyOnUse

    # Use an item (displays use text)
    def use(this, inventory):
        if(this.onUse == None):
            return "This item cannot be used"
        out = this.onUse
        if(this.destroyOnUse):
            del inventory[this.name]
        return out

class character:
    def __init__(this, name, dialog, location, giveItem = None, itemRequired = None, interactOnce = False):
        this.name = name
        this.dialog = dialog
        this.giveItem = giveItem
        this.itemRequired = itemRequired
        this.location = location
        this.interactOnce = interactOnce
    
    def canInteract(this, current):
        if(current == this.location):
            return True
        else:
            return False

    def interact(this, inventory, characters):
        if(this.itemRequired == None or this.itemRequired in list(inventory.keys())):
            out = this.dialog
            if(this.giveItem != None):
                inventory[this.giveItem.name] = this.giveItem
                out += "\n\nYou have recieved: " + this.giveItem.name
            if(this.interactOnce):
                del characters[this.name]
        else:
            out = "Must have " + this.itemRequired + " to interact"
        return out

# The interactable class is very similar to the player class
class interactable:
    def __init__(this, name, dialog, location, giveItem = None, itemRequired = None, interactOnce = False):
        this.name = name
        this.dialog = dialog
        this.giveItem = giveItem
        this.itemRequired = itemRequired
        this.location = location
        this.interactOnce = interactOnce
    
    def canInteract(this, current):
        if(current == this.location):
            return True
        else:
            return False

    def interact(this, inventory, interactables):
        if(this.itemRequired == None or this.itemRequired in list(inventory.keys())):
            out = this.dialog
            if(this.giveItem != None):
                inventory[this.giveItem.name] = this.giveItem
                out += "\n\nYou have recieved: " + this.giveItem.name
            if(this.interactOnce):
                del interactables[this.name]
        else:
            out = "Must have " + this.itemRequired + " to interact"
        return out

# Primary function of library used to initalize the story
def begin_story(locations, characters = [], interactables = [], inventory = []):
    global width, height
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

    currentLoc = list(locations.keys())[0]
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
            if event.type == pygame.MOUSEBUTTONUP:
                click = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h

        # Show the user display text
        lines = userDisplay.split("\n")
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
            tempText = pixelFont.render(loc, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*2-width/8,tempText.get_rect().height*(vistableLocations.index(loc)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    target = loc
                    if locations[target].canTravel(currentLoc, locations):
                        if(locations[target].hasItem(inventory)):
                            currentLoc = target
                            if(locations[target].onTravel != None):
                                userDisplay = locations[target].onTravel
                        else:
                            userDisplay = "Missing item: " + locations[target].itemRequired
        
        for itm in list(inventory.keys()):
            tempText = pixelFont.render(itm, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4-width/8,tempText.get_rect().height*(list(inventory.keys()).index(itm)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                tempText = pixelFontSmall.render(inventory[itm].info, False, (0, 0, 0))
                tempBlit = screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))
                pygame.draw.rect(screen,(255, 255, 255),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height))
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height),3)
                screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))
                if(click):
                    userDisplay = inventory[itm].use(inventory)
        
        interactableCharacters = list(characters.keys())
        for chr in characters:
            if not characters[chr].canInteract(currentLoc):
                interactableCharacters.pop(interactableCharacters.index(chr))

        for chr in interactableCharacters:
            tempText = pixelFont.render(chr, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*3-width/8,tempText.get_rect().height*(interactableCharacters.index(chr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click and characters[chr].canInteract(currentLoc)):
                    userDisplay = characters[chr].interact(inventory, characters)

        interactableInteractables = list(interactables.keys())
        for intr in interactables:
            if not interactables[intr].canInteract(currentLoc):
                interactableInteractables.pop(interactableInteractables.index(intr))

        for intr in interactableInteractables:
            tempText = pixelFont.render(intr, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width-width/8,tempText.get_rect().height*(interactableInteractables.index(intr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    userDisplay = interactables[intr].interact(inventory, interactables)
        
        menuText = pixelFont.render("MENU", False, (0, 0, 0))

        tempBlit = screen.blit(menuText,(width-menuText.get_rect().width-20,height-menuText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                break

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
            if event.type == pygame.MOUSEBUTTONUP:
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
                        exec(f.read())
        
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
    
def story_builder(locations = [location("default","NO START")], characters = [], interactables = [], inventory = []):
    global width, height
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

    currentLoc = list(locations.keys())[0]

    inputs = [InputBox(width/2,height/2-75,200,50,"Name"),InputBox(width/2,height/2-25,200,50,"Start"),InputBox(width/2,height/2+25,200,50,"Dialog"),InputBox(width/2,height/2+75,200,50,"Item Required")]

    while True:
        # Get mouse pos
        mouseX, mouseY = pygame.mouse.get_pos()
        click = False

        # Reset screen
        screen.fill((255, 255, 255))

        for inputObj in inputs:
            inputObj.draw(screen)
            inputObj.update()

        # Check for exit and click events
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONUP:
                click = True
            if event.type == pygame.VIDEORESIZE:
                width = event.w
                height = event.h
            for inputObj in inputs:
                inputObj.handle_event(event)

        # Show the user display text
        lines = userDisplay.split("\n")
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
            tempText = pixelFont.render(loc, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*2-width/8,tempText.get_rect().height*(vistableLocations.index(loc)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    target = loc
                    if locations[target].canTravel(currentLoc, locations):
                        if(locations[target].hasItem(inventory)):
                            currentLoc = target
                            if(locations[target].onTravel != None):
                                userDisplay = locations[target].onTravel
                        else:
                            userDisplay = "Missing item: " + locations[target].itemRequired
        tempText = pixelFont.render("+", False, (0, 0, 0))
        tempBlit = blit_centered(tempText,(width/4*2-width/8,tempText.get_rect().height*(len(vistableLocations)+2)))
        pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-18,tempBlit.top,tempBlit.height,tempBlit.height),5)

        if(tempBlit.collidepoint(mouseX,mouseY) and click):
            print(locations)
            locations[inputs[0].text] = location(inputs[0].text,inputs[1].text if inputs[1].text else None,inputs[2].text if inputs[2].text else None,inputs[3].text if inputs[3].text else None)

        for itm in list(inventory.keys()):
            tempText = pixelFont.render(itm, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4-width/8,tempText.get_rect().height*(list(inventory.keys()).index(itm)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                tempText = pixelFontSmall.render(inventory[itm].info, False, (0, 0, 0))
                tempBlit = screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))
                pygame.draw.rect(screen,(255, 255, 255),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height))
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-6,tempBlit.top,tempBlit.width+8,tempBlit.height),3)
                screen.blit(tempText,(mouseX,mouseY-tempText.get_rect().height))
                if(click):
                    userDisplay = inventory[itm].use(inventory)
        tempText = pixelFont.render("+", False, (0, 0, 0))
        tempBlit = blit_centered(tempText,(width/4-width/8,tempText.get_rect().height*(len(list(inventory.keys()))+2)))
        pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-18,tempBlit.top,tempBlit.height,tempBlit.height),5)
        
        interactableCharacters = list(characters.keys())
        for chr in characters:
            if not characters[chr].canInteract(currentLoc):
                interactableCharacters.pop(interactableCharacters.index(chr))

        for chr in interactableCharacters:
            tempText = pixelFont.render(chr, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width/4*3-width/8,tempText.get_rect().height*(interactableCharacters.index(chr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click and characters[chr].canInteract(currentLoc)):
                    userDisplay = characters[chr].interact(inventory, characters)
        tempText = pixelFont.render("+", False, (0, 0, 0))
        tempBlit = blit_centered(tempText,(width/4*3-width/8,tempText.get_rect().height*(len(interactableCharacters)+2)))
        pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-18,tempBlit.top,tempBlit.height,tempBlit.height),5)

        interactableInteractables = list(interactables.keys())
        for intr in interactables:
            if not interactables[intr].canInteract(currentLoc):
                interactableInteractables.pop(interactableInteractables.index(intr))

        for intr in interactableInteractables:
            tempText = pixelFont.render(intr, False, (0, 0, 0))
            tempBlit = blit_centered(tempText,(width-width/8,tempText.get_rect().height*(interactableInteractables.index(intr)+2)))
            if(tempBlit.collidepoint(mouseX,mouseY)):
                pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+13,tempBlit.height),5)
                if(click):
                    userDisplay = interactables[intr].interact(inventory, interactables)
        tempText = pixelFont.render("+", False, (0, 0, 0))
        tempBlit = blit_centered(tempText,(width-width/8,tempText.get_rect().height*(len(interactableInteractables)+2)))
        pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-18,tempBlit.top,tempBlit.height,tempBlit.height),5)

        menuText = pixelFont.render("MENU", False, (0, 0, 0))

        tempBlit = screen.blit(menuText,(width-menuText.get_rect().width-20,height-menuText.get_rect().height-20))
        if tempBlit.collidepoint(mouseX,mouseY):
            pygame.draw.rect(screen,(0, 0, 0),pygame.Rect(tempBlit.left-10,tempBlit.top,tempBlit.width+14,tempBlit.height),5)
            if(click):
                break

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
            if event.type == pygame.MOUSEBUTTONUP:
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
                story_builder()

        pygame.display.flip()
        fpsClock.tick(fps)

        time += 0.07  

main_menu()
