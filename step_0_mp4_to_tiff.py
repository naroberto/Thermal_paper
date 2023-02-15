# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 15:23:47 2021

@author: Naudascher
see also: https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

Goal: 
Convert first part of a video to .tif images for step_1
In a first step we can assume that for each day of experiments, only one calibration is nessecary, as we did not move the cameras during a single day.
"""
import cv2
import os

# run1
# side_cam


input_vid:  str = r'F:\Thermal_exp\Final_runs\09_07\side_cam\run_1\vid_1\GOPR1255.mp4'
out_folder: str = r'F:\Thermal_exp\Final_runs\09_07\Final\crop_rot_params_side_run_1'
"""
# top_cam
input_vid: str =  r'F:\Thermal_exp\Final_runs\09_07\top_cam\run_1\vid_1\GOPR0304.mp4'
out_folder: str = r'F:\Thermal_exp\Final_runs\09_07\Final\crop_rot_params_top_run_1'
"""
# create Output folder
if not os.path.exists(out_folder):
    os.makedirs(out_folder)
    
cap = cv2.VideoCapture(input_vid)
count = 0
#cap.set(1,count) # eventually remove this line when sta
print ("start..\n")

while cap.isOpened():                    # Start converting the video
    ret, frame = cap.read()              # Extract the frame
    print(ret)                           # this is needed somehow ?! it will break!!
    if ret:
         # cv2.imwrite(output_loc, frame) # Write the results to output location.
          cv2.imwrite(os.path.join(out_folder,"cal_img.tif"), frame) 
          count = count + 1  # Use all frames
          #count += skip_frame # skip the frames
          print("Current frame: " + str(count))
    #else:
        #count = count+1  # this line ensures that non exisitng frames are skipped!
    if count >= 0:        # Stop after ith frame of original file (for debugging)
        print("Saved cal_img to: ")
        print(out_folder)
        break        
cap.release()

