import cv2
import os
import sys
import time
import platform
from datetime import datetime
import keyboard

# =============================
# conf
CONFIG = {
    "CAMERA_INDEX": 0,
    "SAVE_DIR": "./captures",
    "JPEG_QUALITY": 92,
    "BURST_INTERVAL_SEC": 0.5,
}

KEY_CAPTURE = "c"
KEY_BURST = "b"
KEY_QUIT = "k"
# =============================


def open_camera():
    system = platform.system()
    if system == "Linux":
        cap = cv2.VideoCapture(CONFIG["CAMERA_INDEX"], cv2.CAP_V4L2)
    else:
        cap = cv2.VideoCapture(CONFIG["CAMERA_INDEX"])

    if not cap.isOpened():
        print("[ERROR] Tidak bisa membuka kamera index", CONFIG["CAMERA_INDEX"])
        sys.exit(1)

    return cap


def save_frame(frame, prefix="capture"):
    os.makedirs(CONFIG["SAVE_DIR"], exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = os.path.join(CONFIG["SAVE_DIR"], f"{prefix}_{ts}.jpg")
    cv2.imwrite(filename, frame, [int(cv2.IMWRITE_JPEG_QUALITY), CONFIG["JPEG_QUALITY"]])
    print(f"TERSIMPAN DI {filename}")
    return filename


def draw_overlay(frame, status_text, burst_active):
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (0, 0, 0), -1)
    frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

    color = (0, 0, 255) if burst_active else (0, 255, 0)
    cv2.putText(frame, status_text, (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(
        frame,
        f"[{KEY_CAPTURE.upper()}] CAPTURE   [{KEY_BURST.upper()}] BURST   [{KEY_QUIT.upper()}] KELUAR",
        (10, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA
    )
    return frame


def main():
    cap = open_camera()

    window_name = "Kontrol Kamera Lokal - OpenCV"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    burst_active = False
    last_burst_time = 0.0
    status_text = "Live preview"

    print("=" * 60)
    print("Live preview dimulai.")
    print(f"  [{KEY_CAPTURE.upper()}] CAPTURE. Menyimpan 1 foto")
    print(f"  [{KEY_BURST.upper()}] BURST. Tahan untuk burst, lepas untuk berhenti")
    print(f"  [{KEY_QUIT.upper()}] KELUAR")
    print("=" * 60)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[ERROR] Gagal membaca frame dari kamera.")
                break

            burst_active = keyboard.is_pressed(KEY_BURST)

            if burst_active:
                now = time.time()
                if now - last_burst_time >= CONFIG["BURST_INTERVAL_SEC"]:
                    save_frame(frame, prefix="burst")
                    last_burst_time = now
                status_text = "BURST CAPTURE AKTIF..."
            else:
                status_text = "Live preview"

            display_frame = draw_overlay(frame, status_text, burst_active)
            cv2.imshow(window_name, display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord(KEY_CAPTURE):
                save_frame(frame, prefix="capture")
            elif key == ord(KEY_QUIT):
                print(" ")
                print("[INFO] Keluar.")
                break

            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(" ")
        print("[INFO] Program selesai.")
        print(" ")

if __name__ == "__main__":
    main()