import cv2
import mediapipe as mp
import numpy as np
import random
import time

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

class SpellEngine:

    def __init__(self):
        self.smooth_x = 0
        self.smooth_y = 0
        self.alpha = 0.2

    def finger_states(self, lm):
        tips = [4, 8, 12, 16, 20]
        pips = [2, 6, 10, 14, 18]

        states = []

        states.append(lm[tips[0]].x < lm[pips[0]].x)

        for i in range(1, 5):
            states.append(lm[tips[i]].y < lm[pips[i]].y)

        return states

    def detect_gesture(self, lm):

        s = self.finger_states(lm)

        # ✊ FIST
        if not any(s):
            return "FIRE"

        # ✌️ PEACE
        if s[1] and s[2] and not s[3] and not s[4]:
            return "LIGHTNING"

        return None

    def realistic_fire(self, frame, center, size):

        cx, cy = center

        overlay = frame.copy()

        # flame layers
        for _ in range(35):

            offset_x = random.randint(-size//3, size//3)
            offset_y = random.randint(-size//2, size//2)

            radius = random.randint(size//8, size//3)

            color_choice = random.choice([
                (0,140,255),
                (0,90,255),
                (0,200,255),
                (50,50,255)
            ])

            cv2.circle(
                overlay,
                (cx + offset_x, cy + offset_y),
                radius,
                color_choice,
                -1
            )

        # glow
        for i in range(5):
            cv2.circle(
                overlay,
                (cx, cy),
                size + i*15,
                (0,120,255),
                2
            )

        cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

        cv2.putText(
            frame,
            "FIRE",
            (cx - 50, cy - size - 30),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (0,140,255),
            2
        )

    def lightning_branch(self, frame, start, angle, length, depth):

        if depth == 0:
            return

        x1, y1 = start

        x2 = int(x1 + np.cos(angle) * length)
        y2 = int(y1 + np.sin(angle) * length)

        # glow line
        cv2.line(frame, (x1,y1), (x2,y2), (255,255,255), 6)
        cv2.line(frame, (x1,y1), (x2,y2), (255,255,100), 2)

        # recursive branches
        branch_count = random.randint(1, 2)

        for _ in range(branch_count):

            new_angle = angle + random.uniform(-0.7, 0.7)

            self.lightning_branch(
                frame,
                (x2,y2),
                new_angle,
                length * 0.7,
                depth - 1
            )

    def realistic_lightning(self, frame, center, size):

        cx, cy = center

        overlay = frame.copy()

        # screen flash
        flash = np.full(frame.shape, (255,255,255), dtype=np.uint8)

        cv2.addWeighted(flash, 0.08, overlay, 0.92, 0, overlay)

        # main lightning bolts
        for _ in range(4):

            angle = random.uniform(0, np.pi * 2)

            self.lightning_branch(
                overlay,
                (cx, cy),
                angle,
                random.randint(size, size*2),
                4
            )

        # electric particles
        for _ in range(30):

            px = cx + random.randint(-size, size)
            py = cy + random.randint(-size, size)

            cv2.circle(
                overlay,
                (px, py),
                random.randint(1,3),
                (255,255,255),
                -1
            )

        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)

        cv2.putText(
            frame,
            "LIGHTNING",
            (cx - 90, cy - size - 30),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255,255,100),
            2
        )

    def run(self):

        cap = cv2.VideoCapture(0)

        while True:

            success, frame = cap.read()

            if not success:
                break

            frame = cv2.flip(frame, 1)

            h, w, _ = frame.shape

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(rgb)

            if results.multi_hand_landmarks:

                for hand_landmarks in results.multi_hand_landmarks:

                    mp_draw.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_draw.DrawingSpec(
                            color=(0,255,0),
                            thickness=2,
                            circle_radius=3
                        ),
                        mp_draw.DrawingSpec(
                            color=(255,0,0),
                            thickness=2
                        )
                    )

                    lm = hand_landmarks.landmark

                    # hand center
                    center_lm = lm[9]

                    x = int(center_lm.x * w)
                    y = int(center_lm.y * h)

                    # smoothing
                    self.smooth_x = int(
                        self.smooth_x * (1-self.alpha) + x * self.alpha
                    )

                    self.smooth_y = int(
                        self.smooth_y * (1-self.alpha) + y * self.alpha
                    )

                    # hand size
                    wrist = lm[0]
                    tip = lm[12]

                    size = int(
                        np.sqrt(
                            (wrist.x - tip.x)**2 +
                            (wrist.y - tip.y)**2
                        ) * w
                    )

                    gesture = self.detect_gesture(lm)

                    if gesture == "FIRE":
                        self.realistic_fire(
                            frame,
                            (self.smooth_x, self.smooth_y),
                            size
                        )

                    elif gesture == "LIGHTNING":
                        self.realistic_lightning(
                            frame,
                            (self.smooth_x, self.smooth_y),
                            size
                        )

            cv2.imshow("Spell Engine", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    SpellEngine().run()