# 🌈 ESP32 Mood Lamp with Servo & Touch Control

A **smart mood lamp** built using an **ESP32**, **NeoPixel RGB LEDs**, and a **servo motor**, controllable via **touch input** or a **web interface** (including a color picker).  
The ESP32 hosts its own Wi-Fi hotspot and webpage — no internet connection required!

---

## ✨ Features

- 🕹️ **Touch Sensor Control**
  - Short touch → Toggles the servo and light.
  - Long touch → Turns off the light.

- 💡 **Smooth Servo Motion**
  - Servo moves smoothly between open and closed positions.

- 🌈 **RGB Mood Light**
  - Fully controllable via a web-based **color picker**.
  - Option to toggle ON/OFF.

- 🌐 **Built-in Wi-Fi Access Point**
  - Connect your phone directly to `ESP32_HaazMoodlamp`.
  - No external Wi-Fi needed.
  - Fake DNS server auto-redirects to the control page (`http://192.168.4.1`).

---

## ⚙️ Hardware Setup

| Component | Pin | Description |
|------------|-----|-------------|
| Servo | GPIO 0 | Controls servo position |
| Touch Sensor | GPIO 1 | Detects short or long press |
| NeoPixel LED Strip | GPIO 21 | 32 RGB LEDs |
| ESP32 | — | Runs Wi-Fi AP, DNS & Web Server |

---

## 🧠 How It Works

1. **ESP32 starts a Wi-Fi hotspot** named `ESP32_HaazMoodlamp` (password: `12345678`).
2. A **fake DNS server** redirects all connections to `192.168.4.1`.
3. When you open any site, the **web interface** appears automatically.
4. You can:
   - Toggle light ON/OFF.
   - Move the servo.
   - Pick any RGB color from the color wheel.

---

## 🌐 Web Interface

- Access the lamp by connecting to:
  ```
  Wi-Fi: ESP32_HaazMoodlamp
  Password: 12345678
  URL: http://192.168.4.1
  ```

- Control options:
  - **Toggle (Servo + Light)** – turns on the light and moves the servo.
  - **Turn Light OFF** – shuts down the light.
  - **Toggle Servo Only** – moves the servo without affecting the light.
  - **Color Picker** – change NeoPixel color dynamically.

---

## 🧩 Dependencies

Make sure your **MicroPython firmware** supports:
- `_thread`
- `neopixel`
- `network`
- `machine`
- `socket`
- `time`
- `struct`

Flash the MicroPython firmware onto your ESP32 using **Thonny** or **esptool.py**.

---

## 🚀 Installation Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/ESP32-MoodLamp.git
   ```
2. Open `main.py` in **Thonny**.
3. Connect your ESP32 board.
4. Click **Run** (▶️) or **Upload to /flash**.
5. Connect your phone to the Wi-Fi `ESP32_HaazMoodlamp`.
6. Open `http://192.168.4.1` to control your lamp.

---

## 🎨 Demo

| Feature | Description |
|----------|-------------|
| 💡 Color Control | Change colors instantly from the web UI |
| 🔄 Smooth Servo | Gradual motion for realistic movement |
| 🧠 Touch Input | Dual-mode touch for toggling light/servo |

*(You can add photos or GIFs here of your working setup.)*

---

## 🛠️ Future Improvements

- Add brightness control slider  
- Store last color in non-volatile memory (NVS)  
- Add animations (rainbow, breathing, etc.)  
- Integrate with Telegram for remote control  

---

## 📜 License

This project is licensed under the **MIT License** — feel free to use and modify it.
