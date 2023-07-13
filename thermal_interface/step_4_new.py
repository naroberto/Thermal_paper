
""" -------------- NEW VERSION of step_4 --------------------

Created on Wed Feb 1 11:11:01 2023

@author: rob

Goal:
    - get the gradient line (laplacian) for each frame, 
    - (here we store) x and y coords of the laplacian for each time step
    - we post-process this so the line is continous and does not contain wrong detections at the water-line or bottom of the tank
    - output this as exp_id_Treat_grad.npy,
    
"""
import pandas as pd
import numpy as np
import os
import cv2 as cv2
from time import process_time
cv2.destroyAllWindows()  
from scipy import ndimage as nd
t1_start = process_time()

# INPUTS # note that exp 21 is broken !  raw images in: (/Volumes/4_Results/Backup_thermal/all_data/Final_runs/05_07/Final/run_1/treat_side_red)
exps      = [37] # [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,26,27,28,29,30,31,32,      #[1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] #[17]        # [5,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45] # cold: [1,2,3,4,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] # note that control does not have a thermal signal!!
treat_dur = 20         # [minutes]

# conversion constants
meta_real_width   = 202    # cm this paramter is the width of the ima ges, it shoudl remain const. and is used for each experiment in the tracking (TRex procedure), we use it to convert pix  to cm
frame_width  =     1840   # pixel constant
frame_height =      276    # pixel constant
pix_per_cm   = frame_width/meta_real_width

# show intermediate image analysis steps steps 
save_data =      True
show_workflow =  False
save_post_process_data = True

# save some output images as control!!!
save_imgs =      False
store_ith_img =  5 * 24 # 1 frame every 5 seconds, just as a visual control! -> this will save 240 (RGB) images per experiment!

# params - # don't change those!
dt_T =   0.2          # recorded @ 5 Hz 
dt_ink = 1/24       # recorded @ 24 Hz

# subtraction params
R_zero = 20         # needs to be the same in step_1; this will be the new zero it was 0 before

# pessential param for greyscale binarysation: leave it cosnt for all exps! It defines the greyscale value for image binarysation and therefore determines where the gradeint lies and all plunge statistic is dependent on it!
thresh_grey = 175  # derive that value from turning point of polynomial fit, it determines where the gradient line exactyl lies and is exp specifc to some degree!

# input, adapdet to run in MAC
img_path_base = r'/Volumes/4_Results/Backup_thermal/all_data/Final_runs/'             # input images (from disk 4_Results)   # img_path =  /Volumes/4_Results/Backup_thermal/all_data/Final_runs/05_07/Final/run_2
master =        pd.read_excel(r'/Volumes/thermal_tr/thermal/thermal_master.xlsx')     # path =          r'/Volumes/thermal_tr/thermal'

# output
out_path =      r'/Volumes/thermal_tr/thermal/T_data/laplacians/'                     # here we store the main output, which is grad(x,y)(t) for each experiment
img_out =       r'/Volumes/thermal_tr/thermal/T_data/laplacians/laplacian_imgs/'

print('--- DERIVE get gradient line ---')
print('R_zero =    ' + str(R_zero))
print('exps =      ' + str(exps))
print('Saving data and graphs: ' + str(save_data))
print('Saving images:          ' + str(save_imgs))
print('-----------------------------------------')

phase = 'treat'

#%% Functions

# function
def interpolate_nan(y):  # interpolate nans -> no nans anymore: source: https://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array  
    nans = np.isnan(y)
   
    x = lambda z: z.nonzero()[0]
    
    y[nans]= np.interp(x(nans), x(~nans), y[~nans])
    return y.round(3)

from collections import Counter

# functions for gradient post processing
def non_unique(lst):
  return [item for item, count in Counter(lst).items() if count > 1] # print(non_unique([1, 2, 2, 3, 4, 4, 5]))

def grad_filter_warm(x,y):               # input in pixel units
    for i in non_unique(x):         # list containing all non-unique x-values, hier hat y(x) mind. 2 lösungen!
        idx = np.where(x == i)[0]   # array indices of non-unique values
        y[idx] = np.max(y[idx])     # replace all non-unique values wiht the max(y) value among those, as the wrong line at the water surface has low values
    return y

def smooth_grad_warm(y, y_cm_thresh): # inout in pix units
    y[np.where(y < pix_per_cm * y_cm_thresh )] = np.NaN  # remove values on the water surface are wrong... we remove them 
    
    if any(np.isfinite(y)):
        y_new = interpolate_nan(y)
    else: # very very rarely this occurs... but it breaks otherweise
        y_new = y 
    return y_new # previously marken nans will be overwirtten by neighborhood interpolation ... 

def grad_filter_cold(x,y):               # input in pixel units
    for i in non_unique(x):         # list containing all non-unique x-values, hier hat y(x) mind. 2 lösungen!
        idx = np.where(x == i)[0]   # array indices of non-unique values
        y[idx] = np.min(y[idx])     # replace all non-unique values wiht the max(y) value among those, as the wrong line at the water surface has low values
    return y

