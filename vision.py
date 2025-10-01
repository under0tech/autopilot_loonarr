import cv2
import definitions as vars

from datetime import datetime
from picamera2 import Picamera2
from ultralytics import YOLO

model = YOLO(vars.vision_model)
image_width = vars.camera_width
image_height = vars.camera_height
yaw_conversion_factor = 0.002
threshold_percentage=0.40
approach_factor = 0.8
pi_camera_index = 255

def configure_camera():
    camera = {}
    if vars.video_source == pi_camera_index:
        camera = Picamera2()
        config = camera.create_preview_configuration(
            main={"size": (vars.camera_width, vars.camera_height), 
                  "format": "RGB888"})
        camera.configure(config)
        camera.start()
    else:
        camera = cv2.VideoCapture(vars.video_source)
        if not camera.isOpened():
            print('VISION: Camera is not ready!')
    
    return camera

cam = configure_camera()

def get_camera_image():
    result = {}
    png_file_name = \
    f'{vars.logger_directory}/img_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.png'

    if vars.video_source == pi_camera_index:
        frame = cam.capture_array()
        result = get_anotated_frame(frame, 
                                    png_file_name)
    else:
        success, frame = cam.read()
        if success:
            result = get_anotated_frame(frame, 
                                        png_file_name)
    
    cv2.destroyAllWindows()

    return result

def get_anotated_frame(frame, png_file_name):
    results = model(frame, classes=vars.vision_classes, 
                    imgsz=vars.camera_width, verbose=False)
    anotated_frame = results[0].plot()
    cv2.imwrite(png_file_name, anotated_frame)
    result = results[0]

    return result

def get_ned_coordinates(x1, y1, x2, y2, altitude):
    target_x = (x1 + x2) / 2
    target_y = (y1 + y2) / 2

    relative_x = (2 * target_x / image_width) - 1
    relative_y = (2 * target_y / image_height) - 1

    N_coord = relative_y * altitude
    E_coord = relative_x * altitude
    
    D_coord = 0

    return N_coord, E_coord, D_coord

def get_yaw_angle(x1, y1, x2, y2):
    target_x = (x1 + x2) / 2
    yaw_angle = (target_x - image_width / 2) * yaw_conversion_factor

    return yaw_angle

def get_target_threshold_area(x1, y1, x2, y2):
    target_area = (x2 - x1) * (y2 - y1)
    threshold_area = \
        image_width * image_height * threshold_percentage

    return target_area, threshold_area

def is_target_close_enough(x1, y1, x2, y2):
    target_area, threshold_area = \
        get_target_threshold_area(x1, y1, x2, y2)
    
    return target_area > threshold_area

def get_ned_target(x1, y1, x2, y2, altitude):
    N_coord, E_coord, D_coord = get_ned_coordinates(
        x1, y1, x2, y2, altitude)
    yaw_angle = get_yaw_angle(x1, y1, x2, y2)
    target_area, threshold_area = \
        get_target_threshold_area(x1, y1, x2, y2)
    long_factor = threshold_area / target_area

    return round(N_coord * long_factor * approach_factor, 4), \
        round(E_coord, 4), round(D_coord, 4), round(yaw_angle, 4)