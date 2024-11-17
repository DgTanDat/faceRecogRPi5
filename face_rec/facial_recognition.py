import face_recognition
import cv2
import numpy as np
import time
import pickle
import RPi.GPIO as GPIO
import smtplib
from email.message import EmailMessage

#Set the sender email and password and recipient emaiç
from_email_addr ="datdangtan2003@gmail.com"
from_email_pass ="hnxz ohbq hczv eywc"
to_email_addr ="dangtandat2003@gmail.com"

# Create a message object
msg = EmailMessage()

# Set sender and recipient
msg['From'] = from_email_addr
msg['To'] = to_email_addr

# Set your email subject
msg['Subject'] = 'NOTIFY EMAIL'

# Connecting to server and sending email
# Edit the following line with your provider's SMTP server details
server = smtplib.SMTP('smtp.gmail.com', 587)

# Comment out the next line if your email provider doesn't use TLS
server.starttls()
# Login to the SMTP server
server.login(from_email_addr, from_email_pass)

servoPIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
p.start(2.5) # Initialization

# Load pre-trained face encodings
print("[INFO] loading encodings...")
with open("encodings.pickle", "rb") as f:
    data = pickle.loads(f.read())
known_face_encodings = data["encodings"]
known_face_names = data["names"]

# Initialize the camera
cam = cv2.VideoCapture(0)

# Initialize our variables
cv_scaler = 4 # this has to be a whole number
frame_resizing = 0.25

face_locations = []
face_encodings = []
face_names = []
frame_count = 0
fps = 0
isWelcome = False

def process_frame(frame):
    global face_locations, face_encodings, face_names
    
    # Resize the frame using cv_scaler to increase performance (less pixels processed, less time spent)
    resized_frame = cv2.resize(frame, (0, 0), fx=(1/cv_scaler), fy=(1/cv_scaler))
    
    # Convert the image from BGR to RGB colour space, the facial recognition library uses RGB, OpenCV uses BGR
    rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
    
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_resized_frame)
    face_encodings = face_recognition.face_encodings(rgb_resized_frame, face_locations, model='small')
    
    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        
        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        face_names.append(name)
    face_locations = np.array(face_locations)
    face_locations = face_locations / (1/cv_scaler)
    
    return face_locations.astype(int), face_names



while True:
    
    # Capture a frame from camera
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    
       
    f_location, f_name = process_frame(frame)

    index = 0
       
    for face_loc, name in zip(f_location, f_name):
        body = "welcome"
        y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

        cv2.putText(frame, name, (x1, y1-10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
        if name == "dat":
            # print("welcome")
            if not isWelcome:
                body += ' ' + name + ' ' + str(time.ctime())
                isWelcome = True
                welcomeSignal = True
            else:
                welcomeSignal = False
        else:
            index += 1
            
    
    if index >= len(f_name):
        isWelcome = False
        welcomeSignal = False
        
    cv2.imshow('Video', frame)

    if isWelcome:
        p.ChangeDutyCycle(2.5)
    else:
        p.ChangeDutyCycle(7.5)

    if welcomeSignal:
        
        # Set the email body
        
        msg.set_content(body)
        server.send_message(msg)

        print('Email sent')
    
        

    key = cv2.waitKey(1)
    if key == 27:
        break
   
# By breaking the loop we run this code here which closes everything
cam.release()
server.quit()
cv2.destroyAllWindows()
