import time
import queue
import autopilot
import messages
import vision
import commands as mavs
import definitions as vars

command_queue = queue.PriorityQueue()

class Command:
    def __init__(self, priority, name, body):
        self.priority = priority
        self.name = name
        self.body = body

    def __lt__(self, other):
        return self.priority < other.priority

def put_command(command):
    command_queue.put(command)

def command_executor(stop_command):
    connection = False
    while not connection and not stop_command.is_set():
        try:
            time.sleep(2)
            con = mavs.connect()
            messages.display(messages.command_executor_connected, 
                             [vars.mavlink_url])
            mavs.disconnect(con[0])
            connection = True
            autopilot.state['connection'] = True
        except Exception as e:
            messages.display(messages.fatal_error, [e])
            pass

    while not stop_command.is_set():
        try:
            command = command_queue.get(timeout=1)
            execute_command(command)
            command_queue.task_done()
            time.sleep(1)
        except:
            pass

    stopped_time = time.strftime("%H:%M:%S, %Y, %d %B", time.localtime())  
    messages.display(messages.command_executor_done, [stopped_time])

def execute_command(command):
    messages.display(messages.command_executor_executing_command, 
                     [command.name, command.priority, command.body])

    if command.name in commands:
        commands[command.name](command.body)

def command_monitor(params):
    monitor = mavs.telemetry(params['target'])
    messages.display(messages.command_monitor_log, [monitor])

    if monitor != {}:
        if params['target'] == 'SYS_STATUS':
            battery_remaining = int(monitor['battery_remaining'])
            autopilot.state['battery'] = battery_remaining
            if battery_remaining < 20:
                messages.display(
                    messages.command_monitor_battery_remaining, 
                    [monitor])
            # if battery_remaining < 3:
            #     command_queue.queue.clear()
            #     put_command(Command(0,'DISARM',{}))

def command_telemetry_viable_status(telemetry):
    speed = int(round(((telemetry['vx'] ** 2) + (telemetry['vy'] ** 2)) ** 0.5))
    autopilot.state['speed'] = speed
    if speed > 1:
        messages.display(
            messages.command_telemetry_current_speed, 
            [speed])

def command_telemetry_mode_change(telemetry):
    chan7_raw = int(telemetry['chan7_raw'])
    autopilot_mode = autopilot.state['bee_state']
    if chan7_raw == 999:
        autopilot_mode = 'OFF'
    elif chan7_raw == 1503:
        autopilot_mode = 'READY'
    elif chan7_raw == 2000:
        autopilot_mode = 'FOLLOW'
    elif chan7_raw == 0:
        autopilot_mode = 'OFF'

    if autopilot_mode != autopilot.state['bee_state']:
        autopilot.state['bee_state'] = autopilot_mode
        messages.display(
                    messages.bee_state_changed_to, [autopilot_mode])
        command_queue.queue.clear()

def command_telemetry(params):
    telemetry = mavs.telemetry(params['target'])
    messages.display(messages.command_telemetry_log, [telemetry])
    
    if telemetry != {}:
        if params['target'] == 'LOCAL_POSITION_NED':
            command_telemetry_viable_status(telemetry)
        if params['target'] == 'RC_CHANNELS':
            command_telemetry_mode_change(telemetry)
                    
    messages.display(
        messages.command_telemetry_autopilot_state, 
        [autopilot.state])

def command_init(params):
    messages.display(messages.initializing_autopilot)
    mavs.rover_init()

def command_disarm(params):
    mavs.force_disarm()

def command_follow(params):
    altitude = 1
    completed = autopilot.state['completed']
    frame = autopilot.state['frame']
    speed = autopilot.state['speed']
    frame = autopilot.state['frame']
    
    if completed == False:
        # Don't follow if drone on its way
        if frame != {} and speed > 0:
            return
        
        # Find target and follow
        result = vision.get_camera_image()
        if result != {}:
            d = 0
            boxes = result.boxes.xyxy.tolist()
            if len(boxes) > 0:
                autopilot.state['target_lost'] = 0
                x1, y1, x2, y2 = boxes[0]

                if vision.is_target_close_enough(x1, y1, x2, y2) == False:
                    n, e, d, y = vision.get_ned_target(x1, y1, x2, y2, altitude)
                    autopilot.state['frame'] = (n, e, d, y)
                    messages.display(messages.command_follow_following_target,
                                                        [n, e, d, y])
                    mavs.follow_target(n, e, d, y)
                else:
                    # If target close enough
                    autopilot.state['completed'] = True
                    # Mission completed
                    command_queue.queue.clear()
                    messages.display(messages.command_follow_mission_completed)
                    mavs.force_disarm()
            else:
                tl_count = int(autopilot.state['target_lost'])
                messages.display(messages.command_follow_target_lost)
                autopilot.state['target_lost'] = int(tl_count + 1)

                d = mavs.target_search(tl_count)
            
            # if target was lost we have to urgently update state
            if d != 0:
                put_command(
                    Command(0,'TELEMETRY',{'target':'RC_CHANNELS'}))


commands = {
    'INIT': command_init,
    'MONITOR': command_monitor,
    'TELEMETRY': command_telemetry,
    'FOLLOW':command_follow,
    'DISARM': command_disarm,
}