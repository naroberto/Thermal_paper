# -*- coding: utf-8 -*-
"""
Created on Thu Jul 15 15:50:40 2021

@author: Naudascher
# adapted from https://www.geeksforgeeks.org/displaying-the-coordinates-of-the-points-clicked-on-the-image-using-python-opencv/

# Goal: Correct for the fact that the Side camera was slighty moved, depending on the experimental day. 

# Description:
# - set left upper Aquarium corner as origin for rotation and coordinate system. 
# - select 5 or more points along the upper edge of the tank, the script will rotate the image so this line becomes horizontal
# - store that rotation angle 
# - Crop image to size: according to h, w, dx 
# - store rotation and crop parameters for further use in step_2
# - this only has to be run for the side came (in this publication)

# Output: The center of rotation (and origin of the coordinate system) and the size of each image, will be identical on each image and across experiments.

"""
# - do it for side cam (center of rotation is upper left corner of aquarium)
import cv2              # Import the OpenCV library for image processing
import numpy as np      # Import numpy for numerical operations
import os               # Import the os module for interacting with the operating system

# select input
date = '09_07'
top_cam = False     # select side cam
pre_rot_180 = 0     # Set to 1 only if the video needs to be pre-rotated -> fish acclimation area should always be on the left

# Select folder with calibration image
# TOP CAM
if top_cam: 
    # top camrun_1
    #in_dir:  str = r'D:\Thermal_exp\Final_runs\01_07\Final\crop_rot_params_top' #"\cal_img.tif"   
    in_dir = os.path.join('F:\Thermal_exp\Final_runs', date,'Final\crop_rot_params_top_run_1' ) # for other dates: in_dir = os.path.join('D:\Thermal_exp\Final_runs', date,'Final\crop_rot_params_top_run_1' )
    # cropping extent top_cam -> divideable by 2 !!    
    h = 204
    w = 1900
    dx = 570 # cropping extent will be translocated accordingly
    
# SIDE CAM
else:
    in_dir = os.path.join('F:\Thermal_exp\Final_runs', date,'Final\crop_rot_params_side_run_1' ) 
    # cropping extent side_cam -> divideable by 2 !!    
    h = 276
    w = 1840
    dx = 0
    pre_rot_180 = 0 # side cam always ok

# CREATE file path
in_path = os.path.join(in_dir,'cal_img.tif')
# output 
Nametxt  = os.path.join(in_dir,'params.txt')
out_path = os.path.join(in_dir, 'cal_img_rot_crop.tif')

# cropping extent top_cam 
# set area to be set to 0 below edge to avoid reflections on the wall
delta_Y = 0 #20 # Pixel

# GLOBAL VARIABLES
x_cord = []
y_cord = []
rot_angle_all = [] # angle between horizontal and shoreline

# FUNCTIONS --------------------------------------------------------
def click_event(event, x, y, flags, params):
# Function to display and store the coordinates of Rot_center and the rot_angle_
# First click -> center for rotation, click at the upper intersection of the arena
# Clicks after ->edge that will be horizontal after...
    
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:

        # displaying the coordinates on the Shell
        print(x, ' ', y)
        x_cord.append(x) # List with all x-coordinates
        y_cord.append(y) # List with all y-coordinates

        # displaying the coordinates on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(x) + ',' +
                    str(y), (x,y), font,
                    1, (255, 0, 0), 2)
        cv2.imshow('image', img) # show image again
        
        # calc rotation angle between side and horizontal
        if len(x_cord) >= 2  :
            deltaY = y - y_cord[0]
            deltaX = x - x_cord[0]
            angle = np.arctan(deltaY / deltaX) * 180 / np.pi
            rot_angle_all.append(angle)

def rotate_keep_orig_dim(image, angle, cX, cY):              # see also: https://www.pyimagesearch.com/2017/01/02/rotate-images-correctly-with-opencv-and-python/
    height, width = img.shape[:2]                            # grab the dimensions of the image
    M = cv2.getRotationMatrix2D((cX, cY), angle, 1.0)        # grab the rotation matrix (applying angle to rotate counter clockwise)
    return cv2.warpAffine(image, M, (width,height))          # perform the actual rotation and return the image, size of the image wo'nt have changed

