import shutil
import cv2
import os, os.path
import numpy as np 
from scipy import signal, ndimage
import time

from tkinter import Tk
from tkinter.filedialog import askdirectory

#from matplotlib import pyplot as plt
#from skimage import measure


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
	valid_image_extensions = ['.jpeg','.jpg','.png','.tiff','.tif'] #identify the image type that want to work with
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


#learn parameters from reference image
def learn_info(reference, image_height, image_width):
	ref = cv2.imread(reference, 0)
	ref_resize = cv2.resize(ref, (image_height, image_width))

	for i in range(380, 420):
		for j in range(100, 380):
			ref_resize[i][j] = ref_resize[i][0]

	blur = cv2.GaussianBlur(ref_resize,(3,3),0)	
	ret,thresh = cv2.threshold(blur,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)  #Otsu's thresholding
	
	#label every stripe
	#thresh_label = measure.label(thresh, background=0)
	thresh_img, thresh_label = ndimage.label(thresh)

	#measure line width in pixels
	vertical_line = thresh_img[:,240]
	p_num = 0 #count total pixels for white line
	for i in range(0, image_width):
		if vertical_line[i] != 0:
			p_num += 1
	tot_line = np.max(vertical_line) #largest value in the line is the total number of lines

	line_width = p_num/tot_line #average line width in pixels
	line_dist = (image_width-p_num)/tot_line

	if line_width - int(line_width) > 0.5:
		line_width = int(line_width) + 1
	else:
		line_width = int(line_width)
	
	if line_dist - int(line_dist) > 0.5:
		line_dist = int(line_dist) + 1
	else:
		line_dist = int(line_dist)


	# "I" filter to detect break and bridge
	line2 = np.ones(shape=(2*line_dist+line_width,1))
	#loop over the image to find defect:
	f = signal.convolve2d(thresh, line2, 'valid')

	return line_width, line_dist, int(np.min(f)), int(np.max(f)+1)


#processing all the images in sequence
def Image_Processing_and_Binning(image_path_list, imageDir, line_width, line_dist, image_height, image_width, image_min, image_max):
	#loop through image_path_list to read in each image
	for imagePath in image_path_list:
		#print(imagePath)
		image = cv2.imread(imagePath, 0) #0 for grayscale

		#binarize the image first and then do analysis to find defect in the image
		#if there is no defect, put the original image into "good" folder
		#if there is break defect, put the original image into "break" folder
		#if there is bridge defect, put the original image into "bridge" folder
		if image is not None:
			raw_image = cv2.resize(image, (image_height, image_width)) #reduce image size for faster loop over
			width, height = raw_image.shape

			#clear scale bar
			for i in range(380, 420):
				for j in range(100, 380):
					raw_image[i][j] = raw_image[i][0]

			#pixel size in nm
			#pixel = FOV/width

			# line width and line distance in # of pixels
			#line_width = int(Width/pixel)
			#line_dist = int(Dist/pixel)

			# "I" filter to detect break and bridge
			line2 = np.ones(shape=(2*line_dist+line_width,1))

			#ret,thresh1 = cv2.threshold(image,128,255,cv2.THRESH_BINARY) #binary threshold
			blur = cv2.GaussianBlur(raw_image,(3,3),0)	
			ret3,thresh3 = cv2.threshold(blur,0,1,cv2.THRESH_BINARY+cv2.THRESH_OTSU)  #Otsu's thresholding

			#loop over the image to find defect:
			f = signal.convolve2d(thresh3, line2, 'valid') #2d convolution of filter on image to get activation value
			
			#print(np.max(f), np.min(f), np.mean(f), np.median(f))
			curr_min, curr_max = int(np.min(f)), int(np.max(f))
			#print(curr_min, curr_max)
			#save image into different folder
			######
			#try to use the difference between max, min, mean, median (np.)
			if curr_min >= image_min and curr_max <= image_max: #good image
				path3 = imageDir + '/good/' 
				move_image(imagePath, path3)
			
			elif curr_max > image_max: #bridge
				path2 = imageDir + '/bridge/' 
				move_image(imagePath, path2)

			else:
				#np.min(f) < image_min: #break
				path1 = imageDir + '/break/' 
				move_image(imagePath, path1)

		elif image is None:
			print("Error loading: " + imagePath)
			#end this loop iteration and move on to next image
			continue


if __name__ == '__main__':

	#Manually type in the directory path, can do copy and paste
	#imageDir = input("Enter the image directory:")

	Tk().withdraw() # no need to open the tkinter GUI, so keep the root window from appearing
	imageDir = askdirectory() # open an Windows window to select the working directory


	## Image info
	#FOV = float(input("Enter FOV in nm:"))
	#Width = float(input("Enter line width in nm (integer):"))
	#Dist = float(input("Enter line distance in nm (interger)"))


	#monitoring executing time
	tot_time = time.time()

	#learning parameters from reference image
	image_path_list, reference_image = read_images(imageDir)
	#print(image_path_list)
	img_height, img_width = 480, 480

	#info_learning_time = time.time()
	line_width, line_dist, img_min, img_max = learn_info(reference_image, img_height, img_width)
	#print("Learning info time is: %.3f seconds." % (time.time() - info_learning_time))  0.062s
	#print(line_width, line_dist, img_min, img_max)

	#img_process_time = time.time()
	Image_Processing_and_Binning(image_path_list, imageDir, line_width, line_dist, img_height, img_width, img_min, img_max)
	#print("Image processing time is %.3f seconds." % (time.time() - img_process_time))  0.047s/image

	print("Total number of images processed: ", len(image_path_list)) #print # of images processed in this code
	print("Total running time is: %.3f seconds." % (time.time() - tot_time))