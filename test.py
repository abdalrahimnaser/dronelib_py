## notes:
## adjust the [buffer time] command delay in the dronecontroller class
## fix landing command it doesn't seem to be working
## adjust time.sleep  [buffer delay] after each command - currently commented out


import time
from DroneController import Drone  # Assuming your class is in drone.py

# Example of using the unified Drone class

drone = Drone()

drone.connect()
# time.sleep(1.5)

drone.start_video()

drone.calibrate()  # Enable and start sending commands
# time.sleep(1.5)

# # Create an event to signal when to stop the video feed
# stop_event = Event()

# # Start the video feed in a separate thread
# video_thread = Thread(target=drone.show_video, args=(stop_event,))
# video_thread.start()
# # time.sleep(2)


drone.take_off()  # Command the drone to take off
# time.sleep(1.5)

drone.move('forward', 40)  # Move forward with 75% speed
# time.sleep(1)

drone.stop()  # Stop movement and hover

# time.sleep(2)  # Hover for 5 seconds

drone.land()  # Command the drone to land

# # Signal the video thread to stop and wait for it to finish
# stop_event.set()
# video_thread.join()

drone.stop_video()

drone.disconnect()  # Stop the drone and disable control
