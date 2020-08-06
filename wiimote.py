import cwiid
import time
import numpy as np
import math
import sys
import mouse
from pymouse import PyMouse

m = PyMouse()

def projective_transform(points, w, h, screen_points):
  p0 = np.array([points[0][0], points[0][1]])
  p1 = np.array([points[1][0], points[1][1]])
  p2 = np.array([points[2][0], points[2][1]])
  p3 = np.array([points[3][0], points[3][1]])
  
  X_src = np.array([[p0[0], p1[0], p2[0]],
                    [p0[1], p1[1], p2[1]],
                    [1, 1, 1]])

  x_src = np.array([p3[0], p3[1], 1])

  vars_src = np.linalg.solve(X_src, x_src)

  A = np.array([[vars_src[0]*p0[0], vars_src[1]*p1[0], vars_src[2]*p2[0]],
                [vars_src[0]*p0[1], vars_src[1]*p1[1], vars_src[2]*p2[1]],
                [vars_src[0]*1, vars_src[1]*1, vars_src[2]*1]])
  print('A', A)

  r0 = np.array(screen_points[0])
  r1 = np.array(screen_points[1])
  r2 = np.array(screen_points[2])
  r3 = np.array(screen_points[3])
  
  X_dst = np.array([[r0[0], r1[0], r2[0]],
                    [r0[1], r1[1], r2[1]],
                    [1, 1, 1]])

  x_dst = np.array([r3[0], r3[1], 1])

  vars_dst = np.linalg.solve(X_dst, x_dst)

  B = np.array([[vars_dst[0]*r0[0], vars_dst[1]*r1[0], vars_dst[2]*r2[0]],
                [vars_dst[0]*r0[1], vars_dst[1]*r1[1], vars_dst[2]*r2[1]],
                [vars_dst[0]*1, vars_dst[1]*1, vars_dst[2]*1]])
  print('B', B)

  C = np.matmul(B, np.linalg.inv(A))
  print('C', C)

  return C

def get_screen_point(C, p):
  ret = np.matmul(C, p)
  return ret/ret[2]

print('Please press buttons 1 + 2 on your Wiimote now ...')
time.sleep(1)

try:
  wii=cwiid.Wiimote()
except RuntimeError:
  print ("Cannot connect to your Wiimote. Run again and make sure you are holding buttons 1 + 2!")
  quit()

print('Wiimote connection established!\n')
print('Go ahead and press some buttons\n')
print('Press PLUS and MINUS together to disconnect and quit.\n')

time.sleep(3)

button_delay = 0.1
wii.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_IR
do_IR = 1
do_cal = 1
cal_done = 0
create_mats = 1
cur_ir = [None, None, None, None]
prev_ir = [None, None, None, None]
A = None
t = None
release_counter = 0

cal_points = []
screen_points = []
screen_point = [0, 0, 0]

while True:
  if len(screen_points)==4:
    break
  if mouse.is_pressed(button='left'):
    pos=mouse.get_position()
    time.sleep(button_delay+0.1)
    screen_points.append([pos[0], pos[1]])
  print(screen_points)
  time.sleep(button_delay)

w = abs(screen_points[0][0] - screen_points[3][0])
h = abs(screen_points[0][1] - screen_points[1][1])

print('box height: ', h)
print('box width: ', w)
print('Recorded boundaries. onto calibration!')

while True:
  buttons = wii.state['buttons']

  # Detects whether + and - are held down and if they are it quits the program
  if (buttons - cwiid.BTN_PLUS - cwiid.BTN_MINUS == 0):
    print('\nClosing connection ...')
    # NOTE: This is how you RUMBLE the Wiimote
    wii.rumble = 1
    time.sleep(1)
    wii.rumble = 0
    exit(wii)

  if (buttons & cwiid.BTN_A):
    if do_IR:
      print('Turning off IR scanning')
      do_IR = False
    else:
      print('Turning on IR scanning')
      do_IR = True

  if do_IR:
    prev_ir = cur_ir
    cur_ir = wii.state['ir_src']

    if do_cal:
      if not cal_done:
        if prev_ir[0]==None and cur_ir[0]!=None:
          cal_points.append(cur_ir[0]['pos'])
        if len(cal_points)==4:
          cal_done = 1
        print(cal_points)

      else:
        if create_mats:
          print('Calibrated! Creating transformation matrices')
          C = projective_transform(cal_points, w, h, screen_points)
          create_mats = 0

        if cur_ir[0]!=None:
          release_counter = 0
          cam_point = np.array([cur_ir[0]['pos'][0], cur_ir[0]['pos'][1], 1])
##          print('camera point: ', cam_point)

          screen_point = get_screen_point(C, cam_point)
##          print('screen point:', screen_point)
##          mouse.move(screen_point[0], screen_point[1])
##          pos=mouse.get_position()
          print('current pos', pos)
          print('screen point', screen_point)
##          m.press(pos[0], pos[1])
          if mouse.is_pressed(button='left'):
              m.move(screen_point[0], screen_point[1])
          else:
              m.press(screen_point[0], screen_point[1])
        else:
          if mouse.is_pressed(button='left'):
            release_counter = release_counter + 1
            if release_cuonter==5:
              pos=mouse.get_position()
              m.release(pos[0], pos[1])
              release_cuonter = 0

    else:
      print(cur_ir)
      
    
  time.sleep(button_delay)
