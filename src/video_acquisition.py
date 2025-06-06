import cv2

class VideoCaptureError(Exception):
    """Custom exception for video capture errors."""
    pass

class WebcamVideoStream:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise VideoCaptureError(f"Cannot open webcam source: {src}")

        self.grabbed, self.frame = self.stream.read()
        if not self.grabbed:
            raise VideoCaptureError("Failed to grab initial frame from webcam.")

        self.stopped = False

    def start(self):
        # This method is not strictly necessary for cv2.VideoCapture
        # as it starts capturing on initialization.
        # However, it can be used for compatibility with threaded approaches if needed later.
        print("Webcam video stream started.")
        return self

    def read(self):
        if self.stopped:
            return None

        self.grabbed, self.frame = self.stream.read()
        if not self.grabbed:
            # Could indicate end of stream or an error
            self.stop()
            return None
        return self.frame

    def stop(self):
        self.stopped = True
        if self.stream.isOpened():
            self.stream.release()
        print("Webcam video stream stopped and resources released.")

    def isOpened(self):
        return self.stream.isOpened()

if __name__ == '__main__':
    # Example usage:
    try:
        webcam = WebcamVideoStream()
        webcam.start()

        frame_count = 0
        while frame_count < 50: # Capture 50 frames for testing
            frame = webcam.read()
            if frame is None:
                print("Failed to get frame or stream ended.")
                break

            # Display the resulting frame (optional, requires GUI environment)
            # cv2.imshow('Webcam Test', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #    break

            print(f"Frame {frame_count + 1} captured, shape: {frame.shape}")
            frame_count += 1

    except VideoCaptureError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'webcam' in locals() and webcam.isOpened():
            webcam.stop()
        # cv2.destroyAllWindows() # If cv2.imshow was used
        print("Test finished.")
