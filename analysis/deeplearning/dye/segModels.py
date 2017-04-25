# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 10:03:13 2017

@author: mathew
"""
import numpy as np
from bluebook.test.modeltester import ModelOnlineTester
from bluebook.models import ModelLoader


class PinSegmentation(object):
    """
    Base class for dye stain segmentation models.
    """

    def __init__(self, path, device=None, transform = None):

        if device is not None:
            import theano.sandbox.cuda
            theano.sandbox.cuda.use(device)

        model = ModelLoader.load(path)

        self.prob_fn = ModelOnlineTester(output=model)
        
        self.transform = transform

    def __call__(self, img, assign_label=True):
        assert img.shape == (224,224,3)
        lbl = np.argmax(self.prob_fn([255*img[:,:,::-1]]), axis = 1)[0]
        t = self.transform
        if t is not None:
            L = np.zeros(shape = lbl.shape)
            for j in range(len(t)):
                L += t[j]*(lbl==j)
        else:
            L = lbl
        return L