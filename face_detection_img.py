import cv2
import os
import face_recognition
import time


# Codificar los rostros
base_path = 'C:/Users/USER/OneDrive/Escritorio/Proyectos/Deteccion facial/Deming/People/'
employees = os.listdir(base_path)

faces_encodings = []
face_names = []

for employee in employees:
    carpet_photos = base_path + employee + '/Photos/Profile/'
    for name_img in os.listdir(carpet_photos):
        image = cv2.imread(carpet_photos + name_img)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        f_coding = face_recognition.face_encodings(image, known_face_locations=[(0, 150, 150, 0)])[0]
        faces_encodings.append(f_coding)
        face_names.append(name_img.split('.')[0])

#print(faces_encodings)
#print(face_names)

# Leer Video
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Detector Facial
face_classif = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    orig = frame.copy()
    faces = face_classif.detectMultiScale(frame, 1.1, 5)

    for (x, y, w, h) in faces:
        face = orig[y:y + h, x:x + w]
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        actual_face_encoding = face_recognition.face_encodings(face, known_face_locations=[(0, w, h, 0)])[0]
        result = face_recognition.compare_faces(faces_encodings, actual_face_encoding)
        #print(result)
        if True in result:
            index = result.index(True)
            name = face_names[index]
            color = (125, 220, 0)
        else:
            name = 'Desconocido'
            color = (50, 50, 255)

        cv2.rectangle(frame, (x, y + h), (x + w, y + h + 30), color, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        cv2.putText(frame, name, (x, y + h + 25), 2, 1, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Frame', frame)
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()
