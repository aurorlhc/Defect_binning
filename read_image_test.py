import sys
import cv2
import os, os.path
from matplotlib import pyplot as plt
import numpy as np 

#image path and valid extensions
imageDir = 'EUV_images/'
image_path_list = []
valid_image_extensions = ['.jpeg'] #['.jpg','.png','.tiff','.tif'] identify the image type that want to work with
valid_iamge_extensions = [item.lower() for item in valid_image_extensions]


#function to save image into a folder
def save_image_into_folder(newpath, imagepath, newimage):
	os.makedirs(os.path.dirname(newpath), exist_ok=True) #check is the directory exist, if not, create one
	#print(os.path.dirname(path))
	file_name = os.path.basename(imagePath) + "_Binary.png" #output file name
	cv2.imwrite(os.path.join(newpath, file_name), newimage)  #save image into output folder with given name


#create list of all files in directory and 
#append files with a valid extension to image_path_list
for file in os.listdir(imageDir):
	extension = os.path.splitext(file)[1]
	if extension.lower() not in valid_image_extensions:
		continue
	image_path_list.append(os.path.join(imageDir, file))

#loop through image_path_list to read in each image
for imagePath in image_path_list:
	image = cv2.imread(imagePath, 0) #0 for grayscale

	#display image on screen after checking that it loaded
	if image is not None:
		#ret,thresh1 = cv2.threshold(image,128,255,cv2.THRESH_BINARY) #binary threshold
		#thresh2 = cv2.adaptiveThreshold(image,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,27,2)
		blur = cv2.GaussianBlur(image,(5,5),0)	
		ret3,thresh3 = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		#cv2.imshow(imagePath, thresh1)
		#plt.subplot(121),plt.imshow(image),plt.title('Input')
		#plt.subplot(122),plt.imshow(thresh1),plt.title('Output')
		
		#vis = np.concatenate((image, thresh3), axis=1) #combine two image into single image
		#vis = np.concatenate((vis, thresh3), axis=1)
		#cv2.namedWindow('Binarization', cv2.WINDOW_NORMAL) #now we can resize the window
		#cv2.resizeWindow('Binarization', 1200, 600) #set image to specific pixel size -> rescale
		#cv2.imshow('Binarization', vis) #plot image on the screen
	
	elif image is None:
		print("Error loading: " + imagePath)
		#end this loop iteration and move on to next image
		continue

	path1 = 'EUV_images/output/' #output folder path
	save_image_into_folder(path1, imagePath, thresh3)


	### additional functionality: manually separate image into different folder
	"""
	key = cv2.waitKey(0) & 0xFF
	if key == 27: #esc: for good image
		
		#print(os.path.basename(imagePath)) #print just the file name, ignore the path
		path1 = 'EUV_images/output/' #output folder path
		os.makedirs(os.path.dirname(path1), exist_ok=True) #check is the directory exist, if not, create one
		#print(os.path.dirname(path))
		file_name = os.path.basename(imagePath) + "_Binary.png" #output file name
		cv2.imwrite(os.path.join(path1, file_name), thresh1)  #save image into output folder with given name
		path1 = 'EUV_images/output/' #output folder path
		save_image_into_folder(path1, imagePath, thresh3)
		cv2.destroyAllWindows() #close the image window
		continue #move on to the next image in the loop
		#break #break out of the loop

	elif key == ord('k'): #save image if it has break
		path2 = 'EUV_images/break/' #output folder path
		os.makedirs(os.path.dirname(path2), exist_ok=True) #check is the directory exist, if not, create one
		file_name = os.path.basename(imagePath) + "_Binary.png" #output file name
		cv2.imwrite(os.path.join(path2, file_name), thresh1)  #save image into output folder with given name
		cv2.destroyAllWindows() #close the image window
		continue #move on to the next image in the loop

	elif key == ord('g'): #save image if it has bridge
		path3 = 'EUV_images/bridge/' #output folder path
		os.makedirs(os.path.dirname(path3), exist_ok=True) #check is the directory exist, if not, create one
		file_name = os.path.basename(imagePath) + "_Binary.png" #output file name
		cv2.imwrite(os.path.join(path3, file_name), thresh1)  #save image into output folder with given name
		cv2.destroyAllWindows() #close the image window
		continue #move on to the next image in the loop
	"""

print ("Total number of images processed:", len(image_path_list)) #print # of images processed in this code
#cv2.destroyAllWindows()