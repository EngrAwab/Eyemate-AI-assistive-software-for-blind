import User as u
# IP_Adress= u.IP_Address
# u.update_config()

USER_NAME=u.USER_NAME
DEFAULT_MODE=u.DEFAULT_MODE
gpt_en= u.gpt_en
gpt_api=u.gpt_api
mobile_en = u.mobile_en
teddy_en= u.teddy_en
teddy_ip= u.Teddy_ip
# Mode
Modes=["Pocket", "Desk"]
Mode="Pocket"
#Word Declaration 
Activation="Onm"
Screen_Read = "Read Text"
Obstacle_avoidance= "Obstacle Detection"
Sleep = "sleep"
Time = "Time"
Interupt= "stop"
Live_Guide="liveguide"
sensitivity=0.7
path_planning="path"
nevigation ="nav"
path_model="floor.pt"

coordinates = {
    "Stairs 1": [2, 1], "Stairs 2": [7, 1], "Student Washroom": [7, 22], "Room 504a": [10, 12], "Room 504b": [17, 12],
    "Room 502a": [12, 20], "500": [7, 12], "Room 502b": [16, 20], "Room 503a": [19, 12], "Room 503b": [24, 12],
    "Room 501a": [19, 20], "Room 501b": [24, 20], "Computer Lab 1": [26, 12], "Computer Lab 2": [36, 12], "Faculty Lift": [27, 20],
    "Faculty Office": [37, 5], "fc1": [38, 12], "Media Room": [39, 1], "FCR": [41, 5], "Civil Department": [32, 20],
    "Principal NUSET Office": [37, 20], "Male Faculty Washroom": [45, 24], "Female Faculty Washroom": [48, 24], "int": [51, 16],
    "Department Office 2": [59, 5], "Department Office 1": [59, 14], "int2": [59, 17],
    "Stairs 4": [58, 0], "Stairs 3": [58, 26],
    "CS Department": [62, 15], "ME Department": [66, 15], "Principal NUSIT Office": [60, 13], "Conference Room 2": [64, 13],
    "CEN Department": [62, 5], "EE Department": [66, 5], "Dean Office": [60, 7], "Conference Room 1": [64, 7], "Kitchen": [66, 7]
}

edges = {
    "Stairs 1": ["Stairs 2"],
    "Stairs 2": ["Stairs 1", "500"],
    "500": ["Stairs 2", "Student Washroom", "Room 504a"],
    "Student Washroom": ["500", "Room 502a"],
    "Room 504a": ["500", "Room 504b", "Room 502a"],
    "Room 504b": ["Room 504a", "Room 503a", "Room 502b"],
    "Room 502a": ["Room 504a", "Student Washroom", "Room 502b"],
    "Room 502b": ["Room 504b", "Room 502a", "Room 501a"],
    "Room 503a": ["Room 504b", "Room 503b", "Room 501a"],
    "Room 503b": ["Room 503a", "Computer Lab 1", "Room 501b"],
    "Room 501a": ["Room 502b", "Room 503a", "Room 501b"],
    "Room 501b": ["Room 501a", "Room 503b", "Faculty Lift"],
    "Computer Lab 1": ["Room 503b", "Computer Lab 2", "Faculty Lift"],
    "Computer Lab 2": ["Computer Lab 1","fc1", "Principal NUSET Office"],
    "Faculty Lift": ["Room 501b", "Computer Lab 1", "Civil Department"],
    "Faculty Office": ["Computer Lab 2", "fc1", "Media Room", "FCR"],
    "fc1": ["Faculty Office", "Computer Lab 2", "int", "Principal NUSET Office"],
    "Media Room": ["Faculty Office"],
    "FCR": ["Faculty Office", "Principal NUSET Office"],
    "Civil Department": ["Faculty Lift", "Principal NUSET Office"],
    "Principal NUSET Office": ["Civil Department", "int", "Computer Lab 2", "Faculty Office", "fc1"],
    "int": ["Computer Lab 2", "fc1", "Principal NUSET Office", "int2", "Female Faculty Washroom"],
    "Female Faculty Washroom": ["int", "Male Faculty Washroom"],
    "Male Faculty Washroom": ["Female Faculty Washroom"],
    "int2": ["int", "Department Office 1", "Stairs 3"],
    "Department Office 1": ["int2", "Department Office 2", "Principal NUSIT Office", "CS Department"],
    "Department Office 2": ["Department Office 1", "Stairs 4", "CEN Department", "Dean Office"],
    "Stairs 4": ["Department Office 2"],
    "Stairs 3": ["int2"],
    "CEN Department": ["Department Office 2", "EE Department", "Dean Office", "Conference Room 1"],
    "EE Department": ["CEN Department", "Kitchen"],
    "Dean Office": ["CEN Department", "Conference Room 1", "Department Office 2"],
    "CS Department": ["ME Department", "Principal NUSIT Office", "Conference Room 2", "Department Office 1"],
    "ME Department": ["CS Department", "Conference Room 2"],
    "Principal NUSIT Office": ["Department Office 1", "CS Department", "Conference Room 2"],
    "Conference Room 2": ["Principal NUSIT Office", "ME Department", "CS Department"],
    "Conference Room 1": ["Dean Office", "Kitchen", "CEN Department", "EE Department"],
    "Kitchen": ["Conference Room 1", "EE Department"]
}
marker_to_node = {
    500: "500",
    501: "Stairs 1",
    502: "Stairs 2",
    503: "Student Washroom",
    504: "Room 502a",
    505: "Room 502b",
    506: "Room 504a",
    507: "Room 504b",
    508: "Room 501a",
    509: "Room 501b",
    510: "Room 503a",
    511: "Room 503b",
    512: "Faculty Lift",
    513: "Computer Lab 1",
    514: "Computer Lab 2",
    515: "Civil Department",
    516: "Faculty Office",
    517: "Media Room",
    518: "FCR",
    519: "Principal NUSET Office",
    520: "Female Faculty Washroom",
    521: "Male Faculty Washroom",
    522: "int",
    523: "Stairs 3",
    524: "Department Office 1",
    525: "CS Department",
    527: "Principal NUSIT Office",
    528: "Department Office 2",
    529: "Dean Office",
    531: "CEN Department",
    532: "Stairs 4",
    533: "fc1",
    534: "int2",
    535: "EE Department",
    536: "Conference Room 2",
    537: "Kitchen",
    538: "ME Department"
}

#Pram 
conf=False
Activated=False
