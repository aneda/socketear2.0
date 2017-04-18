# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 10:30:00 2015

@author: Mat Rogers
"""
import cv2
import numpy as np

class DrawPredictions(object):

    def __init__(self, guide, mode):
        """
        Draws a pin mask given a dictionary of SJQ predictions.  If
        ground-truth is given, the tool draws circles around errors.

        Input:
            guide = pin guide object

            shape = [l, w], where l and w are the length and width of the label

            pred = {pin: clsf}, where pin = pin name, and
                    clsf = prediction from the deep learning model.

            truth = {pin: clsf}, where pin = pin name, clsf = true
            classification
        """

        self.guide = guide
        
        self.mode = mode
        
        if self.mode == 'SJQ':
            self.colors = {0: (1, 1, 0), 1: (0, 1, 0), 2: (0, 0, 0), 3: (1, 0, 0),
                       4: (0, 0, 1)}
        if self.mode == 'SJR':
            self.colors = {0: (0, 0, 1), 1: (1, 0, 0), 2: (1, 1, 0), 3: (0, 1, 0),
                       4: (0, 0, 0)}
            self.dyecolors = {'A':(1,1,0), 'B':(1,.75,.5), 'C':(1,.5,0), 'D':(0,1,1), 'E':(1,0,0), 'F':(1,1,1)}

    def draw(self, shape=1000, pred=None, dyepred=None):

        L, W = self.guide.dimensions 
        R = self.guide.pinRadius
        r = int(1/5*shape*R/ (L * W)**(.5))
            
        maxX = 0
        maxY = 0
        for pin in self.guide.pins:
            X, Y = self.guide.position(pin)
            if X > maxX: maxX = X
            if Y > maxY: maxY = Y
        
        if maxX > maxY:
            l = shape
            w = int(shape*maxY/maxX)
        else:
            w = shape
            l = int(shape*maxX/maxY)
            
        # Add about a 3% buffer around the pins
        l = int(l*(1.03))
        w = int(w*(1.03))

        # Draw the label with a grey background.
        lbl = 192 / 255. * np.ones(shape=(l, w, 3))

        for pin in self.guide.pins:
            cls = pred[pin]
            X, Y = shape*self.guide.position(pin)
            X = int(X)
            Y = int(Y)
            clr = self.colors[cls]
            cv2.circle(lbl, (Y, X), 5*r, clr, -1)
            if dyepred is not None:
                cls = dyepred[pin]
                clr = self.dyecolors[cls]
                cv2.circle(lbl, (Y, X), 5*r+2, clr, 3)
                cv2.circle(lbl, (Y, X), 5*r+5, (0, 0, 0), 1)
            cv2.circle(lbl, (Y, X), 5*r, (0, 0, 0), 1)

        return lbl

    def __call__(self, shape=1000, pred=None, dyepred=None):

        if dyepred is not None:
            assert len(dyepred) == len(pred)

        # Draw an Intel-style pin mask
        label = self.draw(shape, pred, dyepred)

        return label