import cv2
import mediapipe as mp
import numpy as np
import os
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
class SlimeNode:

    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.vx = 0
        self.vy = 0
class AnimeSpellEngine:

    def __init__(self):
        self.slime_active = False

        self.slime_chains = {
            4: [],
            8: [],
            12: [],
            16: [],
            20: []
        }

        self.slime_initialized = False

        # LOAD EFFECTS
        self.fire_frames = self.load_frames("AnimeSpells/fire", 1200)
        self.lightning_frames = self.load_frames("AnimeSpells/lightning", 900)
        self.shatter_frames = self.load_frames("AnimeSpells/shatter", 1000)

        # HOLLOW PURPLE PNG SEQUENCES
        self.hp1_frames = self.load_frames(
            "AnimeSpells/hollowpurple1",
            1200
        )

        self.hp2_frames = self.load_frames(
            "AnimeSpells/hollowpurple2",
            1300
        )

        self.hp3_frames = self.load_frames(
            "AnimeSpells/hollowpurple3",
            1200
        )

        # ANIMATION INDEXES
        self.fire_index = 0
        self.lightning_index = 0
        self.shatter_index = 0

        # STATES
        self.prev_fire = False
        self.prev_lightning = False
        self.prev_shatter = False

        # HOLLOW PURPLE
        self.hollow_active = False
        self.hollow_timer = 0

    def init_slime_chain(self, fid, p1, p2):

        nodes = []

        segments = 20

        for i in range(segments + 1):

            t = i / segments

            x = p1[0] * (1 - t) + p2[0] * t
            y = p1[1] * (1 - t) + p2[1] * t

            nodes.append(
                SlimeNode(x, y)
            )

        self.slime_chains[fid] = nodes
    
        
        
    def update_slime_chain(self, fid, p1, p2):

        if len(self.slime_chains[fid]) == 0:
            self.init_slime_chain(fid, p1, p2)

        nodes = self.slime_chains[fid]

        nodes[0].x = p1[0]
        nodes[0].y = p1[1]

        nodes[-1].x = p2[0]
        nodes[-1].y = p2[1]

        spring_strength = 0.3
        damping = 0.92
        gravity = 0.8
        sag_amount = 2

        for _ in range(4):

            for i in range(1, len(nodes)-1):

                prev = nodes[i-1]
                curr = nodes[i]
                nxt = nodes[i+1]

                target_x = (prev.x + nxt.x) / 2

                target_y = (
                    (prev.y + nxt.y) / 2
                ) + sag_amount

                curr.vx += (
                    target_x - curr.x
                ) * spring_strength

                curr.vy += (
                    target_y - curr.y
                ) * spring_strength

                curr.vy += gravity

                curr.vx *= damping
                curr.vy *= damping

                curr.x += curr.vx
                curr.y += curr.vy
        
        
        
    # =====================================================
    # LOAD PNG FRAMES
    # =====================================================

    def load_frames(self, folder, target_size):

        frames = []

        if not os.path.exists(folder):
            print(f"Missing folder: {folder}")
            return frames

        files = sorted(os.listdir(folder))

        for file in files:

            if not file.lower().endswith(".png"):
                continue

            path = os.path.join(folder, file)

            img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

            if img is None:
                continue

            # ADD ALPHA IF MISSING
            if len(img.shape) == 3 and img.shape[2] == 3:

                alpha = np.ones(
                    (img.shape[0], img.shape[1], 1),
                    dtype=np.uint8
                ) * 255

                img = np.concatenate([img, alpha], axis=2)

            h, w = img.shape[:2]

            scale = target_size / max(h, w)

            new_w = int(w * scale)
            new_h = int(h * scale)

            img = cv2.resize(img, (new_w, new_h))

            frames.append(img)

        print(f"Loaded {len(frames)} frames from {folder}")

        return frames

    # =====================================================
    # FINGER STATES
    # =====================================================

    def finger_states(self, lm):

        tips = [4, 8, 12, 16, 20]
        pips = [2, 6, 10, 14, 18]

        states = []

        # THUMB
        thumb_open = abs(
            lm[tips[0]].x - lm[pips[0]].x
        ) > 0.04

        states.append(thumb_open)

        # OTHER FINGERS
        for i in range(1, 5):

            finger_open = (
                lm[tips[i]].y < lm[pips[i]].y
            )

            states.append(finger_open)

        return states

    # =====================================================
    # GESTURES
    # =====================================================

    def detect_gesture(self, lm):

        s = self.finger_states(lm)

        # FIRE = FIST
        if not any(s):
            return "FIRE"

        # LIGHTNING = INDEX + MIDDLE TOGETHER
        if (
            s[1] and
            s[2] and
            not s[3] and
            not s[4]
        ):

            index_tip = lm[8]
            middle_tip = lm[12]

            finger_gap = math.sqrt(
                (index_tip.x - middle_tip.x) ** 2 +
                (index_tip.y - middle_tip.y) ** 2
            )

            if finger_gap < 0.06:
                return "LIGHTNING"

        # HOLLOW PURPLE = INDEX ONLY
        if (
            s[1] and
            not s[2] and
            not s[3] and
            not s[4]
        ):
            return "HOLLOW_PURPLE"

        return None

    # =====================================================
    # SHATTER POSE
    # =====================================================

    def detect_shatter_pose(self, left_lm, right_lm):

        left = self.finger_states(left_lm)
        right = self.finger_states(right_lm)

        left_ok = (
            left[0] and
            left[1] and
            not left[2] and
            not left[3] and
            not left[4]
        )

        right_ok = (
            right[0] and
            right[1] and
            not right[2] and
            not right[3] and
            not right[4]
        )

        lx = left_lm[8].x
        ly = left_lm[8].y

        rx = right_lm[8].x
        ry = right_lm[8].y

        dist = math.sqrt(
            (lx - rx) ** 2 +
            (ly - ry) ** 2
        )

        close_enough = dist < 0.30

        return left_ok and right_ok and close_enough

    def detect_slime_pose(self, left_lm, right_lm):

        finger_pairs = [
            (4, 4),    # thumb
            (8, 8),    # index
            (12, 12),  # middle
            (16, 16),  # ring
            (20, 20)   # pinky
        ]

        touching = 0

        for l_idx, r_idx in finger_pairs:

            dx = left_lm[l_idx].x - right_lm[r_idx].x
            dy = left_lm[l_idx].y - right_lm[r_idx].y

            dist = math.sqrt(dx * dx + dy * dy)

            if dist < 0.05:
                touching += 1

        return touching >= 5


    
    # =====================================================
    # HELPERS
    # =====================================================

    def hand_center(self, lm, w, h):

        x = int(lm[9].x * w)
        y = int(lm[9].y * h)

        return x, y

    def hand_size(self, lm, width):

        wrist = lm[0]
        middle = lm[12]

        dist = math.sqrt(
            (wrist.x - middle.x) ** 2 +
            (wrist.y - middle.y) ** 2
        )

        return int(dist * width)

    def resize_effect(self, img, target):

        h, w = img.shape[:2]

        scale = target / max(h, w)

        nw = int(w * scale)
        nh = int(h * scale)

        return cv2.resize(img, (nw, nh))

    # =====================================================
    # PNG OVERLAY
    # =====================================================

    def overlay_png(self, frame, png, x, y):

        if png.shape[2] < 4:
            return

        h, w = png.shape[:2]

        x = int(x - w / 2)
        y = int(y - h / 2)

        if x >= frame.shape[1] or y >= frame.shape[0]:
            return

        if x + w <= 0 or y + h <= 0:
            return

        x1 = max(x, 0)
        y1 = max(y, 0)

        x2 = min(x + w, frame.shape[1])
        y2 = min(y + h, frame.shape[0])

        png_x1 = x1 - x
        png_y1 = y1 - y

        png_x2 = png_x1 + (x2 - x1)
        png_y2 = png_y1 + (y2 - y1)

        png_crop = png[png_y1:png_y2, png_x1:png_x2]

        alpha = png_crop[:, :, 3] / 255.0

        for c in range(3):

            frame[y1:y2, x1:x2, c] = (
                alpha * png_crop[:, :, c] +
                (1 - alpha) * frame[y1:y2, x1:x2, c]
            )

    # =====================================================
    # FIRE
    # =====================================================

    def draw_fire(self, frame, lm, w, h):

        if len(self.fire_frames) == 0:
            return

        effect = self.fire_frames[self.fire_index]

        self.fire_index += 3

        if self.fire_index >= len(self.fire_frames):
            self.fire_index = 0

        x, y = self.hand_center(lm, w, h)

        size = self.hand_size(lm, w)

        scaled = self.resize_effect(
            effect,
            size * 4
        )

        effect_h, effect_w = scaled.shape[:2]

        draw_x = x
        draw_y = y - effect_h // 2 + 165

        self.overlay_png(
            frame,
            scaled,
            draw_x,
            draw_y
        )

        overlay = frame.copy()
        overlay[:] = (0, 30, 70)

        cv2.addWeighted(
            overlay,
            0.04,
            frame,
            0.96,
            0,
            frame
        )

    # =====================================================
    # LIGHTNING
    # =====================================================

    def draw_lightning(self, frame, lm, w, h):

        if len(self.lightning_frames) == 0:
            return

        effect = self.lightning_frames[self.lightning_index]

        self.lightning_index += 1

        if self.lightning_index >= len(self.lightning_frames):
            self.lightning_index = 0

        # INDEX FINGERTIP
        x = int(lm[8].x * w)
        y = int(lm[8].y * h)

        size = self.hand_size(lm, w)

        scaled = self.resize_effect(
            effect,
            size * 3
        )

        self.overlay_png(
            frame,
            scaled,
            x,
            y
        )

        flash = np.full(frame.shape, 255, dtype=np.uint8)

        cv2.addWeighted(
            flash,
            0.03,
            frame,
            0.97,
            0,
            frame
        )

    # =====================================================
    # SHATTER
    # =====================================================

    def draw_shatter(self, frame, left_lm, right_lm, w, h):

        if len(self.shatter_frames) == 0:
            return

        effect = self.shatter_frames[self.shatter_index]

        self.shatter_index += 1

        if self.shatter_index >= len(self.shatter_frames):
            self.shatter_index = 0

        lx, ly = self.hand_center(left_lm, w, h)
        rx, ry = self.hand_center(right_lm, w, h)

        center_x = int((lx + rx) / 2)
        center_y = int((ly + ry) / 2)

        dist = int(
            math.sqrt(
                (lx - rx) ** 2 +
                (ly - ry) ** 2
            )
        )

        scaled = self.resize_effect(
            effect,
            max(500, dist * 3)
        )

        self.overlay_png(
            frame,
            scaled,
            center_x,
            center_y
        )

        flash = np.full(frame.shape, 255, dtype=np.uint8)

        cv2.addWeighted(
            flash,
            0.08,
            frame,
            0.92,
            0,
            frame
        )

    # =====================================================
    # HOLLOW PURPLE
    # =====================================================

    def draw_hollow_purple(self, frame, lm, w, h):

        # PINKY FINGERTIP
        x = int(lm[8].x * w)
        y = int(lm[8].y * h) - 50

        size = self.hand_size(lm, w)

        self.hollow_timer += 1

        # OVERLAP TIMINGS
        stage1_start = 0
        stage2_start = 45
        stage3_start = 90

        # ==========================================
        # DRAW SEQUENCE
        # ==========================================

        def draw_sequence(frames, local_time, fade_in):

            if len(frames) == 0:
                return

            index = min(
                local_time,
                len(frames) - 1
            )

            effect = frames[index]

            scaled = self.resize_effect(
                effect,
                size * 5
            )

            scaled = scaled.copy()

            alpha = max(
                0.0,
                min(1.0, fade_in)
            )

            scaled[:, :, 3] = (
                scaled[:, :, 3] * alpha
            ).astype(np.uint8)

            self.overlay_png(
                frame,
                scaled,
                x,
                y
            )

        # ==========================================
        # STAGE 1
        # ==========================================

        if self.hollow_timer >= stage1_start:

            local = self.hollow_timer - stage1_start

            # Fade in
            fade = min(1.0, local / 30)

            # Fade out when HP3 begins
            if self.hollow_timer > stage3_start:

                fade_out_progress = (
                    self.hollow_timer - stage3_start
                ) / 1

                fade *= max(
                    0.0,
                    1.0 - fade_out_progress
             )

            draw_sequence(
                self.hp1_frames,
                local,
                fade
            )

        # ==========================================
        # STAGE 2
        # ==========================================

        if self.hollow_timer >= stage2_start:

            local = self.hollow_timer - stage2_start

            fade = min(1.0, local / 30)

            draw_sequence(
                self.hp2_frames,
                local,
                fade
            )

        # ==========================================
        # STAGE 3
        # ==========================================

        if self.hollow_timer >= stage3_start:

            local = self.hollow_timer - stage3_start

            index = (
                local %
                len(self.hp3_frames)
            )

            draw_sequence(
                self.hp3_frames,
                index,
                1.0
            )

        # PURPLE GLOW
        overlay = frame.copy()
        overlay[:] = (90, 0, 120)

        cv2.addWeighted(
            overlay,
            0.06,
            frame,
            0.94,
            0,
            frame
        )
    def draw_elastic_link(self, frame, left_lm, right_lm, w, h):

        p1 = np.array([
            int(left_lm[8].x * w),
            int(left_lm[8].y * h)
        ])

        p2 = np.array([
            int(right_lm[8].x * w),
            int(right_lm[8].y * h)
        ])

        dist = np.linalg.norm(p2 - p1)

        if dist > 500:
           return

        mask = np.zeros(
            (frame.shape[0], frame.shape[1]),
            dtype=np.uint8
        )

        radius = max(
            18,
            int(70 - dist / 8)
        )

        cv2.circle(
            mask,
            tuple(p1),
            radius,
            255,
            -1
        )

        cv2.circle(
            mask,
            tuple(p2),
            radius,
            255,
            -1
        )

        cv2.line(
            mask,
            tuple(p1),
            tuple(p2),
            255,
            radius * 2
        )

        mask = cv2.GaussianBlur(
            mask,
            (51, 51),
            0
        )

        _, mask = cv2.threshold(
            mask,
            80,
            255,
            cv2.THRESH_BINARY
        )

        mask = cv2.GaussianBlur(
            mask,
            (31, 31),
            0
        )

        overlay = frame.copy()

        overlay[mask > 0] = (
            255,
            170,
            255
        )

        cv2.addWeighted(
            overlay,
            0.40,
            frame,
            0.60,
            0,
            frame
        )

        cv2.circle(
           frame,
           tuple(p1),
            radius,
            (255, 220, 255),
            -1,
            cv2.LINE_AA
        )

        cv2.circle(
            frame,
            tuple(p2),
            radius,
            (255, 220, 255),
            -1,
            cv2.LINE_AA
        )
    
    
    
    
    def draw_slime_chain(self, frame, fid):

        nodes = self.slime_chains[fid]

        if len(nodes) < 2:
            return

        pts = np.array(
            [
                [int(n.x), int(n.y)]
                for n in nodes
            ],
            np.int32
        )

        overlay = frame.copy()

        cv2.polylines(
            overlay,
            [pts],
            False,
            (255,180,255),
            24,
            cv2.LINE_AA
        )

        for node in nodes:

            cv2.circle(
                overlay,
                (int(node.x), int(node.y)),
                12,
                (255,180,255),
                -1,
                cv2.LINE_AA
            )

        cv2.addWeighted(
            overlay,
            0.40,
            frame,
            0.60,
            0,
            frame
        )



    # =====================================================
    # MAIN LOOP
    # =====================================================

    def run(self):

        cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame = cv2.flip(frame, 1)

            h, w, _ = frame.shape

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = hands.process(rgb)

            fire_active = False
            lightning_active = False
            shatter_active = False
            self.hollow_active = False

            if results.multi_hand_landmarks:

                all_hands = []

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

                    all_hands.append(
                        hand_landmarks.landmark
                    )

                # =================================================
                # SHATTER and GOOEY
                # =================================================

                if len(all_hands) == 2:

                    left_lm = all_hands[0]
                    right_lm = all_hands[1]
                    

                    if not self.detect_slime_pose(
                        left_lm,
                        right_lm
                    ):
                        thumb_dist = math.sqrt(
                        (left_lm[4].x - right_lm[4].x)**2 +
                        (left_lm[4].y - right_lm[4].y)**2
                        )

                        if thumb_dist > 0.7:
                            self.slime_active = False

                            self.slime_chains = {
                                4: [],
                                8: [],
                                12: [],
                                16: [],
                                20: []
                        }
                    
                    
                    if self.detect_slime_pose(
                        left_lm,
                        right_lm
                    ):
                        self.slime_active = True
                    
                    if self.slime_active:

                        finger_ids = [4, 8, 12, 16, 20]

                        for fid in finger_ids:

                            p1 = (
                                int(left_lm[fid].x * w),
                                int(left_lm[fid].y * h)
                            )

                            p2 = (
                                int(right_lm[fid].x * w),
                                int(right_lm[fid].y * h)
                            )

                            self.update_slime_chain(
                                fid,
                                p1,
                                p2
                            )

                            self.draw_slime_chain(
                               frame,
                               fid
                            )
                    
                    
                    if self.detect_shatter_pose(
                        left_lm,
                        right_lm
                    ):

                        shatter_active = True

                        if not self.prev_shatter:
                            self.shatter_index = 0

                        self.draw_shatter(
                            frame,
                            left_lm,
                            right_lm,
                            w,
                            h
                        )

                        cv2.putText(
                            frame,
                            "SHATTER",
                            (40,80),
                            cv2.FONT_HERSHEY_DUPLEX,
                            1.2,
                            (255,255,255),
                            3
                        )

                # =================================================
                # OTHER SPELLS DISABLED DURING SHATTER
                # =================================================

                if not shatter_active:

                    for lm in all_hands:

                        gesture = self.detect_gesture(lm)

                        # FIRE
                        if gesture == "FIRE":

                            fire_active = True

                            if not self.prev_fire:
                                self.fire_index = 0

                            self.draw_fire(
                                frame,
                                lm,
                                w,
                                h
                            )

                            cv2.putText(
                                frame,
                                "FIRE",
                                (40,80),
                                cv2.FONT_HERSHEY_DUPLEX,
                                1.2,
                                (0,140,255),
                                3
                            )

                            self.hollow_timer = 0

                        # LIGHTNING
                        elif gesture == "LIGHTNING":

                            lightning_active = True

                            if not self.prev_lightning:
                                self.lightning_index = 0

                            self.draw_lightning(
                                frame,
                                lm,
                                w,
                                h
                            )

                            cv2.putText(
                                frame,
                                "LIGHTNING",
                                (40,80),
                                cv2.FONT_HERSHEY_DUPLEX,
                                1.2,
                                (255,255,255),
                                3
                            )

                            self.hollow_timer = 0

                        # HOLLOW PURPLE
                        elif gesture == "HOLLOW_PURPLE":

                            self.hollow_active = True

                            self.draw_hollow_purple(
                                frame,
                                lm,
                                w,
                                h
                            )

                            cv2.putText(
                                frame,
                                "HOLLOW PURPLE",
                                (40,140),
                                cv2.FONT_HERSHEY_DUPLEX,
                                1.2,
                                (255,0,255),
                                3
                            )

            # RESET TIMER
            if not self.hollow_active:
                self.hollow_timer = 0

            # SAVE STATES
            self.prev_fire = fire_active
            self.prev_lightning = lightning_active
            self.prev_shatter = shatter_active

            cv2.imshow(
                "Anime Spell Engine",
                frame
            )

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    AnimeSpellEngine().run()