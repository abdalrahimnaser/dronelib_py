import cv2
import torch  # PyTorch is required for YOLOv5
from threading import Thread
from DroneController import Drone  # Assuming your Drone class is in drone.py
import time


# Initialize drone and connect
drone = Drone()
drone.connect()
drone.calibrate()

# Load YOLOv5 model from PyTorch Hub (this example uses YOLOv5x)
model = torch.hub.load('ultralytics/yolov5', 'yolov5x', pretrained=True)

def start_object_detection():
    cap = drone.get_video_feed()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        # rotation
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        # Convert frame to RGB for model compatibility
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        
        
        # Perform object detection
        results = model(rgb_frame)

        # Process results and display bounding boxes with labels
        for detection in results.pred[0]:  # pred[0] contains detections for this frame
            x1, y1, x2, y2, confidence, class_id = detection[:6]
            label = model.names[int(class_id)]  # Get class label
            confidence_text = f"{label}: {confidence:.2f}"  # Format confidence score

            # Draw bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            
            # Display label and confidence on top of the bounding box
            cv2.putText(frame, confidence_text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.5, (0, 255, 0), 2)

        # Display the frame with detections
        cv2.imshow("Object Detection", frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


start_object_detection()

# # Start object detection in a separate thread
# detection_thread = Thread(target=start_object_detection)
# detection_thread.start()


# # Disconnect after the test
# drone.disconnect()

# # Ensure the detection thread ends when you exit the test
# detection_thread.join()
