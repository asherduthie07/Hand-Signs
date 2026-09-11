import cv2
import mediapipe as mp
import numpy as np
import time

# --- INITIALIZATION ---
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
# static_image_mode=False enables tracking optimized for video
hands = mp_hands.Hands(
    static_image_mode=False, 
    max_num_hands=1, 
    min_detection_confidence=0.7, 
    min_tracking_confidence=0.5
)

class RealTimeSpellCaster:
    def __init__(self):
        self.smoothing_factor = 0.25
        self.smooth_pos = None
        self.gesture_buffer = [] # For stabilizing gesture detection
        
    def get_finger_states(self, landmarks):
        """Returns list of 5 bools representing if fingers are 'up'."""
        # MediaPipe Landmarks: 4=ThumbTip, 8=IndexTip, 12=MiddleTip, 16=RingTip, 20=PinkyTip
        tips = [4, 8, 12, 16, 20]
        # Pips/Knuckles: 2=ThumbBase, 6=IndexPip, 10=MiddlePip, 14=RingPip, 18=PinkyPip
        pips = [2, 6, 10, 14, 18]
        
        states = []
        
        # Thumb: Horizontal comparison (for right hand, tip x < base x is 'out/up')
        states.append(landmarks[tips[0]].x < landmarks[pips[0]].x)
        
        # Other fingers: Vertical comparison (y-coordinate: lower value is higher on screen)
        for i in range(1, 5):
            states.append(landmarks[tips[i]].y < landmarks[pips[i]].y)
            
        return states

    def get_gesture(self, landmarks):
        states = self.get_finger_states(landmarks)
        
        # 1. Fist: All fingers down
        if not any(states):
            return "FIST"
        
        # 2. Victory: Index + Middle up
        if states[1] and states[2] and not states[3] and not states[4]:
            return "VICTORY"
        
        # 3. Open Palm: Index, Middle, Ring, Pinky up
        if all(states[1:]):
            return "PALM"
            
        return None

    def draw_effect(self, frame, gesture, pos, size):
        """Renders procedural VFX based on gesture."""
        cx, cy = pos
        overlay = frame.copy()
        
        if gesture == "FIST":
            # FIRE EFFECT: Chaotic orange/red circles
            for _ in range(8):
                radius = np.random.randint(size // 4, size // 2)
                offset = np.random.randint(-size//3, size//3, size=2)
                cv2.circle(overlay, (cx + offset[0], cy + offset[1]), radius, (0, 69, 255), -1)
            label = "FIRE STORM"
            color = (0, 140, 255)

        elif gesture == "VICTORY":
            # LIGHTNING: Jagged lines to random points
            for _ in range(4):
                end_x = cx + np.random.randint(-size, size)
                end_y = cy + np.random.randint(-size, size)
                cv2.line(overlay, (cx, cy), (end_x, end_y), (255, 255, 100), 3)
                cv2.circle(overlay, (end_x, end_y), 4, (255, 255, 255), -1)
            label = "THUNDER BOLT"
            color = (255, 255, 0)

        elif gesture == "PALM":
            # AURA: Pulsing concentric rings
            pulse = int(np.sin(time.time() * 10) * 10)
            cv2.circle(overlay, (cx, cy), size + pulse, (255, 0, 255), 4)
            cv2.circle(overlay, (cx, cy), size - 10 + pulse, (255, 100, 255), 2)
            label = "ARCANE SHIELD"
            color = (255, 0, 255)
        else:
            return frame

        # Blend overlay (alpha transparency)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Render Text UI
        cv2.putText(frame, label, (cx - 80, cy - size - 20), 
                    cv2.FONT_HERSHEY_TRIPLEX, 0.8, color, 2)
        return frame

    def run(self):
        cap = cv2.VideoCapture(0)
        print("Arcanum System Online. Press 'q' to quit.")

        while cap.isOpened():
            success, frame = cap.read()
            if not success: break

            # 1. Pre-process frame
            frame = cv2.flip(frame, 1) # Mirror
            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 2. Hand Tracking
            results = hands.process(rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # landmark[9] is the base of the middle finger (good center)
                    target_lm = hand_landmarks.landmark[9]
                    raw_pos = (int(target_lm.x * w), int(target_lm.y * h))
                    
                    # Size calculation (wrist to middle finger tip)
                    wrist = hand_landmarks.landmark[0]
                    tip = hand_landmarks.landmark[12]
                    size = int(np.sqrt((wrist.x-tip.x)**2 + (wrist.y-tip.y)**2) * w)

                    # 3. Smoothing Movement
                    if self.smooth_pos is None: self.smooth_pos = raw_pos
                    self.smooth_pos = (
                        int(self.smooth_pos[0] * (1-self.smoothing_factor) + raw_pos[0] * self.smoothing_factor),
                        int(self.smooth_pos[1] * (1-self.smoothing_factor) + raw_pos[1] * self.smoothing_factor)
                    )

                    # 4. Gesture Detection & Rendering
                    gesture = self.get_gesture(hand_landmarks.landmark)
                    frame = self.draw_effect(frame, gesture, self.smooth_pos, size)
                    
                    # Optional: Draw tracking skeleton for debugging
                    # mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # 5. Output
            cv2.imshow('Spell Caster Engine', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    engine = RealTimeSpellCaster()
    engine.run()
    