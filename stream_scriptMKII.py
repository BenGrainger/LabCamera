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
        # Enable auto exposure time setting if camera supports it
        try:
            cam.ExposureAuto.set('Continuous')
        except (AttributeError, VimbaFeatureError):
            pass
        # Enable white balancing if camera supports it
        try:
            cam.BalanceWhiteAuto.set('Continuous')
        except (AttributeError, VimbaFeatureError):
            pass
        # Try to adjust GeV packet size. This Feature is only available for GigE - Cameras.
        try:
            cam.GVSPAdjustPacketSize.run()
            while not cam.GVSPAdjustPacketSize.is_done():
                pass
        except (AttributeError, VimbaFeatureError):
            pass
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
        if key == ENTER_KEY_CODE:
            self.shutdown_event.set()
            return

        elif frame.get_status() == FrameStatus.Complete:
            #print('{} acquired {}'.format(cam, frame), flush=True)
            msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'
            cv2.imshow(msg.format(cam.get_name()), frame.as_opencv_image())
            self.frame_number +=1
            img = frame.as_opencv_image()
            result.write(img)
            hr = get_hour()
            if 8 < hr < 23:
                self.shutdown_event.set()

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
    start = str(x.time())
    
    hr = get_hour()
    
    if 8 < hr < 23: # between the hours of 8 and 23
        with Vimba.get_instance():
            cams = vimba.get_all_cameras()

            print('Cameras found: {}'.format(len(cams)))

            for cam in cams:
                cameraID = cam.get_id()

            with get_camera(cameraID) as cam:

                cam.AcquisitionFrameRateAbs = 10
                fps=cam.AcquisitionFrameRateAbs
                single_frame = cam.get_frame().as_numpy_ndarray()
                size = (single_frame.shape[0], single_frame.shape[1])
                video_file_path = r'C:\Users\BMLab21\Documents\CrabStreams\{}.avi'.format(datestr)
                result = cv2.VideoWriter(video_file_path, cv2.VideoWriter_fourcc(*'MJPG'), fps, size[::-1])
                # Start Streaming, wait for five seconds, stop streaming
                setup_camera(cam)
                handler = Handler()

                try:
                    # Start Streaming with a custom a buffer of 10 Frames (defaults to 5)
                    cam.start_streaming(handler=handler, buffer_count=10)
                    handler.shutdown_event.wait()

                finally:
                    cam.stop_streaming()

        result.release()
        cv2.destroyAllWindows()