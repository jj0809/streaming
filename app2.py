from flask import Response, Flask, render_template
import threading
import argparse 
import datetime, time
import imutils
import cv2


app = Flask(__name__)

url = 'rtsp://210.99.70.120:1935/live/cctv001.stream'
camera = cv2.VideoCapture(url)

@app.route('/')
def index():
    return render_template('index.html')


def gen_frames():  
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_video')
def save_video():
    writeVideo()
    return 

def writeVideo():
    # 현재시간 가져오기
    currentTime = datetime.datetime.now()
    
    # (웹)캠 설정
    camera.set(3, 800)  # 영상 가로길이 설정
    camera.set(4, 600)  # 영상 세로길이 설정
    fps = 20
    # 가로, 세로 길이 가져오기
    streaming_window_width = int(camera.get(3))
    streaming_window_height = int(camera.get(4))  
    
    #현재 시간을 '년도 달 일 시간 분 초'로 가져와서 문자열로 생성
    fileName = str(currentTime.strftime('%y%m%d_%H:%M:%S'))

    #파일 저장하기 위한 변수 선언
    path = f'/Users/jjyoun/{fileName}.avi'
    
    # DIVX 코덱 적용 # 코덱 종류 # DIVX, XVID, MJPG, X264, WMV1, WMV2
    # 무료 라이선스의 이점이 있는 XVID를 사용
    fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    
    # 비디오 저장
    # cv2.VideoWriter(저장 위치, 코덱, 프레임, (가로, 세로))
    out = cv2.VideoWriter(path, fourcc, fps, (streaming_window_width, streaming_window_height))

    last_capture_time = time.time()

    while True:
        ret, frame = camera.read()
        # cv2.imshow('streaming video', frame)
        if ret:
            out.write(frame)  # 프레임을 비디오 파일에 저장

        # 10초마다 저장하기
        if time.time() - last_capture_time >= 10:
            last_capture_time = time.time()
            print("프레임 저장")
            out.release()
            output_file = '/Users/jjyoun/' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.avi'
            out = cv2.VideoWriter(output_file, fourcc, fps, (streaming_window_width, streaming_window_height))

        # 1ms뒤에 뒤에 코드 실행
        k = cv2.waitKey(1) & 0xff
        #키보드 esc 누르면 종료된다.
        if k == 27 :
            break

    camera.release()  # cap 객체 해제
    out.release()  # out 객체 해제
    cv2.destroyAllWindows()

if __name__ == "__main__":
    app.run(debug=True)