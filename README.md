# Eyemate-AI-assistive-software-for-blind- 👁️🎓

> **AI-assistive software for blind that can be installed on computer and with the help camera and speakers it can guide blind person.**


---

## 📖 Table of Contents
- [Overview & Motivation](#-overview--motivation)
- [Key Features](#-key-features)
- [System Architecture (Hardware)](#️-system-architecture-hardware)
- [Software & AI Models](#-software--ai-models)
- [Control Interfaces](#-control-interfaces)
- [Installation & Setup Guide](#-installation--setup-guide)
- [Limitations & Future Scope](#️-limitations--future-scope)

---

## 🌟 Overview & Motivation
With over 8 million visually impaired individuals in Pakistan alone, accessing quality education is a significant challenge due to a lack of affordable assistive technologies. While tools like Google Lens or specialized smart glasses exist, they are often cost-prohibitive or rely heavily on continuous internet connections.

**EyeMate** addresses these challenges through a three-phased approach:
1. **Reading & Detection:** Optical Character Recognition (OCR) and object detection for immediate audio feedback.
2. **Indoor Navigation:** Guiding users through academic buildings (classrooms, libraries) using ArUco markers and haptic feedback.
3. **Advanced Scene Understanding:** Employing local Vision-Language Models (VLMs) to provide detailed contextual descriptions of the user's environment.

---

## ✨ Key Features

- **Text-to-Speech (OCR):** Instantly converts printed text from books, handouts, or digital screens (PDFs, websites) into clear audio using **EasyOCR**.
- **Real-Time Object Detection (Live Guide):** Continuously scans for everyday obstacles (doors, chairs, stairs, people) and provides directional voice alerts (e.g., "Chair in front of you", "Door on the right") using **YOLOv11n**.
- **Indoor Navigation (ArUco Markers):** Unlike GPS (which fails indoors) or QR Codes (which require precise alignment and lighting), EyeMate uses **ArUco Markers** placed around buildings to calculate orientation and position, routing users to specific rooms.
- **Scene Description:** Takes a snapshot of the surroundings and uses the **Qwen-VL Large Language Model** to provide a highly detailed, natural language description of the room and its context.
- **Haptic Path Planning:** In addition to voice, Arduino-controlled vibration motors embedded in a waist belt provide tactile feedback to indicate the safest direction of travel.

---

## 🛠️ System Architecture (Hardware)

To ensure the system is adaptable to different budgets and processing needs, EyeMate is deployed using a student-friendly laptop-based configuration:

### DeskMate (Laptop-Based System)
A configuration that utilizes hardware the user may already own.
- **Core Processor:** User's Laptop (CPU/GPU) carried in a backpack.
- **Vision:** Standard USB webcam mounted on a cap.
- **Advantage:** Leverages laptop GPUs for significantly faster inference speeds, particularly for the Qwen-VL Large Language Model.
- **Microcontrollers:** 
  - **ESP32:** Acts as a wireless receiver for remote control commands.
  - **Arduino Nano:** Handles serial communication to actuate the waist-belt vibration motors.

---

## 🧠 Software & AI Models

Extensive testing was conducted to select the best algorithms for fast, offline execution.

| Function | Chosen Model | Why It Was Chosen |
| :--- | :--- | :--- |
| **Object Detection** | **YOLOv11-nano** | Optimized for lightweight execution. Provides real-time inference, high accuracy on small/overlapping objects, and low memory footprint compared to YOLOv5 or v8. |
| **Optical Character Recognition** | **EasyOCR** | Chosen over Tesseract (requires heavy preprocessing) and PaddleOCR (hard to package offline). EasyOCR offers high accuracy on printed text and easy `.exe` deployment. |
| **Scene Description** | **Qwen-VL (Local LLM)** | Chosen over GPT-4/GPT-V APIs to eliminate subscription costs and the need for constant internet access. Qwen provides excellent natural language context locally via GPU. |
| **Navigation Markers** | **ArUco Markers** | Detectable up to 8 feet away (for a 6.8cm marker), handles low-light and severe angles far better than standard QR codes. |
| **Mobile App** | **Kotlin (Android)** | Provides seamless Bluetooth/Wi-Fi integration with the ESP32 and Java-based backend frameworks. |

---

## 🎛️ Control Interfaces

EyeMate is designed to be fully accessible for users with severe visual impairments.

1. **EyeMate Mobile App:** A touch-accessible Android application to toggle system modes (OCR, Live Guide, Navigation, Scene Description).
2. **Teddy Remote Controller:** An ESP32-based physical handheld remote shaped like a teddy bear. It features **Braille-printed physical buttons**, allowing users to send commands to the system entirely via touch, without needing to interact with a smartphone screen.

---

## 🚀 Installation & Setup Guide

### Prerequisites
- Python 3.11+
- Windows/Linux Laptop with a dedicated or integrated GPU

### 1. Main System Setup
1. Clone this repository and navigate into the `Source_Code` directory:
   ```bash
   git clone <repository-url>
   cd Source_Code
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main application file:
   ```bash
   python front.py
   ```

### 2. Microcontroller Setup
1. **ESP32 (Teddy Remote):** Install the ESP32 board manager in Arduino IDE. Flash the remote routing code to map physical button presses to Wi-Fi/Bluetooth commands.
2. **Arduino Nano (Haptic Belt):** Flash the serial communication code to receive directional commands from the Laptop and actuate the left/right vibration motors.

### 3. Networking
- Ensure the ESP32 remote and the Laptop are paired via MAC address or on the same local Wi-Fi network to ensure commands route successfully.

---

## ⚠️ Limitations & Future Scope

While highly capable, the current prototype has a few limitations:
- **Outdoor Navigation:** ArUco markers are strictly for indoor use. Outdoor navigation would require integration with GPS and potentially RTK modules for precision.
- **Lighting Conditions:** Like all vision-based systems, severe low-light environments can degrade OCR and object detection accuracy.

**Future Scope** includes expanding the object detection models to recognize specific cultural or regional items, and integrating more compact, wearable camera solutions that connect directly to the laptop.
