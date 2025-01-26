# import face_recognition
# import numpy as np
# import os
# import cv2 
# import pickle

# class face_labeler:
#     def __init__(self):
#         self.embeddings_dict = {}

#     def save_embeddings(self):
#         with open('facelabel/saved_embeddings.dat', 'wb') as f:
#             pickle.dump(self.embeddings_dict, f)
    
#     # def known_or_not(self, img):
#     #     embeddings_filepath = 'facelabel/saved_embeddings.dat'

#     #     if os.path.exists(embeddings_filepath):
#     #         with open(embeddings_filepath, 'rb') as f:
#     #             self.embeddings_dict = pickle.load(f)
            
#     #     else:
#     #         return False

#     def go(self, unknown_face):
#         """
#         1. takes in an image of a cropped face, 
#         2. if the cropped face is in the embeddings list already then return the id.
#         this is so the program can label them on the image.
#         3. if not, make an embedding and then use that to compare to later.
#             if any more matches come up, save those to compare against later
#         4. this is so we can have "profiles" with IDs, and photos of that person, for later lookups online thorugh an api
#         """
#         embeddings_filepath = 'facelabel/saved_embeddings.dat'

#         if os.path.exists(embeddings_filepath):
#             with open(embeddings_filepath, 'rb') as f:
#                 self.embeddings_dict = pickle.load(f)
#         else:
#             new_id = "person_1"
#             face_location = (0, unknown_face.shape[1], unknown_face.shape[0], 0)
#             unknown_face_embedding = face_recognition.face_encodings(unknown_face, known_face_locations=[face_location])[0]
        
#             self.embeddings_dict[new_id] = unknown_face_embedding

#             self.save_embeddings()

#             return

#         face_ids = list(self.embeddings_dict.keys())
#         print(face_ids)
#         face_embeddings = np.array(list(self.embeddings_dict.values()))
#         # print(face_embeddings)

#         face_location = (0, unknown_face.shape[1], unknown_face.shape[0], 0)
#         unknown_face_embedding = face_recognition.face_encodings(unknown_face, known_face_locations=[face_location])[0]
#         # print(unknown_face_embedding)
#         results = face_recognition.compare_faces(face_embeddings, unknown_face_embedding, tolerance=0.6)

#         if True in results:
#             match = face_ids[results.index(True)]
#             return match
#         else:
#             new_id = f"person_{len(face_ids)+1}"
#             face_location = (0, unknown_face.shape[1], unknown_face.shape[0], 0)
#             new_encoding = face_recognition.face_encodings(unknown_face, known_face_locations=[face_location])[0]
        
#             self.embeddings_dict[new_id] = new_encoding
#             print(new_id)
           
#             return new_id # maybe indicate that this is a new person somehow?

# """    
# labeler_test = face_labeler()

# img = cv2.imread("facelabel/known_faces/August/face_20.jpg")

# print(labeler_test.go(img))

# KNOWN_FACES_DIR = 'facelabel/known_faces'
# UNKNOWN_FACES_DIR = 'facelabel/unknown_faces'
# FRAME_THICKNESS = 3
# MODEL = 'cnn'  # default: 'hog', other one can be 'cnn' - CUDA accelerated (if available) deep-learning pretrained model


# # Returns (R, G, B) from name
# def name_to_color(name):
#     # Take 3 first letters, tolower()
#     # lowercased character ord() value rage is 97 to 122, substract 97, multiply by 8
#     color = [(ord(c.lower())-97)*8 for c in name[:3]]
#     return color


# print('Loading known faces...')
# known_faces = []
# known_names = []

# knowns_filenames = knowns_filenames = [f for f in os.listdir(KNOWN_FACES_DIR) if f != '.DS_Store']

# # We oranize known faces as subfolders of KNOWN_FACES_DIR
# # Each subfolder's name becomes our label (name)
# for name in knowns_filenames:
#     # Load every file of faces of known person
#     for filename in os.listdir(f"{KNOWN_FACES_DIR}/{name}"):
#         profile_filename = f"{KNOWN_FACES_DIR}/{name}/{filename}"

#         #skip the .DS_Store files
#         if (profile_filename == f"{KNOWN_FACES_DIR}/{name}/.DS_Store"):
#             continue
            
#         image = face_recognition.load_image_file(f'{KNOWN_FACES_DIR}/{name}/{filename}')
        
#         # the entire image is the face
#         face_location = (0, image.shape[1], image.shape[0], 0)
        
#         encoding = face_recognition.face_encodings(image, known_face_locations=[face_location])[0]
        
#         known_faces.append(encoding)
#         known_names.append(name)

# print("Processing video stream...")

# video = cv2.VideoCapture(0)

# haarcasc_frontal = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# while True:
#     ret, frame = video.read()
    
#     if not ret:
#         break
    
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     # take multiple photos over the course of the video of the faces. At the end, check all the face pictures for 
#     # faces again and delete the ones without

#     frontal_faces = haarcasc_frontal.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))

#     # profile_faces = haar_cascade_profile.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=6, minSize=(30, 30))

#     # two seprate for loops so that they don't display at the same time
#     for (x, y, w, h) in frontal_faces:
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 3)

#         crop_img = cv2.resize(frame[y:y+h, x:x+w], dsize=(200,200))
#         face_location = (0, crop_img.shape[1], crop_img.shape[0], 0)

#         encoding = face_recognition.face_encodings(crop_img, known_face_locations=[face_location])[0]

#         results = face_recognition.compare_faces(known_faces, encoding, tolerance=0.6)

#         if True in results:
#             match = known_names[results.index(True)]
#             cv2.putText(frame, match, (x + 10, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 200, 200), 4)
  

#     cv2.imshow('WatchDog', frame)
    
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# video.release()
# cv2.destroyAllWindows()
# """
import face_recognition
import numpy as np
import os
import pickle

class face_labeler:
    def __init__(self):
        self.embeddings_dict = {}
        self.load_embeddings()

    def load_embeddings(self):
        embeddings_filepath = 'facelabel/saved_embeddings.dat'
        if os.path.exists(embeddings_filepath):
            with open(embeddings_filepath, 'rb') as f:
                self.embeddings_dict = pickle.load(f)
        else:
            print("no embeddings found, making embeddings")

    def save_embeddings(self):
        with open('facelabel/saved_embeddings.dat', 'wb') as f:
            pickle.dump(self.embeddings_dict, f)
    
    def go(self, unknown_face):
        """
        input: image of a cropped face, sees if it's in the embeddings list, and if it so, returns the ID
        if not, generates a new embedding. Adds it to the dictionary. Saves the updated embeddings.

        output: the ID
        """
        face_location = (0, unknown_face.shape[1], unknown_face.shape[0], 0)
        unknown_face_encoding = face_recognition.face_encodings(unknown_face, known_face_locations=[face_location])

        if len(unknown_face_encoding) == 0:
            print("No face encoding found!")
            return None
        
        unknown_face_encoding = unknown_face_encoding[0]

        if len(self.embeddings_dict) == 0:
            new_id = "person_1"
            self.embeddings_dict[new_id] = unknown_face_encoding
            self.save_embeddings()
            return new_id
        
        face_ids = list(self.embeddings_dict.keys())
        face_embeddings = np.array(list(self.embeddings_dict.values()))
        
        results = face_recognition.compare_faces(face_embeddings, unknown_face_encoding, tolerance=0.6)

        if True in results:
            match = face_ids[results.index(True)]

            return match
        else:
            new_id = f"person_{len(self.embeddings_dict) + 1}"

            self.embeddings_dict[new_id] = unknown_face_encoding

            self.save_embeddings()
            return new_id