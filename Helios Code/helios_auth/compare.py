import face_recognition
import base64
import numpy as np
import cv2

def compare_faces(base64_str1, base64_str2):
    try:
        # Decode Base64 strings into image data
        img_data1 = base64.b64decode(base64_str1)
        img_data2 = base64.b64decode(base64_str2)

        # Convert image data into numpy arrays
        nparr1 = np.frombuffer(img_data1, np.uint8)
        nparr2 = np.frombuffer(img_data2, np.uint8)

        # Decode numpy arrays into RGB images
        img1 = cv2.imdecode(nparr1, cv2.IMREAD_COLOR)
        img2 = cv2.imdecode(nparr2, cv2.IMREAD_COLOR)

        # Detect face locations in the images
        face_locations1 = face_recognition.face_locations(img1)
        face_locations2 = face_recognition.face_locations(img2)

        # Check if exactly one face is detected in each image
        if len(face_locations1) == 1 and len(face_locations2) == 1:
            # Encode face encodings for comparison
            face_encodings1 = face_recognition.face_encodings(img1, face_locations1)[0]
            face_encodings2 = face_recognition.face_encodings(img2, face_locations2)[0]

            # Compare the face encodings
            face_distance = face_recognition.face_distance([face_encodings1], face_encodings2)[0]

            # Return the face distance (0 for identical faces, higher values for more dissimilar faces)
            return face_distance

        else:
            print("Error: Could not detect exactly one face in each image.")

    except Exception as e:
        print("Error occurred during face comparison:", e)
        return None


    
# Example usage
if __name__ == "__main__":
    base64_str1 = ""
    base64_str3 = ""

    similarity_index = compare_faces(base64_str1, base64_str3)
    if similarity_index is not None:
        print("Similarity Index:", similarity_index)
    else:
        print("Error occurred during comparison.")
    
