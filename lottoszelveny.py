import cv2 as cv
import numpy as np

image = cv.imread('pictures/otoslotto_big_x2.jpg')
#cv.imshow('Base Image', image)

gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
blurred = cv.GaussianBlur(gray, (5, 5), 0)
edges = cv.Canny(blurred, 50, 150)
contours, hierarchy = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

rects = []
for contour in contours:
    polygon = cv.approxPolyDP(contour, 0.01 * cv.arcLength(contour, True), True)

    if len(polygon) == 4 and abs(1 - cv.contourArea(polygon) /
                                 (cv.boundingRect(polygon)[2] * cv.boundingRect(polygon)[3])) < 0.1:
        rects.append(polygon)

# Draw the green contours around each rectangle.
for rect in rects:
    cv.drawContours(image, [rect], 0, (0, 255, 0), 2)
cv.imshow("Rectangles", image)

# Use the rectangle points (top left X,Y and bottom right X,Y) to cut out the images.
# We have to check if we already saved a picture so we wont have duplicate images which can lead to false numbers.
# We check it by calculating if the next 2 rect are +-5 pixel close to the already existing ones.
points = []
for i in range(len(rects)):
    X1 = rects[i][0][0][0]
    Y1 = rects[i][0][0][1]
    X2 = rects[i][2][0][0]
    Y2 = rects[i][2][0][1]

    # Check if it's already exist.
    isExist = False
    for p in points:
        if (p[0] - 5 <= Y1 <= p[0] + 5) and (p[2] - 5 <= X1 <= p[2] + 5):
            isExist = True
            break

    if not isExist:
        row = [Y1, Y2, X1, X2]
        points.append(row)
# Crop the images with the 2 rect and save it to a list.
selected_images = []
for p in points:
    cropped_image = image[p[0]:p[1], p[2]:p[3]]
    selected_images.append(cropped_image)

# We will cut out every number from the pictures and check if it has a blue "X" on it. If yes, we will save that number.
k = 0
lucky_numbers_pic = []
for current in selected_images:
    #cv.imshow("Crop - " + str(k), current)
    h, w, channels = current.shape
    little_box_height = h // 9
    little_box_width = w // 10
    k = k + 1
    has_x = False
    lucky_numbers = []

    for i in range(10):
        little_box_x1 = little_box_width * i
        little_box_x2 = little_box_width + little_box_x1

        little_box_y1 = 0
        little_box_y2 = 0
        for j in range(9):
            little_box_y1 = little_box_height * j
            little_box_y2 = little_box_height + little_box_y1
            #print(str(k) + ': Little box: ' + str(i + 1) + ' - ' + str(j + 1))
            current_little_box = current[little_box_y1:little_box_y2, little_box_x1:little_box_x2]

            # Converting it to HSV so the program can see better the colours and recognize them.
            hsv_image = cv.cvtColor(current_little_box, cv.COLOR_BGR2HSV)
            # The colour range which the masking will use to determine if the searched colour is on the picture.
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            mask = cv.inRange(hsv_image, lower_blue, upper_blue)
            # Find the contours. If the colour is not on the picture then it will give 0.
            contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                #print(str(k) +". picture, X has been found inside the box! Column: " + str(i + 1) + ' and row: ' + str(j + 1) + '. The number is: ' + str(j * 10 + (i+1)))
                lucky_numbers_pic.append(current_little_box)
                lucky_numbers.append(str(j * 10 + (i+1)))
                has_x = True
            #cv.imshow('Little box: ' + str(i) + ' - ' + str(j), current_little_box)
    # If the rectangle that contains the numbers have an "X" then write out the lucky numbers otherwise skip the
    # rectangle.
    if has_x:
        sentence = str(k) + ". square lucky numbers: " + ", ".join(map(str, lucky_numbers))
        print(sentence)


# Show the lucky numbers.
o = 0
for current in lucky_numbers_pic:
    cv.imshow("LN-" + str(o), current)
    o = o + 1

cv.waitKey(0)
