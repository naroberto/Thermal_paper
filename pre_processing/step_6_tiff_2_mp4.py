# -*- coding: utf-8 -*-
"""
Created on Tue Oct 12 14:28:16 2021

@author: Naudascher
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Oct 11 10:36:13 2021

@author: Naudascher
"""

import numpy as np
import pandas as pd
import tracktor as tr
import cv2
print('Version of openCV: ', cv2.__version__)
import sys
import scipy.signal
import os
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

# -----  INPUT  -------
dates = ['29_06','01_07','02_07','04_07'] #,'05_07','06_07','07_07','08_07','09_07']
runs =  ['run_1','run_2','run_3','run_4','run_5']
phase_folders = ['acclim_side_green','acclim_top_green','treat_top_green','treat_side_green'] # Select pahse from ['acclim','up_1','p_1','d_1','b_1','up_2','p_2','d_2','b_2','up_3','p_3','d_3','b_3',]
fps = 24 # this needs to be a divisor of 15
codec = 'MP4V'
# ---------------------

#exp_ID = date + '_' + run + '_' + phase

# PARAMS ----
# for background subtraction
frame_skip_median = 2*24 # use every 48th frame for median
R_zero = 240        #125 # rescaling value for zero values
R_min = 1           # new min value in rescaled range
R_max = 255   
for date in dates:
    for run in runs:
        out_base_folder = os.path.join(r'F:\Vids_for_tracking',date,run)
        Nametxt =             os.path.join(out_base_folder ,'mp4_conv_params.txt')
        if not os.path.exists(os.path.join(out_base_folder)):
                os.makedirs(os.path.join(out_base_folder))
        
        for phase in phase_folders:
            
            in_dir =          os.path.join(r'D:\Thermal_exp\Final_runs',date,'Final',run,phase)
            
            # FUNCTIONS ------------
            def getMedian(start_frame_phase, frame_skip_median):
                list_median = list_all[0::frame_skip_median]         # all frames for median of that period
            
                count = 0
                frames = []
                
                # Grab images for calc of Median
                for i in (list_median):
                
                    if i.endswith(".tif"):
                        img = cv2.imread(os.path.join(in_dir, i))  # Load frame
                        img_grey = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)  # Convert to grayscale
                        frames.append(img_grey)  # Collect all frame
                        count += 1
                        print('appending frame for Median: ', count)
                        continue
                    else:
                        continue
            
                # Calculate Median Background
                median = np.median(frames, axis=0).astype(dtype=np.uint8)     #
                std_dev = np.std(frames, axis = 0).astype(dtype= np.uint8)
                #max_background = np.max(frames, axis=0).astype(dtype=np.uint8)
                #cv2.imshow('median Baseflow', median)  
                #cv2.imshow('std_dev',std_dev)
                #cv2.waitKey()
                #cv2.destroyAllWindows() 
                #maximum = np.max(frames,axis=0).astype(dtype=np.uint8)
                #median  = median.astype(np.int32) 
                
                median_grey = median.astype(np.int32)     
                # enlarge for Fre
                #cv2.imwrite(os.path.join(out_dir_median, exp_ID + '_median.tif'),median_grey)
                #cv2.imwrite(os.path.join(out_dir_median, exp_ID + '_std_dev.tif'),std_dev)
                return median_grey, std_dev
            
            def subtractMedian2(frame,median_grey,R_zero,R_min,R_max):
                # Fre approach, Subtract median
                frame_grey = np.array(cv2.cvtColor(np.uint8(frame), cv2.COLOR_RGB2GRAY))
                frame_grey = frame_grey.astype(np.int32)  # enlarge frame
                cor_frame = np.array(frame_grey -  median_grey)  # subtract median
                
                # Reshift pixel values tp positive values
                scale_frame = cor_frame + R_zero
                scale_frame = np.where(scale_frame < R_min, R_min, scale_frame)
                scale_frame = np.where(scale_frame > R_max, R_max, scale_frame)
                scale_frame = np.uint8(scale_frame)
                return scale_frame
            
            # Median background
            list_all = os.listdir(in_dir) # all frames of that phase are already in one folder
            median,std_ = getMedian(0, frame_skip_median)
            
            # total frames
            # video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
            # Check length of video!
            video_length = int(len(list_all))
            print('Total frames: ', video_length)
            if phase =='treat_side_green' or phase =='treat_side_top':
                if video_length < int(20*24*60):
                    print('SEQUENCE TO SHORT: ',video_length)
                    break
            if phase =='acclim_side_green' or phase =='acclim_side_top':
                if video_length < int(15*24*60):
                    print('SEQUENCE TO SHORT: ',video_length)
                    break
            
        
            # video objects fro greyscale vid
            width =  median.shape[1]
            height = median.shape[0]
            out = cv2.VideoWriter(os.path.join(out_base_folder,phase +'.mp4'),cv2.VideoWriter_fourcc(*'MP4V'), 24.0, (width,height),isColor=False)
            out_raw = cv2.VideoWriter(os.path.join(out_base_folder,phase +'_raw.mp4'),cv2.VideoWriter_fourcc(*'MP4V'), 24.0, (width,height),isColor=False)
            # try codec avc1
            # Grab images for Tracking
            for image in (list_all[0:len(list_all):int(24/fps)]): #  #[2800:3250]): # run code on subsection of frames...
            
                if image.endswith(".tif"):
            
                    frame = cv2.imread(os.path.join(in_dir, image))
                    out_raw.write(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
                    # subtrack background
                    frame = subtractMedian2(frame,median,R_zero,R_min,R_max) # subtrackt median background and rescale 
                    
                    if phase == 'acclim_side_green' or phase == 'treat_side_green':
                        frame[0:30,:] = 240 #set very top to grey
                        std_mask = frame[30:50,:]
                        std_mask[std_[30:50,:] > 20] = 240 # set values with high std_dev to white so they do not disturb tracking; these are regions with waves...
                        
                        
                        frame[30:50,:] = std_mask # overwrite frame in the area of water surface, here we have lots of fluctuations
           
                    # write frame
                    out.write(frame)
                    
                    
                    print('CURRENT FRAME: ',image)
                 
            out.release()
            out_raw.release()
            print('COMPLETE:',phase)
            cv2.destroyAllWindows()
                
        ## save params as .txt
        outF = open(Nametxt, "w")
        #for line in [header]: # , basestart]:
        outF = open(Nametxt, "a")             
        
        outF.write("date")
        outF.write("\n")
        outF.write(str(date))
        outF.write("\n")
        
        outF.write(str(run))            # write line to output file
        outF.write("\n")
        outF.write("fps")
        outF.write("\n")
        outF.write(str(fps))
        
        outF.write("\n")
        outF.write("frame_skip_median")  
        outF.write("\n")
        outF.write(str(frame_skip_median))
        
        outF.write("\n")
        outF.write("R_zero")  
        outF.write("\n")
        outF.write(str(R_zero))
        
        outF.write("\n")
        outF.write("R_max")   
        outF.write("\n")
        outF.write(str(R_max))
        
        outF.write("\n")
        outF.write("R_min")   
        outF.write("\n")
        outF.write(str(R_min))
        
        outF.write("\n")
        outF.write("codec")   
        outF.write("\n")
        outF.write(str(codec))
        
        outF.close()                # close file