def smooth_grad_cold(y, y_cm_thresh_lower):              # input in pix units
    y[np.where(y > pix_per_cm * y_cm_thresh_lower )] = np.NaN  # remove values on the bottom of tank larger then  y_cm_thresh_lower 
    return interpolate_nan(y) 

def subtract_rescale(r,g,R_zero):
    
        # subtract red from green channel 
        res = np.array(g.astype(np.int32) -  r.astype(np.int32))
        
        #min_pix_value = np.min(res) # check if rescaling makes sense
        #if min_pix_value <  - R_zero:
            #print('this should not be below -20: ', min_pix_value)
        
        
        #print(res)
        
        # Fre approach - reshift pixel values to positive values
        #R_zero = 20  # -> see function input 
        R_min = 0
        R_max = 255 
        
        # rescale to 8-bit image
        scale_frame = res + R_zero  # shift to positve values 
        scale_frame = np.where(scale_frame < R_min, R_zero, scale_frame) # get values that are still negative
        scale_frame = np.where(scale_frame > R_max, R_max, scale_frame) # get values that are too large
    
        
        return cv2.bitwise_not(scale_frame.astype('uint8')) # convert to 8bit and invert it so ink is 
    
    
def get_gradient (r_list, g_list, thresh_grey):
        
        grad = {}
 
        i , j   = [], []

        total_frames = len(g_list)-1
        print('-> processing frame: ')
        
        
        for i,j,t in zip(r_list,g_list,range(0,total_frames)):   # grab red and green images for through all times, bth list have the sam length as per preprocessing
            
            grad[t] = {}
            print("\r" + str(t) + ' / ' +  str(total_frames) , end = "\r" )
            
            # load intantaneous image
            r = cv2.imread(os.path.join(r_path, i),0)    # red channel as greyscale
            g = cv2.imread(os.path.join(g_path, j),0)    # green ch as grey
        
            # convert to signal 
            ink = subtract_rescale(r,g,R_zero)
                  
            # create white inside mask
            mask_1 = np.zeros(ink.shape[:2], dtype=np.uint8)  # empty mask
            
            # threshhold according to sattel point  thresh_grey is crucial here !
            binary = np.where(ink > thresh_grey,255, mask_1) 
            
            # fill holes
            filled = nd.morphology.binary_fill_holes(cv2.bitwise_not(binary),structure=np.ones((3,3)))  #, structure=None, output=None, origin=0)[source]
            
            # convert bool img to 8 bit image
            f = np.where(filled == True,255,0).astype('uint8')
            
            # dilate erode twice ! -> to enlarge grad on the borders! 
            d_e = f.copy()
            
            kernel = np.ones((10,10), np.uint8)
            d_e = cv2.dilate(d_e, kernel, iterations=1)
            d_e = cv2.erode(d_e, kernel, iterations=1)
            
            kernel = np.ones((20,20), np.uint8)
            d_e = cv2.dilate(d_e, kernel, iterations=1)
            d_e = cv2.erode(d_e, kernel, iterations=1)
            
            # get laplacian and draw it (in white)
            laplacian = cv2.Laplacian(d_e,cv2.CV_64F).astype('uint8') # the gradient line is white (255),, sobelx = cv2.Sobel(d_e,cv2.CV_64F,1,0,ksize=5)  , sobely = cv2.Sobel(d_e,cv2.CV_64F,0,1,ksize=5)
            
            # filter out small line objects and keep only the longest connected line as gradient!
            l = laplacian.copy()                                                 # we need to get rid of some smaller objects that are partially detected and not part of the gradient (in corners or at the top of the water surface)
            nb_edges, output, stats, _ = cv2.connectedComponentsWithStats(l, connectivity=8)  #get all connected components in the image with their stats (including their size, in pixel) ,# output is an image where every component has a different value  
            size = stats[1:,-1]                                                     # extracting the line length of each detected line which coudl be potetianlly the main gradeitn line... 
            if len(size) > 1:                                                     # check only if there are more then 1 line objects    # adapted from: https://stackoverflow.com/questions/41675940/opencv-removing-the-independent-short-line-in-an-image
                
                for e in range(0,nb_edges-1):                                    # iterate through all line objects
                    if size[e] < np.max(size):                                    # if the line length is smaller then the max it is not hte main gradient line! -> drop it    
                        l[output == e + 1] = 0

            # get x,y coords of laplacian (all the white pixels)
            coords = np.where(l == 255)
            #print(coords)
            
            # grad.append(coords)
            grad[t] = coords
            
            # draw on original image
            gray = ink.copy().astype('uint8')
            ink_grad =  cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
            ink_grad[l == 255] = (0,0,255)
            
            
            if show_workflow:
                cv2.putText(ink_grad,'Laplacian',(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),thickness=2)
                cv2.putText(ink,'ink signal, frame: ' + str(t) ,(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),thickness=2)
                cv2.putText(l,'Cleaned Laplacian',(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),thickness=2)
                cv2.putText(binary,'binarised, thresh = ' + str(thresh_grey),(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),thickness=2) # text
                cv2.putText(f,'filled holes' ,(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),thickness=2) # text
                cv2.putText(d_e,'Dilated , Eroded ',(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),thickness=2) # text
                cv2.putText(laplacian,'Laplacian',(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),thickness=2) # text
                
                im_combined = cv2.vconcat([ink.astype('uint8'), binary.astype('uint8'), np.invert(f).astype('uint8'), np.invert(d_e).astype('uint8'), np.invert(laplacian).astype('uint8'),np.invert(l).astype('uint8'),ink_grad])
                #im_combined_short = cv2.vconcat([cv2.cvtColor(ink,cv2.COLOR_GRAY2RGB),ink_grad])
                
                cv2.imshow('workflow', im_combined)  # show workflow !
                cv2.waitKey(2)
                
            if save_imgs and t%store_ith_img == 0:  # stored only every ith.   
                cv2.putText(ink_grad,'Laplacian',(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),thickness=2)
                
                # create dir
                path = os.path.join(img_out,'exp_' + str(exp))
                if not os.path.exists(path): os.makedirs(path)
                
                # store frame
                cv2.imwrite(path +'/f_' + str(t) + '.tif', ink_grad) # to save workflow
                    
        return grad             # this contains the laplacian for each frame, dtype = dictionary 

            
 
