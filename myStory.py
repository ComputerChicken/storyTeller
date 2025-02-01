from storyTeller import *

begin_story(
    [
        location("Home","NO START","Home Sweet Home"),
        location("Closet","Home","Just a small closet with a few items in it"),
        location("Kitchen","Home","Gonna make some food?"),
        location("Garage","Home","Your see your car parked"),
        location("Front Yard","Home","You're standing on your lawn, congratulations!"),
        location("Living Room","Home","You sit down on the couch in your living room."),
        location("Car", "Garage", "Your sitting in your car"),
        location("Park", "Car", "It's a beautiful day to visit the park"),
        location("Mysterious Cave","Park","You enter the mysterious cave and see darkness"),
        location("Left Cave Tunnel","Mysterious Cave","You enter the narrow cave tunnel with your flashlight in hand but it appears to be a dead-end","Flashlight"),
        location("Center Cave Tunnel","Mysterious Cave","You enter the narrow cave tunnel with your flashlight in hand but it appears to be a dead-end","Flashlight"),
        location("Right Cave Tunnel","Mysterious Cave","You enter the narrow cave tunnel with your flashlight in hand wondering what's ahead","Flashlight"),
        location("Strange Room","Right Cave Tunnel","You open an oddly-placed heavy steel door at the end of the tunnel to see what appears to be an old bunker"),
    ],
    [
        character("Old Man","The strange old man standind by the cave enterance says: \"I wouldn't travel any further into that cave if I were you\"","Mysterious Cave",item("Map","The map shows the layout of the cave. It shows 2 dead-ends on the left and center paths, and a clear path on the right"),interactOnce=True)
    ],
    [
        interactable("Flashlight","","Closet",item("Flashlight","It's a flashlight","You click the button on the flashlight and toggle it"),interactOnce=True),
        interactable("Slide","You went down the slide","Park"),
        interactable("Rock","You pick up a medium sized rock from the cave floor","Mysterious Cave",item("Rock","A medium cave rock","You throw the rock, never to be seen again",True)),
        interactable("Couch","You look under the couch cushions to try and find anything interesting, you manage to find a key","Strange Room",item("Key","A key to something")),
        interactable("Safe","You open the safe and find a gold bar!","Strange Room",item("Gold Bar","A 10-pound gold bar, you are now very rich"),"Key"),
        interactable("Cabinet","You open your kitchen cabinet to see a feel chips, among other snacks. You take a snack from the cabinet","Kitchen",item("Snack","A small bag of chips","You have consumed the snack",True)),
        interactable("Remote","You click the power button on the remote and turn on the TV","Living Room"),
    ]
)