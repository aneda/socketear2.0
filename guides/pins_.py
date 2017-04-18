# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 11:04:08 2016

@author: mathew
"""
import cv2
import numpy as np

class Pins(object):
    """
    Base class to return pins and templates associated with Intel boards.
    """
    def __init__(self, pins, dimensions, radius):
        """
        Expects a dictionary of pin names and position vectors, where position
        vectors are scaled between zero and one.  Board dimensions and pin radii
        should have the same units (e.g. pixels or microns).
        """
        self._pins = pins
        self._dimensions = dimensions
        self._radius = radius
    
    @property
    def pins(self):
        if self._pins is not None:
            return sorted(list(self._pins.keys()))
        else:
            raise NotImplementedError()

    @property
    def pinRadius(self):
        return self._radius
        
    @pinRadius.setter
    def pinRadius(self, value):
        self._radius = value
    
    @property
    def dimensions(self):
        return self._dimensions

        
    def position(self, pin):
        if pin in self._pins.keys():
            return self._pins[pin]
        else:
            raise ValueError('Unknown pin')
    
    def template(self, shape, return_img=True):
        R = np.max([1, int(shape[0]/self.dimensions[0]*self.pinRadius)])
        coords = {}        
        for pin in self.pins:
            x, y = self.position(pin)
            X = int(shape[0]*x)
            Y = int(shape[1]*y)
            coords.update({pin:(X, Y)})
        
        if return_img == True:
            tmplt = np.zeros(shape = shape)
            for pin in self.pins:
                X, Y = coords[pin]
                cv2.circle(tmplt, (Y, X), R, (1,1,1), -1)        
            return tmplt
        else:
            return coords
        
    