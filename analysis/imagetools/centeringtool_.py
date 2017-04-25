# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:49:41 2017

@author: mathew
"""

import cv2
import numpy as np

class CenteringTool(object):
    """
    Tool to crop an Intel pin to a fixed size about the pin.  The pin is located by
    thresholding the V-channel after shifting to HSV coordinates.  There
    is an optional threshold parameter for fine-tuning the positioning.
    """
    
    def __init__(self, cropSize):        
        self.cropSize = cropSize
        
    def crop(self, img, t = 30):
        if not self.cropSize:
            return img
        else:
            hsv = cv2.cvtColor((255*img[:,:,::-1]).astype(np.uint8),  cv2.COLOR_BGR2HSV)
            th = (hsv[:,:,2]>t).astype(np.uint8)
            _, cnt, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            # Find all contours which contain the central point
            cnt = [C for C in cnt if (cv2.pointPolygonTest(C, (img.shape[1]//2, img.shape[0]//2), False)==True) and (cv2.contourArea(C)>0)]
            # Select the contour with maximum area.
            if len(cnt) > 0:
                maxArea = np.max([cv2.contourArea(C) for C in cnt])
                cnt2 = [C for C in cnt if cv2.contourArea(C)==maxArea]
                M = cv2.moments(cnt2[0])
                Y = int(M['m10']/M['m00'])
                X = int(M['m01']/M['m00'])
            else:
                X = img.shape[0]//2
                Y = img.shape[1]//2
                
            cropX, cropY = self.cropSize
            if (X-cropX//2 <= 0) or (X+cropX//2 >= img.shape[0]) or (Y-cropY//2 <= 0) or (Y+cropY//2 > img.shape[1]):
                X = img.shape[0]//2
                Y = img.shape[1]//2            
                
            return img[X-cropX//2:X+cropX//2, Y-cropY//2:Y+cropY//2]
        