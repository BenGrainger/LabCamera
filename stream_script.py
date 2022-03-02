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

while(True): # forever loop - planning to always running 
    
    x = datetime.datetime.now()
    datestr = str(x.date())
    start = str(x.time())
    
    hr = get_hour()
    
    if 8 < hr < 23: # between the hours of 8 and 23
        
        # cv2 to create camera object
        
        video = cv2.VideoCapture(0)
        cap = cv2.VideoCapture(0)
        size = (int(video.get(3)), int(video.get(4)))

        video_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
        
        result = cv2.VideoWriter(video_file_path, 
                             cv2.VideoWriter_fourcc(*'MJPG'), # fourcc is how openCV find # MJPG is the codec
                             30, size)
        
        frame_n = 0 # frame counter 
        
        while(8 < hr < 23): # during the hours of 8-23 write a video to video_file_path

            hr = get_hour()
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
        command = 'ffmpeg -i {} -b x265 {}'.format(video_ouput_to_server, out)
        result = subprocess.run(command)
        pathlib.Path(json_server_file_path).write_text(json.dumps(metaData))
        
        # back to start