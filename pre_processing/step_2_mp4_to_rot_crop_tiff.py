# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 18:19:36 2021

@author: Naudascher

Description: 
This script essentially automates the process of rotating and cropping 
each frame of a video captured by the GoPro Hero 6 side camera 
and saves the processed frames as individual RGB .tif files.

Input:  .mp4 videos from GoPro Hero 6, Side camera, rotation and crop params from step_1
Output: Rotated and cropped RGB.tif files of entire video in one folder.

"""

# import libraries
import cv2
import os
import pathlib
import glob

## ----- INPUT -------------
dates = ['07_07','08_07','09_07']
runs =  ['run_1','run_2','run_3','run_4','run_5']       # 5 experimental runs per day

## ---------------------------

for date in dates:    # Loop over dates
    
    for run in runs:        # Loop over runs 
        side_cam = False
        video_ID = 1            # Go from 1  = acclim, 2 = treat_part1 , 3 = treat_part_2
       
        vid = 'vid_' + str(video_ID)
        tif = 'tif_' + str(video_ID)
        
        # SIDE CAM - # set path adapt manually
        if side_cam:                              
            
            # retrieve params
            params            = os.path.join('F:\Thermal_exp\Final_runs',date,'Final\crop_rot_params_side_run_1\params.txt') # camera positions did not change during experimental run, use the same params for the entire side cam for each run
            path              = os.path.join('F:\Thermal_exp\Final_runs',date,'side_cam', run,vid )
            
            for file in glob.glob(path + '\*'): #list of all files in that folder
                input_vid = file  # video path
            out_tif_folder =    os.path.join('F:\Thermal_exp\Final_runs',date,'side_cam',run,tif)    #,tif)         # output folder for tifs
            
        else: 
            
        # TOP CAM
            params            = os.path.join('F:\Thermal_exp\Final_runs',date,'Final\crop_rot_params_top_run_1\params.txt') # camera positions did not change during experimental run, use the same params for the entire side cam for each run 
            path              = os.path.join('F:\Thermal_exp\Final_runs',date,'top_cam', run, vid)
            for file in glob.glob(path + '\*'): #list of all files in that folder
                input_vid = file  # video path
            out_tif_folder =    os.path.join('F:\Thermal_exp\Final_runs',date,'top_cam',run,tif)             # output folder for tifs
           
        print(input_vid)
        
        # create Output folder
        if not os.path.exists(out_tif_folder):
            os.makedirs(out_tif_folder)
        
        # Read parameters for rotation and cropping (output of step_1)
        with open(params) as f:
            contents = f.readlines()
            
        x = int(contents[1])              # rotation center in original frame, upper left corner is (0,0)
        y = int(contents[3])
        rot_angle = float(contents[5])    # angle it will be rotated counter clockwise around this point
        width = int(contents[7])          # width of cropped image
        height = int(contents[9])
        dx = int(contents[11])       # translocation of rotational center only for 
        pre_rot_180 = int(contents[13])
        
        # rotation function
        def rotate_keep_orig_dim(img, angle, cX, cY):  # see also: https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
            h, w = img.shape[:2] # grab the dimensions of the image
            M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0) # grab the rotation matrix (applying angle to rotate counter clockwise)
            return cv2.warpAffine(img, M, (w,h)) # perform the actual rotation and return the image, size of the image wo'nt have changed
        
        cap = cv2.VideoCapture(file)#(input_vid)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        count = 0

        print ("Converting video..\n")
        while cap.isOpened():                    # Start converting the video
            ret, frame = cap.read()              # Extract the frame
            print('count = ', count)             
          
            if ret:
                if pre_rot_180 == 1: # some top_videos are for some reason fliped by 180 degrees !!!
                    frame = cv2.rotate(frame, cv2.ROTATE_180) 
                    
                rotated = rotate_keep_orig_dim(frame, rot_angle, x, y)      # Rotate
                rotated_cropped = rotated[y:y+height, x-dx:x-dx+width]      # Crop

                cv2.imwrite(os.path.join(out_tif_folder,"img_%05d.tif") % count, rotated_cropped) # store frame
                count = count + 1  # Use all frames
                print("Current frame: " + str(count) + " ; " + date + " ; " +  run + " ; " + vid + " ; Side_cam: " + str(side_cam))

            if count == frame_count-5: # stop
                break
                cap.release()
                print("Frames processed:",count)
