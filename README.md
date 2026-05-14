# Spot the Difference — Desktop Application

A Python desktop game built with **Tkinter** (GUI) and **OpenCV** (image processing),
demonstrating Object-Oriented Programming principles.

---

## Requirements

| Package | Version |
|---|---|
| Python | ≥ 3.10 |
| opencv-python | ≥ 4.8 |
| Pillow | ≥ 10.0 |
| numpy | ≥ 1.24 |

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## How to Run

```bash
python app.py
```

---

## How to Play

1. Click **Load Image** and choose any JPG / PNG / BMP file.
2. The left panel shows the **original**; the right panel shows a **modified copy** with 5 hidden differences.
3. Click on the right panel where you think a difference is.
   - ✅ Correct → a **red circle** appears on both images.
   - ❌ Wrong → mistake counter increases (max 3 mistakes allowed).
4. **Reveal All** highlights all remaining differences with magenta circles and ends the round.
5. Load a new image to keep playing — your score accumulates across rounds.

---

## OOP Design

### Modules and Classes

| Module | Class | Role |
|---|---|---|
| [app.py](app.py) | `GameController` | Orchestrates gameplay, connects UI events to game logic |
| [core/difference.py](core/difference.py) | `Difference` | Region model with hit testing and overlap checks |
| [core/effects.py](core/effects.py) | `ImageEffect` + subclasses | Effect inheritance + polymorphism for image edits |
| [core/image_processor.py](core/image_processor.py) | `ImageProcessor` | Loads image and applies 5 non-overlapping differences |
| [core/game_state.py](core/game_state.py) | `GameState` | Tracks mistakes, found count, win/lose state |
| [ui/gui_manager.py](ui/gui_manager.py) | `GUIManager` | Builds the Tkinter UI, draws images and markers |

### OOP Principles Demonstrated

| Principle | Where |
|---|---|
| **Encapsulation** | `GameState` hides round state; `ImageProcessor` owns all OpenCV operations |
| **Inheritance** | All effect types inherit from `ImageEffect` |
| **Polymorphism** | `apply()` is called on any `ImageEffect` subclass uniformly |
| **Constructors** | Each class uses `__init__` to set its internal state |
| **Class interaction** | `GameController` coordinates `GUIManager`, `ImageProcessor`, and `GameState` |

---

## Difference Types (Randomly Applied)

| Type | Effect |
|---|---|
| Color Shift | HSV hue shift + saturation scaling |
| Gaussian Blur | Local blur with random kernel size |
| Brightness/Contrast | Linear brightness/contrast adjustment |
| Pixelation | Mosaic downscale/upscale block effect |
| Sharpen Filter | Local convolution sharpen |

All differences are generated at random sizes (40–90 px) and random positions,
with overlap detection ensuring no two regions touch.
# HIT137-Group-Assignment-3
