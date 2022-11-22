from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess

def killgphoto2process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()
    
    # Search for the Process to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            #kill the process
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)


shot_date = datetime.now().strftime("%Y-%m-%d")
shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
picID = "SelfieShots"
clearCommand = ["--folder", "/store_00020001/DCIM/100CANON", 
                "-R",  "--delete-all-files"]
triggerCommand = ["--trigger-capture"]
downloadCommand = ["--get-all-files"]

folder_name = shot_date + picID
save_location = "/home/pi/Desktop/PhotoMaster/images/" + folder_name

def createSaveFolder():
    try:
        os.makedirs(save_location)
    except:
        print("Failed to create new directory.")
        os.chdir(save_location)

def captureImages():
    gp(triggerCommand)
    sleep(10)
    gp(downloadCommand)
    
def renameFiles(ID):
    for filename in os.listdir("."):
        if len (filename) < 13:
            if filename.endswith(".JPG"):
                os.rename(filename, (shot_time + ID + ".JPG"))
                print ("renamed the JPG")
            elif filename.endswith(".CR2"):
                os.rename(filename, (shot_time + ID + ".CR2"))
                print ("renamed the CR2")

killgphoto2process()
gp(clearCommand)
createSaveFolder()
captureImages()
renameFiles(picID)
