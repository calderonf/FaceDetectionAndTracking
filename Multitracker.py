#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:27:12 2020

@author: francisco
"""
import cv2
import sys
from random import randint
from TrackerUtils import createTrackerByName
import  camutils as cu

 
# Create a video capture object to read videos
cap = cv2.VideoCapture(0)
cu.setfourccmjpg(cap)
cu.setRes1080pFPS30(cap)
 
# Read first frame
success, frame = cap.read()
# quit if unable to read the video file
if not success:
    print('Failed to read video')
    sys.exit(1)
else:
    ## Select boxes
    bboxes = []
    colors = [] 
     
    # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
    # So we will call this function in a loop till we are done selecting all objects
    while True:
      # draw bounding boxes over objects
      # selectROI's default behaviour is to draw box starting from the center
      # when fromCenter is set to false, you can draw box starting from top left corner
      bbox = cv2.selectROI('MultiTracker', frame)
      bboxes.append(bbox)
      colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
      print("Press q to quit selecting boxes and start tracking")
      print("Press any other key to select next object")
      k = cv2.waitKey(0) & 0xFF
      if (k == 113 or k==ord("Q")):  # q is pressed
        break
     
    print('Selected bounding boxes {}'.format(bboxes))
    
    
    
    # Specify the tracker type
    trackerType = "MOSSE"   
     
    # Create MultiTracker object
    multiTracker = cv2.MultiTracker_create()
     
    # Initialize MultiTracker 
    for bbox in bboxes:
      multiTracker.add(createTrackerByName(trackerType), frame, bbox)
      
      
      # Process video and track objects
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
       
        # get updated location of objects in subsequent frames
        success, boxes = multiTracker.update(frame)
         
        # draw tracked objects
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
             
        # show frame
        cv2.imshow('MultiTracker', frame)
           
        # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
            break
        
    cap.release()
    cv2.destroyAllWindows()