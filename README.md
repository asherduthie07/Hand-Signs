#  Hand Sign Recognition

A real-time **hand gesture controlled anime spell engine** built with **Python, OpenCV, and MediaPipe**.

The project uses your webcam to detect hand gestures and overlays animated PNG effects onto your hands in real time. Different hand poses trigger different abilities, including **Fire, Lightning, Hollow Purple, Shatter, and a dynamic Slime/Elastic effect**.

---

##  Features

* Real-time webcam hand tracking
* Hand gesture recognition using MediaPipe
* Fire spell animation
* Lightning spell animation
* Hollow Purple multi-stage animation
* Two-hand Shatter ability
* Dynamic elastic/slime effect between fingers
* PNG frame-based animations
* Automatic animation frame sequencing
* Dynamic effect scaling based on hand size
* Support for tracking up to two hands
* macOS camera support through AVFoundation

---

##  Spell Controls

| Gesture                                  | Ability             |
| ---------------------------------------- |  ------------------ |
| ✊ Fist                                   | 🔥 Fire           |
| ✌️ Index + Middle fingers together        | ⚡ Lightning      |
| ☝️ Index finger only                      | 🟣 Hollow Purple  |
| ☝️☝️ Both hands with index fingers close | 💥 Shatter         |
| 🫱🫲 All corresponding fingers touching  | 🫧 Slime / Elastic |


# 🛠️ Technologies Used

* **Python**
* **OpenCV**
* **MediaPipe**
* **NumPy**
* **Math / Physics calculations**
* **PNG animation sequences**

### Main Python Libraries

```text
opencv-python
mediapipe
numpy
```

---

# 📁 Project Structure

Your project should follow this structure:

```text
AnimeSpells/
│
├── main.py
│
├── fire/
│   ├── frame_001.png
│   ├── frame_002.png
│   ├── frame_003.png
│   └── ...
│
├── lightning/
│   ├── frame_001.png
│   ├── frame_002.png
│   ├── frame_003.png
│   └── ...
│
├── shatter/
│   ├── frame_001.png
│   ├── frame_002.png
│   ├── frame_003.png
│   └── ...
│
├── hollowpurple1/
│   ├── frame_001.png
│   ├── frame_002.png
│   └── ...
│
├── hollowpurple2/
│   ├── frame_001.png
│   ├── frame_002.png
│   └── ...
│
└── hollowpurple3/
    ├── frame_001.png
    ├── frame_002.png
    └── ...
```

The program specifically loads animation frames from these folders:

```text
AnimeSpells/fire
AnimeSpells/lightning
AnimeSpells/shatter
AnimeSpells/hollowpurple1
AnimeSpells/hollowpurple2
AnimeSpells/hollowpurple3
```

---

# Installation

## 1. Clone the repository

```bash
git clone <YOUR-REPOSITORY-URL>
cd AnimeSpells
```

---

## 2. Create a virtual environment

It is recommended to use a virtual environment so the project's dependencies don't interfere with your other Python projects.

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Install the dependencies

Install the required Python packages:

```bash
pip install opencv-python mediapipe numpy
```

Or install them individually:

```bash
pip install opencv-python
pip install mediapipe
pip install numpy
```

---

# 4. Add Your Own Animation Frames

**This step is required for the visual effects to work.**

Place your own `.png` animation frames inside the corresponding folders.

```text
fire/              → Fire animation frames
lightning/         → Lightning animation frames
shatter/           → Shatter animation frames
hollowpurple1/     → Hollow Purple stage 1
hollowpurple2/     → Hollow Purple stage 2
hollowpurple3/     → Hollow Purple stage 3
```

For example:

```text
fire/
├── 001.png
├── 002.png
├── 003.png
├── 004.png
└── ...

lightning/
├── 001.png
├── 002.png
├── 003.png
└── ...
```

### ⚠️ Important

* Use **PNG files**.
* Transparent backgrounds are recommended.
* Keep the frames in the correct sequence.
* Make sure the folders have the exact names expected by the program.
* You can use your **own animation frames/effects** instead of the original assets.
* The program automatically reads the PNG files from these folders and resizes them during runtime.

If a required folder doesn't exist, the program will report:

```text
Missing folder: <folder-name>
```

The frame loader only processes `.png` files and automatically adds an alpha channel if an image doesn't already have one.

---

# 5. Run the Project

Once your dependencies and animation frames are ready:

```bash
python main.py
```

On some systems you may need:

```bash
python3 main.py
```

Your webcam should open automatically.

---

#  Using the Engine

After starting the program:

1. Allow the application to access your webcam.
2. Position your hands in front of the camera.
3. Perform one of the supported gestures.
4. The corresponding spell effect will appear.
5. Try combining both hands for Shatter or the Slime effect.
6. Press **`Q`** to exit the application.

The application opens the webcam using OpenCV and processes frames continuously through MediaPipe's hand tracking system.

---

# Customization

You can modify the project to create your own spells and gestures.

For example, you could add:

```text
🌪️ Wind
❄️ Ice
🔥 Flame Burst
⚡ Thunder
🌌 Black Hole
💚 Energy Beam
🩸 Blood Manipulation
🌀 Teleportation
```

You can also create your own gestures by modifying the gesture detection logic inside:

```python
detect_gesture()
```

and add additional two-hand poses inside:

```python
detect_shatter_pose()
detect_slime_pose()
```

---

# 📌 Requirements

* Python 3
* Webcam
* OpenCV
* MediaPipe
* NumPy
* Animation PNG assets

A reasonably good webcam and lighting will provide better hand-tracking results.

---


## ⭐ If you like the project

Give the repository a ⭐ on GitHub and feel free to experiment with your own gestures and animation frames!

---

If the animation assets belong to someone else, make sure you have permission to redistribute them before publishing them with the repository.
