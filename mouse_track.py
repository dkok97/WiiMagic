import mouse
import time

while True:
    if mouse.is_pressed(button='left'):
        print('clicked')
    time.sleep(0.1)
