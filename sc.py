import cv2
import mediapipe as mp
import numpy as np
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

class SpellCaster:
    def __init__(self):
        self.smooth_pos = None
        self.smoothing = 0.25

        self.trail = []
        self.max_trail = 40
        self.last_spell = ""

    def get_finger_states(self, lm):
        tips = [4, 8, 12, 16, 20]
        pips = [2, 6, 10, 14, 18]

        states = []
        states.append(lm[tips[0]].x < lm[pips[0]].x)

        for i in range(1, 5):
            states.append(lm[tips[i]].y < lm[pips[i]].y)

        return states

    def is_gojo(self, lm):
        i1 = lm[8]
        i2 = lm[12]
        dist = abs(i1.x - i2.x) + abs(i1.y - i2.y)
        return dist < 0.05

    def is_gun(self, states):
        return states[0] and states[1] and not states[2] and not states[3] and not states[4]

    def recognize_spell(self, trail):
        xs = [p[0] for p in trail]
        ys = [p[1] for p in trail]

        dx = max(xs) - min(xs)
        dy = max(ys) - min(ys)

        if dx > 150 and dy < 80:
            return "FIRE"
        elif dy > 150 and dx < 80:
            return "WATER"
        elif dx > 100 and dy > 100:
            return "RED"
        return ""

    def update_trail(self, pos, drawing):
        if drawing:
            self.trail.append(pos)
            if len(self.trail) > self.max_trail:
                self.trail.pop(0)
        else:
            if len(self.trail) > 10:
                self.last_spell = self.recognize_spell(self.trail)
            self.trail = []

    def draw_trail(self, frame):
        for i in range(1, len(self.trail)):
            cv2.line(frame, self.trail[i-1], self.trail[i], (0,255,255), 3)

        if self.last_spell:
            cv2.putText(frame, f"SPELL: {self.last_spell}", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)

    def glow(self, frame, center, size, color):
        for i in range(4):
            overlay = frame.copy()
            cv2.circle(overlay, center, size + i*8, color, -1)
            cv2.addWeighted(overlay, 0.15, frame, 0.85, 0, frame)

    def draw_effect(self, frame, gesture, pos, size):
        cx, cy = pos

        if gesture == "FIST":
            self.glow(frame, (cx,cy), size, (0,140,255))

        elif gesture == "VICTORY":
            for _ in range(4):
                x = cx + np.random.randint(-size, size)
                y = cy + np.random.randint(-size, size)
                cv2.line(frame, (cx,cy), (x,y), (255,255,0), 2)

        elif gesture == "PALM":
            pulse = int(np.sin(time.time()*10)*10)
            self.glow(frame, (cx,cy), size+pulse, (255,0,255))

        elif gesture == "GOJO":
            frame[:] = (20,0,40)
            for _ in range(150):
                x = np.random.randint(0, frame.shape[1])
                y = np.random.randint(0, frame.shape[0])
                cv2.circle(frame, (x,y), 1, (255,255,255), -1)
            cv2.putText(frame, "DOMAIN EXPANSION", (100,100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255,0,255), 3)

        elif gesture == "GUN":
            cv2.line(frame, (cx,cy), (cx+200,cy), (255,255,255), 4)

    def run(self):
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                hands_list = results.multi_hand_landmarks

                # 🔴 SUKUNA (2 hands close)
                if len(hands_list) == 2:
                    h1 = hands_list[0].landmark[9]
                    h2 = hands_list[1].landmark[9]

                    dist = np.sqrt((h1.x-h2.x)**2 + (h1.y-h2.y)**2)

                    if dist < 0.1:
                        frame[:] = (0,0,50)
                        cv2.putText(frame, "MALEVOLENT SHRINE", (80,120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,255), 3)

                for hand_landmarks in hands_list:

                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=3),
                        mp_drawing.DrawingSpec(color=(255,0,0), thickness=2)
                    )

                    lm = hand_landmarks.landmark
                    states = self.get_finger_states(lm)

                    index_tip = lm[8]
                    pos = (int(index_tip.x*w), int(index_tip.y*h))

                    if self.smooth_pos is None:
                        self.smooth_pos = pos

                    self.smooth_pos = (
                        int(self.smooth_pos[0]*(1-self.smoothing) + pos[0]*self.smoothing),
                        int(self.smooth_pos[1]*(1-self.smoothing) + pos[1]*self.smoothing)
                    )

                    # ✍️ Drawing mode (only index finger)
                    drawing = states[1] and not any(states[2:])
                    self.update_trail(self.smooth_pos, drawing)

                    # Gesture detection
                    gesture = None

                    if not any(states):
                        gesture = "FIST"
                    elif states[1] and states[2] and not states[3]:
                        gesture = "VICTORY"
                    elif all(states[1:]):
                        gesture = "PALM"
                    elif self.is_gojo(lm):
                        gesture = "GOJO"
                    elif self.is_gun(states):
                        gesture = "GUN"

                    # Size calc
                    wrist = lm[0]
                    mid = lm[12]
                    size = int(np.sqrt((wrist.x-mid.x)**2 + (wrist.y-mid.y)**2)*w)

                    if gesture:
                        self.draw_effect(frame, gesture, self.smooth_pos, size)

                self.draw_trail(frame)

            cv2.imshow("Spell Caster", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    SpellCaster().run()