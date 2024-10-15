import cv2
import numpy as np
import time

class DroneFollower:
    def __init__(self, drone):
        self.drone = drone
        self.center_region = ((300, 220), (340, 260))  # Define a region in the center of the frame

        # Define thresholds for the object size (used for forward/backward movement)
        self.min_object_size = 2000  # Minimum size threshold to move forward
        self.max_object_size = 10000  # Maximum size threshold to move backward

    def follow_object(self):
        cap = self.drone.get_video_feed()  # Get video feed from the drone camera
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Convert the frame to HSV for color detection
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define the color range for the object (e.g., red shirt)
            lower_color = np.array([0, 120, 70])
            upper_color = np.array([10, 255, 255])

            # Create a mask for the object
            mask = cv2.inRange(hsv, lower_color, upper_color)

            # Find contours of the object
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                # Get the largest contour (assuming the tracked object is the largest red object)
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)

                # Calculate the object's area (as a proxy for distance)
                object_area = w * h

                # Draw the bounding box around the object
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Compute the center of the object
                obj_center_x = x + w // 2
                obj_center_y = y + h // 2

                # Calculate the offset of the object from the center of the frame
                frame_center_x = frame.shape[1] // 2
                frame_center_y = frame.shape[0] // 2

                error_x = frame_center_x - obj_center_x
                error_y = frame_center_y - obj_center_y

                # Define thresholds to avoid small movements
                threshold_x = 30
                threshold_y = 30

                # Drone control logic based on object position
                if abs(error_x) > threshold_x:
                    if error_x > 0:
                        self.drone.move('left', speed=30)
                    else:
                        self.drone.move('right', speed=30)

                if abs(error_y) > threshold_y:
                    if error_y > 0:
                        self.drone.move('up', speed=30)
                    else:
                        self.drone.move('down', speed=30)

                # Forward/backward logic based on the object's size
                if object_area < self.min_object_size:
                    self.drone.move('forward', speed=40)  # Move forward if the object is far
                elif object_area > self.max_object_size:
                    self.drone.move('backward', speed=40)  # Move backward if the object is too close
                else:
                    self.drone.hover()  # Hover if the object is within the acceptable range

            else:
                # Hover if no object is detected
                self.drone.hover()

            # Display the video feed
            cv2.imshow("Follow Me Mode", frame)

            # Press 'q' to stop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# # Usage:
# drone = Drone()  # Assuming the Drone class from your provided API is used
# drone.connect()  # Connect to the drone

# # Start video feed and follow the object
# follower = DroneFollower(drone)
# drone.start_video()  # Start video feed
# follower.follow_object()  # Begin following

# drone.stop_video()  # Stop video feed after following
# drone.disconnect()  # Disconnect the drone
