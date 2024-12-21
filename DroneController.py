
################################ PROTOCOL ####################################
#     1st byte – Header: 66
#     2nd byte – Left/right movement (0-254, with 128 being neutral)
#     3rd byte – Forward/backward movement (0-254, with 128 being neutral)
#     4th byte – Throttle (elevation) (0-254, with 128 being neutral)
#     5th byte – Turning movement (0-254, with 128 being neutral)
#     6th byte – Reserved for commands (0 = no command)
#     7th byte – Checksum (XOR of bytes 2, 3, 4, and 5)
#     8th byte – Footer: 99

# Command Bits (can be ORed):
#     01 – Auto Take-Off
#     02 - Land
#     04 - Emergency Stop
#     08 - 360 Deg Roll
#     10 - Headless mode
#     20 - Lock
#     40 – Unlock Motor
#     80 – Calibrate Gyro

import socket
import os
import time
from threading import Thread,Event,Timer
import cv2


COMMAND_TAKE_OFF = 0x01
COMMAND_LAND = 0x02
COMMAND_CALIBRATE_GYRO = 0x80
COMMAND_UNLOCK_MOTOR = 0x40

def debug(msg):
    if os.getenv('DRONELIB_DEBUG'):
        print(f"[dronelib] {msg}")

class Drone:
    def __init__(self):
        self.enabled = False
        self.send_interval = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Control values initialized
        self.throttle = 128
        self.turn = 128
        self.forward_backward = 128
        self.left_right = 128
        self.current_command = 0

    # Enable the drone, start sending commands periodically
    def connect(self):
        self.enabled = True
        self.send_interval = Timer(0.05, self._send_message)
        self.send_interval.start()

    # Disable the drone and stop sending commands
    def disconnect(self):
        self.enabled = False
        if self.send_interval:
            self.send_interval.cancel()
            self.send_interval = None

    # Build the message to send to the drone based on the current state
    def _build_message(self):
        message = [0x03, 0x66]

        if self.current_command == 0:
            message.extend([
                self.left_right,
                self.forward_backward,
                self.throttle,
                self.turn,
                0,
                self.left_right ^ self.forward_backward ^ self.throttle ^ self.turn
            ])
        else:
            message.extend([0x80, 0x80, 0x80, 0x80, self.current_command, self.current_command])

        message.append(0x99)
        return bytearray(message)

    # Send the built message periodically
    def _send_message(self):
        if self.enabled:
            self.socket.sendto(self._build_message(), ("192.168.1.1", 7099))
            self.send_interval = Timer(0.05, self._send_message)
            self.send_interval.start()

    # Send command to the drone
    def _send_command(self, cmd):
        if self.current_command == 0:
            self.current_command = cmd
            Timer(0.5, self._reset_command).start()

    # Reset command after a timeout
    def _reset_command(self):
        self.current_command = 0

    # Drone actions
    def take_off(self, wait):
        self._send_command(COMMAND_TAKE_OFF)
        time.sleep(wait)

    def land(self, wait):
        self._send_command(COMMAND_LAND)
        time.sleep(wait)

    def calibrate(self):
        self._send_command(COMMAND_CALIBRATE_GYRO)
        time.sleep(2) # artificial delay

    def unlock_motor(self):
        self._send_command(COMMAND_UNLOCK_MOTOR)
        time.sleep(2) # artificial delay

    # Converts a normalized speed (0 to 100) to the control range (128 to 254)
    def _convert_speed(self, speed):
        return int(128 + (speed / 100) * (254 - 128))



    def get_video_feed(self):
        rtsp_url = "rtsp://192.168.1.1:7070/webcam"  
              
        # Open the RTSP stream
        cap = cv2.VideoCapture(rtsp_url)
        if not cap.isOpened():
            print("Error: Unable to open the RTSP stream.")
            exit()

        return cap
        


    def _start_video(self):
        cap = self.get_video_feed()
        # while not self.stop_event_camfeed.is_set():
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break
            
            # rotation
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            
            # Display the frame
            cv2.imshow("RTSP Stream", frame)
            
            # Press 'q' to exit the window
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
        cap.release()
        cv2.destroyAllWindows()
        
    def start_video(self):
        self.stop_event = Event()
        self.video_thread = Thread(target=self._start_video)
        self.video_thread.start()
        time.sleep(3) # delay to allow the video to show up before any furhter control motion [e.g monitoring takeoff]


    def stop_video(self):
        # Signal the video thread to stop and wait for it to finish
        self.stop_event.set()
        self.video_thread.join()


    # Move the drone in a specified direction with a given speed (0 to 100)
    def move(self, direction, speed=50, wait = 0):
        speed = self._convert_speed(speed)
        if direction == 'forward':
            self.forward_backward = speed
        elif direction == 'backward':
            self.forward_backward = 256 - speed
        elif direction == 'left':
            self.left_right = 256 - speed
        elif direction == 'right':
            self.left_right = speed
        elif direction == 'up':
            self.throttle = speed
        elif direction == 'down':
            self.throttle = 256 - speed
        time.sleep(wait)

    # Stop the drone by resetting controls to neutral
    def stop(self):
        self.forward_backward = 128
        self.left_right = 128
        self.throttle = 128
        self.turn = 128

    # Rotate the drone (yaw) with a given speed
    def rotate(self, direction, speed=50, wait = 0):
        speed = self._convert_speed(speed)
        if direction == 'left':
            self.turn = 256 - speed
        elif direction == 'right':
            self.turn = speed
        time.sleep(wait)

    # Hover the drone by stopping movement, maintaining current position
    def hover(self, wait = 0):
        self.stop()
        time.sleep(wait)