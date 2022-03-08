import vimba
from vimba import *
import sys
from typing import Optional
import cv2
import time
import datetime
import json
import pathlib
import subprocess
from time import sleep
import numpy as np
import threading

def get_camera(camera_id: Optional[str]) -> Camera:
    with Vimba.get_instance() as vimba:
        if camera_id:
            try:
                return vimba.get_camera_by_id(camera_id)
            except VimbaCameraError:
                print('Failed to access Camera \'{}\'. Abort.'.format(camera_id))
        else:
            cams = vimba.get_all_cameras()
            if not cams:
                print('No Cameras accessible. Abort.')
            return cams[0]

def setup_camera(cam: Camera):
    with cam:
        settings_file = r'C:\Users\BMLab21\Desktop\camera\fourth.xml'
        cam.load_settings(settings_file, PersistType.All)
        # Query available, open_cv compatible pixel formats
        # prefer color formats over monochrome formats
        cv_fmts = intersect_pixel_formats(cam.get_pixel_formats(), OPENCV_PIXEL_FORMATS)
        color_fmts = intersect_pixel_formats(cv_fmts, COLOR_PIXEL_FORMATS)
        if color_fmts:
            cam.set_pixel_format(color_fmts[0])
        else:
            mono_fmts = intersect_pixel_formats(cv_fmts, MONO_PIXEL_FORMATS)
            if mono_fmts:
                cam.set_pixel_format(mono_fmts[0])
            else:
                abort('Camera does not support a OpenCV compatible format natively. Abort.')


class Handler:
    def __init__(self):
        self.shutdown_event = threading.Event()
        self.frame_number = 0

    def __call__(self, cam: Camera, frame: Frame):
        ENTER_KEY_CODE = 13
    
        key = cv2.waitKey(1)
        time = get_hour()
        
        if key == ENTER_KEY_CODE:
            self.shutdown_event.set()
            return 
        

        elif frame.get_status() == FrameStatus.Complete:
            time = get_hour()
            if stream_begin < time < stream_end:
                msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'
                cv2.imshow(msg.format(cam.get_name()), frame.as_opencv_image())
                self.frame_number +=1
                img = frame.as_opencv_image()
                result.write(img)
            else:
                print('shut down camera')
                self.shutdown_event.set()
                return

        cam.queue_frame(frame)

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
    stream_begin = 8
    stream_end = 17
    
    hr = get_hour()
    
    if stream_begin < hr < stream_end: # between the hours of 8 and 23
        
        start = str(datetime.datetime.now().time())
        
        with Vimba.get_instance() as vimba:
            cams = vimba.get_all_cameras()

            print('Cameras found: {}'.format(len(cams)))

            for cam in cams:
                cameraID = cam.get_id()

            with get_camera(cameraID) as cam:

                single_frame = cam.get_frame().as_numpy_ndarray()
                size = (single_frame.shape[0], single_frame.shape[1])
                video_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
                # Start Streaming, wait for five seconds, stop streaming
                
                setup_camera(cam)
                
                cam.AcquisitionFrameRateAbs = 25
                fps=cam.AcquisitionFrameRateAbs
                
                result = cv2.VideoWriter(video_file_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, size[::-1])
                
                handler = Handler()

                try:
                    # Start Streaming with a custom a buffer of 10 Frames (defaults to 5)
                    cam.start_streaming(handler=handler, buffer_count=10)
                    handler.shutdown_event.wait()
                    end = str(datetime.datetime.now().time())

                finally:
                    cam.stop_streaming()
                    print('Streaming has stopped')

        result.release()
        print('video released')
        cv2.destroyAllWindows()
        
        
        # save accompanying Json
        
        json_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}_Meta.JSON'.format(datestr)
        metaData = {'date': datestr, 'start': start, 'end': end}
        pathlib.Path(json_file_path).write_text(json.dumps(metaData))
        
        # compression
        
        video_ouput_to_server = r'C:\Users\BMLab21\Documents\CrabStreams\{}_x264.avi'.format(datestr)
        command = 'ffmpeg -i {} -c:v x264 -crf 26 {}'.format(video_file_path, video_ouput_to_server)
        try:
            result = subprocess.run(command)
            print('video compressed')
        except CompressionError:
            print('compression failed')
            
        os.remove(video_file_path)