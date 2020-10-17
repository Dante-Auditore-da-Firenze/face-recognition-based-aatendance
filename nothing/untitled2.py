import cv2
import numpy as np
import sqlite3
from keras.models import load_model
from keras.models import load_model
from keras.preprocessing import image
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import re

person={}
n_id = os.listdir("./dataset/train")
#print(n_id)
for i,id1 in enumerate(n_id):
    person[i]=id1

faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam=cv2.VideoCapture(0)

rec = load_model("./classifier.h5")
font = cv2.FONT_HERSHEY_SIMPLEX

def getProfile(id):
    conn=sqlite3.connect("FaceBase.db")
    c = conn.cursor()
    c.execute("SELECT * FROM People WHERE Id=:id", {'id': id})
    ans = c.fetchone()
    c.close()
    return ans

while(True):
    ret,img=cam.read();
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    faces=faceDetect.detectMultiScale(gray,1.3,5);
    for(x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
        input_im = img[y:y + h, x:x + w]
        input_im = cv2.resize(input_im, (100,100))
        input_im = input_im / 255.
        input_im = input_im.reshape(1,100,100,3)     
        # Get Prediction
        asd=rec.predict(input_im, 1, verbose = 0)
        maxp_index = np.argmax(asd)
        id = person[maxp_index]
        #print(asd[0][np.argmax(rec.predict(input_im, 1, verbose = 0))])
        profile=getProfile(id)
        conf=asd[0][maxp_index]
#        print(conf)
        if(profile!=None):
            if conf*100 < 30:
                cv2.putText(img, "Unknown",  (x,y-40), font, 1, (255,255,255), 3 )
            else:
                cv2.putText(img, str(profile[1]) + " - " + str(profile[3]) + " ( {0:.2f}% )".format(round(100*conf, 2)) , (x,y-40), font, 1, (255,255,255), 3)
    cv2.imshow("Face",img);
    if(cv2.waitKey(1)==ord('q')):
        break;
cam.release()
cv2.destroyAllWindows()