#%% Part 1 - main loop - get laplacian line form images
for exp in exps: 
    
    # exp specifics
    exp_props = master[master['exp_ID']==exp]                             # respective row in master file 
    date =      exp_props.loc[:, 'date'].apply(str).squeeze()
    run =       'run_' + exp_props.loc[:, 'run'].apply(str).squeeze()
    
    # path to images                                                                            # Temperatrue data, not needed here..     # T_file_name = 'treat_temp_data_' + date + '_' + run +'.txt' # we only run this for treatment!! no phase loop needed
    r_path =   os.path.join(img_path_base, date,'Final', run , 'treat_side_red') #/00000_red_12_41_04_866667.tif
    g_path =   os.path.join(img_path_base, date,'Final', run , 'treat_side_green')
    
    """
    r_path =   os.path.join(img_path, date, run , phase + '_side_red') #/00000_red_12_41_04_866667.tif
    g_path =   os.path.join(img_path, date, run , phase + '_side_green')
    """
    print('exp_' + str(exp) + ' ---- collecting img names')
    r_list = os.listdir(r_path) # red frames  # list of all frames 
    g_list = os.listdir(g_path) # green frames

    print('Get laplacian')  # get gradient for this experiment, key is the frame, this can be used for all 4 fish in this run... 
    grad = get_gradient(r_list,g_list,thresh_grey)   #grad = get_gradient(r_list,g_list,thresh_grey) # to run supsequence r_list[:400] ,g_list[:400]

    if save_data: 
        output_npz_file = out_path + 'exp_' + str(exp) + '_laplacian' # treatment only...
        np.save(output_npz_file, grad)
        print('Laplacian saved to:'  )
        print(output_npz_file)

# Stop the stopwatch / counter
t1_stop = process_time()
print("Elapsed time in minutes: ", round((t1_stop-t1_start) / 60,1) )

#%% Part 2 - Post_process - this can be run independently!
print('Post-process laplacian') 

for exp in exps: 
    print('exp_' + str(exp) )
    
    in_dir = out_path # reload previously saved file
    grad   = np.load(in_dir + 'exp_' + str(exp) + '_laplacian.npy',allow_pickle=True).item() # load raw version that was created in the step above... 
    
    # Post-processing, goal: remove water level line which was sometimes detected
    grad_post = {}

    for i in range(0,len(grad)): # each fram has one gradient line
        
        print(i,len(grad))
        grad_post[i] = {} 
        x_ =   grad.get(i)[1]       # x-coords of grad line at this time                               # unit already in pixel
        y_ =   grad.get(i)[0]       # y-coords ...
        
        # reorder 
        y_sort = y_[np.argsort(x_)].astype(float) # reorder y based on sorted x values so y becomes continuous spatial function of x
        x_sort = x_[np.argsort(x_)].astype(float) # here we do not need nan...
        
        # filter out water-line, (over write non-unique values with max(y) )
        if exp > 24:        # warm treats
            y_grad_f = grad_filter_warm(x_sort,y_sort)                  # we hereby kick out the wrong water-line, hence there are some wrong points remaining, those we will smotth out later
            y_grad   = smooth_grad_warm(y_grad_f, y_cm_thresh = 5)       # remove outliers
            
        else:               # cold treats remove outliers based on other criteria (see function)
            y_grad_f = grad_filter_cold(x_sort,y_sort)
            y_grad   = smooth_grad_cold(y_grad_f,y_cm_thresh_lower = 27) # removes outliers
              
        x_grad = x_sort
        
        grad_post[i] = [x_grad,y_grad] # this is the final output 
        
    if save_post_process_data: 
        output_npz_file = out_path + 'exp_' + str(exp) + '_laplacian_post' # treatment only...
        np.save(output_npz_file, grad_post)


print('------- step_4 complete -------')