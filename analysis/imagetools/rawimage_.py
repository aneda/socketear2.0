# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 11:04:08 2016

@author: mathew
"""
import cv2

class RawImage(object):
    """
    Base class to return a raw image and pin positions attached to the image.
    """
    def __init__(self, pins, image):
        """
        Expects a dictionary of pin names and position vectors, where position
        vectors are in pixels, relative to the large image.  Pin radius should
        be in pixels.
        """
        self._pins = pins
        self._image = image
    
    @property
    def pins(self):
        if self._pins is not None:
            return sorted(list(self._pins.keys()))
        else:
            raise NotImplementedError()
            
    def position(self, pin):
        if pin in self._pins.keys():
            return self._pins[pin]
        else:
            raise ValueError('Unknown pin')
    
    @property
    def img(self):
        return cv2.imread(self._image)[:,:,::-1]/255.
        
    