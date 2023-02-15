# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 15:43:40 2021

@author: Naudascher
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 18:48:40 2021
@author: Naudascher
"""
import cv2
import os
import datetime
#import time

# ---------------   RUN THIS SCRIPT ONLY FOR TREATMENT ---------------

# We should have a distinct final output folder, redo this analog to step_3 !!!
# directory with rotated and cropped RGB -tifs to be processed 

# path to output file from step 3 -> rethink the path and folder structure!!!

dates = ['07_07','08_07','09_07']
runs =  ['run_1','run_2','run_3','run_4','run_5']

for date in dates:
    for run in runs:
    
        txt_file = 'time_conversion_' + str(date) + '_' + str(run) + '.txt'
        time_file =               os.path.join('G:\Thermal_exp\Final_runs', date, 'Final', run, txt_file )
        
        in_dir_side_treat_part1 = os.path.join('G:\Thermal_exp\Final_runs', date, 'side_cam' , run , 'tif_2' )
        in_dir_top_treat_part1  = os.path.join('G:\Thermal_exp\Final_runs', date, 'top_cam' , run , 'tif_2' )
        in_dir_side_treat_part2 = os.path.join('G:\Thermal_exp\Final_runs', date, 'side_cam' , run , 'tif_3' )
        in_dir_top_treat_part2  = os.path.join('G:\Thermal_exp\Final_runs', date, 'top_cam' , run , 'tif_3' )
        
        r_side_path =             os.path.join('G:\Thermal_exp\Final_runs', date, 'Final' , run , 'treat_side_red')# ALWAYS treat_side here here ;# These folders will be created if not yet existing
        g_side_path =             os.path.join('G:\Thermal_exp\Final_runs', date, 'Final' , run , 'treat_side_green')
        r_top_path =              os.path.join('G:\Thermal_exp\Final_runs', date, 'Final' , run , 'treat_top_red')
        g_top_path =              os.path.join('G:\Thermal_exp\Final_runs', date, 'Final' , run , 'treat_top_green')
        
        # SAVE Output
        if not os.path.exists(r_side_path):
            os.makedirs(r_side_path)
            
        if not os.path.exists(g_side_path):
            os.makedirs(g_side_path)
            
        if not os.path.exists(r_top_path):
            os.makedirs(r_top_path)
            
        if not os.path.exists(g_top_path):
            os.makedirs(g_top_path)
            
        
        list_part_1 = os.listdir(in_dir_top_treat_part1)
        frames_in_part_1 = len(list_part_1)
        list_part_2 = os.listdir(in_dir_top_treat_part2)
        
        list_all = list_part_1 + list_part_2 # big lsit with all fram names
            
        treat_dur = 21*60*24 # constant amount of frames for all treatment periods added on minute as buffer in the end in case we lose soemthing at the beginning
        
        ## Read time file
        with open(time_file) as f:
            contents = f.readlines()
        
        treat_start_frame = int(contents[5])                       # as defined in step_3
        treat_frames = list_all[treat_start_frame:treat_start_frame + treat_dur]
        
        # load start time that coresponds to that frame and the identical time from the previously abstracted temperatrue data!!
        treat_start_date_time = str(contents[7].strip('\n'))   
        
        try:                                            # convert to string, cut the white space at the end of the line 
            treat_start_date_time = datetime.datetime.strptime(treat_start_date_time , '%Y-%m-%d %H:%M:%S.%f') # convert to time format
        except ValueError:              # This is to account for the fact that sometimes we have no decimal places in the TIMESTAMP
            treat_start_date_time = datetime.datetime.strptime(treat_start_date_time, '%Y-%m-%d %H:%M:%S')
        #time_stamp = acclim_start_time + datetime.timedelta(0,count/24)  # 24 fps
        
                                             # abstract only the time
        
        #acclim_synch_time = datetime(str(contents[14]))  
        #print(acclim_synch_time)
        
        
        # LOAD images, split channels, rename them
        
        # initialize indices
        time_stamp = treat_start_date_time
        count = 0
        
        # SIDE CAM & TOP CAM ; ACCLIM
        for i in (treat_frames): #
        
            if i.endswith(".tif"):
        
                if count < (frames_in_part_1-treat_start_frame):  # first part is in one folder, second part in second folder...
                # Load frame from tif_2
                    img = cv2.imread(os.path.join(in_dir_side_treat_part1, i))
                    img_top = cv2.imread(os.path.join(in_dir_top_treat_part1, i))   # TOP CAM!
                 #   
                else: # Load frames from tif_3
                    img = cv2.imread(os.path.join(in_dir_side_treat_part2, i))     # side CAM!
                    img_top = cv2.imread(os.path.join(in_dir_top_treat_part2, i))  # TOP CAM!
                
                # Convert to grayscale
                blue, green, red = cv2.split(img)
                #cv2.imshow('red', red)
                #cv2.imshow('green', green)
                
                # add 1/24 seconds for this frame, first frame nothing is added...
                time_stamp = treat_start_date_time + datetime.timedelta(0,count/24)  # 24 fps
                time_stamp_str = time_stamp.time().strftime("%H_%M_%S_%f") 
                
                # insert:
                # - Convert this time to a string  and add it to the filename below using hh_mm_ss_ffff
                # - in the end we want to store r_img_00001_14_06_12_034958.tif
                cv2.imwrite(os.path.join(r_side_path,"%05d_red_" + time_stamp_str + ".tif") % count, red) # Write the results to output location.
                cv2.imwrite(os.path.join(g_side_path,"%05d_green_" + time_stamp_str + ".tif") % count, green) # Write the results back to output location.
                
                blue, green_top, red_top = cv2.split(img_top)
                
                cv2.imwrite(os.path.join(r_top_path,"%05d_red_" + time_stamp_str + ".tif") % count, red_top) # Write the results to output location.
                cv2.imwrite(os.path.join(g_top_path,"%05d_green_" + time_stamp_str + ".tif") % count, green_top) # Write the results back to output location.
                
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
                count = count + 1  # Use all frames
                #count += skip_frame # skip the frames
                print("Current frame: " + str(count))
                if count > 28000:
                    print('More then 20 min. are processed')
                
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