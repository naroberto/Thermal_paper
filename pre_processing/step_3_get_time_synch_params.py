# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 11:48:00 2021

@author: Naudascher
- plot thermal data and find synchronization time (time at which the temp sensor was touched)
- 
"""

# to work with this open .tif stack of acclim and treatment phase

import plotly.io as pio
import plotly.express as px
import pandas as pd
import os
import datetime 
import math

pio.renderers.default='browser'  # set browser as display 

# INPUT GOES HERE
date = '09_07'
run =  'run_4'
temp_file =     'run_4_2021_07_09_14_10_21.dat'
# END INPUT

exp_ID =        '_' + date + '_' + run


#out_data_folder = os.path.join('D:\Thermal_exp\Final_runs',date,'Final',run)# check if you use data on D: or G: drive
#in_folder =       os.path.join('D:\Thermal_exp\Final_runs',date,'temp')


out_data_folder = os.path.join('G:\Thermal_exp\Final_runs',date,'Final',run)
in_folder =       os.path.join('G:\Thermal_exp\Final_runs',date,'temp')


# Select probe to show (mostly probe 1 -Top left; sometimes probe 4 as well (-top right))
probe = 1

# FINE TUNE THESE during the run
# set acclim start based on plot from this script
acclim_synch_frame = 145    # load vid_1 stack in imageJ, this is the frame coinciding with the respective Temp_peak, # frame ID where the finger leaves the sensor
acclim_start_frame = 876  # frame ID where the fish is released and no surface waves are present anymore, this is the real start of the run
acclim_synch_idx = 6997    # this is the row of the temperature data where we see the peak for the acclimation start
#acclim_start_time = acclim_start_frame + (acclim_start_frame - acclim_synch_frame) * (1/24) 

# Open the fiji stack at the same time

# TREATMENT
# (df.loc[[acclim_synch_idx],['TIMESTAMP']])
treat_synch_frame  =128 # load vid_2 stack first frame where finger is not on sensor anymore
treat_start_frame = 762  # frame ID where the gate is detaching the water surface, note that this is a different video
treat_synch_idx = 11813     # " " treament start maximum of curve
# -------  END INPUT  ---------------

seconds_between_acclim_and_treat = (treat_synch_idx-acclim_synch_idx)/5
print('GAP between acclim and treatment: ' + str(seconds_between_acclim_and_treat / 60) + ' min; it shoul be around 16 min.')
if seconds_between_acclim_and_treat < 15*60: 
    print('ERROR!! you reconsider the selection' + str(seconds_between_acclim_and_treat/60) + ' min gap, it should be around 16 min.')
    
# generate output file_names
time_output = 'time_conversion' + exp_ID + '.txt' 
acclim_temp_out = 'acclim_temp_data' + exp_ID + '.txt'
treat_temp_out = 'treat_temp_data' + exp_ID + '.txt'

# generate out_path
time_conversion_path = os.path.join(out_data_folder, time_output) 
acclim_temp_path = os.path.join(out_data_folder, acclim_temp_out)
treat_temp_path = os.path.join(out_data_folder, treat_temp_out)

    
if not os.path.exists(out_data_folder):
    os.makedirs(out_data_folder)
    
# Load data 
file_path = os.path.join(in_folder, temp_file)

# read data and drop lines
df = pd.read_csv(file_path, sep=",", encoding= 'utf-8', header = 0,parse_dates=True, skiprows=[0], usecols=[0,4,5,6,7,8,9,10,11])
df = df.drop([0, 1]).reset_index(drop=True) # drop 2 useless rows, reset index 

cols = df.columns[1:9]
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce', axis=1) # convert to float




# constant for all experiments 
treat_dur = 21 # in minutes
acclim_dur = 15 # 

if treat_start_frame < treat_synch_frame: 
    print('ERROR 1')
    
if acclim_start_frame < acclim_synch_frame: 
    print('ERROR 2')

# plot against index
fig_all =          px.line(df, x=df.index, y=df.columns[probe], title=df.columns[probe] + ' entire time series')
fig_acclim_start = px.line(df[acclim_synch_idx:], x=df[acclim_synch_idx:].index, y=df.columns[probe], title=df.columns[probe] + ' Acclim_synch')
fig_treat_start =  px.line(df[treat_synch_idx:], x=df[treat_synch_idx:].index, y=df.columns[probe], title=df.columns[probe] + ' Treat_synch')

fig_all.show()
fig_acclim_start.show()
fig_treat_start.show()

# plot against time
#fig_all =          px.line(df, x=df.columns[0], y=df.columns[probe], title=df.columns[probe] + 'All Data')
#fig_acclim_start = px.line(df[acclim_synch_idx:], x=df.columns[0], y=df.columns[probe], title=df.columns[probe] + ' Acclim_synch')#
#fig_treat_start =  px.line(df[treat_synch_idx:], x=df.columns[0], y=df.columns[probe], title=df.columns[probe] + ' Treat_synch')

# get those timestamps (from the Temperature and oxygen probes) This can be used for top_cam and side cam
# synch_time to datetime object
try:
    acclim_synch_time = datetime.datetime.strptime(df.loc[acclim_synch_idx,'TIMESTAMP'], '%Y-%m-%d %H:%M:%S.%f')
    # Insert same for treat_time
except ValueError:              # This is to account for the fact that sometimes we have no decimal places in the TIMESTAMP
    acclim_synch_time = datetime.datetime.strptime(df.loc[acclim_synch_idx,'TIMESTAMP'], '%Y-%m-%d %H:%M:%S')
   
 # same for treat_time
try: 
    treat_synch_time = datetime.datetime.strptime(df.loc[treat_synch_idx,'TIMESTAMP'], '%Y-%m-%d %H:%M:%S.%f')
except ValueError:              
    treat_synch_time = datetime.datetime.strptime(df.loc[treat_synch_idx,'TIMESTAMP'], '%Y-%m-%d %H:%M:%S')
    
    
    
# derive timelag between synchronization and experimental start (for both acclimatization and treatment)
dt_acclim = (acclim_start_frame - acclim_synch_frame) * 1/24  # [seconds] this time needs to be added to get the actual start time of the experimental phase 
dt_treat = (treat_start_frame - treat_synch_frame) * 1/24  #

# get start_time of experiment (in timesystem of temperature probes)
acclim_start_time = acclim_synch_time + datetime.timedelta(0,dt_acclim) # add the two times
treat_start_time = treat_synch_time + datetime.timedelta(0,dt_treat)

#treat_synch_time = df.loc[[treat_synch_idx],['TIMESTAMP']]

## WRITE times to .txt file

outF = open(time_conversion_path, "w")
#for line in [header]: # , basestart]:
outF = open(time_conversion_path, "a")

outF.write("acclim_start_frame")    # write line to output file
outF.write("\n")                    # go to next line
outF.write(str(acclim_start_frame))

outF.write("\n")
outF.write("acclim_start_time")   
outF.write("\n")
outF.write(str(acclim_start_time))

outF.write("\n")
outF.write("treat_start_frame")   
outF.write("\n")
outF.write(str(treat_start_frame))

outF.write("\n")
outF.write("treat_start_time")  
outF.write("\n")
outF.write(str(treat_start_time))

outF.write("\n")
outF.write("acclim_synch_idx")
outF.write("\n")               
outF.write(str(acclim_synch_idx))

outF.write("\n")
outF.write("acclim_synch_frame")
outF.write("\n")                
outF.write(str(acclim_synch_frame))

outF.write("\n")
outF.write("acclim_synch_time")
outF.write("\n")
outF.write(str(df.loc[acclim_synch_idx,'TIMESTAMP']))

outF.write("\n")
outF.write("treat_synch_idx")   
outF.write("\n")
outF.write(str(treat_synch_idx))

outF.write("\n")
outF.write("treat_synch_frame")  
outF.write("\n")
outF.write(str(treat_synch_frame))

outF.write("\n")
outF.write("treat_synch_time")  
outF.write("\n")
outF.write(str(df.loc[treat_synch_idx,'TIMESTAMP']))

outF.close()                # close file

# write ACCLIM: Cut Temperature file accordingly and save it
start_acclim_idx  = math.trunc(acclim_synch_idx + ((acclim_start_frame - acclim_synch_frame) / 24  * 5)) # temp file has temporal res. of 5 meas./s
end_acclim_idx = start_acclim_idx + acclim_dur*60*5 + 1
acclim_temp_O2 = df.truncate(before=start_acclim_idx, after=end_acclim_idx)
acclim_temp_O2.to_csv(acclim_temp_path)

# write TREAT: Cut Temperature file accordingly and save it
start_treat_idx  = math.trunc(treat_synch_idx + ((treat_start_frame - treat_synch_frame) / 24  * 5))
end_treat_idx = start_treat_idx + treat_dur*60*5 + 1
treat_temp_O2 = df.truncate(before=start_treat_idx, after=end_treat_idx)
treat_temp_O2.to_csv(treat_temp_path)

# plot ACCLIM
fig_acclim_final = px.line(acclim_temp_O2, x=acclim_temp_O2.columns[0], y=acclim_temp_O2.columns[probe], title=acclim_temp_O2.columns[probe] + ' cut and saved ACCLIMATISATION period')
fig_acclim_final.show()

# plot TREATment
fig_treat_final = px.line(treat_temp_O2, x=treat_temp_O2.columns[0], y=treat_temp_O2.columns[probe], title=treat_temp_O2.columns[probe] + ' cut and saved TREATMENT cut period')
fig_treat_final.show()