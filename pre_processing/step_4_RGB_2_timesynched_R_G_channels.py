# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 18:48:40 2021

@author: Naudascher
"""
import cv2
import os
import datetime
#import time

#---------------- RUN THIS SCRIPT ONLY FOR ACCLIM ----------------------------------

# We should have a distinct final output folder, redo this analog to step_3 !!!
# directory with rotated and cropped RGB -tifs to be processed 
# adapt this accorsingly ...

#date = '06_07'
#run =  'run_5'
dates = ['07_07','08_07','09_07']
runs =  ['run_1','run_2','run_3','run_4','run_5']

for date in dates:
    for run in runs:
    
        in_dir_side_acclim = os.path.join('G:\Thermal_exp\Final_runs', date, 'side_cam', run, 'tif_1')
        #in_dir_side_acclim = r'D:\Thermal_exp\Final_runs\01_07\side_cam\run_1\tif_1'
        
        in_dir_top_acclim = os.path.join('G:\Thermal_exp\Final_runs', date, 'top_cam', run, 'tif_1')
        #in_dir_top_acclim =  r'D:\Thermal_exp\Final_runs\01_07\top_cam\run_1\tif_1'
        
        # path to output file from step 3 -> rethink the path and folder structure!!!
        #time_file =   r'D:\Thermal_exp\Final_runs\01_07\Final\run_1\time_conversion_01_07_run_1.txt'
        txt_file = 'time_conversion_' + str(date) + '_' + str(run) + '.txt'
        time_file = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, txt_file )
        
        # These folders will be created if not yet existing
        #r_side_path = r'D:\Thermal_exp\Final_runs\01_07\Final\run_1\acclim_side_red'
        r_side_path = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_side_red')
        
        #g_side_path = r'D:\Thermal_exp\Final_runs\01_07\Final\run_1\acclim_side_green'
        g_side_path = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_side_green')
        
        #r_top_path = r'D:\Thermal_exp\Final_runs\01_07\Final\run_1\acclim_top_red'
        r_top_path = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_top_red')
        #g_top_path = r'D:\Thermal_exp\Final_runs\01_07\Final\run_1\acclim_top_green'
        g_top_path = os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, 'acclim_top_green')
        
        list_all = os.listdir(in_dir_side_acclim)
        acclim_dur = 15*60*24 # constant amount of frames for all acclimation periods
        
        ## Read time file
        with open(time_file) as f:
            contents = f.readlines()
        
        acclim_start_frame = int(contents[1])                       # as defined in step_3
        acclim_frames = list_all[acclim_start_frame:acclim_start_frame + acclim_dur]
        
        # load start time that coresponds to that frame and the identical time from the previously abstracted temperatrue data!!
        acclim_start_date_time = str(contents[3].strip('\n'))                                               # convert to string, cut the white space at the end of the line 
        acclim_start_date_time = datetime.datetime.strptime(acclim_start_date_time , '%Y-%m-%d %H:%M:%S.%f') # convert to time format
        
        #time_stamp = acclim_start_time + datetime.timedelta(0,count/24)  # 24 fps
        
                                             # abstract only the time
        
        #acclim_synch_time = datetime(str(contents[14]))  
        #print(acclim_synch_time)
        
        # create directories
        if not os.path.exists(r_side_path):
            os.makedirs(r_side_path)
            
        if not os.path.exists(g_side_path):
            os.makedirs(g_side_path)
            
        if not os.path.exists(r_top_path):
            os.makedirs(r_top_path)
            
        if not os.path.exists(g_top_path):
            os.makedirs(g_top_path)
            
        # LOAD images, split channels, rename them
        
        # initialize indices
        time_stamp = acclim_start_date_time
        count = 0
        
        # SIDE CAM & TOP CAM ; ACCLIM
        for i in (acclim_frames):
        
            if i.endswith(".tif"):
        
                # Load frame
                img = cv2.imread(os.path.join(in_dir_side_acclim, i))
                
        
                # Convert to grayscale
                blue, green, red = cv2.split(img)
                #cv2.imshow('red', red)
                #cv2.imshow('green', green)
                
                # add 1/24 seconds for this frame, first frame nothing is added...
                time_stamp = acclim_start_date_time + datetime.timedelta(0,count/24)  # 24 fps
                time_stamp_str = time_stamp.time().strftime("%H_%M_%S_%f") 
                
                # insert:
                # - Convert this time to a string  and add it to the filename below using hh_mm_ss_ffff
                # - in the end we want to store r_img_00001_14_06_12_034958.tif
                cv2.imwrite(os.path.join(r_side_path,"%05d_red_" + time_stamp_str + ".tif") % count, red) # Write the results to output location.
                cv2.imwrite(os.path.join(g_side_path,"%05d_green_" + time_stamp_str + ".tif") % count, green) # Write the results back to output location.
                
                # same for TOP CAM!
                img_top = cv2.imread(os.path.join(in_dir_top_acclim, i))
                blue, green_top, red_top = cv2.split(img_top)
                
                cv2.imwrite(os.path.join(r_top_path,"%05d_red_" + time_stamp_str + ".tif") % count, red_top) # Write the results to output location.
                cv2.imwrite(os.path.join(g_top_path,"%05d_green_" + time_stamp_str + ".tif") % count, green_top) # Write the results back to output location.
                
                
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                count = count + 1  # Use all frames
                #count += skip_frame # skip the frames
                print("Current frame: " + str(count))
                if count > 15*60*24:
                    print('More then 15 min. are processed')
        
# TOP CAM; ACCLIM        

        
# THIS IS JUST AN  EXAMPLE
#str_date = '2021-06-29 14:30:08.916667'
#d_date = datetime.datetime.strptime(str_date , '%Y-%m-%d %H:%M:%S.%f')
#print(d_date)
#d_date_added = d_date + datetime.timedelta(0,216/24) # way to add a delta_time in seconds 
#print(d_date_added)
#d_date_added_time = d_date_added.time().isoformat() # abstract only the time
#print(d_date_added_time)
#print(type(d_date_added_time)) # check d_date type.
# END OF EXAMPLE