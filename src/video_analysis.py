import cv2
import numpy as np
import face_recognition
import os # Added for directory operations

class MotionDetector:
    def __init__(self, bg_subtractor_type="MOG2", history=500, var_threshold=16, detect_shadows=True):
        """
        Initializes the motion detector.
        Args:
            bg_subtractor_type (str): Type of background subtractor to use ("MOG2" or "KNN").
            history (int): Number of previous frames that affect the background model.
            var_threshold (int): Threshold on the squared Mahalanobis distance between the pixel and the model.
            detect_shadows (bool): If true, the algorithm will detect shadows and mark them.
        """
        if bg_subtractor_type == "MOG2":
            self.back_sub = cv2.createBackgroundSubtractorMOG2(history=history, varThreshold=var_threshold, detectShadows=detect_shadows)
        elif bg_subtractor_type == "KNN":
            self.back_sub = cv2.createBackgroundSubtractorKNN(history=history, dist2Threshold=var_threshold, detectShadows=detect_shadows)
        else:
            self.back_sub = None

        self.previous_frame_gray = None
        self.min_contour_area = 500

    def detect_motion_background_subtraction(self, frame: np.ndarray) -> tuple[bool, list, np.ndarray]:
        if frame is None:
            return False, [], None
        if self.back_sub is None:
            raise RuntimeError("Background subtractor was not initialized. Call __init__ with 'MOG2' or 'KNN'.")
        fg_mask = self.back_sub.apply(frame)
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_motion_areas = []
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > self.min_contour_area:
                motion_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                detected_motion_areas.append((x, y, w, h))
        return motion_detected, detected_motion_areas, fg_mask

    def detect_motion_frame_differencing(self, frame: np.ndarray, threshold_value=25, blur_ksize=21, min_area=500) -> tuple[bool, list, np.ndarray | None]:
        if frame is None:
            return False, [], None
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.GaussianBlur(frame_gray, (blur_ksize, blur_ksize), 0)
        if self.previous_frame_gray is None:
            self.previous_frame_gray = frame_gray
            return False, [], None
        frame_delta = cv2.absdiff(self.previous_frame_gray, frame_gray)
        thresh = cv2.threshold(frame_delta, threshold_value, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.previous_frame_gray = frame_gray
        detected_motion_areas = []
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > min_area:
                motion_detected = True
                x, y, w, h = cv2.boundingRect(contour)
                detected_motion_areas.append((x, y, w, h))
        return motion_detected, detected_motion_areas, thresh

class FaceDetector:
    def __init__(self, model="hog"):
        if model not in ["hog", "cnn"]:
            raise ValueError("Unsupported face detection model. Choose 'hog' or 'cnn'.")
        self.model = model

    def detect_faces(self, frame_rgb: np.ndarray) -> list:
        if frame_rgb is None:
            return []
        face_locations = face_recognition.face_locations(frame_rgb, model=self.model)
        return face_locations

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

    def load_known_faces(self, known_faces_dir: str):
        if not os.path.isdir(known_faces_dir):
            print(f"Warning: Known faces directory '{known_faces_dir}' not found.")
            return
        for filename in os.listdir(known_faces_dir):
            try:
                image_path = os.path.join(known_faces_dir, filename)
                if os.path.isfile(image_path):
                    face_image = face_recognition.load_image_file(image_path)
                    face_encodings_list = face_recognition.face_encodings(face_image)
                    if face_encodings_list:
                        face_encoding = face_encodings_list[0]
                        self.known_face_encodings.append(face_encoding)
                        self.known_face_names.append(os.path.splitext(filename)[0])
                        print(f"Loaded known face: {os.path.splitext(filename)[0]} from {filename}")
                    else:
                        print(f"Warning: No faces found in {filename} in known_faces_dir.")
            except Exception as e:
                print(f"Error loading known face from {filename}: {e}")
        if not self.known_face_names:
            print("Warning: No known faces were loaded. Recognition will not be possible.")

    def recognize_faces(self, frame_rgb: np.ndarray, detected_face_locations: list) -> list:
        if frame_rgb is None or not self.known_face_encodings: # No locations needed if no known faces
             return ["Unknown"] * len(detected_face_locations)
        if not detected_face_locations: # If locations list is empty, return empty list
            return []

        current_face_encodings = face_recognition.face_encodings(frame_rgb, known_face_locations=detected_face_locations)
        recognized_names = []
        for face_encoding in current_face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
            recognized_names.append(name)
        return recognized_names

if __name__ == '__main__':
    # --- Motion Detection Test ---
    print("--- Motion Detection Test ---")
    dummy_frame_bgr_md = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(dummy_frame_bgr_md, "Frame 1 BGR", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    detector_mog2 = MotionDetector(bg_subtractor_type="MOG2")
    motion_detected_mog2, areas_mog2, fg_mask_mog2 = detector_mog2.detect_motion_background_subtraction(dummy_frame_bgr_md.copy())
    print(f"MOG2 (Frame 1): Motion detected: {motion_detected_mog2}, Areas: {len(areas_mog2) if areas_mog2 else 0}, Mask shape: {fg_mask_mog2.shape if fg_mask_mog2 is not None else 'None'}")

    dummy_frame_bgr_md_2 = dummy_frame_bgr_md.copy()
    cv2.rectangle(dummy_frame_bgr_md_2, (100,100), (200,200), (0,255,0), -1)
    cv2.putText(dummy_frame_bgr_md_2, "Frame 2 BGR", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    motion_detected_mog2_2, areas_mog2_2, fg_mask_mog2_2 = detector_mog2.detect_motion_background_subtraction(dummy_frame_bgr_md_2)
    print(f"MOG2 (Frame 2): Motion detected: {motion_detected_mog2_2}, Areas: {len(areas_mog2_2) if areas_mog2_2 else 0}, Mask shape: {fg_mask_mog2_2.shape if fg_mask_mog2_2 is not None else 'None'}")

    detector_fd = MotionDetector(bg_subtractor_type="NONE_FOR_FD")
    motion_detected_fd, areas_fd, diff_img_fd = detector_fd.detect_motion_frame_differencing(dummy_frame_bgr_md.copy())
    print(f"Frame Diff (Frame 1): Motion detected: {motion_detected_fd}, Areas: {len(areas_fd) if areas_fd else 0}, Diff image shape: {diff_img_fd.shape if diff_img_fd is not None else 'None'}")

    motion_detected_fd_2, areas_fd_2, diff_img_fd_2 = detector_fd.detect_motion_frame_differencing(dummy_frame_bgr_md_2.copy())
    print(f"Frame Diff (Frame 2): Motion detected: {motion_detected_fd_2}, Areas: {len(areas_fd_2) if areas_fd_2 else 0}, Diff image shape: {diff_img_fd_2.shape if diff_img_fd_2 is not None else 'None'}")
    print("Motion detection example with dummy frames finished.")

    # --- Face Detection Test ---
    print("\n--- Face Detection Test ---")
    dummy_frame_bgr_face_test = np.zeros((480, 640, 3), dtype=np.uint8)
    dummy_frame_rgb_face_test = dummy_frame_bgr_face_test[:, :, ::-1]
    face_detector_hog = FaceDetector(model="hog")
    detected_faces_hog = face_detector_hog.detect_faces(dummy_frame_rgb_face_test)
    print(f"HOG Model: Detected faces (locations): {detected_faces_hog}")
    if not detected_faces_hog:
        print("HOG Model: No faces detected in the dummy RGB frame (as expected).")

    print("Attempting CNN model for face detection (might be slow)...")
    try:
        face_detector_cnn = FaceDetector(model="cnn")
        detected_faces_cnn = face_detector_cnn.detect_faces(dummy_frame_rgb_face_test)
        print(f"CNN Model: Detected faces (locations): {detected_faces_cnn}")
        if not detected_faces_cnn:
            print("CNN Model: No faces detected in the dummy RGB frame (as expected).")
    except Exception as e:
        print(f"CNN Model: Could not run test due to an error: {e}")
    print("Face detection example with dummy frames finished.")

    # --- Face Recognition Test ---
    print("\n--- Face Recognition Test ---")
    known_faces_test_dir = "temp_known_faces_for_testing"
    os.makedirs(known_faces_test_dir, exist_ok=True)

    dummy_known_face1 = np.zeros((100, 100, 3), dtype=np.uint8)
    dummy_known_face1[:, :, 0] = 255 # Blue square
    cv2.imwrite(os.path.join(known_faces_test_dir, "person1.png"), dummy_known_face1)
    print(f"Created dummy known face: {os.path.join(known_faces_test_dir, 'person1.png')}")

    dummy_known_face2 = np.zeros((100, 100, 3), dtype=np.uint8)
    dummy_known_face2[:, :, 1] = 255 # Green square
    cv2.imwrite(os.path.join(known_faces_test_dir, "person2.jpg"), dummy_known_face2)
    print(f"Created dummy known face: {os.path.join(known_faces_test_dir, 'person2.jpg')}")

    unknown_face_img_bgr = np.zeros((100, 100, 3), dtype=np.uint8)
    unknown_face_img_bgr[:,:,2] = 255 # Red square
    unknown_face_img_rgb = unknown_face_img_bgr[:,:,::-1]

    test_frame_for_recognition_rgb = np.zeros((480, 640, 3), dtype=np.uint8)
    test_frame_for_recognition_rgb[50:150, 50:150, :] = unknown_face_img_rgb

    face_recognizer = FaceRecognizer()
    face_recognizer.load_known_faces(known_faces_test_dir)
    print(f"Loaded known faces: {face_recognizer.known_face_names}")

    temp_face_detector = FaceDetector(model="hog")
    detected_locations_in_test_frame = temp_face_detector.detect_faces(test_frame_for_recognition_rgb)
    print(f"Face locations detected in test frame for recognition: {detected_locations_in_test_frame}")

    if detected_locations_in_test_frame:
        recognized_names = face_recognizer.recognize_faces(test_frame_for_recognition_rgb, detected_locations_in_test_frame)
        print(f"Recognized names in test frame: {recognized_names}")
        if recognized_names and recognized_names[0] == "Unknown":
            print("Correctly recognized the face in the test frame as 'Unknown'.")
        elif recognized_names:
            print(f"Unexpected recognition result: {recognized_names[0]}")
    else:
        print("No faces were detected in the test frame by FaceDetector, so recognition was not performed.")
        print("This can be expected if the dummy 'face' (red square) is not detected by the HOG model.")

    names_no_faces = face_recognizer.recognize_faces(test_frame_for_recognition_rgb, [])
    print(f"Recognition with no detected faces: {names_no_faces} (expected empty list)")

    face_recognizer_no_known = FaceRecognizer()
    dummy_location = [(50, 150, 150, 50)]
    names_no_known = face_recognizer_no_known.recognize_faces(test_frame_for_recognition_rgb, dummy_location)
    print(f"Recognition with no known faces loaded: {names_no_known} (expected ['Unknown'])")

    try:
        os.remove(os.path.join(known_faces_test_dir, "person1.png"))
        os.remove(os.path.join(known_faces_test_dir, "person2.jpg"))
        os.rmdir(known_faces_test_dir)
        print(f"Cleaned up temporary directory: {known_faces_test_dir}")
    except OSError as e:
        print(f"Error cleaning up temp directory: {e}")

    print("Face recognition example finished.")
