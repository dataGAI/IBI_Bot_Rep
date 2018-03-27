from IBI_raspisan import get_updates, handle_updates
import time
updates = get_updates()
while True:
    new_updates = get_updates()
    if len(new_updates['result']) > len(updates['result']):
        handle_updates(new_updates, len(new_updates['result']) - len(updates['result']))
        updates = new_updates
    elif len(new_updates['result']) == 0:
        updates = new_updates
    time.sleep(1)
