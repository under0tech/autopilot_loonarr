import math
import time
import definitions as vars
from pymavlink import mavutil

command_delays =  {
    'disconnect': 0.2,
    'disarm': 1,
    'target_search' : 0.5
}

def wait_for_execution(target, delay=0):
    if delay == 0:
        delay = command_delays.get(target)
    time.sleep(delay)

def connect(system=255):
    master = mavutil.mavlink_connection(vars.mavlink_url,
                                        baud=57600,
                                        source_system=system)
    vehicle = master.wait_heartbeat()
    return master, vehicle

def odometry_connect(system=1):
    master = mavutil.mavlink_connection(vars.odometry_url,
                                        baud=57600,
                                        source_system=system)
    vehicle = master.wait_heartbeat()
    return master, vehicle

def disconnect(master):
    wait_for_execution('disconnect')
    master.close()

def send_message_to_gc(message):
    master, vehicle = connect(1)
    master.mav.statustext_send(
        mavutil.mavlink.MAV_SEVERITY_NOTICE, message.encode())
    disconnect(master)

def rover_init():
    master, vehicle = connect(1)
    master.mav.request_data_stream_send(
    master.target_system,
    master.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL, 1, 1)
    disconnect(master)

def telemetry(target):
    master, vehicle = connect(1)
    msg = master.recv_match(type=target, blocking=True)
    telemetry = {}
    if msg is not None and msg.get_srcSystem() == 1 \
        and msg.get_srcComponent() == 1:
            telemetry = msg.to_dict()
    disconnect(master)
    return telemetry

def force_disarm():
    master, vehicle = connect(1)
    print("Disarming!")
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,
        0,  # Param1: 0 = Disarm
        21196,  # Param2: Magic number to force disarm
        0, 0, 0, 0, 0)

    wait_for_execution('disarm')
    disconnect(master)

def follow_target(n_coord, e_coord, d_coord, yaw_angle):
    master, vehicle = connect()
    msg = master.mav.set_position_target_local_ned_encode(
        0, 0, 0, 9, 3580,
        n_coord,
        e_coord,
        0,
        1, 0, 0, 0, 0, 0, 0, 0)
        # 0, 0, 0, 9, 3576,
        # n_coord,
        # e_coord,
        # d_coord,
        # 1, 0, 0, 0, 0, 0, yaw_angle, 0)
    
    # 0 0 0 1 3580 100 0 0 1 0 0 0 0 0 0 0
    master.mav.send(msg)

    # waiting for command to be executed
    delay = int(n_coord / 7 + 1)
    wait_for_execution(None, delay)

    disconnect(master)

def target_search(target_lost_count):
    master, vehicle = connect()
    
    yaw_angle = 0 
    d = 0
    if target_lost_count > vars.target_lost_limit:
        yaw_angle = 0.7854 # 15 deg
        d = 1
    
    msg = master.mav.set_position_target_local_ned_encode(
        0, 0, 0, 9, 3576,
        -1,
        0,
        d,
        1, 0, 0, 0, 0, 0, yaw_angle, 0)
    master.mav.send(msg)

    wait_for_execution('target_search')
    disconnect(master)
    return d

def vision_position_estimate_send(master, usec):
    # EXPERIMENTAL: Fake 3D pose
    # You will need to transmit 
    # RPLidar sensor data here instead
    x = 2.0  # meters forward
    y = 2.0  # meters right
    z = -0.2 # -Z is up in NED
    roll = 0.0
    pitch = 0.0
    yaw = math.radians(90)  # face east

    master.mav.vision_position_estimate_send(
        usec,
        x, y, z,
        roll, pitch, yaw
    )