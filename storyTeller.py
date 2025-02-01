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
        print(this.onUse)
        if(this.destroyOnUse):
            del inventory[this.name]

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
            print(this.dialog)
            if(this.giveItem != None):
                inventory[this.giveItem.name] = this.giveItem
                print("You have recieved: " + this.giveItem.name)
            if(this.interactOnce):
                del characters[this.name]
        else:
            print("Must have " + this.itemRequired + " to interact")

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
            print(this.dialog)
            if(this.giveItem != None):
                inventory[this.giveItem.name] = this.giveItem
                print("You have recieved: " + this.giveItem.name)
            if(this.interactOnce):
                del interactables[this.name]
        else:
            print("Must have " + this.itemRequired + " to interact")

# Primary function of library used to initalize the story
def begin_story(locations, characters = [], interactables = [], inventory = []):
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

    currentLoc = list(locations.keys())[0]
    inp = ""
    while inp != "stop":
        print("\nCurrent Location: " + currentLoc)
        inp = input("What would like to do: ")
        print()

        # Display possible commands
        if inp == "help":
            print("Type \"list all\" lo list all locations, characters, and interactables")
            print("Type \"list locations\" to list all available locations")
            print("Type \"inventory\" to list all items in inventory")
            print("Type \"list characters\" to list all characters you can interact with")
            print("Type \"list interactables\" to list all interactables you can interact with")
            print("To see information about an item type \"info [item name]\"")
            print("To use an item (if possible) type \"use [item name]\"")
            print("To visit a location type \"travel [location name]\"")
            print("To interact with a character type \"character [character name]\"")
            print("To interact with an interactable type \"interact [interactable name]\"")

            print("Type stop to stop the game")
        
        # Check for commands shown above
        if inp == "list locations":
            for loc in locations.values():
                if loc.canTravel(currentLoc,locations):
                    print(loc.name)

        if "travel" in inp[:6]:
            try:
                target = " ".join(inp.split()[1:])
                if locations[target].canTravel(currentLoc, locations):
                    if(locations[target].hasItem(inventory)):
                        currentLoc = target
                        if(locations[target].onTravel != None):
                            print(locations[target].onTravel)
                    else:
                        print("Missing item: " + locations[target].itemRequired)
                else:
                    print("Invalid Selection")
            except KeyError:
                print("Invalid Selection")
        
        if inp == "inventory":
            for itm in inventory.keys():
                print(itm)

        if "info" in inp[:4]:
            try:
                print(inventory[" ".join(inp.split()[1:])].info)
            except KeyError:
                print("Invalid Selection")
        
        if "use" in inp[:3]:
            try:
                itm = inventory[" ".join(inp.split()[1:])]
                if(itm.onUse != None):
                    itm.use(inventory)
                else:
                    print("This item cannot be used")
            except KeyError:
                print("Invalid Selection")
        
        if "list characters" == inp:
            for chr in characters.values():
                if(chr.canInteract(currentLoc)):
                    print(chr.name)

        if "character" in inp[:9]:
            try:
                target = characters[" ".join(inp.split()[1:])]
                if(target.canInteract(currentLoc)):
                    target.interact(inventory,characters)
            except KeyError:
                print("Invalid Selection")
        
        if "list interactables" == inp:
            for int in interactables.values():
                if(int.canInteract(currentLoc)):
                    print(intr.name)

        if "interact" in inp[:8]:
            try:
                target = interactables[" ".join(inp.split()[1:])]
                if(target.canInteract(currentLoc)):
                    target.interact(inventory,interactables)
            except KeyError:
                print("Invalid Selection")
        
        if "list all" == inp:
            # Locations
            print("Locations:")
            for loc in locations.values():
                if loc.canTravel(currentLoc,locations):
                    print(loc.name)
            
            print("\nCharacters:")
            for chr in characters.values():
                if(chr.canInteract(currentLoc)):
                    print(chr.name)
            
            print("\nInteractables:")
            for int in interactables.values():
                if(int.canInteract(currentLoc)):
                    print(int.name)
    
    print("Thank you for playing!")