# Driver function
if __name__=="__main__":
    
    img = cv2.imread(in_path, 1) # read the image
    
    if pre_rot_180:                 # some top_videos are fliped by 180 degrees !!!
        img = cv2.rotate(img, cv2.ROTATE_180) 
   
    height, width = img.shape[:2] # dimensions
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', width, height)
    cv2.imshow('image', img)
    cv2.setMouseCallback('image', click_event)     # setting mouse hadler for the image and calling the click_event() function
    cv2.waitKey(0)                                 # wait for a key to be pressed to exit
    cv2.destroyAllWindows()   # close the window

    # Calc mean rotation angle
    rot_angle_mean = round(np.mean(rot_angle_all),7)
    
img = cv2.imread(in_path, 1)
if pre_rot_180: # some top_videos are for some reason fliped by 180 degrees !!!
        img = cv2.rotate(img, cv2.ROTATE_180) 
        
height, width = img.shape[:2]
cv2.namedWindow('rotated', cv2.WINDOW_NORMAL)
cv2.resizeWindow('rotated', width, height)
#rotated = imutils.rotate(img, rot_angle_mean) # rotates around center of image!!

rotated = rotate_keep_orig_dim(img, rot_angle_mean,x_cord[0],y_cord[0])

cv2.imshow("rotated", rotated)
cv2.waitKey(0)

# Rotational center
x_R = x_cord[0] 
y_R = y_cord[0]

# this delta_y will be set to black (its the vertical height from lower edge to be blacked)
# d_y = 0 #20

# this will be the upper left corner (0,0) after cropping
y = y_R #- (h-d_y) # increase extent from y coord of rotational center so that width is visible
x = x_R #- int(w/2)

# This is the rotational center in coordinates after cropping and rotation
y_R_crop = y #h-d_y
x_R_crop = x #w/2

# Crop the image
rotated_crop = rotated[y:y+h, x-dx : x-dx+w]
height, width = rotated_crop.shape[:2]
cv2.namedWindow('rotated_cropped', cv2.WINDOW_NORMAL)
cv2.resizeWindow('rotated_cropped', width, height)
cv2.imshow('rotated_cropped', rotated_crop)
cv2.waitKey(0)
cv2.imwrite(out_path, rotated_crop) # Write the results to output location.
if rotated_crop.shape[1] < 1900 or rotated_crop.shape[0] < 204:
    print('relocate rot center')

# Print to console
#print('First point = selected Rotation Point (x,y) : ', x_R, ',', y_R) # + ',' + str(y_cord(1)))
#print('All rotation angles: ', rot_angle_all)
#print('Mean rotation angle: ', rot_angle_mean)
#print('Dimensions of cropped image (width,height) : ', w, ',', h)

## WRITE OUTPUT PARAMETERS TO .txt, (they will be used to process the entire video later...) 

outF = open(Nametxt, "w")
#for line in [header]: # , basestart]:
outF = open(Nametxt, "a")
outF.write("rotation center x-coordinate")
outF.write("\n")                # go to next line
outF.write(str(x_R))
outF.write("\n")
outF.write("rotation center y-cordinate")
outF.write("\n")
outF.write(str(y_R))
outF.write("\n")
outF.write("rotation angle")   # write line to output file
outF.write("\n")
outF.write(str(rot_angle_mean))


outF.write("\n")
outF.write("cropped_width")   # write line to output file
outF.write("\n")
outF.write(str(w))

outF.write("\n")
outF.write("cropped_height")   # write line to output file
outF.write("\n")
outF.write(str(h))

outF.write("\n")
outF.write("dx")   # write line to output file
outF.write("\n")
outF.write(str(dx))

outF.write("\n")
outF.write("pre_rot_180")   # write line to output file
outF.write("\n")
outF.write(str(pre_rot_180))
outF.close()                # close file

print(" params saved to: ")
print(Nametxt)

cv2.destroyAllWindows()
