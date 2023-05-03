import pytesseract
import numpy as np
import pyautogui
import time
import cv2


time.sleep(3)

# 定位
def localion():
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    save = cv2.imread('save.jpg', cv2.IMREAD_COLOR)
    quit = cv2.imread('quit.jpg', cv2.IMREAD_COLOR)
    result_save = cv2.matchTemplate(screenshot, save, cv2.TM_CCOEFF_NORMED)
    result_quit = cv2.matchTemplate(screenshot, quit, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc_save = cv2.minMaxLoc(result_save)
    a,b,c,max_loc_quit = cv2.minMaxLoc(result_quit)
    x, y, w, h = max_loc_quit[0]-50,max_loc_save[1]+50,max_loc_save[0]-max_loc_quit[0]+200,max_loc_quit[1]-max_loc_save[1]
    return [x, y, w, h]


def gettext(x,y,w,h):
    screen = np.array(pyautogui.screenshot())
    image = screen[y:y+h, x:x+w]
    text_data = pytesseract.image_to_data(image, output_type='dict')
    current_line = []
    for i, text in enumerate(text_data['text']):
        if text.strip():
            if 'SOURCE' in text:
                current_line = []
                continue
            if 'CONTEXT' in text:
                break
            current_line.append(text)
    text = ' '.join(current_line)
    text2 = text.replace('STRING','')
    print(text2)
    return text2