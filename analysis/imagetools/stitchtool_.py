# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:49:41 2017

@author: mathew
"""

import os
import pandas as pd
import numpy as np
from os.path import join, isfile
from .rawimage_ import RawImage


class StitchTool(object):
    def __init__(self, sampleID, guide, segDataPath, imgPath, savePath=None):

        self.sampleID = str(sampleID)

        df = pd.read_csv(segDataPath, index_col=False)
        self.segData = np.array(df)

        self.imgPath = imgPath

        self.guide = guide

        if savePath is None: savePath = imgPath
        self.savePath = savePath

    def stitch(self, includeSampleID=False, focusLayer=1):

        # Wrap all raw images and associated pin locations into RawImage objects.
        # Store them in a list called bigImages.

        rawImages = os.listdir(self.imgPath)
        rawImages = [r for r in rawImages if int(str.split(str.split(r, '.')[0], '_')[-1]) == focusLayer]

        if len(rawImages) == 0:
            raise ValueError('Please select a known focus layer')

        bigImages = []

        for rawImgName in rawImages:

            # Split the field number from the image name
            j = int(str.split(rawImgName, '_')[0])

            # Find all pins in the field of view
            pins = [pin for pin in self.segData if pin[0] == j]

            rawImgPath = join(self.imgPath, rawImgName)
            pinLoc = {}
            if isfile(rawImgPath):
                for pin in pins:
                    fieldNumber, Row, Col, startRow, stopRow, startCol, stopCol = pin
                    X = (stopRow + startRow) // 2
                    Y = (stopCol + startCol) // 2
                    pinLoc.update({str(Row) + '_' + str(Col): [X, Y]})
                if len(pinLoc) > 0:
                    bigImages += [RawImage(pinLoc, rawImgPath)]

                    # Calculate the size ratio of the final stitched image to the pin guide.
        # The pin guide scales all pins between 0 and 1.  The segmentation data
        # gives the location of each pin in every big image.  Calculate
        # the rescaling factor by averaging the ratio of distances between pins
        # in a big image compared to their distances in the guide.

        guide = self.guide

        count = 0
        scale = 0
        for b in bigImages:
            for pin_a, pin_b in zip(b.pins, b.pins[::-1]):
                if pin_a != pin_b:
                    dist_ab_img = np.linalg.norm(np.array(b.position(pin_a)) - np.array(b.position(pin_b)))
                    dist_ab_guide = np.linalg.norm(np.array(guide.position(pin_a)) - np.array(guide.position(pin_b)))
                    if dist_ab_guide > 0:
                        scale += dist_ab_img / dist_ab_guide
                        count += 1
        scale = scale // count

        # Assemble a stitched image.  Keep track of overlapping
        # regions with an integer mask.  We'll use the mask to average
        # out overlaps in the end.  The size of the stitched image
        # is selected to give about a 3% buffer on the bottom
        # and right-hand side of the image.  The pin guide already
        # gives a buffer on the left-hand side and the top.

        coords = []
        for pin in guide.pins:
            coords += [guide.position(pin)]
        X, Y = 1.03 * scale * np.array(coords).transpose(1, 0)
        maxX = np.int(np.max(X))
        maxY = np.int(np.max(Y))

        output = {}
        for pin in guide.pins:
            output.update({pin: (int(scale * guide.position(pin)[0]), int(scale * guide.position(pin)[1]))})

        I = np.zeros(shape=(maxX, maxY, 3))
        mask = np.zeros(shape=I.shape, dtype=np.int)

        for b in bigImages:
            if isfile(b._image):
                img = b.img
                pins = b.pins
                refpin = pins[0]

                # Position of the reference pin in stitched image
                X, Y = np.round(scale * np.array(guide.position(refpin)))
                X = np.int(X)
                Y = np.int(Y)

                # Position of reference pin in unstitched image
                x, y = np.array(b.position(refpin))

                # Add the unstitched images to the stitched image.
                # Make sure to stay within the boundaries.
                w, l, _ = img.shape
                W, L, _ = I.shape
                print('indices = {}, {}, {}, {}, {}, {}'.format(X, x, Y, Y, y, l))
                I[np.max([0, X - x]):np.min([W, X - x + w]), np.max([0, Y - y]):np.min([L, Y - y + l])] += img[np.max(
                    [x - X, 0]):np.min([W - (X - x), w]), np.max([y - Y, 0]):np.min([L - (Y - y), l])]
                mask[np.max([0, X - x]):np.min([W, X - x + w]), np.max([0, Y - y]):np.min([L, Y - y + l])] += 1

        # Increment unmasked pixels, then divide the stitched image by the mask.
        mask += (mask == 0)
        I = I / mask

        return I, output


if __name__ == '__main__':
    sampleID = 'R6ZGH_40X'
    from experiments.mat.intel.pinPositions.r6s_ import R6s

    guide = R6s()
    imgPath = '/media/mnt/datasets/IntelStitching/R6SBB/63'
    segDataPath = '/home/mathew/Documents/experiments/experiments/mat/intel_stitching/Pattern/Pine_Point_pack' + '/' + 'Pine_Point_pseudo_mosaic_segmentation_data_pack_63X.csv'

    stitcher = StitchTool(sampleID, guide, segDataPath, imgPath)

    from time import time

    st = time()
    I, loc, bigImages = stitcher.stitch()
    sp = time() - st
    print('Stitching took {} seconds'.format(sp))
    import matplotlib.pyplot as plt

    plt.imshow(I);
    plt.show()