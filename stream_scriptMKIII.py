import numpy as np
import cv2
import time
import datetime
import json
import pathlib
import subprocess

def get_hour():
    """
    returns the current hour only
    """
    current = datetime.datetime.now().time() #creates a datetime now object
    hr = int(current.hour) # collects and integerizes the hour object
    return hr

def in_time():
    start = 8
    end = 22
    hr = get_hour()
    return start < hr < end

framecount = 0
prevMillis = 0

def fpsCount():
    global prevMillis
    global framecount
    millis = int(round(time.time() * 1000))
    framecount += 1
    if millis - prevMillis > 1000:
        print(framecount)
        prevMillis = millis 
        framecount = 0

while(True): # forever loop - planning to always running 
    
    x = datetime.datetime.now()
    datestr = str(x.date())
    start = str(x.time())
    
    if in_time(): 
        
        # cv2 to create camera object
        cameraNumber = 0
        cap = cv2.VideoCapture()
        cap.open(cameraNumber + cv2.CAP_DSHOW)
        
        # delay before setting up camera parameters
        time.sleep(1)
        
        # set to 4K 4096 x 2160 (not currently possible), 30fps
        
        fps = 30
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # have to set codec before resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        size = (int(cap.get(3)), int(cap.get(4)))

        video_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
        
        result = cv2.VideoWriter(video_file_path, 
                             cv2.VideoWriter_fourcc(*'MJPG'), # fourcc is how openCV find # MJPG is the codec
                             20, size) # 20 appears to be the max fps when using openCV
        
        frame_n = 0 # frame counter 
        
        while(True): 
            frame_n += 1
            ret, frame = cap.read()
            result.write(frame)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if in_time()==False:
                break
            
        
        # stop writing and release after 23
        
        cap.release()
        result.release()
        cv2.destroyAllWindows()
        
        print('end recording')
        
        end = str(datetime.datetime.now().time())
        
        # save accompanying Json
        
        json_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}_Meta.JSON'.format(datestr)
        metaData = {'date': datestr, 'start': start, 'end': end, 'frames': frame_n}
        pathlib.Path(json_file_path).write_text(json.dumps(metaData))
        
        print('video outputted')
        
        # compress and output to server
        
        video_ouput_to_server = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
        json_server_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}_Meta.JSON'.format(datestr)
        command = 'ffmpeg -i {} -c:v libx265 -crf 29 {}'.format(video_file_path, video_ouput_to_server)
        result = subprocess.run(command)
        pathlib.Path(json_server_file_path).write_text(json.dumps(metaData))
        
        print('compression completed')
        
        # back to start