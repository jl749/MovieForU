import os
import cv2
import numpy
import numpy as np
import DIR

BLOB_SIZE = (608, 608)
CONFIDENCE = 0.57
GUN_PATH = DIR.GUN_PATH
IMG_PATH = DIR.IMG_PATH


def readImg(myImg: numpy.ndarray):
    height, width, channels = myImg.shape
    myBlob = cv2.dnn.blobFromImage(myImg, 0.00392, BLOB_SIZE, (0, 0, 0), True, crop=False)
    return (height, width), myBlob


class Gun:
    __instance = None
    font = cv2.FONT_HERSHEY_SIMPLEX

    @staticmethod
    def GET():
        """ Static access method. """
        if Gun.__instance is None:
            Gun()
        return Gun.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Gun.__instance is not None:
            raise Exception("Singleton class can not be retrieved")
        else:
            Gun.__instance = self
            self.net = cv2.dnn.readNet(GUN_PATH + "yolov3.weights", GUN_PATH + "yolov3.cfg")
            self.classes = []
            with open(GUN_PATH + "obj.names", "r") as f:
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
    model = Gun().GET()
    for name in [name for name in os.listdir(".\img")]:
        myImg = cv2.imread(IMG_PATH+name)
        class_ids_, indexes_, boxes_ = model.forward(myImg)
        objsDetected = model.extractLabels(class_ids_, indexes_, boxes_)
        print(name, objsDetected)
        # model.display(myImg, class_ids_, indexes_, boxes_)

