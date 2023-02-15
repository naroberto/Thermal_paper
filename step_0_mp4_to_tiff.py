# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 15:23:47 2021

@author: Naudascher
see also: https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

Goal: 
Convert one image of video to RGB .tif image for step_1

Description: 
For each day of experiments, only one calibration is nessecary, as cameras were never moved during single day.
Hence step_0 and step_1 had to be run for only one video per experimental day.

"""
#%%  Routines & Input
import cv2
import os

# side camera
input_vid:  str = r'F:\Thermal_exp\Final_runs\09_07\side_cam\run_1\vid_1\GOPR1255.mp4' # path to video
out_folder: str = r'F:\Thermal_exp\Final_runs\09_07\Final\crop_rot_params_side_run_1'  # folder of calibration params

#%% Load and store first frame

if not os.path.exists(out_folder): 
    os.makedirs(out_folder)              # create Output folder
    
cap = cv2.VideoCapture(input_vid)        # load video
count = 0                               

while cap.isOpened():                    # Start converting the video
    ret, frame = cap.read()              # Extract the frame
    print(ret)                           # print to console 
    
    if ret:
          cv2.imwrite(os.path.join(out_folder,"cal_img.tif"), frame) # store frame to output location.
          count = count + 1              # Use other frames, #count += skip_frame # skip the frame
          print("Current frame: " + str(count))

    if count >= 0:                      # Stop after ith frame of original file (for debugging)
        print("Saved cal_img to: ")
        print(out_folder)
        break                               # stop code if condition is met
    
cap.release()