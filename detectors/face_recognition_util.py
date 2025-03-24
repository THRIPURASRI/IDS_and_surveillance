# detectors/face_recognition_util.py
import face_recognition
import cv2

def is_registered_face(frame, registered_image_path, tolerance=0.6):
    """
    Compares the face in the live frame with the registered user image.
    Returns True if the face matches, False otherwise.
    """
    # Load the registered image from disk
    registered_image = face_recognition.load_image_file(registered_image_path)
    registered_encodings = face_recognition.face_encodings(registered_image)
    if not registered_encodings:
        return False
    registered_encoding = registered_encodings[0]

    # Convert live frame from BGR (OpenCV default) to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_encodings = face_recognition.face_encodings(rgb_frame)
    if not frame_encodings:
        return False

    # Compare the first detected face in the frame with the registered encoding
    match_results = face_recognition.compare_faces([registered_encoding], frame_encodings[0], tolerance=tolerance)
    return match_results[0]
