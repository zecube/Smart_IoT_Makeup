import cv2
import utils
import mediapipe as mp
import numpy as np


FACE_OVAL=[ 10, 338, 297, 332, 284, 251, 389, 356, 454, 
            323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 
            148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 
            127, 162, 21, 54, 103,67, 109]

LIPS=[ 61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 
    308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
    185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 
    415, 310, 311, 312, 13, 82, 81, 42, 183, 78 ] # 아랫입술+윗입술
LOWER_LIPS =[61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]   # 윗입술
UPPER_LIPS=[ 185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78]    # 아래입술

CLOSE_LIP=[61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185] # 닫힌입술 (입술+입술안 포함)

LEFT_EYE =[ 362, 382, 381, 380, 374, 373, 390, 249, 263,   466, 388, 387, 386, 385,384, 398 ]
LEFT_EYEBROW =[ 336, 296, 334, 293, 300, 276, 283, 282, 295, 285 ]
LEFT_CLOWN = [357,350,349,348,347,346,340,372, 345,352,411,425,266,371,355]

RIGHT_EYE=[ 33, 7, 163, 144, 145, 153, 154, 155, 133,    173, 157, 158, 159, 160, 161 , 246 ]  
RIGHT_EYEBROW=[ 70, 63, 105, 66, 107, 55, 65, 52, 53, 46 ]
RIGHT_CLOWN=[143,111,117,118,119,120,121,128, 126,142,36,205,187,123,116]

def fillPolyTrans(img, points, color, opacity):
    """
    @param img: (mat) input image, where shape is drawn.
    @param points: list [tuples(int, int) these are the points custom shape,FillPoly
    @param color: (tuples (int, int, int)
    @param opacity:  it is transparency of image.
    @return: img(mat) image with rectangle draw.

    """
    list_to_np_array = np.array(points, dtype=np.int32)
    overlay = img.copy()  # coping the image
    cv2.fillPoly(overlay,[list_to_np_array], color )
    new_img = cv2.addWeighted(overlay, opacity, img, 1 - opacity, 0)
    # print(points_list)
    img = new_img
    cv2.polylines(img, [list_to_np_array], True, color,1, cv2.LINE_AA)
    return img
# landmark detection function 
def landmarksDetection(img, results, draw=False):
    img_height, img_width= img.shape[:2]
    # list[(x,y), (x,y)....]
    mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
    if draw :
        [cv2.circle(img, p, 2, utils.GREEN, -1) for p in mesh_coord]

    # returning the list of tuples for each landmarks 
    return mesh_coord

def nothing(x):
    pass

map_face_mesh = mp.solutions.face_mesh

# 카메라를 엽니다.
camera = cv2.VideoCapture(0)
face_mesh = map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5)

cv2.namedWindow('result')
cv2.createTrackbar('mix','result',0,100,nothing)
mix = cv2.getTrackbarPos('mix','result')


while camera.isOpened():
    # 프레임을 가져옵니다.
    ret, frame = camera.read()
    # frame = cv2.resize(frame,(1920,1080))
    copy = frame.copy()
    mask = np.zeros_like(frame)          # 캠 크기와 같은 검정색으로 이루어진 화면 (마스킹 사용시 사용됨)
    

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    results  = face_mesh.process(rgb_frame)


    if results.multi_face_landmarks:
        mesh_coords = landmarksDetection(frame, results, False)
        mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LIPS], utils.WHITE, opacity=1 )
        masked = cv2.bitwise_and(copy, mask)
        mask_copy = mask.copy
        # mask_copy =~mask
        # #  마스킹 하기
        # masked = cv2.bitwise_or(copy, mask_copy)
        cv2.imshow('masked', mask)
        
        

        # 프레임을 HSV 색상 공간으로 변환합니다.
        hsv_frame = cv2.cvtColor(masked, cv2.COLOR_BGR2HSV)
        # HSV 색상 공간에서 색상을 변경합니다.
        hsv_frame[:, :, 1] += 100

        # 프레임을 RGB 색상 공간으로 다시 변환합니다.
        frame2 = cv2.cvtColor(hsv_frame, cv2.COLOR_HSV2BGR)
        cv2.imshow("Video", frame2)

        mask_copy = mask.copy
        mask_copy =~mask
        frame_mask = cv2.bitwise_and(copy, mask_copy)
        
        frame_mask = cv2.bitwise_or(frame2, frame_mask)
        cv2.imshow('frame_mask', frame_mask)
        
    
        result = cv2.addWeighted(frame, mix/100, frame_mask, 1-(mix/100), 0) # 두개의 이미지를 가중치에 따라서 다르게 보여줍니다.
        cv2.imshow('result', result)
        mix = cv2.getTrackbarPos('mix','result')
                    

    
    # 프레임을 화면에 표시합니다.
    
    cv2.imshow("Video2", frame)

    # 키 입력을 기다립니다.
    key = cv2.waitKey(1)

    # 'q'를 누르면 종료합니다.
    if key == ord("q"):
        break