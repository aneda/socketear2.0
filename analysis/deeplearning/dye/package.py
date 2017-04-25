# -*- coding: utf-8 -*-
"""
Created on Thu December 29 13:51:56 2016

@author: Mat Rogers

"""
import numpy as np
import cv2
from os.path import join, split
import importlib

class PackageDye(object):
    """
    Package dye stain segmentation model.  
    """
    
    def __init__(self, device=None):

        if device is not None:
            import theano.sandbox.cuda
            theano.sandbox.cuda.use(device)
        
        # Set parameters folder
        caller = importlib.import_module(self.__module__)
        
        self.current_dir, _ = split(caller.__file__)
        
        self.params_folder = join(self.current_dir, 'params')
        
        # Load SJR classifier
        from ...deeplearning.sjr.package import PackageSJR
        self.packagesjr = PackageSJR(device=device)
        
        # Load segmentation models for package pins types 1, 2, 3, 4, and rejected
        from .segModels import PinSegmentation
        self.segmodels = [PinSegmentation(join(self.params_folder, '20170311_22h19m32s_390135','params.dill'), device, transform = [0,3,1]),  #! -- Model 13 achieved 75% on type-1 pins on a difficult test set
                          PinSegmentation(join(self.params_folder, '20170303_14h43m13s_760580','params.dill'), device),
                          PinSegmentation(join(self.params_folder, '20170306_16h45m58s_911288','params.dill'), device),
                          None #! -- No good model yet for type 4 pins
                         ]
                         
    def __fallback__(self, img):
        """
        Pathetic fallback model.  Sorry...
        """
        R, G, B = img.transpose(2,0,1)
        X, Y, _ = img.shape
        pin = np.zeros(shape = (X, Y))
        cv2.circle(pin, (Y//2, X//2), X//3, (1,1,1), -1)
        
        dye = 1*(pin*(R>.3)*(G<.3))
        segm = pin + 2*pin*dye
        return segm
                         
    def __pred__(self, segm, sjr):
        """
        Convert the segmentation mask into a prediction
        
        Dye stain mask conventions are
            0 = background
            1 = pin without dye
            2 = pin exterior (for type-3)
            3 = red dye
        """
        dyelabels = {0:'A', 1:'B', 2:'C', 3:'D', 4:'E'}        
        
        eps = 10**-6
        
        # Strip out all contours on the outside.  These shouldn't factor into the
        # prediction, since they typically come from other pins.
        
        X, Y = segm.shape
        _, cnt, _ = cv2.findContours((segm>0).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnt = [C for C in cnt if cv2.pointPolygonTest(C, (X//2, Y//2), False) == True]
        Z = np.zeros(shape = (X, Y))
        cv2.drawContours(Z, cnt, -1, (1,1,1), -1)
        if np.sum(Z) > 0:
            segm = Z*segm
        
        if sjr in [0,1,3]:
            percnt = int(100*np.sum(segm>1)/(np.sum(segm>0)+eps))
            print(percnt)
        elif sjr in [2,4]:
            percnt = int(100*np.sum(segm==3)/(np.sum(segm==1)+np.sum(segm==3)+eps))
        
        pred = np.min([4, percnt//20])
        
        return dyelabels[pred]
        
    def __call__(self, img, sjr_pred = None, return_mask = False):
        assert img.shape == (224,224,3)
        
        # Only run the sjr classifier if the classification is unknown
        if sjr_pred is None:
            sjr_pred = self.packagesjr(img[2:-2,2:-2])
        
        # Run the appropriate segmentation model.  If the pin is rejected
        # by the sjr classifier, then default to type 3 segmentation model.
        # For type-4 breaks we use type-1 model to find the pin + threshold to find dye.
        if sjr_pred in [0,1,2]:
            segm = self.segmodels[sjr_pred](img)
        elif sjr_pred == 3:
            segm = self.__fallback__(img)
        else:
            segm = self.segmodels[2](img)
                
        if return_mask == False:
            return self.__pred__(segm, sjr_pred)
        else:
            return segm, sjr_pred, self.__pred__(segm, sjr_pred)