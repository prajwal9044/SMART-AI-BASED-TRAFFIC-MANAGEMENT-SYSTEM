import cv2
import numpy as np
import vehicles
import time
import serial
from urllib.request import urlopen
import requests
import imutils
global ser
try:
    print("[INFO] Connecting To Board")
    ser = serial.Serial('COM4', 9600, timeout=1)     #enter ur arduino COM port number
    print("Sucessfully Connected")
except:
    print("[INFO] Failed To Connect To Board Check COM Port Number And Connection")
    pass

# Initialize Blynk
#token = ''

#myAPI = ""

cnt_up=0
cnt_down=0
cap=cv2.VideoCapture("test_video.mp4")

#Get width and height of video

w=cap.get(3)
h=cap.get(4)
frameArea=h*w
areaTH=frameArea/400

#Lines
line_up=int(3.5*(h/5))#red line
line_down=int(3*(h/5))#blue line

up_limit=int(2.5*(h/5))
down_limit=int(4*(h/5))

line_down_color=(255,0,0)#rgb
line_up_color=(0,0,255)

pt1 =  [0, line_down]
pt2 =  [w, line_down]
pts_L1 = np.array([pt1,pt2], np.int32)
pts_L1 = pts_L1.reshape((-1,1,2))
pt3 =  [0, line_up]
pt4 =  [w, line_up]
pts_L2 = np.array([pt3,pt4], np.int32)
pts_L2 = pts_L2.reshape((-1,1,2))

pt5 =  [0, up_limit]
pt6 =  [w, up_limit]
pts_L3 = np.array([pt5,pt6], np.int32)
pts_L3 = pts_L3.reshape((-1,1,2))
pt7 =  [0, down_limit]
pt8 =  [w, down_limit]
pts_L4 = np.array([pt7,pt8], np.int32)
pts_L4 = pts_L4.reshape((-1,1,2))

#Background Subtractor
fgbg=cv2.createBackgroundSubtractorMOG2(detectShadows=True)

#Kernals
kernalOp = np.ones((3,3),np.uint8)
kernalOp2 = np.ones((5,5),np.uint8)
kernalCl = np.ones((11,11),np.uint8)


font = cv2.FONT_HERSHEY_SIMPLEX
cars = []
max_p_age = 5
pid = 1

def thingspeak():
   print('Uploading to ThingSpeak...Wait!!!') 
   baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI   
   f = urlopen(baseURL + "&field1=%s&field2=%s" %(cnt_up,cnt_down))
   print(f.read()) 
   f.close()


def upload_blynk():
     val = requests.get("http://188.166.206.43/" + token + "/update/V1?value=" + str(cnt_up))
     val = requests.get("http://188.166.206.43/" + token + "/update/V2?value=" + str(cnt_down))
     
while(cap.isOpened()):
    ret,frame=cap.read()
    #frame = imutils.resize(frame,width=1000)
    for i in cars:
        i.age_one()
    fgmask=fgbg.apply(frame)
    fgmask2=fgbg.apply(frame)

while(cap.isOpened()):
    ret,frame=cap.read()
    #frame = imutils.resize(frame,width=1000)
    for i in cars:
        i.age_one()
    fgmask=fgbg.apply(frame)
    fgmask2=fgbg.apply(frame) 

    if ret==True:

        #Binarization
        ret,imBin=cv2.threshold(fgmask,200,255,cv2.THRESH_BINARY)
        ret,imBin2=cv2.threshold(fgmask2,200,255,cv2.THRESH_BINARY)
        #Opening i.e First Erode the dilate
        mask=cv2.morphologyEx(imBin,cv2.MORPH_OPEN,kernalOp)
        mask2=cv2.morphologyEx(imBin2,cv2.MORPH_CLOSE,kernalOp)

        #Closing i.e First Dilate then Erode
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,kernalCl)
        mask2=cv2.morphologyEx(mask2,cv2.MORPH_CLOSE,kernalCl)


        #Find Contours
        countours0,hierarchy=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        for cnt in countours0:
            area=cv2.contourArea(cnt)
            #print(area)
            if area>areaTH:
                ####Tracking######
                m=cv2.moments(cnt)
                cx=int(m['m10']/m['m00'])
                cy=int(m['m01']/m['m00'])
                x,y,w,h=cv2.boundingRect(cnt)

                new=True
                if cy in range(up_limit,down_limit):
                    for i in cars:
                        if abs(x - i.getX()) <= w and abs(y - i.getY()) <= h:
                            new = False
                            i.updateCoords(cx, cy)

                            if i.going_UP(line_down,line_up)==True:
                                cnt_up+=1
                            elif i.going_DOWN(line_down,line_up)==True:
                                cnt_down+=1
                            break
                        if i.getState()=='1':
                            if i.getDir()=='down'and i.getY()>down_limit:
                                i.setDone()
                            elif i.getDir()=='up'and i.getY()<up_limit:
                                i.setDone()
                        if i.timedOut():
                            index=cars.index(i)
                            cars.pop(index)
                            del i

                    if new==True: #If nothing is detected,create new
                        p=vehicles.Car(pid,cx,cy,max_p_age)
                        cars.append(p)
                        pid+=1

                cv2.circle(frame,(cx,cy),5,(0,0,255),-1)
                img=cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

        for i in cars:
            cv2.putText(frame, str(''), (i.getX(), i.getY()), font, 0.3, i.getRGB(), 1, cv2.LINE_AA)
            
        str_up='UP: '+str(cnt_up)
        str_down='DOWN: '+str(cnt_down)
        frame=cv2.polylines(frame,[pts_L1],False,line_down_color,thickness=2)
        frame=cv2.polylines(frame,[pts_L2],False,line_up_color,thickness=2)
        frame=cv2.polylines(frame,[pts_L3],False,(0,255,255),thickness=1)
        frame=cv2.polylines(frame,[pts_L4],False,(0,255,255),thickness=1)
        cv2.putText(frame, str_up, (10, 40), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, str_up, (10, 40), font, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, str_down, (10, 90), font, 0.5, (255, 0, 0), 1, cv2.LINE_AA)
        cv2.imshow('Frame',frame)
        time.sleep(0.01)
        print(str_up)
        print(str_down)
        if cnt_up >= 20 :
            tu =int((cnt_up*30)/(cnt_up+cnt_down))
            ser.write((str(1) + ',' + str(tu)).encode())
            cnt_up=0
            cnt_down=0
            
        if cnt_down >=20 :
            td =int((cnt_down*30)/(cnt_up+cnt_down))
            ser.write((str(2) + ',' + str(td)).encode())
            cnt_down=0
            cnt_up=0
            
        if cv2.waitKey(1)&0xff==ord('q'):
            break
        
upload_blynk()
cap.release()
cv2.destroyAllWindows()








