import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from utils.db import init_db, get_db
from utils.security import hash_password, check_password
from models.user import User
from detectors import yolov8_detector, face_recognition_util
from alerts import email_alert, sms_alert

app = Flask(__name__)
app.config.from_object("config.Config")


# Initialize Database
init_db(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    db = get_db()
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])  # Secure password hashing
        email = request.form['email']
        phone = request.form['phone']
        image_data = request.form['captured_image']

        image_path = os.path.join('static/uploads', f'{username}.png')
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        header, encoded = image_data.split(',', 1)
        with open(image_path, 'wb') as f:
            f.write(base64.b64decode(encoded))

        user = User(username=username, password=password, email=email, phone=phone, image_path=image_path)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_db()
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password(password, user.password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        else:
            error = "Invalid credentials. Please try again."
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/process_frame', methods=['POST'])
def process_frame():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    user = User.query.get(session['user_id'])

    frame_data = request.json.get('frame')
    if not frame_data:
        return jsonify({'error': 'No frame data provided'}), 400

    header, encoded = frame_data.split(',', 1)
    frame_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(frame_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    detections = yolov8_detector.detect_objects(frame)
    face_match = face_recognition_util.is_registered_face(frame, user.image_path)
    
    if not face_match:
        sms_alert.send_sms_alert("+91" + user.phone, "🚨 Intruder Alert: Unrecognized face detected! 🚨")
        email_alert.send_email_alert(user.email, "Intruder Alert", "An unrecognized face was detected on your live feed.")
        return jsonify({'intrusion': True, 'detections': detections})
    return jsonify({'intrusion': False, 'detections': detections})

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/send_alerts')
def send_alerts():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = User.query.get(session['user_id'])
    sms_alert.send_sms_alert("+91"+user.phone, "Test Alert: Intruder detected!")
    email_alert.send_email_alert(user.email, "Test Alert", "Intruder detected!")
    return "Alerts sent successfully!"

if __name__ == '__main__':
    os.makedirs(os.path.join('static/uploads'), exist_ok=True)
    app.run(debug=True)
