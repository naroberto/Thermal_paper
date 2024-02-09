# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 15:23:47 2021

@author: Naudascher
see also: https://stackoverflow.com/questions/33311153/python-extracting-and-saving-video-frames

Goal: 
Convert one image of video to RGB .tif image for step_1

Description: 
For each day of experiments, only one calibration is nessecary, as camera orientation was not moved during single day.
Hence step_0 and step_1 had to be run for only one video per experimental day.

"""
import cv2  # Import the OpenCV library for video processing
import os   # Import the os module for interacting with the operating system

# Folders
input_vid: str = r'F:\Thermal_exp\Final_runs\09_07\side_cam\run_1\vid_1\GOPR1255.mp4'   # Define the path to the input video
out_folder: str = r'F:\Thermal_exp\Final_runs\09_07\Final\crop_rot_params_side_run_1'   # Define the folder where the output images will be stored

# Load the video file
cap = cv2.VideoCapture(input_vid)      # load video
count = 0                              # Initialize a counter for the frames processed

# Check if the output folder doesn't exist, create it if necessary
if not os.path.exists(out_folder): 
    os.makedirs(out_folder)          # create Output folder

# Iterate through the frames of the video
while cap.isOpened():  # Start converting the video
    # Read the next frame from the video
    ret, frame = cap.read()  # Extract the frame
    # Print the return value, indicating whether a frame was successfully read
    print(ret)  # print to console 
    
    # If a frame was successfully read
    if ret:
        # Write the frame as an image file in the output folder
        cv2.imwrite(os.path.join(out_folder,"cal_img.tif"), frame)  # store frame to output location.
        # Increment the frame counter
        count = count + 1  # Use other frames, #count += skip_frame # skip the frame
        # Print the current frame number
        print("Current frame: " + str(count))

    # Check if the number of frames processed exceeds a certain threshold (debugging)
    if count >= 0:  # Stop after ith frame of original file (for debugging)
        
        # Print the path where the image was saved
        print("Saved cal_img to: ")
        print(out_folder)
        
        # Exit the loop
        break  # stop code if condition is met
    
# Release the video capture object
cap.release()
