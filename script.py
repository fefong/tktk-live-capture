import pyautogui
import keyboard
import pyperclip
import re
import time
import os
from dotenv import load_dotenv

# =========================
# Global Config
# =========================

pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

# =========================
# Load Environment Variables
# =========================

load_dotenv()

MAX_SCROLLS = int(os.getenv("MAX_SCROLLS"))
OUTPUT_FILE = os.getenv("OUTPUT_FILE")
BLACKLIST_FILE = os.getenv("BLACKLIST_FILE")
SCROLL_DELAY = float(os.getenv("SCROLL_DELAY"))
COPY_DELAY = float(os.getenv("COPY_DELAY"))
RELOAD_WAIT = int(os.getenv("RELOAD_WAIT"))

# =========================

def extract_username(url):
    pattern = r"@([^/]+)/live"
    match = re.search(pattern, url)
    return match.group(1) if match else None

# =========================

def load_file_to_set(filename):
    if not os.path.exists(filename):
        open(filename, "w").close()
        return set()

    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# =========================

def get_current_url():
    pyautogui.hotkey("ctrl", "l")
    time.sleep(COPY_DELAY)

    pyperclip.copy("")
    pyautogui.hotkey("ctrl", "c")

    url = ""
    for _ in range(20):
        url = pyperclip.paste()
        if url.startswith("http"):
            break
        time.sleep(0.01)

    pyautogui.press("esc")
    time.sleep(0.03)
    pyautogui.press("esc")
    time.sleep(0.03)

    return url.strip()

# =========================

def reload_page():
    print("\nDetected repeated failure. Reloading page...\n")

    pyautogui.hotkey("ctrl", "l")
    time.sleep(0.1)
    pyautogui.press("enter")

    print(f"Waiting {RELOAD_WAIT} seconds for reload...")
    time.sleep(RELOAD_WAIT)

# =========================

def scroll_and_capture():
    print(f"\nStarting automation ({MAX_SCROLLS} scrolls)...")
    print("Press F8 at any time to stop.\n")

    users_set = load_file_to_set(OUTPUT_FILE)
    blacklist_set = load_file_to_set(BLACKLIST_FILE)

    last_username = None
    consecutive_skips = 0

    for i in range(MAX_SCROLLS):

        # 🔴 Force Stop (F8)
        if keyboard.is_pressed("f8"):
            print("\nForce stop detected (F8). Exiting safely.")
            return

        url = get_current_url()
        username = extract_username(url)

        if username:
            if username in blacklist_set:
                print(f"[{i+1}] Ignored (blacklisted): {username}")
                consecutive_skips += 1

            elif username in users_set:
                print(f"[{i+1}] Ignored (already saved): {username}")
                consecutive_skips += 1

            elif username != last_username:
                print(f"[{i+1}] Saved:", username)
                with open(OUTPUT_FILE, "a", encoding="utf-8") as file:
                    file.write(username + "\n")

                users_set.add(username)
                last_username = username
                consecutive_skips = 0
            else:
                print(f"[{i+1}] Skipped (duplicate in cycle)")
                consecutive_skips += 1
        else:
            print(f"[{i+1}] Skipped (invalid URL)")
            consecutive_skips += 1

        # Auto-recovery
        if consecutive_skips >= 2:
            reload_page()
            consecutive_skips = 0
            last_username = None
            continue

        pyautogui.press("down")
        time.sleep(SCROLL_DELAY)

    print("\nProcess finished successfully.")

# =========================

def main():
    print("\nOpen your browser already on a live page.")
    print("Example: https://www.tiktok.com/@username/live")
    print("\nFocus the browser window.")
    print("Press F7 to start automation.")

    keyboard.wait("f7")

    scroll_and_capture()

# =========================

if __name__ == "__main__":
    main()