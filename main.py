import os
import threading
import messages
import router
import odometry
import telemetry
import follower

import definitions as vars

# INIT
bee_commands = router.command_queue
stop_command = threading.Event()

# BEE
os.system('clear')
messages.display(messages.main_autopilot_started)

executor_thread = threading.Thread(target=router.command_executor, 
                                   args=[stop_command])
telemetry_thread = threading.Thread(target=telemetry.telemetry_requestor, 
                                   args=[stop_command])
follower_thread = threading.Thread(target=follower.following_process,
                                   args=[stop_command])

executor_thread.start()
telemetry_thread.start()
follower_thread.start()

if vars.odometry_enabled:
    odometry_thread = threading.Thread(target=odometry.odometry_provider,
                                    args=[stop_command])
    odometry_thread.start()

router.put_command(router.Command(0,'INIT',{}))

input('Press enter to stop process...\n')
messages.display(messages.main_stopping_threads)

stop_command.set()

executor_thread.join()
telemetry_thread.join()
follower_thread.join()

if vars.odometry_enabled:
    odometry_thread.join()

messages.display(messages.main_autopilot_finished)