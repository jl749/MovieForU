# https://pysource.com/2019/06/27/yolo-object-detection-using-opencv-with-python/
import os
import cv2
import numpy
import numpy as np
import DIR

BLOB_SIZE = (608, 608)
CONFIDENCE = 0.5
COCO_PATH = DIR.COCO_PATH
IMG_PATH = DIR.IMG_PATH


def readImg(myImg: numpy.ndarray):
    height, width, channels = myImg.shape
    myBlob = cv2.dnn.blobFromImage(myImg, 0.00392, BLOB_SIZE, (0, 0, 0), True, crop=False)
    return (height, width), myBlob


class Coco:
    __instance = None
    font = cv2.FONT_HERSHEY_SIMPLEX

    @staticmethod
    def GET():
        """ Static access method. """
        if Coco.__instance is None:
            Coco()
        return Coco.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Coco.__instance is not None:
            raise Exception("Singleton class can not be retrieved")
        else:
            Coco.__instance = self
            self.net = cv2.dnn.readNet(COCO_PATH + "yolov3.weights", COCO_PATH + "yolov3.cfg")
            self.classes = []
            with open(COCO_PATH + "coco.names", "r") as f:
                self.classes = [line.strip() for line in f.readlines()]

            self.layer_names = self.net.getLayerNames()  # 'conv_0', 'bn_0', 'leaky_1', 'conv_1', 'bn_1'
            self.output_layers = [self.layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def forward(self, img):
        size, blob = readImg(img)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        # interpret result on the screen
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > CONFIDENCE:
                    center_x = int(detection[0] * size[1])
                    center_y = int(detection[1] * size[0])
                    w = int(detection[2] * size[1])
                    h = int(detection[3] * size[0])

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        return class_ids, indexes, boxes

    def extractLabels(self, class_ids, indexes, boxes):
        # labels = []
        # for i in range(len(boxes)):
        #     if i in indexes:
        #         label = self.classes[class_ids[i]]
        #         labels.append(label)
        # return labels
        return [self.classes[class_ids[i]] for i in range(len(boxes)) if i in indexes]

    def display(self, img, class_ids, indexes, boxes):
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = self.classes[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, label, (x, y + 30), self.font, 1, (0, 255, 0), 1)

        cv2.imshow("image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    model = Coco().GET()
    for name in [name for name in os.listdir(".\img")]:
        myImg = cv2.imread(IMG_PATH+name)
        class_ids_, indexes_, boxes_ = model.forward(myImg)
        # print(class_ids_, indexes_)
        objsDetected = model.extractLabels(class_ids_, indexes_, boxes_)
        print(objsDetected)
        model.display(myImg, class_ids_, indexes_, boxes_)

