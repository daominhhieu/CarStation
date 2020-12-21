import cv2
import pytesseract
import numpy as np
import os
from PIL import Image
from operator import itemgetter

path = os.getcwd()+'\\captcha.png'



def test_img():
    img = cv2.imread(path)

    noise = [140, 180, 210]
    white = np.array([255, 255, 255])

    indices = np.where(np.all(img == noise, axis=-1))

    for i in range(indices[0].shape[0]):
        img[indices[0][i]][indices[1][i]] = white
    

    # cv2.imshow('image', ~img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return img



def CV2_test():
    gray = cv2.cvtColor(test_img(), cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 50, 150)
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    out_below = pytesseract.image_to_string(canny, config='--psm 9')
    print("OUTPUT:"+ out_below)
    # cv2.imshow('image', canny)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

if __name__ == "__main__":
    CV2_test()