from DroneController import Drone

drone = Drone()

drone.connect()

drone.calibrate()

drone.start_video()

drone.take_off(wait=1)  

drone.move('forward', speed=50, wait=1)  

drone.hover(wait=1)  

drone.land(wait=1)  

drone.stop_video()

drone.disconnect()  

