import sys
import cv2
import os, os.path
from matplotlib import pyplot as plt
import numpy as np 

image = cv2.imread('..\EUV_images\Manual-Window1-Top-CMix0-0516075351.jpeg', 0) #0 for grayscale
raw_image = cv2.resize(image, (200,200))
#ret,thresh1 = cv2.threshold(raw_image,128,255,cv2.THRESH_BINARY) #binary threshold
#blur = cv2.GaussianBlur(raw_image,(3,3),0)	
ret3,thresh3 = cv2.threshold(raw_image,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)  #Otsu's thresholding
#cv2.namedWindow('resize', cv2.WINDOW_NORMAL) #now we can resize the window
#cv2.imshow('raw_image', raw_image)
#cv2.imshow('Otsu',thresh3)
#cv2.imshow('binary', thresh1)
#cv2.waitKey(0) & 0xFF

width, height = thresh3.shape
#print(width, height) # 200, 200