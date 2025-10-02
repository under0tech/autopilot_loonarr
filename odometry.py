import time
import autopilot
import messages
import commands as mavs
import definitions as vars

def odometry_provider(stop_command):
    connection = False
    master = {}
    while not connection and not stop_command.is_set():
        try:
            time.sleep(2)
            master = mavs.odometry_connect()[0]
            messages.display(messages.odometry_provider_connected, 
                             [vars.odometry_url])
            connection = True
            autopilot.state['odometry_connection'] = True
        except Exception as e:
            messages.display(messages.fatal_error, [e])
            pass
        
    start_time = time.time()
    while not stop_command.is_set():
        try:            
            usec = int((time.time() - start_time) * 1e6)
            mavs.vision_position_estimate_send(master, usec)
            time.sleep(0.05)  # 20Hz
        except:
            pass

    if master:
        mavs.disconnect(master)

    stopped_time = time.strftime("%H:%M:%S, %Y, %d %B", time.localtime())
    messages.display(messages.odometry_provider_done, [stopped_time])
