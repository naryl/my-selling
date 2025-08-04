
# Совместимость с Python 2.7

import threading

def start_new_thread(func, args):
    t = threading.Thread(target=func, args=args)
    t.start()
    return t