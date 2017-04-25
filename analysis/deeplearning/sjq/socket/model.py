# -*- coding: utf-8 -*-
"""
Created on Thu December 29 13:51:56 2016

@author: Mat Rogers

"""
import numpy as np

class SocketSJQ(object):
    """
    Defective socket pins are almost always (mis)classified as Type-3 breaks by 
    the Socket SJR model.  To check for defective socket pins, run the Socket 
    SJR model, and if it returns a Type-3 break, run the Package SJQ model to 
    determine if the pin is normal or defective.
    """
    
    def __init__(self, device=None):
        
        self._info = "Socket SJQ classifier."

        # Model input
        from ..package import PackageSJQ
        self.packagesjq = PackageSJQ(device=device)
        
        from ...sjr.package import PackageSJR
        self.packagesjr = PackageSJR(device=device)
        
        from ...sjr.socket import SocketSJR        
        self.socketsjr = SocketSJR(device=device)

        
    def __call__(self, img, assign_label = True):
        assert img.shape == (220,220,3)
        clsf = self.socketsjr(img)
        # If socket sjr classification in [0,1] it can't be a defect
        if clsf in [0,1]:
            final_clsf = 2
        elif clsf in [2,3]:
            clsf_sjr = self.packagesjr(img)
            # If package sjr classification gives types 0, 4, or rejected 
            # the pin is probably brown and can't be a defect
            if clsf_sjr in [0,3,4]:
                final_clsf = 2
            elif clsf_sjr in [1,2]:
                prob_sjq = self.packagesjq(img, assign_label=False)
                # Pins with less than 60% chance of being normal probably aren't
                if prob_sjq[2] < .6:
                    prob_sjq[2] = 0
                final_clsf = np.argmax(prob_sjq)
        if assign_label == True:
            return final_clsf
        else:
            out = np.zeros(shape = 4)
            out[final_clsf]+=1
            return out