#!/usr/bin/env python3

import subprocess
import os
import sys

# --- Configuration ---
# IMPORTANT: Replace with your Keylight's IP address and a memorable name.
# You can find the IP address in your router's client list or using network scanning tools.
LIGHT_IP = "192.168.4.42"  # <--- CHANGE THIS
LIGHT_NAME = "Keylight"

# Preset configurations: (Brightness %, Temperature K)
# Temperature range for Keylight is 2900K to 7000K.
PRESETS = {
    "Cozy": (20, 2900),
    "Standard": (50, 4700),
    "Daylight": (80, 7000),
}

# --- YAD Dialog ---
def show_yad_dialog():
    """
    Constructs and displays a YAD dialog with presets and sliders.
    Returns the user's selection from YAD.
    """
    # Get current light status for slider defaults
    try:
        # The user mentioned installing with pipx, so the command should be in the PATH
        info_cmd = ["keylight", "--uri", f"http://{LIGHT_IP}:9123", "info"]
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        # Expected output format is like: "Brightness: 50% | Temperature: 4500K | On: True"
        parts = result.stdout.strip().split(" | ")
        current_brightness = int(parts[0].split(": ")[1].replace("%", ""))
        current_temp_str = parts[1].split(": ")[1].replace("K", "")
        # Handle potential float temperature from some versions
        current_temp = int(float(current_temp_str))
    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
        print(f"Error getting current light state: {e}")
        # Fallback to default values if info command fails
        current_brightness = 50
        current_temp = 4500

    yad_cmd = [
        "yad",
        "--title", f"Control {LIGHT_NAME}",
        "--form",
        "--width=400",
        "--text", "Select a preset or adjust manually:",
        "--field", "<b>Presets</b>:LBL",
        "",  # Empty label for spacing
    ]

    # Add preset buttons
    for preset_name in PRESETS:
        yad_cmd.extend(["--field", f"{preset_name}:BTN", f"bash -c 'echo {preset_name}'"])

    # Add separator and sliders
    yad_cmd.extend([
        "--field", ":SEP",
        "--field", "<b>Brightness (%)</b>:SCALE",
        f"{current_brightness},0,100,1",
        "--field", "<b>Temperature (K)</b>:SCALE",
        f"{current_temp},2900,7000,50",
    ])

    try:
        proc = subprocess.run(yad_cmd, capture_output=True, text=True, check=True)
        return proc.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"YAD dialog failed: {e}")
        return None
    except FileNotFoundError:
        # Show a notification if YAD is not installed.
        subprocess.run([
            "notify-send",
            "YAD Not Found",
            "Please install 'yad' to use the Keylight control.",
            "--icon=dialog-error"
        ])
        return None


# --- Keylight Control ---
def is_light_on():
    """
    Checks if the light is currently on.
    Returns True if on, False otherwise.
    """
    try:
        info_cmd = ["keylight", "--uri", f"http://{LIGHT_IP}:9123", "info"]
        result = subprocess.run(info_cmd, capture_output=True, text=True, check=True)
        return "On: True" in result.stdout
    except (subprocess.CalledProcessError, IndexError, ValueError) as e:
        print(f"Error getting current light state: {e}")
        return False

def toggle_light():
    """
    Toggles the light on or off.
    """
    if is_light_on():
        subprocess.run(["keylight", "--uri", f"http://{LIGHT_IP}:9123", "off"], check=True, capture_output=True)
        print(f"Turned {LIGHT_NAME} off.")
    else:
        subprocess.run(["keylight", "--uri", f"http://{LIGHT_IP}:9123", "on"], check=True, capture_output=True)
        print(f"Turned {LIGHT_NAME} on.")

def get_status():
    """
    Prints Waybar-compatible JSON output.
    """
    import json

    if is_light_on():
        icon = "󰌵"  # Icon for on state
        tooltip = f"{LIGHT_NAME} is On"
    else:
        icon = "󰌶"  # Icon for off state
        tooltip = f"{LIGHT_NAME} is Off"

    print(json.dumps({
        "text": icon,
        "tooltip": tooltip,
    }))

def apply_settings(brightness, temperature):
    """
    Applies brightness and temperature settings using keylight-cli.
    """
    try:
        base_cmd = ["keylight", "--uri", f"http://{LIGHT_IP}:9123"]
        # Ensure light is on before setting values
        subprocess.run(base_cmd + ["on"], check=True, capture_output=True)
        # Apply settings
        subprocess.run(base_cmd + ["--brightness", str(brightness)], check=True, capture_output=True)
        subprocess.run(base_cmd + ["--temperature", str(temperature)], check=True, capture_output=True)
        print(f"Set {LIGHT_NAME} to {brightness}% brightness and {temperature}K.")
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else "An unknown error occurred."
        subprocess.run([
            "notify-send",
            "Keylight Control Error",
            f"Failed to control light. Is the IP ({LIGHT_IP}) correct?\nError: {error_message}",
            "--icon=dialog-warning"
        ])
        print(f"Error controlling Keylight: {e}")


# --- Main Logic ---
def main():
    """
    Main function to run the script.
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == "toggle":
            toggle_light()
        elif sys.argv[1] == "status":
            get_status()
    else:
        yad_output = show_yad_dialog()

        if not yad_output:
            return

        output_parts = yad_output.split("|")

        # YAD returns field values separated by '|'.
        # Preset buttons output their name to stdout, which YAD captures in the first field.
        # The button bash command's output goes into the first form field result.
        preset_selection = output_parts[0]
        brightness_val = output_parts[-2] # Second to last is brightness
        temp_val = output_parts[-1]       # Last is temperature

        if preset_selection in PRESETS:
            # User clicked a preset button
            brightness, temperature = PRESETS[preset_selection]
            apply_settings(brightness, temperature)
        elif brightness_val and temp_val:
            # User used sliders and clicked OK
            try:
                brightness = int(float(brightness_val))
                temperature = int(float(temp_val))
                apply_settings(brightness, temperature)
            except ValueError:
                print("Invalid slider values received from YAD.")


if __name__ == "__main__":
    main()
