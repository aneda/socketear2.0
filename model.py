# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 12:17:59 2017

@author: Mat Rogers
"""

from analysis.imagetools import CropTool
from analysis.imagetools import StitchTool
from analysis.imagetools import CenteringTool
import cv2
import numpy as np
import pandas as pd
import os
from os.path import splitext, join

class Model(object):
    
    def __init__(self, sampleID, analysisType, guide, addedCrop, rawImgPath, segDataPath, cropSavePath, savePath, device=None):
        
        self.sampleID = str(sampleID)
        self.analysisType = analysisType
        
        if self.analysisType in ['PackageSJR', 'PackageSJQ']:
            from analysis.deeplearning.sjq.package import PackageSJQ
            from analysis.deeplearning.sjr.package import PackageSJR
            from analysis.deeplearning.dye.package import PackageDye
            self.sjqclassifier = PackageSJQ(device=device)
            self.sjrclassifier = PackageSJR(device=device)
            self.dyeclassifier = PackageDye(device=device)
        elif self.analysisType in ['SocketSJR', 'SocketSJQ']:
            from analysis.deeplearning.sjq.socket import SocketSJQ
            from analysis.deeplearning.sjr.socket import SocketSJR
            from analysis.deeplearning.dye.socket import SocketDye
            self.sjqclassifier = SocketSJQ(device=device)
            self.sjrclassifier = SocketSJR(device=device)
            self.dyeclassifier = SocketDye(device=device)
        else:
            raise ValueError('Please select either PackageSJR, PackageSJQ, SocketSJR, or SocketSJQ')

        self.guide = guide
        self.addedCrop = addedCrop
        self.cropSavePath = cropSavePath
        self.cropper = CropTool(sampleID, segDataPath, rawImgPath, cropSavePath)
        self.centerCrop = CenteringTool(addedCrop)
        self.savePath = savePath
        self.stitcher = StitchTool(sampleID, guide, segDataPath, rawImgPath)
        
    def export(self, sjqClsf, sjrClsf, dyeClsf, stchdImg, pos):
        import pandas as pd
        output = []
        for pinName in sorted(pos.keys()):
            row, col = str.split(pinName, '_')[0:2]
            sjqpred = None
            sjrpred = None
            dyepred = None
            X = None
            Y = None
            if pinName in sjqClsf.keys(): sjqpred = sjqClsf[pinName]
            if pinName in sjrClsf.keys(): sjrpred = sjrClsf[pinName]
            if pinName in dyeClsf.keys(): dyepred = dyeClsf[pinName]
            if pinName in pos.keys(): X, Y = pos[pinName]
            output += [[row, col, X, Y, sjqpred, sjrpred, dyepred]]
        
        df = pd.DataFrame(output)
        df.columns = ['Row', 'Col', 'StitchedX', 'StitchedY', 'SJQ', 'SJR', 'DYE']
        df.to_csv(join(self.savePath, 'classification.csv'), index=False)
        cv2.imwrite(join(self.savePath, 'stitched.png'), 255*stchdImg[:,:,::-1])

    
    def __call__(self, saveResults):
        # Crop all raw images to self.cropSavePath
        self.cropper.crop()

        # List all tif images in self.cropSavePath
        crops = os.listdir(self.cropSavePath)
        crops = [c for c in crops if splitext(c)[1] == '.tif']
        
        # Find all focus layers
        firstLayer = [c for c in crops if '1.tif' in c]
        focusLayers = list(set([int(str.split(splitext(c)[0], '_')[-1]) for c in crops]))        
        
        # Classify all pins.  If mode is SJQ run both SJR and SJQ models.
        # If mode is SJR run SJR and dye-stain models.
        sjqClsf = {}
        sjrClsf = {}
        dyeClsf = {}

        for imgName in firstLayer:
            pinName = '_'.join(str.split(str.split(imgName)[0], '_')[0:2])
            if pinName not in self.guide.pins:
                raise ValueError('Unknown pins present.  Please verify that segmentation file and stage file are for an indentical package.')
                
            for l in focusLayers:

                imgPath = join(self.cropSavePath, imgName)
                imgPath = str.replace(imgPath, '1.tif', str(l)+'.tif')
                img = cv2.imread(imgPath)[:,:,::-1]/255.
                img = cv2.resize(self.centerCrop.crop(img), (226,226))
                if pinName not in sjrClsf.keys():
                    if 'SJQ' in self.analysisType:
                        sjqClsf.update({pinName: self.sjqclassifier(img[3:-3,3:-3], assign_label=False)})
                        print('sjqpred = {}'.format(sjqClsf[pinName]))
                        sjrClsf.update({pinName: self.sjrclassifier(img[3:-3,3:-3], assign_label=False)})
                    elif 'SJR' in self.analysisType:
                        sjrpred = self.sjrclassifier(img[3:-3,3:-3], assign_label=False)
                        sjrClsf.update({pinName: sjrpred})
                        print('sjrpred = {}'.format(sjrpred))
                        dyeClsf.update({pinName: self.dyeclassifier(img[1:-1,1:-1], sjr_pred=np.argmax(sjrpred), return_mask=False)})
                        print('dyepred = {}'.format(dyeClsf[pinName]))
                else:
                    # !-- To speed up run-time we only use the first focus layer for SJR classifications.
                    if 'SJQ' in self.analysisType:
                        sjqClsf[pinName] += self.sjqclassifier(img[3:-3,3:-3], assign_label=False)
                        print('sjqpred = {}'.format(sjqClsf[pinName]))

            if pinName in sjqClsf.keys(): sjqClsf[pinName] = np.argmax(sjqClsf[pinName])
            if pinName in sjrClsf.keys(): sjrClsf[pinName] = np.argmax(sjrClsf[pinName])
        
        stchdImg, pos = self.stitcher.stitch()

        if saveResults == True:
            self.export(sjqClsf, sjrClsf, dyeClsf, stchdImg, pos)
        else:
            return sjqClsf, sjrClsf, dyeClsf, stchdImg, pos