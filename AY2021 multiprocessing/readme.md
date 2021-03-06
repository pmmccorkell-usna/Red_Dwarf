sudo python3 multi.py


- Requires xbox360 controller w/ wifi dongle and RasPi script to intercept driver:
  - https://github.com/FRC4564/Xbox
- Requires 3space IMU libraries for python:
  - https://yostlabs.com/3-space-application-programming-interface/


- Controller commands:
  - left joystick moves boat in that vector (relative), ie forward / back / strafing
  - right joystick changes heading, ie spins in place
  - left + right shoulder quits program
  - left trigger starts / stops live graphing comparing available telemetry sources:
    - Qualisys Motion Capture camera system, from the QTM server
    - Bosch BNO-055 IMU
    - 3space IMU


Adapted to test telemetry sources against each other, and compare to "absoute" telemetry Qualisys motion capture system.
Each element of the control system is now executed from a silo'd process via Multiprocessing in order to aleviate python' Global Interpreter Lock issues (https://www.youtube.com/watch?v=Obt-vMVdM8s)
Pipes are used to communicate commands and data between the processes.

Driven by poor performance of IMUs in the lab environment.
Awaiting QTM equipped pool repairs 2021-2022.
