# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 18:19:36 2021

@author: Naudascher

Input:  .mp4 videos from GoPro Hero 6, Side camera
Output: Rotated and cropped RGB.tif files of entire video

"""

import cv2
import os
import pathlib
import glob

## ----- INPUT -------------
dates = ['07_07','08_07','09_07']
runs =  ['run_1','run_2','run_3','run_4','run_5']       # 5 experimental runs per day

for date in dates:          # Loop over dates
    for run in runs:        # Loop over runs 
        side_cam = False
        video_ID = 1            # Go from 1  = acclim, 2 = treat_part1 , 3 = treat_part_2
        ## ----- END INPUT ---------
        
        vid = 'vid_' + str(video_ID)
        tif = 'tif_' + str(video_ID)
        
        # SIDE CAM - # set path adapt manually
        if side_cam:                                                         # !!! special param file for run_2        
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
        x = int(contents[1])            # rotation center in original frame, upper left corner is (0,0)
        y = int(contents[3])
        rot_angle = float(contents[5])    # angle it will be rotated counter clockwise around this point
        width = int(contents[7])          # width of cropped image
        height = int(contents[9])
        dx = int(contents[11])       # translocation of rotational center only for 
        pre_rot_180 = int(contents[13])
        
        # rotation function
        def rotate_keep_orig_dim(img, angle, cX, cY):  # see also: https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
            # grab the dimensions of the image
            h, w = img.shape[:2]
            # grab the rotation matrix (applying angle to rotate counter clockwise)
            M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)
            # perform the actual rotation and return the image, size of the image wo'nt have changed
            return cv2.warpAffine(img, M, (w,h))
        
        #print (duration)
        #cam1
        #input_vid = "D:\Thermal_Experiments\Time_test\cam1\cam1_part1\GOPR1152.mp4"
        #output_loc = "D:\Thermal_Experiments\Time_test\cam1\cam1_part1\GOPR1152\ "
        
        # vidcap = cv2.VideoCapture(input_vid)
        #success,image = vidcap.read()
        cap = cv2.VideoCapture(file)#(input_vid)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        #frame_count = 20
        count = 0
        
        #cap.set(1,count) # eventually remove this line when sta
        print ("Converting video..\n")
        
        while cap.isOpened():                    # Start converting the video
            ret, frame = cap.read()              # Extract the frame
            print('count = ', count)                        # this is needed somehow ?! it will break!!
            #if ret:
        
            if ret:
                if pre_rot_180 == 1: # some top_videos are for some reason fliped by 180 degrees !!!
                    frame = cv2.rotate(frame, cv2.ROTATE_180) 
                    
                rotated = rotate_keep_orig_dim(frame, rot_angle, x, y)  # Rotate
                #print('rotated dim:',rotated.shape[:2])
                rotated_cropped = rotated[y:y+height, x-dx:x-dx+width]        # Crop
                #print('rotated_cropped dim:',rotated_cropped.shape[:2])
                
                cv2.imwrite(os.path.join(out_tif_folder,"img_%05d.tif") % count, rotated_cropped) # store frame
                count = count + 1  # Use all frames
            
                #count += skip_frame # skip the frames
                print("Current frame: " + str(count) + " ; " + date + " ; " +  run + " ; " + vid + " ; Side_cam: " + str(side_cam))
            
            #else:
                #count = count+1  # this line ensures that non exisitng frames are skipped!
                #if count >= 20:        # Stop after ith frame of original file (for debugging)
                 #   break
                    
            if count == frame_count-5:
                break
                cap.release()
                print("Frames processed:",count)
