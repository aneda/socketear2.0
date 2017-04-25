# -*- coding: utf-8 -*-
"""
Created on Thu December 29 13:51:56 2016

@author: Mat Rogers

"""
import numpy                    as np
from bluebook.layers import ConvVanilla, ConvPreprocess, ConvMaxPool
from bluebook.layers.hidden import Hidden
from bluebook.layers.softmax import Softmax
from bluebook.layers.onlineinput import OnlineInput
from bluebook.utils.theano.all  import shared_x
from os.path import join, split
import importlib

class PackageSJR(object):
    
    def __init__(self, device=None):
        import theano as th

        if device is not None:
            import theano.sandbox.cuda
            theano.sandbox.cuda.use(device)
        
        self._info = "Package SJR classifier.  VGG16 pretraining."
        
        # import model. There might be a better way of doing this but this works for now.
        caller = importlib.import_module(self.__module__)

        # retrieve the current file location
        self.current_dir, self.current_file = split(caller.__file__)

        # params should be the only folder in the same directory as model
        self.params_folder = join(self.current_dir, 'params')

        # Model input
        self.input = OnlineInput(tensorname='input_tensor4')        
               
        # Preprocess layer
        path = join(self.params_folder,'000_conv_preprocess')
        dc = shared_x(np.load(join(path, 'dc.npy')))
        std = shared_x(np.load(join(path, 'std.npy')))
        self.model = ConvPreprocess(inp=self.input, dc=dc, std=std)
        
        # Conv layer
        path = join(self.params_folder,'001_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(64, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'002_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(64, 3, 3), border_mode='half', W=W, b=b)
        
        # Maxpool layer
        self.model = ConvMaxPool(downsample_sz = 2, inp=self.model)

        # Conv layer
        path = join(self.params_folder,'004_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(128, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'005_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(128, 3, 3), border_mode='half', W=W, b=b)

         # Maxpool layer
        self.model = ConvMaxPool(downsample_sz = 2, inp=self.model)

        # Conv layer
        path = join(self.params_folder,'007_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(256, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'008_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(256, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'009_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(256, 3, 3), border_mode='half', W=W, b=b)

        
        # Maxpool layer
        self.model = ConvMaxPool(downsample_sz = 2, inp=self.model)

        # Conv layer
        path = join(self.params_folder,'011_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(512, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'012_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(512, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'013_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(512, 3, 3), border_mode='half', W=W, b=b)
               
         # Maxpool layer
        self.model = ConvMaxPool(downsample_sz = 2, inp=self.model)

        # Conv layer
        path = join(self.params_folder,'015_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(512, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'016_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(512, 3, 3), border_mode='half', W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'017_conv_vanilla')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = ConvVanilla(inp=self.model, act='relu', filters=(512, 3, 3), border_mode='half', W=W, b=b)
        
        # Maxpool layer
        self.model = ConvMaxPool(downsample_sz = 2, inp=self.model)

        # Hidden layer
        path = join(self.params_folder,'019_hidden')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = Hidden(inp=self.model, act='relu', nb_hid=2048, W=W, b=b)

        # Hidden layer
        path = join(self.params_folder,'021_hidden')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = Hidden(inp=self.model, act='relu', nb_hid=2048, W=W, b=b)
        
        # Conv layer
        path = join(self.params_folder,'023_logistic')
        W = shared_x(np.load(join(path, 'W.npy')))
        b = shared_x(np.load(join(path, 'b.npy')))
        self.model = Softmax(inp=self.model, nb_out=4, W=W, b=b)
        
        self.prob_fn = th.function(inputs=[self.input('Test')], outputs=self.model('Test'), allow_input_downcast=True)

        
    def __call__(self, img, assign_label = True):
        assert img.shape == (220,220,3)
        if assign_label == True:
            return np.argmax(self.prob_fn(img.transpose(2,0,1)[None,:,:,:]), axis = 1)[0]
        else:
            return self.prob_fn(img.transpose(2,0,1)[None,:,:,:])
    
    @property
    def info(self):
        return self._info
