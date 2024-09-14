import cv2
import numpy as np
from PIL import Image
import time
import os
import win32gui
import win32con
import ctypes
import io

# Constants
INTERVAL = 0.1  # 100 milliseconds for faster updates
TEMP_FILE = 'temp_photo.png'
PROCESSED_FILE = 'processed_photo.png'

def get_screen_resolution():
    # Get screen resolution using ctypes
    user32 = ctypes.windll.user32
    screen_width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
    screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    return screen_width, screen_height

def capture_photo():
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Camera not found.")
            return None

        ret, frame = cap.read()
        cap.release()

        if ret:
            _, buffer = cv2.imencode('.png', cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            return io.BytesIO(buffer)
        else:
            print("Error: Failed to capture image.")
            return None
    except Exception as e:
        print(f"Exception in capture_photo: {e}")
        return None

def change_background(image_file_like):
    try:
        img = Image.open(image_file_like).convert("RGBA")
        screen_width, screen_height = get_screen_resolution()
        img = img.resize((screen_width, screen_height), Image.LANCZOS)

        new_bg = Image.new('RGBA', (screen_width, screen_height), (255, 255, 255, 255))
        new_img = Image.alpha_composite(new_bg, img)

        # Save to a bytes buffer
        buffer = io.BytesIO()
        new_img.save(buffer, format='PNG')
        buffer.seek(0)  # Go to the beginning of the buffer
        return buffer
    except Exception as e:
        print(f"Exception in change_background: {e}")
        return None

def set_wallpaper_with_win32gui(image_buffer):
    try:
        # Save the buffer to a temporary file
        with open(PROCESSED_FILE, 'wb') as f:
            f.write(image_buffer.read())
        
        # Convert image path to absolute path
        image_path = os.path.abspath(PROCESSED_FILE)
        # Use win32gui to set wallpaper
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, image_path, win32con.SPIF_UPDATEINIFILE | win32con.SPIF_SENDCHANGE)
        print("Wallpaper set successfully.")
    except Exception as e:
        print(f"Exception in set_wallpaper_with_win32gui: {e}")

def main():
    while True:
        photo_file_like = capture_photo()
        if photo_file_like:
            processed_image_buffer = change_background(photo_file_like)
            if processed_image_buffer:
                print("Processed image ready.")

                # Set the new image as the wallpaper using win32gui
                set_wallpaper_with_win32gui(processed_image_buffer)

        # Wait for the next capture
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
