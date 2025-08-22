import os, threading, socket
from flask import Flask, request, jsonify, send_from_directory, Response
import cv2, numpy as np, qrcode
from datetime import datetime

# -------------------- Setup --------------------
app = Flask(__name__)
ORDERS = []
ORDER_ID = 1
RECORDINGS_DIR = "recordings"
QRCODES_DIR = "qrcodes"
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(QRCODES_DIR, exist_ok=True)

# -------------------- OpenCV / Mask Detection --------------------
CAP = cv2.VideoCapture(0)  # default webcam
CURRENT_VIDEO_WRITER = None
CURRENT_ORDER_ID = None
RECORDING = False

# Load Haar cascade for face detection
FACE_CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_mask(frame, face_bbox):
    """
    Improved mask detection:
    - Supports white, blue, black masks
    - Uses HSV + edge variance check
    """
    x, y, w_box, h_box = face_bbox
    # Focus only on lower half of face
    y_start = y + int(h_box * 0.45)
    y_end = y + h_box
    x_start = x
    x_end = x + w_box
    h, w, _ = frame.shape
    y_start, y_end = max(0, y_start), min(h, y_end)
    x_start, x_end = max(0, x_start), min(w, x_end)
    mask_region = frame[y_start:y_end, x_start:x_end]
    if mask_region.size == 0:
        return "Unknown"

    hsv = cv2.cvtColor(mask_region, cv2.COLOR_BGR2HSV)

    # Define multiple mask color ranges (white, blue, black)
    lower_white = np.array([0, 0, 180]); upper_white = np.array([179, 50, 255])
    lower_blue  = np.array([90, 50, 50]); upper_blue  = np.array([130, 255, 255])
    lower_black = np.array([0, 0, 0]);   upper_black = np.array([180, 255, 50])

    mask_white = cv2.inRange(hsv, lower_white, upper_white)
    mask_blue  = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_black = cv2.inRange(hsv, lower_black, upper_black)

    combined_mask = cv2.bitwise_or(mask_white, mask_blue)
    combined_mask = cv2.bitwise_or(combined_mask, mask_black)

    mask_percent = np.sum(combined_mask > 0) / (mask_region.shape[0] * mask_region.shape[1]) * 100

    # Edge variance helps distinguish mask cloth from skin
    gray = cv2.cvtColor(mask_region, cv2.COLOR_BGR2GRAY)
    edges = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Decision logic
    if mask_percent > 25 or edges < 40:
        return "Mask"
    else:
        return "No Mask"

def generate_frames():
    """Generate video frames with mask detection for streaming"""
    while True:
        ret, frame = CAP.read()
        if not ret:
            break
            
        # Create a copy for display (we'll draw on this)
        display_frame = frame.copy()
        
        # Perform face and mask detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, 1.3, 5)
        
        mask_status = "No Face"
        color = (0, 0, 255)  # Default red for no face
        
        for (x, y, w_box, h_box) in faces:
            mask_status = detect_mask(frame, (x, y, w_box, h_box))
            color = (0, 255, 0) if mask_status == "Mask" else (0, 0, 255)  # Green for mask, red for no mask
            cv2.rectangle(display_frame, (x, y), (x + w_box, y + h_box), color, 2)
            cv2.putText(display_frame, mask_status, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Add overall status text
        cv2.putText(display_frame, f"Status: {mask_status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', display_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

def start_recording(order_id):
    global CURRENT_VIDEO_WRITER, CURRENT_ORDER_ID, RECORDING
    if RECORDING: return
    CURRENT_ORDER_ID = order_id
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{RECORDINGS_DIR}/order_{order_id}_{timestamp}.avi"
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    width = int(CAP.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(CAP.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = 20.0
    CURRENT_VIDEO_WRITER = cv2.VideoWriter(filename, fourcc, fps, (width,height))
    RECORDING = True

    def record_loop():
        global RECORDING
        while RECORDING:
            ret, frame = CAP.read()
            if not ret: break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = FACE_CASCADE.detectMultiScale(gray,1.3,5)
            mask_status = "No Face"
            color=(0,0,255)
            for (x,y,w_box,h_box) in faces:
                mask_status = detect_mask(frame,(x,y,w_box,h_box))
                color=(0,255,0) if mask_status=="Mask" else (0,0,255)
                cv2.rectangle(frame,(x,y),(x+w_box,y+h_box),color,2)
            cv2.putText(frame, mask_status,(10,50),cv2.FONT_HERSHEY_SIMPLEX,1,color,2)
            CURRENT_VIDEO_WRITER.write(frame)
        CURRENT_VIDEO_WRITER.release()

    threading.Thread(target=record_loop, daemon=True).start()

def stop_recording(order_id):
    global RECORDING
    RECORDING = False
    video_files = [f for f in os.listdir(RECORDINGS_DIR) if f.startswith(f"order_{order_id}")]
    if video_files:
        video_file = video_files[-1]
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8",80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"
        video_url = f"http://{ip}:8000/{RECORDINGS_DIR}/{video_file}"
        qr_img = qrcode.make(video_url)
        qr_path = f"{QRCODES_DIR}/order_{order_id}.png"
        qr_img.save(qr_path)
        return qr_path
    return None

# -------------------- Flask Routes --------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/place_order", methods=["POST"])
def place_order():
    global ORDER_ID
    data = request.get_json()
    ORDERS.append({"id":ORDER_ID,"item":data['item'],"status":"pending","qr":""})
    ORDER_ID += 1
    return jsonify({"status":"ok"})

@app.route("/get_orders")
def get_orders():
    return jsonify(ORDERS)

@app.route("/start_order/<int:order_id>")
def start_order(order_id):
    for o in ORDERS:
        if o['id']==order_id:
            o['status']='in_progress'
            start_recording(order_id)
    return jsonify({"status":"recording"})

@app.route("/complete_order/<int:order_id>")
def complete_order(order_id):
    qr = stop_recording(order_id)
    for o in ORDERS:
        if o['id']==order_id:
            o['status']='completed'
            o['qr'] = qr
    return jsonify({"status":"completed","qr":qr})

@app.route("/recordings/<path:path>")
def send_recordings(path):
    return send_from_directory(RECORDINGS_DIR, path)

@app.route("/qrcodes/<path:path>")
def send_qrcodes(path):
    return send_from_directory(QRCODES_DIR, path)

@app.route('/video_feed')
def video_feed():
    """Video streaming route with mask detection"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# -------------------- Start HTTP file server for videos --------------------
def start_file_server():
    import subprocess
    subprocess.Popen(["python","-m","http.server","8000"])

# -------------------- Main --------------------
if __name__=="__main__":
    threading.Thread(target=start_file_server,daemon=True).start()
    app.run(host="0.0.0.0",port=9000, debug=True)