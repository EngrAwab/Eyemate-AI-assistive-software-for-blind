import param
import requests
import User as U
import numpy as np
import time
from requests.exceptions import ConnectionError, Timeout, RequestException
from urllib3.exceptions import MaxRetryError
import base64
import requests
import cv2
import io
import cv2
import requests
import Default as df
import math 
import heapq
import serial
from cv2 import aruco
from ultralytics import YOLO

class utilss(param.Main_Param):
    def __init__(self):
        super().__init__()
        self.last = ""
        self.speaking = False
        self.engine=None
        self.coordinates=df.coordinates
        self.edges= df.edges
        self.marker_to_node = df.marker_to_node
        self.aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_5X5_1000)
        self.parameters = aruco.DetectorParameters()
        self.detector = aruco.ArucoDetector(self.aruco_dict,self.parameters)
        self.cam_frame= None
        self.in_proces= False
        self.exe_nav= False
        model = YOLO(df.path_model)
        FLOOR_CLASS_ID = 2
    def open_serial(port: str, baud: int, *, timeout: float = 1.0) -> serial.Serial:
        ser = serial.Serial(port, baud, timeout=timeout)
        time.sleep(2)                    # give MCU time to reboot if DTR toggled
        return ser

    def send_line(ser: serial.Serial, line: str, *, eol: str = "\n") -> None:
        ser.write((line + eol).encode("ascii"))
        ser.flush()
    def compute_path_points(mask: np.ndarray):
        kernel = np.ones((3, 3), np.uint8)
        m = cv2.erode(mask, kernel, iterations=4)
        m = cv2.dilate(m, kernel, iterations=4)
        num_labels, labels = cv2.connectedComponents(m)
        sizes = [np.sum(labels == i) for i in range(1, num_labels)]
        if not sizes:
            return []
        largest = np.argmax(sizes) + 1
        patch   = (labels == largest).astype(np.uint8)
        h, w    = patch.shape
        pts     = []
        prev_x  = w // 2
        for y in range(h):
            xs = np.where(patch[y] == 1)[0]
            if xs.size:
                splits   = np.split(xs, np.where(np.diff(xs) > 1)[0] + 1)
                segments = [(seg[0], seg[-1]) for seg in splits if seg.size]
                centers  = [int((s + e) / 2) for s, e in segments]
                idx      = int(np.argmin([abs(c - prev_x) for c in centers]))
                prev_x   = centers[idx]
                pts.append((prev_x, y))
        if len(pts) < 5:
            return []
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        window = 5
        sm_x   = np.convolve(xs, np.ones(window) / window, mode='valid')
        sm_y   = ys[len(ys) - len(sm_x):]
        return [(int(x), y) for x, y in zip(sm_x, sm_y)]

    def draw_gradient_path_on_image(img: np.ndarray, path: list):
        out = img.copy()
        for i in range(1, len(path)):
            p1, p2 = path[i - 1], path[i]
            intensity = int(255 * i / len(path))
            color     = (255 - intensity, intensity, 128)
            cv2.line(out, p1, p2, color, 2)
        return out
    def local (self ,opencv_img, url, prompt,  *, fmt=".png", timeout=30, session=None):
        """
        Send an already-loaded OpenCV image to a Qwen-VL Flask endpoint.

        Returns
        -------
        str
            • The model’s clean reply on success.  
            • The constant SERVER_DOWN_TOKEN if the request fails (timeout,
            connection error, non-JSON reply, etc.).  You can compare against
            this value outside the function to detect server problems.
        """
        # 1) Encode the OpenCV (BGR) image to bytes in memory
        ok, buf = cv2.imencode(fmt, opencv_img)
        if not ok:
            raise ValueError("Failed to encode image with OpenCV")

        img_bytes = buf.tobytes()
        files = {
            "image": (f"upload{fmt}",
                    io.BytesIO(img_bytes),
                    "image/png" if fmt == ".png" else "image/jpeg")
        }
        data  = {"prompt": prompt}

        sess = session or requests.Session()

        # try:
        resp = sess.post(url, files=files, data=data, timeout=timeout)
        resp.raise_for_status()
        payload = resp.json()                 # may raise ValueError if not JSON
        # except (requests.RequestException, ValueError):
        #     # Connection, timeout, HTTP error, or bad JSON → signal server problem
        #     return "<<SERVER_DOWN>>"

        raw = payload.get("description", "")
        if "\nassistant\n" in raw:
            return raw.split("\nassistant\n")[-1].strip()
        return raw.strip()

    def analyze_image(self, image, api_key, prompt , model):
        def encode_image(image):
            _, buffer = cv2.imencode('.jpg', image)
            return base64.b64encode(buffer).decode('utf-8')

        base64_image = encode_image(image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        print("Picture is passed to GPT")

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            assistant_response = response_data['choices'][0]['message']['content']
            return assistant_response
        else:
            return f"Error: {response.json()}"

    def phone_data(self,ip):
        data_ip = f"http://{ip}:8080/" 
        # print (data_ip)
        # while (True): 
        try:
            response = requests.get(data_ip)
            if response.status_code == 200:
                if self.last !=response.text:
                    self.last=response.text
                    self.data= response.text.lower()
                    # print(self.data)
                else :
                    self.data= ""
        except MaxRetryError as e:
            # Handle MaxRetryError, raised when the max retries have been exceeded
            print("Max retry attempts exceeded")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying, to avoid continuous errors

        except ConnectionError as e:
            # If a connection error occurs (e.g., machine actively refusing the connection)
            print("Remote off - Connection Error")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying

        except Timeout as e:
            # If a timeout occurs
            print("Request timed out")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying

        except RequestException as e:
            # Handle any other type of request exceptions
            print("An error occurred during the request")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying
    def get_teddy_data(self,ip):
        data_ip = f"http://{ip}" 
        # print (data_ip)
        # while (True): 
        try:
            response = requests.get(data_ip)
            if response.status_code == 200:
                if self.last !=response.text and response.text!="" :
                    self.last=response.text
                    self.data= response.text.lower()
                    print ("IN TEDDY")
                    print(self.data)
                    print ("OUT TEDYY")
                else :
                    self.data= ""
        except MaxRetryError as e:
            # Handle MaxRetryError, raised when the max retries have been exceeded
            print("Max retry attempts exceeded")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying, to avoid continuous errors

        except ConnectionError as e:
            # If a connection error occurs (e.g., machine actively refusing the connection)
            print("Remote off - Connection Error")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying

        except Timeout as e:
            # If a timeout occurs
            print("Request timed out")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying

        except RequestException as e:
            # Handle any other type of request exceptions
            print("An error occurred during the request")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying
    def get_teddy_data_old(self, ip):
        data_ip = f"http://{ip}" 
        # print (data_ip)
        # while (True): 
        try:
            response = requests.get(data_ip)
            if response.status_code == 200:
                # if self.last !=response.text:
                d= response.text.lower()
                if d== "":
                    self.data=self.last
                    # print ('khali')
                    
                else :
                    self.data=d
                    self.last=d
                    # print(self.data)
        # data_ip = f"http://{ip}" 
        # # print (data_ip)
        # # while (True): 
        # try:
        #     response = requests.get(data_ip)
        #     if response.status_code == 200:
        #         # if self.last !=response.text:
        #         self.last=response.text
        #         self.data= response.text.lower()
                    # print(self.data)
                
        except MaxRetryError as e:
            # Handle MaxRetryError, raised when the max retries have been exceeded
            print("Max retry attempts exceeded")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying, to avoid continuous errors

        except ConnectionError as e:
            # If a connection error occurs (e.g., machine actively refusing the connection)
            print("Remote off - Connection Error")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying

        except Timeout as e:
            # If a timeout occurs
            print("Request timed out")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying

        except RequestException as e:
            # Handle any other type of request exceptions
            print("An error occurred during the request")
            # print(f"Error details: {e}")
            time.sleep(5)  # Adding a delay before retrying
        
        
    def analyze_scene(self ,image, api_key, prompt , model):
        def encode_image(image):
            _, buffer = cv2.imencode('.jpg', image)
            return base64.b64encode(buffer).decode('utf-8')

        base64_image = encode_image(image)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that provides detailed and accessible scene descriptions for visually impaired users."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt  # e.g. "Describe the scene."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        print("Picture is passed to GPT For Scene")

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            assistant_response = response_data['choices'][0]['message']['content']
            return assistant_response
        else:
            return f"Error: {response.json()}"
    def stop(self):
        self.voi_text=[]
        if self.speaking:
            self.engine.stop()  
            self.speaking = False  
    def speech(self):
         # Max volume
        
        # self.engine = pyttsx3.init()
        # self.engine.setProperty('rate', 170)  # Words per minute
        # self.engine.setProperty('volume', 1.0) 
        while (True):
            # print (len(self.voi_text))   
            # voi_t= self.voi_text
            # voi_t=list(set(voi_t))
            # self.voi_text= voi_t
            if len(self.voi_text)>0:
                speech_text=self.voi_text[0].lower()
            else :
                speech_text=""  
            if speech_text!="":
                self.voi_text.pop(0)
                # print ("*******\n\n\n\n\n\n\n\n******")
                # print (speech_text)
                # print ("*******\n\n\n\n\n\n\n\n******")
                import pyttsx3
                self.engine= None
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 170)  # Words per minute
                self.engine.setProperty('volume', 1.0) 
                self.speaking = True
                self.engine.say(speech_text)
                self.engine.runAndWait()   
                self.speaking = False  
                # print ("Repat")
                speech_text=""
        print ("Speech Thread Ended")
        # speech_thread = threading.Thread(target=self.talk, args=(engine,))
        # speech_thread.start()
        # speech_thread = threading.Thread(target=self.stop)
        print ("Ended ")
    def speak(self, data):
        self.app(data)
    def euclidean(self , a, b):
        x1, y1 = self.coordinates[a]
        x2, y2 = self.coordinates[b]
        return math.hypot(x2 - x1, y2 - y1)

    # === A* Pathfinding ===
    def a_star(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {node: float('inf') for node in self.coordinates}
        g_score[start] = 0

        f_score = {node: float('inf') for node in self.coordinates}
        f_score[start] = self.euclidean(start, goal)

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for neighbor in self.edges.get(current, []):
                tentative_g = g_score[current] + self.euclidean(current, neighbor)
                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.euclidean(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None

    # === Relative Direction: Turn-based ===
    def get_relative_direction(self , prev_node, current_node, next_node):
        def angle(a, b):
            dx, dy = b[0] - a[0], b[1] - a[1]
            return math.atan2(dy, dx)

        angle1 = angle(self.coordinates[prev_node], self.coordinates[current_node])
        angle2 = angle(self.coordinates[current_node], self.coordinates[next_node])
        diff = (math.degrees(angle2 - angle1) + 360) % 360

        if diff < 45 or diff > 315:
            return "Go straight"
        elif diff < 135:
            return "Turn right"
        elif diff < 225:
            return "Turn back"
        else:
            return "Turn left"
        
    def detect_aruco_marker(self):
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW, (cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY)) # Open default camera (webcam)
    # if not cap.isOpened():
    #     print("⚠️ Error: Could not open camera.")
    #     return None

    # Set up ArUco dictionary and detector parameters
        

        print("📷 Detecting ArUco marker for CURRENT location...")

        
        while True:
            
            gray = cv2.cvtColor(self.cam_frame, cv2.COLOR_BGR2GRAY)

            # Detect markers
            corners, ids, _ = self.detector.detectMarkers(gray)
            
            if self.exe_nav ==True:
                1/0
            # Draw bounding box and display frame
            if ids is not None and len(ids) > 0:
                marker_id = ids[0][0]  # Take the first detected marker ID
                aruco.drawDetectedMarkers(self.cam_frame, corners, ids)
                # cv2.putText(self.cam_frame, f"ID: {marker_id}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                # cv2.imshow('ArUco Marker Detection', self.cam_frame)
                print(f"📷 Detected marker ID: {marker_id}")
                self.speak(f"Marker {marker_id} detected. Location is {self.marker_to_node.get(marker_id, 'unknown')}.")
                return marker_id  # Automatically return the detected marker ID
            
            # time.sleep(4)
            
    def nav(self , start_id , goal_id ):
        print (f'Your start node is {start_id} and end node is {goal_id}')
        start =self.marker_to_node[start_id]
        goal = self.marker_to_node[goal_id]

        full_path = [start]
        prev_node = None
        current = start
        while current != goal:
            # Calculate path
            path =self.a_star(current, goal)
            if not path or len(path) < 2:
                print("❌ No path found from your current location to the goal.")
                # user_input = input("📍 Type 'exit' to quit or press Enter to try again: ")
                
                continue

            next_node = path[1]

            # Provide navigation instructions
            if prev_node:
                direction = self.get_relative_direction(prev_node, current, next_node)
                instruction = f"Move from {current} to {next_node}. {direction}."
                print(f"\n➡️ {instruction}")
                self.speak(instruction)
            else:
                direction = self.get_relative_direction(current, current, next_node)
                print(f"\n➡️ First move: {current} → {next_node}: {direction}")

            # Detect ArUco marker for current location

            try:
                marker_id = self.detect_aruco_marker()   ### CURRENT FRAME
            except:
                break
            time.sleep(2)

            if marker_id is None or marker_id not in self.marker_to_node:
                print("⚠️ Invalid or no marker detected.")
                # user_input = input("📍 Type 'exit' to quit or press Enter to try again: ")

                # #df.exit
                # if user_input.lower() == 'exit':
                #     print("🚪 Exiting navigation. Goodbye!")
                #     exit()
                continue

            user_current = self.marker_to_node[marker_id]
            if user_current not in self.coordinates:
                print(f"⚠️ Node {user_current} not found in coordinates.")
                continue    

            if user_current != current:
                full_path.append(user_current)

            if user_current == next_node:
                prev_node = current
                current = user_current
                continue
            else:
                print("🔄 Recalculating path from new location...")
                prev_node = current
                current = user_current

        if current == goal:
            print("\n🎉 You have reached your destination!")
            print("🧭 Full path taken:", " → ".join(full_path))
        

# Run the recognition function

    
