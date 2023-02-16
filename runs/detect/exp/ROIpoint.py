"""
To fix ROI
Click the images, print x,y position value
"""

import cv2

#number = '261'
#img = cv2.imread('./images/CCTV_B1_ORG_' + number + ".jpg")

img = cv2.imread('./test_result.jpg')
img = cv2.resize(img, dsize=(960,540))

cv2.imshow('image', img)

# cause images are too big, resize to half and multiple the x,y position value
def get_coordinate(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        x *= 2
        y *= 2
        print(f"({x}, {y})")

cv2.setMouseCallback('image', get_coordinate)
cv2.waitKey(0)
cv2.destroyAllWindows()
