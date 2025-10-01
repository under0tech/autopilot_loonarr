import logger
import commands as mavs

main_autopilot_started = {
    "log_info": "[AUTOPILOT STARTED]",
    "console": "\033[93m[AUTOPILOT STARTED]\033[0m"
    }

main_stopping_threads = {
    "log_info": "[STOPPING THREADS]",
    "console": "\033[93m[STOPPING THREADS]\033[0m"
    }

command_executor_done = {
    "log_info": "thread \'Command executor\', DONE.",
    "console": "thread \033[93mCommand executor\033[0m, DONE at {0}."
    }

command_executor_connected = {
    "log_info": "MAVLink connection is established: '{0}'",
    "console": "MAVLink connection is established: \033[92m{0}\033[0m"
    }

odometry_provider_done = {
    "log_info": "thread \'Odometry provider', DONE.",
    "console": "thread \033[93mOdometry provider\033[0m, DONE at {0}."
    }

odometry_provider_connected = {
    "log_info": "Odometry MAVLink connection is established: '{0}'",
    "console": "Odometry MAVLink connection is established: \033[92m{0}\033[0m"
    }

command_executor_executing_command = {
    "log_debug": "Executing command: {0}, Priority: {1}, Body: {2}",
    "console": "Executing command: {0}, Priority: {1}, Body: {2}"
    }

command_monitor_log = {
    "log_debug": "Monitoring: {0}",
    "console": "Monitoring: {0}"
    }

command_telemetry_log = {
    "log_debug": "Telemetry: {0}",
    "console": "Telemetry: {0}"
    }

command_monitor_battery_remaining = {
    "log_info": "low battery voltage {0}%",
    "console": "\033[93m[low battery voltage {0}%]\033[0m",
    "gc": "low battery voltage {0}%"
    }

command_telemetry_current_speed = {
    "log_info": "Current speed [{0} m/s]",
    "console": "current speed: - \033[93m[{0} m/s]\033[0m"
    }

command_telemetry_autopilot_state = {
    "log_info": "Autopilot state: {0}",
    "console": "AUTOPILOT STATE: \033[95m{0}\033[0m"
    }

bee_state_changed_to = {
    "log_info": "Bee state changed to [{0}]",
    "console": "Bee state changed to [{0}]",
    "gc": "{0}"
    }

initializing_autopilot = {
    "log_info": "Initializing autopilot",
    "console": "Initializing autopilot",
    "gc": "Initializing autopilot"
    }

command_follow_following_target = {
    "log_info": "[FOLLOWING TARGET N:{0}, E:{1}, D:{2}, Y:{3}]",
    "console": "\033[93m[FOLLOWING TARGET N:{0}, E:{1}, D:{2}, Y:{3}]\033[0m",
    "gc": "Target following"
    }

command_follow_mission_completed = {
    "log_info": "[MISSION COMPLETED]",
    "console": "\033[93mMISSION COMPLETED\033[0m",
    "gc": "MISSION COMPLETED"
    }

command_follow_target_lost = {
    "log_info": "[TARGET LOST]",
    "console": "\033[93mTARGET LOST\033[0m",
    "gc": "TARGET LOST"
    }

telemetry_requestor_done = {
    "log_info": "thread \'Telemetry requestor\', DONE.",
    "console": "thread \033[93mTelemetry requestor\033[0m, DONE at {0}."
    }

follower_process_done = {
    "log_info": "thread \'Follower process\', DONE.",
    "console": "thread \033[93mFollower process\033[0m, DONE at {0}."
    }

follower_process_connecting = {
    "log_info": "Follower: attempting to connect with '{0}'",
    "console": "Follower: attempting to connect with \033[91m{0}\033[0m"
    }

follower_process_connected = {
    "log_info": "Follower: connected with '{0}'",
    "console": "Follower: connected with \033[92m{0}\033[0m"
    }

telemetry_process_connecting = {
    "log_info": "Telemetry: attempting to connect with '{0}'",
    "console": "Telemetry: attempting to connect with \033[91m{0}\033[0m"
    }

telemetry_process_connected = {
    "log_info": "Telemetry: connected with '{0}'",
    "console": "Telemetry: connected with \033[92m{0}\033[0m"
    }

fatal_error = {
    "log_fatal": "{0}"
    }

main_autopilot_finished = {
    "log_info": "[AUTOPILOT FINISHED]",
    "console": "\033[93m[AUTOPILOT FINISHED]\033[0m"
    }

def display(msg, params=[]):
    if msg.get('log_info'):
        logger.log_message(None, msg['log_info'].format(*params), 'info')
    if msg.get('log_debug'):
        logger.log_message(None, msg['log_debug'].format(*params), 'debug')
    if msg.get('log_fatal'):
        logger.log_message(None, msg['log_fatal'].format(*params), 'fatal')
    if msg.get('console'):
        print(msg['console'].format(*params))
    if msg.get('gc'):
        mavs.send_message_to_gc(msg['gc'].format(*params))
