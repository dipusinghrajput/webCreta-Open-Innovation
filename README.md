Team Name - webCreta

Team lead -Dipu Kumar Singh

member 1- Ashirwad Pandey

member 2- Astha Singh

member 3- Shiwani Dwivedi

PROJECT TITLE - AI POWERED HYGIENE MONITORING FOR INDIAN FOOD PRODUCTION UNIT (HOTEL AND RESTURANTS)


A **restaurant kitchen management dashboard** built with **Flask + OpenCV**.
It lets customers place food orders while kitchen staff manage them with a **live camera feed**, automatic **video recording**, and **mask detection** for safety. Completed orders generate a **QR code** linking to the saved recording.

---

## ✨ Features & Workflow

### 👤 Customer Side

1. Customer opens the web page and switches to **Customer Mode**.
2. They enter a food item and place an order.
3. The order is added to the system with status **Pending**.

### 👨‍🍳 Kitchen Side

1. Kitchen switches to **Kitchen Mode** and sees all orders:

   * **Pending** (new orders)
   * **In Progress** (being prepared)
   * **Completed** (finished, with QR code)
2. When kitchen clicks **Start**, the system:

   * Updates order status → *In Progress*
   * Starts **live camera feed** in the dashboard
   * Begins **recording video** with **mask detection overlay**
3. When kitchen clicks **Complete**, the system:

   * Stops recording and saves video in `/recordings`
   * Generates a **QR code** that links to the recording
   * Updates order status → *Completed* with QR code displayed

### 🎥 Mask Detection (During Recording & Live Feed)

* The camera tracks faces in real time.
* The lower half of the face is analyzed to detect if a **mask is worn**.
* The live feed shows status: **Mask** (green) or **No Mask** (red).
* Video recordings save these overlays for later review.

---

## 🛠 Tech Stack

* **Backend:** Python, Flask
* **Computer Vision:** OpenCV, Haar Cascade, NumPy
* **QR Code Generation:** qrcode (Pillow)
* **Frontend:** HTML, CSS, Vanilla JS
* **Storage:** Local filesystem (`recordings/`, `qrcodes/`)

---

## 📂 Project Structure

```
.
├── ppe_detection_rewrite.py   # Flask + OpenCV backend
├── index.html                 # Web UI (Customer + Kitchen)
├── requirements.txt           # Dependencies
├── recordings/                # Saved video files
└── qrcodes/                   # Generated QR codes
```

---

## ⚡ Installation & Local Access

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/kitchen-mask-dashboard.git
cd kitchen-mask-dashboard
```

### 2. Install Requirements

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python ppe_detection_rewrite.py
```

### 4. Access Locally

* Open browser → [http://localhost:9000](http://localhost:9000)
* Switch between **Customer Mode** and **Kitchen Mode**

---

## 🚀 Workflow (Step-by-Step Usage)

1. **Customer places order** → order added to system (`Pending`).
2. **Kitchen views queue** → order shows up in Kitchen Mode.
3. **Click Start** →

   * Order status changes to `In Progress`
   * Camera feed + recording begins with mask detection.
4. **Click Complete** →

   * Recording stops, saved in `/recordings/`
   * QR code generated in `/qrcodes/`
   * QR code displayed in dashboard linking to recording.

---

## 🎯 Example Use Case

* A restaurant wants to **track food preparation safely**.
* Every order gets a **video log** proving food was prepared while staff wore masks.
* Managers can scan QR codes later to verify recordings.

---

## 🔮 Future Improvements

* CNN/DNN-based mask detection for higher accuracy.
* Support for multiple cameras.
* Admin authentication & role-based access.
* Sound alerts for new orders or no-mask detection.
* Cloud video storage + analytics.

---

## 📜 License

MIT License – free to use, modify, and distribute.

---

Would you like me to also include a **diagram (workflow image)** in the README (Customer → Server → Camera → QR → Kitchen) so it’s more visual on GitHub?
