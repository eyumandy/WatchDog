# import numpy as np
import cv2
import os
import shutil

import sys
sys.path.append('facelabel')

import face_labeler as fl

# may need to use the side face detection as well
# opens the video, and returns and error if it can't be opened/read
# full body pictures

# add video input
# take a face image and give it an id
# api to find info about them
# generative ai useage?


video = cv2.VideoCapture(0)

frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)
mp4 = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter("output.mp4", mp4, fps, (frame_width, frame_height))

if (video.isOpened() == False):
    print("Error: opening/reading video file")

haarcasc_frontal = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
# haar_cascade_profile = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
# haarcasc_frontal_alt = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
# haarcasc_frontal_alt2 = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
# hand_cascade = cv2.CascadeClassifier('models/right.xml') 

labeler = fl.face_labeler()

save_every = 10 # saves every tenth face
frame_count = 1
face_number = 1 # this is for the face file's name
while True:
    c=0
    ret, frame = video.read()
    
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # take multiple photos over the course of the video of the faces. At the end, check all the face pictures for 
    # faces again and delete the ones without

    frontal_faces = haarcasc_frontal.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))
    hands = hand_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=2, minSize=(50, 50))

    # profile_faces = haar_cascade_profile.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))

    # two seprate for loops so that they don't display at the same time
    for (x, y, w, h) in frontal_faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)
        
        if frame_count % save_every == 0:
            crop_img = cv2.resize(frame[y:y+h, x:x+w], dsize=(500,500)) # lowering the size could make it more effiecient if it is slow
            
            
            faceImgFilename = f"faces/face_{face_number}.jpeg"
            face_number+=1

            cv2.imwrite(faceImgFilename, crop_img)

    for (x, y, w, h) in hands:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
        
    out.write(frame)

    frame_count+=1
    cv2.imshow('WatchDog', frame)
    
    if cv2.waitKey(2) & 0xFF == ord('q'):
        break

if not os.path.exists('faces/false_positives'): os.makedirs('faces/false_positives')
model_path = 'models/deploy.prototxt'
weights_path = 'models/res10_300x300_ssd_iter_140000.caffemodel'
net = cv2.dnn.readNetFromCaffe(model_path, weights_path)

saved_faces = os.listdir('faces')
saved_faces.remove("false_positives") # so that there isn't an error when os deletes files

for saved_face in saved_faces:

    possible_face = cv2.imread(f"faces/{saved_face}")

    if possible_face is None:
        continue

    blob = cv2.dnn.blobFromImage(possible_face, 1.0, (300, 300), (104.0, 177.0, 123.0), swapRB=False, crop=False)

    net.setInput(blob)
    detections = net.forward()

    face_detected = False
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        
        if confidence > 0.7: 
            face_detected = True
            break

    if not face_detected:
        # print(f"False positive: {saved_face}")
        shutil.move(f"faces/{saved_face}", f"faces/false_positives/{saved_face}")

video.release()
out.release
cv2.destroyAllWindows()

faces_filenames = os.listdir('faces')
if "false_positives" in faces_filenames: faces_filenames.remove("false_positives")
if ".DS_Store" in faces_filenames: faces_filenames.remove(".DS_Store")

ids = []
face_number = 0
for face_file in faces_filenames:
    # print(f"faces/{face_file}")
    face_file = f"faces/{face_file}"

    face = cv2.imread(face_file)

    if face is not None:
        id = labeler.go(face)

        if id is not None:  
            if id not in ids: ids.append(id)
            id_faces_folder = f"faces/{id}"
            if not os.path.exists(id_faces_folder):
                os.makedirs(id_faces_folder)

            shutil.move(face_file, id_faces_folder)
    else:
        continue

# handles the leftover faces
# leftovers = os.listdir('faces')
# files_only = [f for f in leftovers if os.path.isfile(os.path.join('faces', f))]
# if not os.path.exists('faces/person_unknown'): os.makedirs('faces/person_unknown')

# for file in files_only:  
#     shutil.move(file, 'faces/person_unknown')
