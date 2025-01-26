import os

os.remove("facelabel/saved_embeddings.dat")

faces = os.listdir('faces')
faces.remove("false_positives")

for file in faces:
    os.remove(f"faces/{file}")

if os.path.exists('faces/false_positives'):
    false_faces = os.listdir('faces/false_positives')
    for file in false_faces:
        os.remove(f"faces/false_positives/{file}")

