# -*- coding: utf-8 -*-
"""
Created on Sun Sep 16 17:05:37 2018

@author: jjk1223
"""

import os
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from skimage.io import imread
import matplotlib.pyplot as plt
from skimage.segmentation import mark_boundaries
#from skimage.util.montage import montage2d as montage
from skimage.morphology import binary_opening, disk, label
import gc; gc.enable() # memory is tight
from keras.losses import binary_crossentropy
import tensorflow as tf
import scipy
from skimage import io,data,color
import keras
import tensorflow as tf
from keras import models, layers
#from unet_VGG11 import unet
from resnet_unet_scse import unet
import scipy


ship_dir = r'/home/jjk/Desktop/kaggle2/data'
train_image_dir = os.path.join(ship_dir, 'train')
test_image_dir = os.path.join(ship_dir, 'test')

def rle_encode(img, min_max_threshold=1e-3, max_mean_threshold=None):
    '''
    img: numpy array, 1 - mask, 0 - background
    Returns run length as string formated
    '''
    if np.max(img) < min_max_threshold:
        return '' ## no need to encode if it's all zeros
    if max_mean_threshold and np.mean(img) > max_mean_threshold:
        return '' ## ignore overfilled mask
    pixels = img.T.flatten()
    pixels = np.concatenate([[0], pixels, [0]])
    runs = np.where(pixels[1:] != pixels[:-1])[0] + 1
    runs[1::2] -= runs[::2]
    return ' '.join(str(x) for x in runs)

def rle_decode(mask_rle, shape=(101, 101)):
    '''
    mask_rle: run-length as string formated (start length)
    shape: (height,width) of array to return 
    Returns numpy array, 1 - mask, 0 - background
    '''
    s = mask_rle.split()
    starts, lengths = [np.asarray(x, dtype=int) for x in (s[0:][::2], s[1:][::2])]
    starts -= 1
    ends = starts + lengths
    img = np.zeros(shape[0]*shape[1], dtype=np.uint8)
    for lo, hi in zip(starts, ends):
        img[lo:hi] = 1
    return img.reshape(shape).T  # Needed to align to RLE direction

class TTA_ModelWrapper():
    """A simple TTA wrapper for keras computer vision models.
    Args:
        model (keras model): A fitted keras model with a predict method.
    """

    def __init__(self, model):
        self.model = model

    def predict(self, X):
        """Wraps the predict method of the provided model.
        Augments the testdata with horizontal and vertical flips and
        averages the results.
        Args:
            X (numpy array of dim 4): The data to get predictions for.
        """

        pred = []
        for x_i in X:
            #print(x_i.shape)
            p0 = self.model.predict(self._expand(x_i))
            p1 = self.model.predict(self._expand(np.fliplr(x_i)))
            p = (p0 + self._expand(np.fliplr(p1[0]))) / 2
            pred.append(p)
        return np.array(pred)

    def _expand(self, x):
        return np.expand_dims(x, axis=0)


test_masks = pd.read_csv(os.path.join(ship_dir, 'sample_submission.csv'))
masks = pd.read_csv(os.path.join(ship_dir, 'train2.csv'))

seg_model0 = unet(sigmod_output=False)
weight_path0="{}_weights.best.hdf5".format('seg_model0')
seg_model0.load_weights(weight_path0)

seg_model1 = unet(sigmod_output=False)
weight_path1="{}_weights.best.hdf5".format('seg_model1')
seg_model1.load_weights(weight_path1)

seg_model2 = unet(sigmod_output=False)
weight_path2="{}_weights.best.hdf5".format('seg_model2')
seg_model2.load_weights(weight_path2)

seg_model3 = unet(sigmod_output=False)
weight_path3="{}_weights.best.hdf5".format('seg_model3')
seg_model3.load_weights(weight_path3)

seg_model4 = unet(sigmod_output=False)
weight_path4="{}_weights.best.hdf5".format('seg_model4')
seg_model4.load_weights(weight_path4)
#seg_model.save('seg_model.h5')

empty=0
seg_model0 = TTA_ModelWrapper(seg_model0)
seg_model1 = TTA_ModelWrapper(seg_model1)
seg_model2 = TTA_ModelWrapper(seg_model2)
seg_model3 = TTA_ModelWrapper(seg_model3)
seg_model4 = TTA_ModelWrapper(seg_model4)

for i in range(18000
               ):
    rgb_path = os.path.join(test_image_dir, (test_masks['id'][i]+'.png'))
    #rgb_path = os.path.join(train_image_dir, (masks['ImageId'][i]+'.png'))
    img = imread(rgb_path)
    img = np.expand_dims(img,axis=0)/255.0
    pred_y0 = seg_model0.predict(img[:,:,:,0:1])
    pred_y1 = seg_model1.predict(img[:,:,:,0:1])
    pred_y2 = seg_model2.predict(img[:,:,:,0:1])
    pred_y3 = seg_model3.predict(img[:,:,:,0:1])
    pred_y4 = seg_model4.predict(img[:,:,:,0:1])
    a=1/5
    pred_y=a*pred_y0+a*pred_y1+a*pred_y2+a*pred_y4+a*pred_y3
    
    #a = 1/3
    #pred_y = a*(pred_y0+pred_y1+pred_y2)
    pred_binary=pred_y[0,:,:,0]#TTA 5 dim
    pred_binary[pred_binary>0.00]=1
    pred_binary[pred_binary<=0.00]=0
    l=rle_encode(pred_binary)
    test_masks['rle_mask'][i]=l
    if i%1000==0:
        print(i)
    if len(l)==0:
        empty=empty +1
   # masks['EncodedPixels'][i]=l
    
#encoder
   
b=masks['EncodedPixels'][3]
label2=rle_decode(b)
c_mask1=color.gray2rgb(label2) 
c_mask1=scipy.misc.imresize(c_mask1,[96,96,3])
c_mask1=color.gray2rgb(c_mask1[:,:,0]) 
c_mask1=scipy.misc.imresize(c_mask1,[101,101,3])
plt.imshow(c_mask1[:,:,0])
a=rle_encode(c_mask1[:,:,0])

test_masks.to_csv('result.csv',index=False)




