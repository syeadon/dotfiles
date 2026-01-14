#!/usr/bin/env python3
"""
Elgato Key Light Controller for Waybar
Displays current status and opens control interface on click
"""

import json
import sys
import subprocess
import requests
from typing import Optional, Dict, Any

# Configuration
KEY_LIGHT_IP = "192.168.4.42"  # Change to your Key Light IP
KEY_LIGHT_PORT = 9123


class ElgatoKeyLight:
    def __init__(self, ip: str, port: int = 9123):
        self.base_url = f"http://{ip}:{port}/elgato"

    def get_status(self) -> Optional[Dict[str, Any]]:
        """Get current light status"""
        try:
            response = requests.get(f"{self.base_url}/lights", timeout=2)
            response.raise_for_status()
            data = response.json()
            #print(f"DEBUG: get_status: {data}")
            if data.get("lights") and len(data["lights"]) > 0:
                return data["lights"][0]
            return None
        except Exception as e:
            return None

    def set_light(
        self,
        on: Optional[bool] = None,
        brightness: Optional[int] = None,
        temperature: Optional[int] = None,
    ) -> bool:
        """Set light parameters"""
        try:
            current = self.get_status()
            if not current:
                return False

            payload = {"lights": [{"on": current["on"]}]}

            if on is not None:
                payload["lights"][0]["on"] = 1 if on else 0
            if brightness is not None:
                payload["lights"][0]["brightness"] = max(0, min(100, brightness))
            if temperature is not None:
                payload["lights"][0]["temperature"] = max(143, min(344, temperature))

            print(f"DEBUG: set_lights: {json.dumps(payload)}")

            response = requests.put(f"{self.base_url}/lights", json=payload, timeout=2)
            response.raise_for_status()
            return True
        except Exception:
            return False


def get_waybar_output(light: ElgatoKeyLight) -> str:
    """Generate waybar JSON output"""
    status = light.get_status()

    if not status:
        output = {"text": "󰛨", "tooltip": "Key Light: Offline", "class": "offline"}
    else:
        is_on = status.get("on", 0) == 1
        brightness = status.get("brightness", 0)
        temperature = status.get("temperature", 200)

        # Convert temperature (143-344) to Kelvin approximation (2900-7000)
        kelvin = int(((344 - temperature) / (344 - 143)) * (7000 - 2900) + 2900)

        icon = "󰛨" if is_on else "󰹐"

        output = {
            "text": icon,
            "tooltip": f"Key Light: {'ON' if is_on else 'OFF'}\nBrightness: {brightness}%\nTemperature: {kelvin}K",
            "class": "on" if is_on else "off",
        }

    return json.dumps(output)


def show_control_interface(light: ElgatoKeyLight):
    """Show walker control interface with yad sliders"""
    status = light.get_status()
    if not status:
        subprocess.run(["notify-send", "Key Light", "Cannot connect to light"])
        return

    is_on = status.get("on", 0) == 1
    brightness = status.get("brightness", 50)
    temperature = status.get("temperature", 200)
    # Convert Elgato temperature (143=cool/7000K, 344=warm/2900K) to Kelvin
    kelvin = int(7000 - ((temperature - 143) / (344 - 143)) * (7000 - 2900))

    print(f"DEBUG: show_control_interface - Current brightness: {brightness}")
    print(f"DEBUG: show_control_interface - Current temperature: {kelvin}K")
    print(f"DEBUG: show_control_interface - Current temperature: {temperature}")

    # Create menu options
    options = [
        f"{'Turn OFF' if is_on else 'Turn ON'}",
        "Preset: Dim & Warm (20%, 3200K)",
        "Preset: Medium & Neutral (50%, 4500K)",
        "Preset: Bright & Cool (100%, 7000K)",
        "Adjust Brightness & Temperature",
    ]

    menu = "\n".join(options)

    # Use walker for main menu
    result = subprocess.run(
        ["walker", "--dmenu"], input=menu, text=True, capture_output=True
    )

    if result.returncode != 0:
        return

    choice = result.stdout.strip()

    # Handle choice
    if "Turn OFF" in choice:
        light.set_light(on=False)
    elif "Turn ON" in choice:
        light.set_light(on=True)
    elif "Adjust Brightness & Temperature" in choice:
        show_yad_sliders(light, brightness, kelvin)
    elif "Bright & Cool" in choice:
        light.set_light(on=True, brightness=100, temperature=143)
    elif "Medium & Neutral" in choice:
        light.set_light(on=True, brightness=50, temperature=230)
    elif "Dim & Warm" in choice:
        light.set_light(on=True, brightness=20, temperature=300)


def show_yad_sliders(
    light: ElgatoKeyLight, current_brightness: int, current_kelvin: int
):
    """Show yad dialog with sliders for brightness and temperature"""
    try:
        # Convert current Kelvin (2900-7000) to slider position (0-100)
        temp_slider_pos = int(((current_kelvin - 2900) / (7000 - 2900)) * 100)

        result = subprocess.run(
            [
                "yad",
                "--form",
                "--title=Key Light Control",
                "--width=400",
                "--center",
                "--on-top",
                "--skip-taskbar",
                "--undecorated",
                "--borders=20",
                "--text=Adjust brightness and color temperature",
                "--field=Brightness (%):SCL",
                "--field=Temperature (%):SCL",
                "--button=Apply:0",
                "--button=Cancel:1",
                f"{current_brightness}!0..100!1!0",
                f"{temp_slider_pos}!0..100!1!0",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Parse output: "brightness|temperature|"
            values = result.stdout.strip().split("|")
            if len(values) >= 2:
                # Yad sliders return 0-100 regardless of the range we set
                brightness_slider = float(values[0])  # 0-100
                temp_slider = float(values[1])  # 0-100

                # Convert brightness slider (0-100) to actual brightness
                new_brightness = int(brightness_slider)

                # Convert temperature slider (0-100) to Kelvin (2900-7000)
                new_kelvin = int(2900 + (temp_slider / 100) * (7000 - 2900))

                # Convert Kelvin to Elgato range (143-344)
                # Elgato: 143=cool/7000K, 344=warm/2900K (inverted)
                temp_value = int(
                    143 + ((7000 - new_kelvin) / (7000 - 2900)) * (344 - 143)
                )
                temp_value = max(143, min(344, temp_value))  # Clamp to valid range

                print(f"DEBUG: show_yad_sliders - Set brightness to: {new_brightness}")
                print(f"DEBUG: show_yad_sliders - Set temperature slider position: {temp_slider_pos}")
                print(f"DEBUG: show_yad_sliders - Set temperature to: {new_kelvin}K")
                print(f"DEBUG: show_yad_sliders - Set temperature to: {temp_value}")

                # Turn on the light and set values
                light.set_light(
                    on=True, brightness=new_brightness, temperature=temp_value
                )
                subprocess.run(
                    [
                        "notify-send",
                        "Key Light",
                        f"Set to {new_brightness}% brightness, {new_kelvin}K",
                    ]
                )
    except Exception as e:
        subprocess.run(
            ["notify-send", "Key Light Error", f"Failed to adjust: {str(e)}"]
        )


def main():
    light = ElgatoKeyLight(KEY_LIGHT_IP, KEY_LIGHT_PORT)

    if len(sys.argv) > 1 and sys.argv[1] == "control":
        show_control_interface(light)
    else:
        print(get_waybar_output(light))


if __name__ == "__main__":
    main()
