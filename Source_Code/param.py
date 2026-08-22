import Default as df
import User as u
class Main_Param:
    def __init__(self) :
        # self.IP_Adress=df.IP_Adress
        self.DEFAULT_MODE=df.DEFAULT_MODE
        self.Mode= df.Mode
        self.Activated=df.Activated
        self.Sleep=df.Sleep
        self.time=df.Time
        self.interpt=df.Interupt.lower()
        self.voi_text=[]
        self.done=False
        self.data=""
        self.temp=False
        self.gpt_api=df.gpt_api
        self.gpt_en= df.gpt_en
        self.busy= False
    def app(self , text):
        self.voi_text.append(text)
        # print (self.voi_text)
    def stop(self):
        self.voi_text=[]
    def refresh (self):
        u.update_config()
        
        self.DEFAULT_MODE=df.DEFAULT_MODE
        self.Mode= df.Mode
        self.Activated=df.Activated
        self.Sleep=df.Sleep
        self.time=df.Time
        self.interpt=df.Interupt.lower()
        self.voi_text=[]
        self.done=False
        self.data=""

# #!/usr/bin/env python3

# import time
# import cv2

# # Open the webcam
# cap = cv2.VideoCapture(f"http://192.168.100.5:4747/video")  # Use the correct camera index if it's not the default (0)

# if not cap.isOpened():
#     print("Error: Could not open video stream.")
#     exit()

# # Track time and display FPS
# prev_time = time.time()

# while True:
#     # Capture the frame
#     ret, frame = cap.read()
    
#     if not ret:
#         print("Error: Failed to capture frame.")
#         break
    
#     current_time = time.time()

#     # Only process and display 1 frame per second
#     if current_time - prev_time >= 0.25:  # 1 second has passed
#         prev_time = current_time  # Update the previous time to current time
        
#         # Display the frame
#         cv2.imshow('Webcam Feed', frame)

#     # Check if 'q' key is pressed to quit
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the capture and close the window
# cap.release()
# cv2.destroyAllWindows()

# import requests
# from requests.exceptions import ConnectionError, Timeout, RequestException
# from urllib3.exceptions import MaxRetryError
# import time

# # Replace with the actual ESP32 IP address
# esp32_ip = "http://192.168.100.5:8080/"

# last = ""  # To track the last response and print only if there's a new message

# while True:  
#     try:
#         # Send a GET request to the ESP32 server with a timeout of 10 seconds
#         response = requests.get(esp32_ip, timeout=10)  # Timeout to avoid hanging indefinitely

#         # Check if the request was successful
#         if response.status_code == 200:
#             if last != response.text:
#                 last = response.text
#                 print(f"Received message from ESP32: {response.text}")
#         else:
#             print(f"Unexpected status code: {response.status_code}")

#     except MaxRetryError as e:
#         # Handle MaxRetryError, raised when the max retries have been exceeded
#         print("Max retry attempts exceeded")
#         # print(f"Error details: {e}")
#         time.sleep(5)  # Adding a delay before retrying, to avoid continuous errors

#     except ConnectionError as e:
#         # If a connection error occurs (e.g., machine actively refusing the connection)
#         print("Remote off - Connection Error")
#         # print(f"Error details: {e}")
#         time.sleep(5)  # Adding a delay before retrying

#     except Timeout as e:
#         # If a timeout occurs
#         print("Request timed out")
#         # print(f"Error details: {e}")
#         time.sleep(5)  # Adding a delay before retrying

#     except RequestException as e:
#         # Handle any other type of request exceptions
#         print("An error occurred during the request")
#         # print(f"Error details: {e}")
#         time.sleep(5)  # Adding a delay before retrying
