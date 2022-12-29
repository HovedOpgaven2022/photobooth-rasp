import json

import pygame, sys
import pygame.camera
import requests
from pygame.locals import *
from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess

# init pygame, display and window
pygame.init()
pygame.display.set_caption('PhotoMaster')
monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]

screen = pygame.display.set_mode((monitor_size), pygame.FULLSCREEN)

# setting up api for pushing images
cloudinary_url = "https://api.cloudinary.com/v1_1/disswjmhm/image/upload"
api_url = "http://185.51.76.204:8090/api/"

# init pygame camera module
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0",(800,530))
cam.start()

# init states
menuStates = ("startMenu","partyMenu","barMenu")
currentState = menuStates[0]

# init favicon and various other images
bg_image = pygame.image.load('resources/bg.png')

# init gphoto variables
shot_date = datetime.now().strftime("%Y-%m-%d")
shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
picID = "SelfieShots"
clearCommand = ["--folder", "/store_00020001/DCIM/100CANON", 
                "-R",  "--delete-all-files"]
triggerCommand = ["--trigger-capture"]
downloadCommand = ["--get-all-files"]

folder_name = shot_date + picID
save_location = "/home/pi/Desktop/PhotoMaster/images/" + folder_name

                    
# method for rendering the main menu based on the menu state
# and its including logic
def mainMenu():
    running = True
    currentStates = menuStates[1]
    if(pygame.mouse.get_visible()):
        pygame.mouse.set_visible(False)
    if(currentStates == menuStates[1]):
        while running:
            image = cam.get_image()
            screen.blit(bg_image, (0,0))
            screen.blit(image, (0,0))
            pygame.display.update()
        
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    if event.key == K_k:
                        captureImage()
                          
                
         
def killgphoto2process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    
    # Search for the Process to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            #kill the process
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)


def createSaveFolder():
    try:
        os.makedirs(save_location)
    except:
        print("Failed to create new directory.")
        os.chdir(save_location)

def captureImages():
    gp(triggerCommand)
    sleep(2)
    gp(downloadCommand)
    
def renameFiles(ID):
    shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for filename in os.listdir("."):
        if len (filename) < 13:
            if filename.endswith(".JPG"):
                os.rename(filename, (shot_time + ID + ".JPG"))
                print ("renamed the JPG")
            elif filename.endswith(".CR2"):
                os.rename(filename, (shot_time + ID + ".CR2"))
                print ("renamed the CR2")

def push_image_to_db(image_url):
    api = api_url + "Photo/UploadPhoto"
    headers = {"Content-Type": "application/json"}
    res = requests.post(api, json={"url": str(image_url)}, headers=headers)

def push_image():
    file = save_location + "/" + shot_time + picID + ".JPG"
    data = {"upload_preset":"photobooth"}
    files = {"file": open(file, "rb")}
    response = requests.post(cloudinary_url, data=data, files=files).text
    response = json.loads(response)

    image_url = response["url"]
    push_image_to_db(image_url)

def captureImage():
    killgphoto2process()
    gp(clearCommand)
    createSaveFolder()
    captureImages()
    renameFiles(picID)
    push_image()


if __name__ == '__main__':
    
    print(monitor_size)
    # Kill the Gphoto Process which starts when you connect the camera
    # and occupies the usb
    killgphoto2process()
    
    # Start the main menu based on the menu state
    mainMenu()
    
    # if you break from any of the menuStates close the program
    sys.exit()