import sys, shutil
import cv2
import os, os.path
#from matplotlib import pyplot as plt
import numpy as np 
from scipy import signal
from skimage import measure


def move_image(imagepath, newpath):
	os.makedirs(os.path.dirname(newpath), exist_ok=True)
	newpath = newpath + os.path.basename(imagepath)
	shutil.move(imagepath, newpath)
	#print(newpath)
	return None


#create list of all files in directory and 
#append files with a valid extension to image_path_list
def read_images(imageDir):
	#image path and valid extensions
	#imageDir = '../EUV_images/code_test'
	image_path_list = []
	valid_image_extensions = ['.jpeg'] #['.jpg','.png','.tiff','.tif'] identify the image type that want to work with
	valid_iamge_extensions = [item.lower() for item in valid_image_extensions]

	for file in os.listdir(imageDir):
		extension = os.path.splitext(file)[1]
		#print(os.path.splitext(file)[0])
		if extension.lower() not in valid_image_extensions:
			continue
		elif os.path.splitext(file)[0] == 'reference':
			reference_image = os.path.join(imageDir, file)
			continue

		image_path_list.append(os.path.join(imageDir, file))
	
	return image_path_list, reference_image

def learn_info(reference):
	ref = cv2.imread(reference, 0)
	ref_resize = cv2.resize(ref, (480,480))
	blur = cv2.GaussianBlur(ref_resize,(5,5),0)	
	ret,thresh = cv2.threshold(blur,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)  #Otsu's thresholding
	
	#label every stripe
	thresh_label = measure.label(thresh, background=0)

	#measure line width in pixels
	vertical_line = thresh_label[:,240]
	p_num = 0 #count total pixels for white line
	for i in range(0, 480):
		if vertical_line[i] != 0:
			p_num += 1
	tot_line = np.max(vertical_line) #largest value in the line is the total number of lines

	line_width = int(p_num/tot_line) #average line width in pixels
	line_dist = int((480-p_num)/tot_line)

	return line_width, line_dist

def Image_Processing_and_Binning(image_path_list, imageDir, line_width, line_dist):
	#loop through image_path_list to read in each image
	for imagePath in image_path_list:
		#print(imagePath)
		image = cv2.imread(imagePath, 0) #0 for grayscale

		#binarize the image first and then do analysis to find defect in the image
		#if there is no defect, put the original image into "good image" folder
		#if there is defect, put the original image into "bad image" folder
		if image is not None:
			raw_image = cv2.resize(image, (480,480)) #reduce image size for faster loop over
			width, height = raw_image.shape

			#pixel size in nm
			#pixel = FOV/width

			# line width and line distance in # of pixels
			#line_width = int(Width/pixel)
			#line_dist = int(Dist/pixel)

			# "I" filter to detect break and bridge
			line2 = np.ones(shape=(2*line_dist+line_width,1))

			#ret,thresh1 = cv2.threshold(image,128,255,cv2.THRESH_BINARY) #binary threshold
			blur = cv2.GaussianBlur(raw_image,(5,5),0)	
			ret3,thresh3 = cv2.threshold(raw_image,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)  #Otsu's thresholding

			#loop over the image to find defect:
			f = signal.convolve2d(thresh3, line2, 'valid') #2d convolution of filter on image to get activation value
			
			#print(np.max(f), np.min(f), np.mean(f), np.median(f))

			#save image into different folder
			######
			#try to use the difference between max, min, mean, median (np.)
			if np.min(f) > line_width/3 and np.max(f) < 2*line_dist + 0.5*line_width: #good image
				path3 = imageDir + '/good/' 
				move_image(imagePath, path3)
			elif np.min(f) <= line_width/3: #break
				path1 = imageDir + '/break/' 
				move_image(imagePath, path1)
			elif np.max(f) >= 2*line_dist + 0.5*line_width: #bridge
				path2 = imageDir + '/bridge/' 
				move_image(imagePath, path2)

		elif image is None:
			print("Error loading: " + imagePath)
			#end this loop iteration and move on to next image
			continue


if __name__ == '__main__':

	#still need to type in the directory, need to figure out a better way to do this
	imageDir = input("Enter the image directory:")

	## Image info
	#FOV = float(input("Enter FOV in nm:"))
	#Width = float(input("Enter line width in nm (integer):"))
	#Dist = float(input("Enter line distance in nm (interger)"))

	image_path_list, reference_image = read_images(imageDir)
	#print(image_path_list)
	line_width, line_dist = learn_info(reference_image)
	Image_Processing_and_Binning(image_path_list, imageDir, line_width, line_dist)

	print ("Total number of images processed:", len(image_path_list)) #print # of images processed in this code







