# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:08:05 2016

@author: mathew
"""

import pandas as pd
import numpy as np
from os.path import abspath, dirname, join
from guides.pins_ import Pins

class GeneralGuide(Pins):
    
    def __init__(self, csvpath, b2p_ratio):
        df = pd.read_csv(csvpath)
        row, col, Y, X = np.array(df)[:,0:4].transpose(1,0)
        # Scale pin cooordinates between zero and one.  Reverse Y-direction
        # to match up with existing photos of boards.
        S = np.max([np.max(Y)-np.min(Y), np.max(X)-np.min(X)])
        Y = (Y - np.min(Y))/S
        X = 1 - (X - np.min(X))/S
        # Add an offset of 1.5% on the sides and 3% on the top and bottom.
        X = (X + .03)/1.03
        Y = (Y + .03)/1.03
        pins = []
        for j in range(len(row)):
            pins += [[str(row[j])+'_' + str(col[j]), np.array([X[j], Y[j]])]]
        
        pins = dict(pins)
        
        super(GeneralGuide, self).__init__(pins, [b2p_ratio, b2p_ratio], 1)
        
    