import cv2
import numpy as np
import sqlite3

faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam=cv2.VideoCapture(0)
rec=cv2.face.LBPHFaceRecognizer_create()
rec.read("recognizer/trainningData.yml")
font = cv2.FONT_HERSHEY_SIMPLEX

def getProfile(id):
    conn=sqlite3.connect("FaceBase.db")
#    cmd="SELECT * FROM People WHERE ID="+str(id)
#    cursor=conn.execute(cmd)
#    profile=None
#    for row in cursor:
#        profile=row
#    conn.close()
#    return profile
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
        id,conf=rec.predict(gray[y:y+h,x:x+w])
        profile=getProfile(id)
        if(profile!=None):
            if conf > 70:
                cv2.putText(img, "Unknown",  (x,y-40), font, 1, (255,255,255), 3 )
            else:
                cv2.putText(img, str(profile[1]) + " - " + str(profile[3]) + " ( {0:.2f}% )".format(round(100 - conf, 2)) , (x,y-40), font, 1, (255,255,255), 3)
#            cv2.cv.PutText(cv2.cv.fromarray(img),"Name : "+str(profile[1]),(x,y+h+20),font,(0,255,0));
#            cv2.cv.PutText(cv2.cv.fromarray(img),"Age : "+str(profile[2]),(x,y+h+45),font,(0,255,0));
#            cv2.cv.PutText(cv2.cv.fromarray(img),"Gender : "+str(profile[3]),(x,y+h+70),font,(0,255,0));
#            cv2.cv.PutText(cv2.cv.fromarray(img),"Criminal Records : "+str(profile[4]),(x,y+h+95),font,(0,0,255));
    cv2.imshow("Face",img);
    if(cv2.waitKey(1)==ord('q')):
        break;
cam.release()
cv2.destroyAllWindows()