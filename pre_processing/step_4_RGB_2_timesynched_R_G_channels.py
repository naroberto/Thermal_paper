# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 18:48:40 2021
@author: Naudascher

Description: 
This script is for the top and side camera during acclimation phase (first 15 minutes; fish are in the left compartment).
Here we split the RGB image into RED and GREEN channel. 

Input:  Output of step_2 and 3 (cropped and rotated color images and time conversion file.txt).
Output: RED and GREEN channel of each image, time stamped in the file name.

"""

import cv2
import os
import datetime

dates = ['07_07','08_07','09_07']                                 # not all dates...
runs =  ['run_1','run_2','run_3','run_4','run_5']

for date in dates:
    
    for run in runs:
    
        in_dir_side_acclim = os.path.join('G:\Thermal_exp\Final_runs', date, 'side_cam', run, 'tif_1')
        in_dir_top_acclim = os.path.join('G:\Thermal_exp\Final_runs', date, 'top_cam', run, 'tif_1')
        
        # path to output files from step 3 
        txt_file  = 'time_conversion_' + str(date) + '_' + str(run) + '.txt'
        time_file = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, txt_file )
        
        # Create folders for output images
        r_side_path = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_side_red')
        g_side_path = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_side_green')
        r_top_path  = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_top_red')
        g_top_path  = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_top_green')

        if not os.path.exists(r_side_path):
            os.makedirs(r_side_path)
            
        if not os.path.exists(g_side_path):
            os.makedirs(g_side_path)
            
        if not os.path.exists(r_top_path):
            os.makedirs(r_top_path)
            
        if not os.path.exists(g_top_path):
            os.makedirs(g_top_path)
        
        list_all = os.listdir(in_dir_side_acclim)   # list with all input images
        acclim_dur = 15*60*24                       # 15 minutes of acclimation at 24 fps -> N frames
        
        ## Read time conversion file
        with open(time_file) as f:
            contents = f.readlines()
        
        acclim_start_frame = int(contents[1])                       # as defined in step_3
        acclim_frames = list_all[acclim_start_frame:acclim_start_frame + acclim_dur]
        
        # load start time that coresponds to that frame and the identical time from the previously abstracted temperatrue data!!
        acclim_start_date_time = str(contents[3].strip('\n'))                                               # convert to string, cut the white space at the end of the line 
        acclim_start_date_time = datetime.datetime.strptime(acclim_start_date_time , '%Y-%m-%d %H:%M:%S.%f') # convert to time format
        
        # initialize indices
        time_stamp = acclim_start_date_time
        count = 0
        
        # SIDE CAM & TOP CAM ; ACCLIM, # LOAD images, split channels, rename and store them 
        for i in (acclim_frames):           # loop over all frames
        
            if i.endswith(".tif"):
        
                # Load frame
                img = cv2.imread(os.path.join(in_dir_side_acclim, i))

                # Split image into its channels
                blue, green, red = cv2.split(img)                   #cv2.imshow('red', red)    #cv2.imshow('green', green)
             
                # add 1/24 seconds for this frame, first frame nothing is added...
                time_stamp = acclim_start_date_time + datetime.timedelta(0,count/24)  # 24 fps
                time_stamp_str = time_stamp.time().strftime("%H_%M_%S_%f") 
                
                cv2.imwrite(os.path.join(r_side_path,"%05d_red_" + time_stamp_str + ".tif") % count, red)       # RED image: Write the results to output location.
                cv2.imwrite(os.path.join(g_side_path,"%05d_green_" + time_stamp_str + ".tif") % count, green)   # GREEN image: Write the results back to output location.
                
                # same for TOP CAM!
                img_top = cv2.imread(os.path.join(in_dir_top_acclim, i))
                blue, green_top, red_top = cv2.split(img_top)
                
                cv2.imwrite(os.path.join(r_top_path,"%05d_red_" + time_stamp_str + ".tif") % count, red_top)     # Write the results to output location.
                cv2.imwrite(os.path.join(g_top_path,"%05d_green_" + time_stamp_str + ".tif") % count, green_top) # Write the results back to output location.
                
                count = count + 1  # Use all frames                   #count += skip_frame # skip the frames

                print("Current frame: " + str(count))
                if count > 15*60*24:
                    print('More then 15 min. are processed')
       
