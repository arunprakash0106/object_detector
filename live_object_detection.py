import cv2
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO

import datetime
import threading
import requests  # Sends data to PHP

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Classes of interest (COCO dataset)
TARGET_CLASSES = {39: 'bottle', 73: 'notebook'}

# API URL for PHP server
API_URL = "http://localhost/object_detector/save_data.php"

class LiveObjectDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Live Object Detector")

        self.start_btn = tk.Button(root, text="Start Detection", command=self.start_detection)
        self.start_btn.pack(pady=10)

        self.stop_btn = tk.Button(root, text="Stop Detection", command=self.stop_detection, state=tk.DISABLED)
        self.stop_btn.pack(pady=10)

        self.video_label = tk.Label(root)
        self.video_label.pack()

        self.event_log = []  # Stores detected objects
        self.running = False
        self.cap = None
        self.thread = None
        self.total_counts = {'bottle': 0, 'notebook': 0}
        self.previous_frame_objects = {}

    def start_detection(self):
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.thread = threading.Thread(target=self.detect_objects)
        self.thread.start()

    def stop_detection(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.export_event_log()

    def detect_objects(self):
        self.cap = cv2.VideoCapture(0)
        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            results = model(frame)
            detected_now = {}

            for obj in results[0].boxes.data:
                class_id = int(obj[5])
                if class_id in TARGET_CLASSES:
                    x1, y1, x2, y2 = map(int, obj[:4])
                    label = TARGET_CLASSES[class_id]
                    detected_now[label] = detected_now.get(label, 0) + 1
                    color = (0, 255, 0) if class_id == 39 else (255, 0, 0)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            detected_at_time = {}
            for obj_name in TARGET_CLASSES.values():
                if obj_name not in self.previous_frame_objects:
                    self.previous_frame_objects[obj_name] = 0
                if detected_now.get(obj_name, 0) > self.previous_frame_objects[obj_name]:
                    additional_count = detected_now[obj_name] - self.previous_frame_objects[obj_name]
                    self.total_counts[obj_name] += additional_count
                    detected_at_time[obj_name] = additional_count

            if detected_at_time:
                event_description = ", ".join([f"Total {obj}(s): {self.total_counts[obj]}" for obj in detected_at_time])
                event_data = {
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'event': event_description,
                    'object': ", ".join(detected_at_time.keys()),
                    'detected_count': ", ".join(map(str, detected_at_time.values())),
                    'total_bottle': self.total_counts['bottle'],
                    'total_notebook': self.total_counts['notebook']
                }
                self.send_data_to_server(event_data)
                self.event_log.append(event_data)

            self.previous_frame_objects = detected_now.copy()

            frame_resized = cv2.resize(frame, (640, 360))
            img = Image.fromarray(cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
            self.root.update()
        self.cap.release()

    def send_data_to_server(self, event_data):
        try:
            response = requests.post(API_URL, data=event_data)
            if response.status_code == 200:
                print("Data sent successfully")
            else:
                print("Failed to send data", response.text)
        except Exception as e:
            print(f"Error sending data: {e}")

    def export_event_log(self):
        if self.event_log:
            df_events = pd.DataFrame(self.event_log)
            output_file = filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[["CSV files", "*.csv"]],
                                                       title="Save Event Log")
            if output_file:
                df_events.to_csv(output_file, index=False)
                messagebox.showinfo("Success", f"Event log saved to {output_file}")
            else:
                messagebox.showwarning("Cancelled", "Event log export was cancelled.")
        else:
            messagebox.showinfo("No Events", "No events were recorded during detection.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LiveObjectDetector(root)
    root.mainloop()
