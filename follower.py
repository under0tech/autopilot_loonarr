import time
import autopilot
import messages
import router
import definitions as vars

def following_process(stop_command):
    while autopilot.state['connection'] == False and not stop_command.is_set():
        try:
            time.sleep(7)
            messages.display(messages.follower_process_connecting, 
                             [vars.mavlink_url])
        except Exception as e:
            messages.display(messages.fatal_error, [e])
            pass
    
    if not stop_command.is_set():
        messages.display(messages.follower_process_connected, 
                         [vars.mavlink_url])

    while not stop_command.is_set():
        try:
            if autopilot.state['bee_state'] in ['READY']:
                if autopilot.state['completed'] == True:
                    autopilot.state['completed'] = False
            elif autopilot.state['bee_state'] in ['KILL', 'FOLLOW']:
                if autopilot.state['completed'] == False:
                    router.put_command(router.Command(1,'FOLLOW',{}))
            time.sleep(2)
        except:
            pass

    stopped_time = time.strftime("%H:%M:%S, %Y, %d %B", time.localtime())
    messages.display(messages.follower_process_done, [stopped_time])
