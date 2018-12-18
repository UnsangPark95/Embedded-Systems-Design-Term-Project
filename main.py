from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import RPi.GPIO as GPIO

pin1=18
pin2=17

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin1, GPIO.OUT)
GPIO.setup(pin2, GPIO.OUT)
p1 = GPIO.PWM(pin1, 1)
p1.start(0)
p2=GPIO.PWM(pin2, 1)
p2.start(0)
cnt = 0

def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),
                                     flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return rects

def draw_rects(img, rects, color):
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        if(x2>380):
            print(x2, y2, "left")
            p1.ChangeDutyCycle(0.5)
        else:
            print(x2, x2, "right")

            p1.ChangeDutyCycle(0.1)
        if(y2 < 280):
            print(x2, y2, "Up")
            p2.ChangeDutyCycle(0.1)
        else:
            print(x2, y2, "down")
            p2.ChangeDutyCycle(0.05)

def send_mail():
    # -*- coding : cp949 -*-
    import smtplib
    import mimetypes
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.mime.image import MIMEImage

    # global value
    imageFileName='image.jpg'
    host = "smtp.naver.com"
    port = "465"

    senderAddr='iloveunhs@naver.com'
    recipientAddr='iloveunhs@naver.com'
    # create MIMEBase
    msg=MIMEBase("multipart","mixed")
    msg['Subject']="Someone was caught on CCTV!"
    msg['From']=senderAddr
    msg['To']=recipientAddr

    imageFD=open(imageFileName,'rb')
    ImagePart=MIMEImage(imageFD.read())
    imageFD.close()
    msg.attach(ImagePart)
    msg.add_header('Content-Disposition', 'attachment', filename=imageFileName
    s=smtplib.SMTP_SSL('smtp.naver.com',465)
    s.login(senderAddr, 'aaa156846')
    s.sendmail(senderAddr,[recipientAddr],msg.as_string())
    s.close()
    print("Successfully sent the mail")

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
cascade = cv2.CascadeClassifier("/home/pi/opencv-3.3.0/samples/python/haarcascade_frontalface_default.xml")

print("Someone was caught on CCTV!")
camera.capture('image.jpg')
print("Sending Image File to Email")
time.sleep(1)
send_mail()
print("Send Image FIle Complete!")

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    img = frame.array
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    rects = detect(gray, cascade)
    vis = img.copy()
    draw_rects(vis, rects, (0, 255, 0))

    # show the frame
    cv2.imshow("Frame", vis)
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
