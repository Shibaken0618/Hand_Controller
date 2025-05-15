import cv2, time, numpy as np, pyautogui
import handTrackingModule as htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc

class HandController:
    def __init__(self, width=640, height=480):
        # initialize camera, detector, audio, brightness
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, width)
        self.cap.set(4, height)
        self.detector = htm.handDetector(detectionCon=0.7, maxHands=1)
        dev = AudioUtilities.GetSpeakers()
        intf = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = intf.QueryInterface(IAudioEndpointVolume)
        self.minVol, self.maxVol = self.volume.GetVolumeRange()[:2]
        # state vars
        self.modes = ['Volume','Scroll','Brightness']
        self.mode_idx = 0
        self.last_toggle = 0
        self.last_scroll = 0
        self.cfg = {
            'width': width,'height': height,
            'toggle_cooldown':1.0,'scroll_interval':0.2,'scroll_speed':35
        }

    def next_frame(self):
        # read & process one frame
        success, img = self.cap.read()
        if not success: return None, None
        img = cv2.flip(img, 1)
        img = self.detector.findHands(img)
        lmList, bbox = self.detector.findPosition(img, draw=True)

        # draw menu bar…
        # [Insert identical menu‐drawing code here]

        cur_t = time.time()
        mode = self.modes[self.mode_idx]
        # if hand detected and sized, read fingers
        if lmList:
            fingers = self.detector.fingersUp()
            # toggle gesture = rock sign
            if (fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and fingers[4]
                and cur_t - self.last_toggle > self.cfg['toggle_cooldown']):
                self.mode_idx = (self.mode_idx + 1) % len(self.modes)
                self.last_toggle = cur_t
            # call into per‐mode handlers:
            if mode in ['Volume','Brightness']:
                self._handle_volume_brightness(img, lmList, fingers, mode)
            else:
                self._handle_scroll(fingers, cur_t)

        return img, mode

    def _handle_volume_brightness(self, img, lmList, fingers, mode):
        # pinch length → percent
        length, img, info = self.detector.findDistance(4,8,img)
        per = np.interp(length,[50,250],[0,100])
        per = round(per/2)*2
        if mode=='Volume':
            vol = np.interp(length,[50,250],[self.minVol,self.maxVol])
            if not fingers[4]: self.volume.SetMasterVolumeLevel(vol,None)
            label = f'Vol: {int(per)}%'
        else:
            if not fingers[4]: sbc.set_brightness(int(per))
            label = f'Bri: {int(per)}%'
        cv2.putText(img,label,(50,450),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        # bar drawing…

    def _handle_scroll(self, fingers, now):
        if now - self.last_scroll > self.cfg['scroll_interval']:
            amt = self.cfg['scroll_speed']
            pyautogui.scroll( amt if fingers[1] else -amt )
            self.last_scroll = now

    def cleanup(self):
        self.cap.release()