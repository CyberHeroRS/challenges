#!/usr/bin/env python3
"""
Morse Code 67 Cat Encoder

Uses the 67 meme cat gestures to encode FLAG as Morse code:
- Left hand gesture = DASH (long signal)
- Right hand gesture = DOT (short signal)
"""

import os
import subprocess
import tempfile
import shutil
from PIL import Image

MORSE_CODE = {
    'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
    'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
    'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
    'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
    'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
    'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
    'Y': '-.--',  'Z': '--..',
    '0': '-----', '1': '.----', '2': '..---', '3': '...--',
    '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.',
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FPS = 12


def text_to_morse(text):
    result = []
    for char in text.upper():
        if char == ' ':
            result.append((' ', ' '))
        elif char in MORSE_CODE:
            result.append((MORSE_CODE[char], char))
    return result


def load_gesture_frames(gif_path):
    gif = Image.open(gif_path)
    frames = []
    try:
        while True:
            frames.append(gif.copy().convert('RGB'))
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    return frames


def generate_morse_video(text, output_path, audio_path=None):
    left_gif_path = os.path.join(SCRIPT_DIR, 'gesture_LEFT.gif')
    right_gif_path = os.path.join(SCRIPT_DIR, 'gesture_RIGHT.gif')
    
    print("Loading gestures...")
    left_frames = load_gesture_frames(left_gif_path)
    right_frames = load_gesture_frames(right_gif_path)
    neutral_frame = left_frames[0]
    
    print(f"  Left gesture (DASH): {len(left_frames)} frames")
    print(f"  Right gesture (DOT): {len(right_frames)} frames")
    
    morse_data = text_to_morse(text)
    print(f"\nEncoding: {'*' * len(text)}")  # Don't print actual flag
    morse_str = ' '.join(m for m, c in morse_data)
    print(f"Morse length: {len(morse_str)} symbols")
    
    output_frames = []
    
    for _ in range(5):
        output_frames.append(neutral_frame)
    
    for morse, char in morse_data:
        if morse == ' ':
            for _ in range(15):
                output_frames.append(neutral_frame)
            continue
        
        for symbol in morse:
            if symbol == '-':
                for frame in left_frames:
                    output_frames.append(frame)
            elif symbol == '.':
                for frame in right_frames:
                    output_frames.append(frame)
            
            for _ in range(3):
                output_frames.append(neutral_frame)
        
        for _ in range(8):
            output_frames.append(neutral_frame)
    
    for _ in range(10):
        output_frames.append(neutral_frame)
    
    print(f"\nTotal frames: {len(output_frames)}")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        print("Saving frames...")
        for i, frame in enumerate(output_frames):
            frame.save(os.path.join(temp_dir, f'frame_{i:05d}.png'))
        
        duration = len(output_frames) / FPS
        print(f"Video duration: {duration:.2f}s @ {FPS} fps")
        
        if audio_path and os.path.exists(audio_path):
            print(f"Adding audio (looped)")
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(FPS),
                '-i', os.path.join(temp_dir, 'frame_%05d.png'),
                '-stream_loop', '-1',
                '-i', audio_path,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-c:a', 'aac',
                '-shortest',
                '-movflags', '+faststart',
                output_path
            ]
        else:
            print("No audio file found, creating silent video")
            cmd = [
                'ffmpeg', '-y',
                '-framerate', str(FPS),
                '-i', os.path.join(temp_dir, 'frame_%05d.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                output_path
            ]
        
        print("Running ffmpeg...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr}")
            return None
        
        print(f"Done! Output: {output_path}")
        return output_path
        
    finally:
        shutil.rmtree(temp_dir)


def main():
    flag = os.environ.get('FLAG', 'SCC{fake_flag}')
    # Prune to alphanumeric only and uppercase
    flag = ''.join(c for c in flag.upper() if c.isalnum())
    
    audio_file = os.path.join(SCRIPT_DIR, 'bosnov-67.wav')
    output_file = '/app/static/67.mp4'
    
    os.makedirs('/app/static', exist_ok=True)
    
    print("=" * 55)
    print("  67 Cat Morse Code Encoder")
    print("=" * 55)
    print()
    
    generate_morse_video(flag, output_file, audio_file)


if __name__ == '__main__':
    main()
