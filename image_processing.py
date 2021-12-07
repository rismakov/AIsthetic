import cv2  # for image processing
import numpy as np

from PIL import Image


import streamlit as st

def image_processing(filepath):
    """
    Convert image to an array of size 100x1.
  
    The array represents an OpenCV grayscale version of the original image.
    The image will get cropped along the biggest red contour (4 line polygon) 
    tagged on the original image (if any).
    """
    # load image file and import as a numpy array
    # type of `uint8` so values will be between 0-255
    # image = np.asarray(Image.open(filepath), dtype='uint8')     
    # image = image.astype('uint8') 

    # st.header(image.shape)
    image_gray = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    # st.header(image_bgr.shape)
    # st.image(image)
    # read the numpy arrays as color images in OpenCV
    # image_bgr = cv2.imdecode(image, cv2.IMREAD_COLOR)
  
    # convert to grayscale to be used for training 
    # image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # resize the image to 100x100 pixels size
    image_100x100 = cv2.resize(image_gray, (100, 100))

    return image_100x100.flatten()
