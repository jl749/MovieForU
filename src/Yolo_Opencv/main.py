# https://pysource.com/2019/06/27/yolo-object-detection-using-opencv-with-python/
import os
import cv2
import numpy as np

net = cv2.dnn.readNet(f"{os.getcwd()}\yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]
layer_names = net.getLayerNames()  # 'conv_0', 'bn_0', 'leaky_1', 'conv_1', 'bn_1'
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

img = cv2.imread("img/4-0.jpg")
# img = cv2.resize(img, None, fx=0.4, fy=0.4)
height, width, channels = img.shape

# detect obj
blob = cv2.dnn.blobFromImage(img, 0.00392, (608, 608), (0, 0, 0), True, crop=False)

# for b in blob:
#     for n, img_blob in enumerate(b):
#         cv2.imshow(str(n), img_blob)  # RGB

net.setInput(blob)
outs = net.forward(output_layers)

# interpret result on the screen
class_ids = []
confidences = []
boxes = []
for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)

            #cv2.circle(img, (center_x, center_y), 10, (0, 255, 0), 2)

            x = int(center_x - w / 2)
            y = int(center_y - h / 2)
            # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)

howMany_detected = len(boxes)
indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
font = cv2.FONT_HERSHEY_SIMPLEX
for i in range(howMany_detected):
    if i in indexes:
        x, y, w, h = boxes[i]
        label = classes[class_ids[i]]
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, label, (x, y+30), font, 1, (0, 255, 0), 1)

cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()