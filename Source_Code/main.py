import param
import time 
import Default as df
import utilities 
import threading
import pyautogui
import torch
from datetime import datetime
import numpy as np
# from paddleocr import PaddleOCR
import easyocr
import User as u
import cv2
import multiprocessing
from ultralytics import YOLO
# Initialize PaddleOCR
global voice, feed, para, current_frame, ocr, tempo
tempo = False
# ocr = PaddleOCR(use_angle_cls=True, lang='en') 
# Load the YOLO model
model = YOLO("yolo11n.pt")  
feed = "Mobile"
voice = ''
current_frame = ''

def Video_feed(shared):
    global feed, current_frame
    temp= shared.feed
    feed=shared.feed
    if (shared.activated):
        # cap = cv2.VideoCapture(0)
        if feed== "Mobile":
            ut.app( "Acessing Camera")
            try :
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW, (cv2.CAP_PROP_HW_ACCELERATION, cv2.VIDEO_ACCELERATION_ANY))
                mm=True
            except:
                ut.app("Failed to Open Camera... Shifting on the Desktop Mode")
                # ut.speech()
                feed="Desktop"
        elif feed=="Desktop":
            mm=False
        while (shared.activated):
            # print (shared.feed)
            if mm:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to grab frame. Exiting...")
                    time.sleep(1)
                    break
            else:
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
            shared.current_frame = frame
            cv2.imshow('Android Camera Feed', frame)
            if cv2.waitKey(1) and  temp!=shared.feed:
                if mm:
                    cap.release()
                cv2.destroyAllWindows()
                Video_feed(shared)    
                break
            elif 0xFF == ord('q'):
                break
        cv2.destroyAllWindows()
    
    while (not shared.activated):
        # print("Waiting")
        if (shared.activated):
            Video_feed(shared)
            break
    time.sleep(1)
    Video_feed(shared)

# ------------------ DO NOT CHANGE ANY OTHER LOGIC BELOW ------------------ #
def detect_objects(frame, pos=False):
    """
    Detect objects in the frame and return the class names and their corresponding positions.

    Parameters:
    - frame: The input frame (image) from the webcam.
    - pos: Boolean flag to determine if position classification is required.
          If True, positions 'left', 'right', 'front' will be calculated.

    Returns:
    - class_labels: List of detected class labels.
    - positions: List of positions ('left', 'right', 'front') corresponding to each detected object.
    """

    # Perform inference on the frame
    results = model(frame)

    # Access the detected boxes from results[0] (first result in the list)
    boxes = results[0].boxes

    # Access class names from the model
    class_names = model.names

    # Initialize the lists for class labels and positions
    class_labels = []
    positions = []

    # Get the frame width and height
    frame_height, frame_width, _ = frame.shape

    # Set to track unique class labels and positions
    detected_classes_positions = {}

    # Loop through each detected object and extract the bounding box information
    for box in boxes:
        # Extract coordinates (xyxy format) of the bounding box
        xyxy = box.xyxy[0].cpu().numpy()  # Coordinates in (x1, y1, x2, y2) format
        x1, y1, x2, y2 = xyxy

        # Extract the class ID of the detected object
        class_id = int(box.cls[0])  # Class ID of the detected object
        class_name = class_names[class_id]  # Class name
        confidence = box.conf[0].cpu().numpy()  # Confidence score of the detection

        # Only proceed if the confidence score is greater than or equal to 0.85
        if confidence >= df.sensitivity:
            # Find the center of the bounding box
            center_x = (x1 + x2) / 2

            # If position classification is enabled (pos=True)
            if pos:
                # Classify the position based on the horizontal center of the frame
                if center_x < frame_width / 3:
                    position = 'left'
                elif center_x > 2 * frame_width / 3:
                    position = 'right'
                else:
                    position = 'front'
            else:
                # If position is not required, set position to an empty string
                position = ""

            # Add the class and its position to the dictionary if not already added
            if class_name not in detected_classes_positions:
                detected_classes_positions[class_name] = set()

            detected_classes_positions[class_name].add(position)

    # Flatten the dictionary to generate lists of class labels and their corresponding positions
    for class_name, positions_set in detected_classes_positions.items():
        for position in positions_set:
            class_labels.append(class_name)
            positions.append(position if pos else "")

    return class_labels, positions

