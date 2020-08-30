from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import imutils
import time
import cv2
import serial
length = None
sox = 0
soy = 0 
flag = True
# Construct argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str, help="path to video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf", help="Object Tracker type")
args = vars(ap.parse_args())

OPENCV_OBJECT_TRACKER = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}

#Initialize Ardiuno
ardiuno = serial.Serial('COM6', 9600)
print("Connecting to ardiuno...")

#Grab the approperiate tracker
tracker = OPENCV_OBJECT_TRACKER[args["tracker"]]()
#Initialize1 the bounding box coordinates of the object we are going to track
initBB = None

#if video path was not supplied grab the reference to the webcame
if not args.get("video", False):
    print("[INFO] Video stream starting...")
    vs = VideoStream(src=0).start()
    #vs = cv2.VideoCapture(0)
    time.sleep(5)
else: 
    #grab reference to the video file
    vs = cv2.VideoCapture(args["video"])
"""def onChange(trackbarValue):
    vs.set(cv2.CAP_PROP_POS_FRAMES,trackbarValue)
    err,img = vs.read()
    cv2.imshow("SERB Tracker", img)
    pass   q
    #initialize the fps throughput estimator"""
fps = None
    #fps = FPS().start()
    #Loop over frames from the video stream
while True:
    #grabe the video frame if we using videostream or cam stream
    #length = int(vs.get(cv2.CAP_PROP_FRAME_COUNT))
    frame = vs.read()
    frame = frame[1] if args.get("video", False) else frame
    #cv2.rectangle(frame, (217, 154), (67, 68), (255,0,0), 2)   #(217, 154, 67, 68)
    if flag:
        cv2.rectangle(frame, (280, 200), (360, 280), (255,0,0), 2)
    #height, width = frame.shape[:2]
    #width  = vs.get(3) # float
    #height = vs.get(4) # float
    
    #print("WIdth: {0}".format())
    #ROI Details (217,154,75,75) where 217 is X->(downward) & 154 is Y->(leftToright) & 75,75 is width & height

    #check to see if we reached to end of stream
    if frame is None:
        break
    #resize frame so we can process it faster adn grabe the frame dimensions
    #frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]
    #print("WIdth: {0} Hight: {1}".format(W,H))
    #check to see if we currently tracking an object
    if initBB is not None:
        #grab the new bounding box cooardinates of the object
        (success, box) = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0,255,0), 2)
            
            #Draw Circle in center of the bounding Box
            x2 = x + int(w/2)
            y2 = y + int(h/2)
            cv2.circle(frame, (x2,y2), 5, (0,255,0), 1)
            txt = "X: " + str(x2) + ", Y: " + str(y2)
            cv2.putText(frame, txt, (x2 - 40, y2 - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 1)
            #cv2.line(frame, (x,0), (x,480), (0,255,0), 1)
            #the offsets for the x,y tracking from the center
            sox = str(x2 - (W/2))
            soy = str((H/2) - y2)

            #update ardiuno
            data = "X-{0:04d}-Y-{1:04d}-Z".format(x2,y2)
            print("output = '" +data+ "'")
            ardiuno.write(data.encode())
            ardiuno.flush()

        #update the FPS counter
       # if fps is not None:
        fps.update() 
        fps.stop()   
             #initialize the set of information we are going to display on our frmae
        info = [
            ("Tracker", args["tracker"]),
            ("Success", "Yes" if success else "No" ),
            ("FPS", "{:.2f}".format(fps.fps())),
            ("coord:","{}: {}".format(sox, soy))
            
            ]
                # loop over the info tupples and show them on frame
        for(i, (k,v)) in enumerate(info):
            text = "{}: {}".format(k, v)  
            cv2.putText(frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    #time.sleep(.025)    

    cv2.imshow("Tracker Test Cases", frame)
    cv2.namedWindow('Tracker Test Cases')
    #cv2.createTrackbar( 'start', 'mywindow', 0, length, onChange )
    #cv2.createTrackbar( 'end'  , 'mywindow', 100, length, onChange )
    key = cv2.waitKey(1) & 0xFF
    # if the s key is selected 
 
    if key == ord('s'):
           #if 'S' key is selected then we are going to select the bounding box
            #Sure you press SPACE or ENTER after selecting the ROI
        if(fps != None):
            print("FPS: {}".format(fps))
            fps.update()
            fps.stop()
            if not args.get("video", False):
	            vs.stop()
            # otherwise, release the file pointer
            else:
	            vs.release()
                
        #initBB = cv2.selectROI("Frame", frame, fromCenter= False, showCrosshair= True)
        print(initBB)
        #Start the opencv objectTracker using supplied bounding box 
        initBB = (280, 200, 75, 75)
        #(280, 200), (360, 280)
        tracker.init(frame, initBB)
        print(initBB)
        flag = False
        #(217, 154, 67, 68)
        #(217, 154, 67, 68)
        #fps.stop
        fps = FPS().start() 
    elif key == ord("z"):
        break
        cv2.destroyAllWindows()

    #if not args.get("video", False):
       # vs.stop()

    #else:
      #  vs.release()
    
       


