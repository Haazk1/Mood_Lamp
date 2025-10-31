# 🌈 ESP32 Mood Lamp + Servo Control (MicroPython)

This project turns your ESP32 into a **Wi-Fi hotspot** that hosts a web-based control panel for:
- Changing RGB NeoPixel colors using a **color wheel** 🎨  
- Controlling a **servo motor** smoothly between open and close positions 🔄  
- Toggling light ON/OFF 💡  
- Long-press touch input to turn off light 🔘  

---

## 🧠 Features

- 🔥 **Captive portal-like behavior** — automatically resolves DNS queries to `192.168.4.1`
- 🌐 **Built-in Wi-Fi Access Point**
  - SSID: `ESP32_HaazMoodlamp`
  - Password: `12345678`
- 🎨 **Web Interface**
  - Live RGB color picker
  - Buttons for servo and light control
- 🤖 **Smooth servo motion**
- 🖐 **Touch button control**
  - Short press → Toggle servo + light ON
  - Long press (>1.5s) → Turn off light
- 💡 **NeoPixel support** for up to 32 LEDs

---

## ⚙️ Hardware Connections

| Component        | Pin (ESP32) | Description         |
|------------------|-------------|---------------------|
| Servo Motor      | GPIO 0      | PWM control signal  |
| Touch Sensor     | GPIO 1      | Input for touch     |
| NeoPixel Strip   | GPIO 21     | RGB data pin        |
| Power Supply     | 5V + GND    | Shared with all devices |

> ⚠️ Make sure to use an external 5V power source for servo + NeoPixels to avoid brownouts.

---

## 📲 How to Use

1. Flash the provided MicroPython script to your **ESP32** using **Thonny** or **ampy**.  
2. Once flashed, reboot the ESP32.
3. Connect your phone or laptop to the Wi-Fi network:

   ```
   SSID: ESP32_HaazMoodlamp
   Password: 12345678
   ```

4. Open your browser and go to:
   ```
   http://192.168.4.1
   ```

5. Use the web controls to:
   - Toggle servo movement
   - Turn light ON/OFF
   - Adjust the LED color with the color wheel

---

## 🌈 Web Interface Preview

The web interface includes:
- Buttons:
  - “Toggle (Servo + Light ON)”
  - “Turn Light OFF”
  - “Toggle Servo Only”
- RGB Color Wheel:
  - Instantly updates the NeoPixel color.

---

## 🧩 File Overview

| File | Description |
|------|--------------|
| `main.py` | Main MicroPython program for ESP32 (includes Wi-Fi, servo, LED, and web server logic) |
| `README.md` | This documentation file |

---

## 🧰 Dependencies

- MicroPython (latest build for ESP32)
- Libraries:
  - `machine`
  - `neopixel`
  - `_thread`
  - `network`
  - `socket`
  - `time`
  - `struct`

---

## 🚀 Future Improvements

- Add brightness control slider
- Add presets for color moods
- Enable OTA updates for easier firmware upgrades

---

## 🧑‍💻 Author

**Haaziq Raif**  
Created using ESP32 SuperMini C3 with MicroPython  
For educational and IoT experimentation 🌍

---

## 📝 License

MIT License — free for modification and use.
