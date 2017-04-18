# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 10:08:05 2016

@author: mathew
"""

import pandas as pd
import numpy as np
from os.path import abspath, dirname, join
from guides.pins_ import Pins

class R6m(Pins):
    
    data_path = join(dirname(abspath(__file__)), 'data')

    def __init__(self):
        df = pd.read_csv(join(self.data_path, 'R6MYC_SJR_FCBGA_pack_all.csv'))
        row, col, Y, X = np.array(df)[:,0:4].transpose(1,0)
        # Scale pin cooordinates between zero and one.  Reverse Y-direction
        # to match up with existing photos of boards.
        S = np.max([(np.max(Y)-np.min(Y)), (np.max(X)-np.min(X))])
        Y = (Y - np.min(Y))/S
        X = 1 - (X - np.min(X))/S
        # Add an offset of 1.5% on the sides and 3% on the top and bottom.
        X = (X + .05)/1.1
        Y = (Y + .05)/1.1
        pins = []
        for j in range(len(row)):
            pins += [[str(row[j])+'_' + str(col[j]), np.array([X[j], Y[j]])]]
        
        pins = dict(pins)
        
        super(R6m, self).__init__(pins, [100,100], 1)
        
    