def Main_Hierarchy(para):
    global voice, feed, ocr, current_frame, tempo
    reader = easyocr.Reader(['en'])
    mode = para.Mode.lower()
    while (para.Activated):
        
        if mode == df.Modes[0].lower():
            #2 functioin availble obstacle and OCR 
            feed = "Mobile"
            ut.app("Pocket Mode")
            while(True):
                if voice != "" and voice != df.Activation.lower() and voice not in df.Modes:
                    import User as u
                    if voice == df.Screen_Read.lower():
                        print("Doing the OCR in Pocket")  # do the OCR capure the frame store it some where and then read 
                        try :
                            if  (u.lan_en):
                                ut.app("Doing OCR on local GPT ")
                                txt=ut.local(current_frame,f'http://{u.lan_ip}:5000/predict' , "Please read the text")
                                ut.app(txt)
                                ut.app("Reading Ended")
                            else :
                                1/0
                        except:
                            if u.gpt_en == "false":
                                ut.app("Doing the OCR in Pocket Mode locally ")
                                result = reader.readtext(current_frame)
                                print(result)
                                if result != []:
                                    for (bbox, text, prob) in result:
                                        ut.app(text)
                                    ut.app("Reading Ended")
                                else:
                                    ut.app("Nothing")

                            elif u.gpt_en == "true":
                                # current_frame
                                gp_text = ut.analyze_image(current_frame, u.gpt_api, "Please Read the text only", "gpt-4o-mini")
                                ut.app(gp_text)
                                ut.app("Reading Ended")

                        # result = ocr.ocr(current_frame, det=True, rec=True, cls=True)
                        # for line in result[0]:
                        #     ut.app(line[1][0])
                        # print (result)
                        # ut.speech()
                        voice = ""
                    elif voice == df.Obstacle_avoidance.lower():
                        # print ("Doing the obstacle avoidance") # Do the Obstacle avoidence 
                        ut.app("Obstacle Avoidance")
                        class_labels, positions = detect_objects(current_frame, pos=False   )  # pos=True to classify position
                        
    # Print the results (class labels and corresponding positions)
                        print("Class Labels:", class_labels)
                        print("Positions:", positions)
                        for labe in class_labels:
                            # print (labe)
                            ut.app(labe)
                        # ut.speech()
                        voice=""

                    elif voice == "vlm":
                        try :
                            if  (u.lan_en):
                                    ut.app("Trying Scene Describing on local GPT ")
                                    txt=ut.local(current_frame,f'http://{u.lan_ip}:5000/predict' , "Please Describe the Scene")
                                    ut.app(txt)
                                    ut.app("Scene Ended")
                            else:
                                1/0
                        except:
                            if u.gpt_en=="true":
                                print (u.gpt_api)
                                ut.app("Scene Describing Activated")
                                current_frame=cv2.resize(current_frame , (256,256))
                                env_data=ut.analyze_scene(current_frame,u.gpt_api , "Please Describe the Scene", "gpt-4o-mini")
                                ut.app(env_data)
                                ut.app("Scene Ended")

                            else :
                                ut.app("Can't Describe Scene, API Not Available ")
                        voice=""
                    elif voice == "Guide":
                        print("Live Guide Mode")  # Do the Obstacle avoidence 
                        ut.app("Live Guide Mode")
                        
                        while (True):
                            # time.sleep(2)
                            if (ut.temp==False):
                                voice=""
                                print ("EXITING ")
                                ut.stop()
                                ut.app ("Exiting Live Guide Mode")
                                break   
                            class_labels, positions = detect_objects(current_frame, pos=True   )  # pos=True to classify position
                            #can't exit     
        # Print the results (class labels and corresponding positions)
                            print("Class Labels:", class_labels)
                            print("Positions:", positions)
                            for i, labe in enumerate(class_labels):
                                if str(labe) != "":
                                    ut.app(f'{str(labe)}  ,{str(positions [i])}')
                            # ut.speech()

                        voice = ""
                    elif voice == df.Time.lower():
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S").split(':')
                        
                        ut.app(f'{current_time[0]} hours and {current_time[1]} minute')
                        # ut.speech()
                        voice = ""
                    elif voice == df.nevigation.lower():
                        # print (" WARR gy nevigation ")
                        i =0
                        go = []
                        ut.app ("Nevigation Activated")
                        while(voice !="lvl5"):
                            if voice =="lvlexit":
                                ut.exe_nav=True
                                break
                        if ut.exe_nav ==False:

                            print("Enterned LEVL5 ")
                            time.sleep(1)
                            nav_pre= ""
                            ut.stop()
                            ut.app("Please Give the Starting Node")
                            # print (len(go))
                            while (len(go)<2):
                                if "_"  not in voice and  voice !="lvlexit" and voice !="lvl5" and voice !="" and voice !=nav_pre:
                                    # print ("INSIDE")
                                    go.append(voice)
                                    nav_pre= voice 
                                    time.sleep(1)
                                    if len(go)!=2:
                                        ut.app("Please Give Destination")
                                    print (go)
                                    # i+=1
                                if voice == "lvlexit":
                                    ut.exe_nav=True
                                    break
                            if ut.exe_nav ==False:
                                print ("Strating")
                                print (go)
                                ut.stop()
                                ut.app("Nav Starting")
                                ut.in_proces= True
                                ut.nav (int (go[0]),int ( go[1]))
                                ut.in_proces= False
                                ut.exe_nav= False
                                print ("Sucessfully OUT")
                        ut.exe_nav=False

                        # voice = ""
                    elif voice == df.Modes[1].lower():
                        mode = df.Modes[1].lower()
                        ut.app("Leaving Pocket Mode")
                        voice = ""
                        break
                    elif voice == df.Sleep.lower():
                        mode = "sleep"
                        ut.app("Going to Sleep")
                        break
                    elif voice == df.path_planning.lower():
                        ut.app("Path Planning ativated")
                        # PORT, BAUD = "COM5", 9600
                        # print(f"Opening {PORT}@{BAUD} …")
                        # ser = ut.open_serial(PORT, BAUD)
                        print("Serial ready – continuously streaming commands.\n")
                        cv2.namedWindow("Gradient Path Overlay", cv2.WINDOW_NORMAL)
                        cv2.resizeWindow("Gradient Path Overlay", 640, 480)
                        cv2.namedWindow("Direction", cv2.WINDOW_NORMAL)
                        cv2.resizeWindow("Direction", 300, 100)
                        # ─── Main loop ────────────────────────────────────────────────────────────────
                        alpha       = 0.8   # smoothing for path centre
                        prev_center = None

                        while True:
                            frame = cv2.resize(current_frame, (320, 240))
                            t0    = time.time()
                            results   = model.predict(source=frame, verbose=False)
                            overlay   = frame.copy()
                            direction = "Straight"
                            for res in results:
                                masks = res.masks.data if res.masks else None
                                ids   = res.boxes.cls.cpu().numpy() if res.boxes else None
                                if masks is not None and ids is not None:
                                    floor_masks = masks[[i for i, c in enumerate(ids) if c == ut.FLOOR_CLASS_ID]]
                                    if floor_masks.numel() > 0:
                                        raw   = (torch.any(floor_masks, 0).int()*255).cpu().numpy().astype(np.uint8)
                                        mask  = cv2.resize(raw, (320, 240), cv2.INTER_NEAREST)
                                        path  = ut.compute_path_points(mask)
                                        if path:
                                            last_x      = path[-1][0]
                                            prev_center = last_x if prev_center is None else int(alpha*prev_center + (1-alpha)*last_x)
                                            path[-1]    = (prev_center, path[-1][1])
                                            overlay     = ut.draw_gradient_path_on_image(frame, path)
                                            delta       = prev_center - frame.shape[1]//2
                                            if   delta < -20: direction = "Left"
                                            elif delta >  20: direction = "Right"
                            cmd = {"Straight": "0", "Left": "1", "Right": "2"}[direction]
                            # ut.send_line(ser, cmd)          # <-- always transmit
                            time.sleep(0.02)             #   ≈ 50 Hz; tweak or remove if needed

                            # visualisation
                            fps = 1.0 / (time.time() - t0)
                            cv2.putText(overlay, f"FPS: {fps:.2f}", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                            cv2.imshow("Gradient Path Overlay", overlay)

                            dir_img = np.zeros((100, 300, 3), np.uint8)
                            cv2.putText(dir_img, direction, (50, 60),
                                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
                            cv2.imshow("Direction", dir_img)

                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                    else:
                        # print("No Such Feature available in Pocket Mode")
                        if (voice !="stop"):
                            try:
                                if  (u.lan_en):
                                            ut.app("Sending Your text to local server")
                                            txt=ut.local(current_frame,f'http://{u.lan_ip}:5000/predict' , voice)
                                            ut.app(txt)
                                            ut.app("Let me know if you need any help")
                                else :
                                    ut.app("Local Server is not available")
                            except:
                                ut.app("Server Not available")
                            print ("OUT")
                        voice = ""
        elif mode == df.Modes[1].lower():
            feed= "Desktop"
            ut.app("Desktop Mode")
            # ut.speech()
            while(True):
                if voice!="":
                    if voice == df.Screen_Read.lower():
                        ut.app( "Doing the OCR in Desktop Mode")
                        # ut.speech() # do the OCR capure the frame store it some where and then read
                        current_frame=cv2.cvtColor(current_frame , cv2.COLOR_BGR2GRAY)
                        result = reader.readtext(current_frame)
                        # print(result)
                        for (bbox, text, prob) in result:
                            ut.app(text)
                        # print (current_frame.shape)
                        # current_frame=cv2.resize(current_frame, (int(h/2), int (w/2))) 
                        # result = ocr.ocr(current_frame, det=True, rec=True, cls=True)
                        # for line in result[0]:
                        #     ut.app(line[1][0])
                        voice=""
                    elif voice == df.Time.lower():
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S").split(':')
                        ut.app (f'{current_time[0]} hours and {current_time[1]} minute')
                        voice=""
                    elif voice==df.Modes[0].lower()  :
                        mode=df.Modes[0].lower()
                        ut.app("Leaving Desktop Mode")
                        break
                    elif voice== df.Sleep.lower():
                        mode="sleep"
                        ut.app("Going to Sleep")
                        break
                    else :
                        print ("No Such Feature Avaiable in Desktop Mode")
                        voice=""
        elif mode == df.Sleep.lower():
            para.Activated = False
            print("Sleeping")
            break
        else:
            pass
    

def Sec_Hierarchy():
    global voice 
    while (True):
        # print (voice)
        if voice == df.Activation.lower():
            ut.app("Activating")
            para.Activated = True
            Main_Hierarchy(para) 
        

def voice_fetch(shared,ip , enb, ted_ip):
    global voice, tempo 
    # print (df.teddy_en)
    # import User as u
    if (enb):
        data_rec = "T"
    else:
        data_rec = ""
    # print(ted_ip)
    print ("Ready!")
    while(True):
        # print(voice)
        # voice = (ut.continuous_voice_to_text()).lower() # Need to work on tha voice to text 
        if (data_rec == "T"):
            ut.get_teddy_data(ted_ip)
            # print("Teddy")
        else:
            ut.phone_data(ip)
            # print ("Phone")
        fetch = ut.data.lower()
        if fetch!= "" and "_"  not in  fetch:

            shared.voice=fetch

ut = utilities.utilss()
para = param.Main_Param()
def main():
    para.refresh()
    # ut.refresh()    
    
    # time.sleep(0.5)
    import User as u
    
    sec_hierarchy_thread = threading.Thread(target=Sec_Hierarchy)
    sec_hierarchy_thread.start()
    speech_thread = threading.Thread(target=ut.speech)
    speech_thread.start()
    # Start threads
    # time.sleep(0.5)
    # --- Setup multiprocessing for the video feed ---
    
    manager = multiprocessing.Manager()
    shared = manager.Namespace()
    shared.current_frame = current_frame
    shared.activated = para.Activated
    shared.feed=feed
    shared.voice=voice
    voice_fetch_thread = multiprocessing.Process(target=voice_fetch, args=(shared,u.IP_Address,u.teddy_en,u.Teddy_ip,))
    voice_fetch_thread.start()
    video_feed_process = multiprocessing.Process(target=Video_feed, args=(shared,))
    video_feed_process.start()
    # --- Synchronize shared variables with globals so other parts of your code work as-is ---
    def update_shared_vars():
        global current_frame, para , feed , voice , ut 
        pre = shared.voice
        while True:
            shared.feed=feed
            if shared.current_frame is not None:
                current_frame = shared.current_frame
                ut.cam_frame=shared.current_frame
            shared.activated = para.Activated
            # voice=shared.voice 
            # if shared.voice != pre:
            # # # if shared.voice =-
            if shared.voice !="":
                print (shared.voice )
            voice = shared.voice
            if (voice == para.interpt):
                ut.stop()
                # print("stop")
                # ut.app("Cleared")
                ut.done = True
            elif voice == "sleep" and para.Activated == False:
                print("ON")
                voice = df.Activation.lower()
            if (voice == df.Live_Guide.lower()):
                voice = "Guide"
                if (ut.temp == False):
                    ut.temp = True
                    # print ("TT")
                else:
                    ut.temp = False
                    # print ("Back")    
                time.sleep(0.5)
            elif voice=="mode":
                if feed=="Mobile":
                    voice="desk"
                else:
                    voice="pocket"
                time.sleep(1)
            elif voice == "lvlexit":
                print ("DOWN EX")
                if ut.in_proces: 
                    ut.exe_nav =True
            shared.voice=""

        
    sync_thread = threading.Thread(target=update_shared_vars, daemon=True)
    sync_thread.start()
if __name__ == '__main__':
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn', force=True)
    main()
