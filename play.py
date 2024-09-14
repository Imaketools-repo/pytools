import cv2
import os
import sys
import numpy as np
import shutil
from yt_dlp import YoutubeDL
from colorama import init

# Initialize Colorama
init()

# ASCII characters for conversion (in order of increasing "intensity")
ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

def get_terminal_size():
    """Get the current size of the terminal."""
    try:
        size = shutil.get_terminal_size((80, 20))  # Default size if detection fails
        return size.columns, size.lines
    except:
        return 80, 20

def image_to_ascii_with_color(image, width):
    """Convert an image frame to ASCII with color."""
    height, original_width, _ = image.shape
    aspect_ratio = height / original_width
    new_height = int(width * aspect_ratio * 0.55)  # Adjust height for ASCII aspect ratio
    resized_image = cv2.resize(image, (width, new_height))
    
    # Convert to grayscale and normalize
    grayscale_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    
    # Check for min and max values to avoid division by zero
    min_val = grayscale_image.min()
    max_val = grayscale_image.max()
    if max_val == min_val:
        max_val += 1  # Prevent division by zero
    
    normalized_image = (grayscale_image - min_val) / (max_val - min_val) * 255
    
    # Ensure no NaN values are present
    normalized_image = np.nan_to_num(normalized_image, nan=0, posinf=255, neginf=0)
    
    # Build ASCII string frame
    ascii_str = ''
    for i, row in enumerate(normalized_image):
        for j, pixel in enumerate(row):
            # Pick the ASCII character based on brightness
            ascii_char = ASCII_CHARS[int(pixel / 255 * (len(ASCII_CHARS) - 1))]
            # Get color information from the original image
            b, g, r = resized_image[i, j]
            # Apply ANSI color codes for RGB color
            ascii_str += f"\033[38;2;{r};{g};{b}m{ascii_char}\033[0m"
        ascii_str += '\n'
    
    return ascii_str

def play_video_as_ascii_with_color(video_path):
    """Play video as ASCII in the terminal with color."""
    # Get terminal size
    term_width, term_height = get_terminal_size()
    
    # Set a smaller width for better performance
    frame_width = min(term_width, 80)  # Adjust this value for desired performance
    
    # Open the video using OpenCV
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("\033[1;31mError: Unable to open video.\033[0m")
        return
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize frame to fit terminal width
            ascii_frame = image_to_ascii_with_color(frame, width=frame_width)

            # Clear the terminal and print the ASCII frame
            os.system('cls' if os.name == 'nt' else 'clear')
            print(ascii_frame)
            
            # Wait for a short time before showing the next frame (adjust delay to control frame rate)
            cv2.waitKey(10)  # Adjust delay to control frame rate (~100 FPS)
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()

def download_youtube_video(url):
    """Download YouTube video using yt-dlp."""
    ydl_opts = {
        'format': 'mp4/bestvideo',
        'outtmpl': 'video.mp4',  # Downloaded video will be saved as 'video.mp4'
        'quiet': True
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print("\033[1;32mDownloading video...\033[0m")
            ydl.download([url])
            return 'video.mp4'
    except Exception as e:
        print(f"\033[1;31mError downloading video: {e}\033[0m")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\033[1;31mUsage: python play_youtube.py <YouTube URL>\033[0m")
        sys.exit(1)

    video_url = sys.argv[1]
    
    # Step 1: Download the YouTube video
    video_path = download_youtube_video(video_url)
    
    if video_path:
        # Step 2: Play the video as ASCII in the terminal
        play_video_as_ascii_with_color(video_path)

        # Step 3: Clean up by removing the downloaded video
        os.remove(video_path)
