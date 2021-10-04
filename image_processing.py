import cv2  # for image processing
import numpy as np

from PIL import Image


def image_processing(filepath):
    """
    Convert image to an array of size 100x1.
  
    The array represents an OpenCV grayscale version of the original image.
    The image will get cropped along the biggest red contour (4 line polygon) 
    tagged on the original image (if any).
    """

    print('DEBUG', filepath)
    # load image file and import as a numpy array
    image = np.asarray(Image.open(filepath), dtype='uint8')                

    # read the numpy arrays as color images in OpenCV
    image_bgr = cv2.imdecode(image, cv2.IMREAD_COLOR)

    # convert to HSV in order to create a mask
    image_hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # create a mask that detects the red rectangular tags present in each image
    mask = cv2.inRange(image_hsv, (0,255,255), (0,255,255))
    x1, x2, y1, y2 = get_red_rect_coords(mask)
  
    # convert to grayscale to be used for training 
    image_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # crop the grayscle image along those coordinates
    image_cropped = image_gray[y1:y2, x1:x2]

    # resize the image to 100x100 pixels size
    image_100x100 = cv2.resize(image_cropped, (100, 100))

    return image_100x100.flatten()
