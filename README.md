# Smart Patio Project

## Overview
The Smart Patio project is designed to create an intelligent outdoor space that can be controlled and monitored remotely. It utilizes Wi-Fi and MQTT protocols to connect various devices, allowing users to manage lighting, alarms, and other features of their patio environment.

## Features
- Wi-Fi connectivity for remote access
- MQTT protocol for efficient message handling
- Control of outdoor devices such as lights and alarms
- Real-time status updates and notifications

## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/smartPatio.git
   cd smartPatio
   ```

2. **Install PlatformIO**
   Ensure you have PlatformIO installed in your development environment. You can install it as a plugin for Visual Studio Code or use the command line interface.

3. **Configure Wi-Fi and MQTT Settings**
   Open `src/main.cpp` and update the Wi-Fi SSID and password, as well as the MQTT broker settings to match your network configuration.

4. **Build the Project**
   Use PlatformIO to build the project:
   ```bash
   pio run
   ```

5. **Upload to Device**
   Connect your ESP32 or compatible device and upload the firmware:
   ```bash
   pio run --target upload
   ```

## Usage
Once the project is uploaded to your device, you can control the smart patio features through MQTT messages. Subscribe to the relevant topics to receive updates and send commands to control the devices.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.