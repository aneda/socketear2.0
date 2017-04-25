# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:49:41 2017

@author: mathew
"""

import cv2
import pandas as pd
import numpy as np
import os
from os.path import join, isdir, splitext

class CropTool(object):
    
    def __init__(self, sampleID, segDataPath, imgPath, savePath=None):
        
        self.sampleID = str(sampleID)

        df = pd.read_csv(segDataPath, index_col=False)
        self.segData = np.array(df)
        
        self.imgPath = imgPath

        if savePath is None: savePath = join(self.imgPath, 'pins')
        self.savePath = savePath
        
    
    def crop(self, includeSampleID=False):
        
        # Create the path for cropped images
        if not isdir(self.savePath):
            os.makedirs(self.savePath)
        
        # Read all of the available big images
        bigImages = os.listdir(self.imgPath)
        bigImages = [b for b in bigImages if splitext(b)[1] == '.tif']
        
        for img in bigImages:
            bigImg = cv2.imread(join(self.imgPath, img))
            # Get the number of the image
            j = int(str.split(img, '_')[0])
            # Get the number of the focus layer
            layer = int(str.split(splitext(img)[0], '_')[-1])
            # Select the appropriate segmentation data
            J = np.where(self.segData[:,0] == j)
            pins = self.segData[J]
            # Crop and save all pins
            for pin in pins:
                fieldNumber, Row, Col, startRow, stopRow, startCol, stopCol = pin
                pinImg = bigImg[startRow:stopRow,startCol:stopCol]
                pinName = '_'.join([str(Row),str(Col),str(layer)]) + '.tif'
                if includeSampleID: pinName = '_'.join([self.sampleID, pinName])
                cv2.imwrite(join(self.savePath, pinName), pinImg)
                
if __name__ == '__main__':
    
    sampleID = '02061'
    imgPath = '/media/mnt/datasets/IntelStitching/02061/20'
    segDataPath = '/home/mathew/Documents/experiments/experiments/mat/intel_stitching/Pattern/R3W Socket_pack/R3W Socket_pseudo_mosaic_segmentation_data_pack_20X.csv'
   
    savePath = '/media/mnt/datasets/IntelStitching/02061/pins'
    
    from time import time
    st = time()
    cropper = CropTool(sampleID, segDataPath, imgPath, savePath)
    cropper.crop(includeSampleID=False)
    sp = time() - st
    print('Cropping took {} seconds'.format(sp))