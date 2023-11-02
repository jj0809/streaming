#Import necessary libraries
from flask import Flask, render_template, Response, request , jsonify
import cv2
import numpy as np
from PIL import Image
from flask_socketio import SocketIO, emit


#Initialize the Flask app
app = Flask(__name__)
socketio = SocketIO(app=app,logger=True)

url = 'rtsp://210.99.70.120:1935/live/cctv001.stream'
camera = cv2.VideoCapture(url)

car_cascade = cv2.CascadeClassifier('haarcascade_cars.xml')


@socketio.on('test')
def test(data):
    camera = cv2.VideoCapture(url)
    while True:
        success, frame = camera.read()
        if not success:
            print('break')
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            #detect cars in the video
            cars = car_cascade.detectMultiScale(gray, 1.1, 3)
            #cv2.im_write(cars)

            #to draw a rectangle in each cars 
            for (x,y,w,h) in cars:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                # cv2.imshow('video', frame)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            cv2.waitKey(1)
            frame = buffer.tobytes()

            emit('response_back', frame)

@socketio.on('test2')
def test2(data):
    camera = cv2.VideoCapture(url)
    while True:
        success, frame = camera.read()
        if not success:
            print('break')
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            cv2.waitKey(1)
            frame = buffer.tobytes()

            emit('response_back', frame)

def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            cv2.waitKey(1)
            frame = buffer.tobytes()
            # ai 바운딩 frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_frames2():  
    while True:
        success, frame = camera.read()  # read the camera frame

        if not success:
            break
        else:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            #detect cars in the video
            cars = car_cascade.detectMultiScale(gray, 1.1, 3)
            #cv2.im_write(cars)

            #to draw a rectangle in each cars 
            for (x,y,w,h) in cars:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                # cv2.imshow('video', frame)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            cv2.waitKey(1)
            frame = buffer.tobytes()
            # ai 바운딩 frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    return Response(gen_frames2(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feed2')
def feed2():
    return render_template('feed2.html')
@app.route('/origin')
def origin():
    return render_template('origin.html')
@app.route('/socketorigin')
def socketorigin():
    return render_template('socketorigin.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)