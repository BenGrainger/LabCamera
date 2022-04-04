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
    hr = get_hour():
    return start < hr < end

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
        
        # set to 4K 4096 x 2160, 30fps
        
        fps = 30
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) # have to set codec before resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        size = (int(cap.get(3)), int(cap.get(4)))

        video_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
        
        result = cv2.VideoWriter(video_file_path, 
                             cv2.VideoWriter_fourcc(*'MJPG'), # fourcc is how openCV find # MJPG is the codec
                             24, size)
        
        frame_n = 0 # frame counter 
        
        while(in_time()): # during the hours of 8-23 write a video to video_file_path

            frame_n += 1
            ret, frame = cap.read()
            result.write(frame)
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # stop writing and release after 23
        
        cap.release()
        result.release()
        cv2.destroyAllWindows()
        
        end = str(datetime.datetime.now().time())
        
        # save accompanying Json
        
        json_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}_Meta.JSON'.format(datestr)
        metaData = {'date': datestr, 'start': start, 'end': end, 'frames': frame_n}
        pathlib.Path(json_file_path).write_text(json.dumps(metaData))
        
        # compress and output to server
        
        video_ouput_to_server = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
        json_server_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}_Meta.JSON'.format(datestr)
        command = 'ffmpeg -i {} -c:v libx264 -crf 26 {}'.format(video_file_path, video_ouput_to_server)
        result = subprocess.run(command)
        pathlib.Path(json_server_file_path).write_text(json.dumps(metaData))
        
        # back to start