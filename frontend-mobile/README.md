# 📱 CrisisSync AI - Mobile Native (Flutter)

This directory contains the complete native Dart/Flutter rewrite of the Civilian PWA, specifically engineered for mobile device deployments.

Because the local machine does not have the Flutter SDK installed, this folder contains the raw, essential codebase (`pubspec.yaml` and `lib/` directory) required to drop into a functioning Flutter environment.

## App Features
*   **Native GPS Trigger:** Uses the `geolocator` package to leverage the actual phone's GPS for the SOS beacon, preventing accurate location drops even if the web browser masks IP location.
*   **Live Background Polling:** The app pings the remote server every 3 seconds to fetch new hazard zones and the latest Gemini/OpenAI Civilian Adversary.
*   **Native Map Rendering:** Implements `flutter_map` instead of `react-leaflet`, massively increasing map render frame rate on low-end mobile hardware compared to running Leaflet inside a Chromium web view.

## How to Run It

1. **Install Flutter:** Ensure you have the Flutter SDK installed on your presentation device (Windows/Mac/Linux).
2. **Create a Scaffold:** Open your terminal and run `flutter create crisissync_mobile`.
3. **Copy The Code:** 
   * Replace the auto-generated `pubspec.yaml` with the `pubspec.yaml` found in this folder.
   * Replace the auto-generated `lib/` folder with the `lib/` folder found in this folder.
4. **Fetch Packages:** Run `flutter pub get` in the terminal to download the dependencies.
5. **Launch:** Run `flutter run` with an Android Emulator or iOS Simulator plugged in!

### Important Networking Note
In `lib/main.dart`, the `apiBase` variable is currently set to `http://10.0.2.2:8000/api`. This is the special IP address an Android Emulator uses to connect to the computer's `localhost`. 
*   If running on a physical phone, you must change this IP to your computer's actual local WiFi IP (e.g., `http://192.168.1.5:8000/api`).
