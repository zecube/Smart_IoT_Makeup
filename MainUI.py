import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from threading import Thread
import datetime
from time import sleep
from pyowm import OWM #pip install pyowm  [Weather api] [https://github.com/csparpa/pyowm/]
import googlemaps, requests #pip install -U googlemaps      [Geocoding API,Geolocation API] [Google Cloud]
import json
from skimage import exposure
from skimage.exposure import match_histograms
import pandas as pd
import cv2
import numpy as np
import matplotlib.pylab as plt
from PersonalColor import personal_color
import mediapipe as mp

import makeup_ref_img
import utils
#==========머리 마스킹 ========
from HairSegmentation import HairSegmentation
from PIL import Image
from keras.models import load_model
#=========헬스 케어 ============
import HealthCare_stress_and_melanoma as health


QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)     #고해상도 설정
df = pd.read_excel("savedata.xlsx")


############################################################################################################
####################################   LOAD DATA WINDOW    #################################################
############################################################################################################
class LoadWindow(QWidget):
    def __init__(self):
        super().__init__()
        loadLayout = QVBoxLayout()

        self.label = QLabel("불러올 데이터를 선택하세요.")
        loadLayout.addWidget(self.label)

        self.radioButton = QRadioButton("save data1")
        self.radioButton.clicked.connect(self.radiobtn1_func)
        loadLayout.addWidget(self.radioButton)
        self.radioButton_2 = QRadioButton("save data2")
        self.radioButton_2.clicked.connect(self.radiobtn2_func)
        loadLayout.addWidget(self.radioButton_2)
        self.radioButton_3 = QRadioButton("save data3")
        self.radioButton_3.clicked.connect(self.radiobtn3_func)
        loadLayout.addWidget(self.radioButton_3)

        self.loadButton = QPushButton("LOAD")
        self.loadButton.clicked.connect(self.load_func)
        loadLayout.addWidget(self.loadButton)

        self.setLayout(loadLayout)


    def radiobtn1_func(self):
        self.loaddata = 'savedata1'
        return self.loaddata
    def radiobtn2_func(self):
        self.loaddata = 'savedata2'
        return self.loaddata
    def radiobtn3_func(self):
        self.loaddata = 'savedata3'
        return self.loaddata
    
    def load_func(self):
        global loadlst
        loadlst = list(df[self.loaddata].head(3))

        self.close()


############################################################################################################
####################################     SAVE DATA WINDOW    ###############################################
############################################################################################################
class SaveWindow(QWidget):
    def __init__(self):
        super().__init__()
        saveLayout = QVBoxLayout()

        self.label = QLabel("데이터를 저장할 위치를 선택하세요.")
        saveLayout.addWidget(self.label)

        self.radioButton = QRadioButton("save data1")
        self.radioButton.clicked.connect(self.radiobtn1_func)
        saveLayout.addWidget(self.radioButton)
        self.radioButton_2 = QRadioButton("save data2")
        self.radioButton_2.clicked.connect(self.radiobtn2_func)
        saveLayout.addWidget(self.radioButton_2)
        self.radioButton_3 = QRadioButton("save data3")
        self.radioButton_3.clicked.connect(self.radiobtn3_func)
        saveLayout.addWidget(self.radioButton_3)

        self.saveButton = QPushButton("SAVE")
        self.saveButton.clicked.connect(self.save_func)
        saveLayout.addWidget(self.saveButton)

        self.setLayout(saveLayout)


    def radiobtn1_func(self):
        self.savedata = 'savedata1'
        return self.savedata
    def radiobtn2_func(self):
        self.savedata = 'savedata2'
        return self.savedata
    def radiobtn3_func(self):
        self.savedata = 'savedata3'
        return self.savedata
    
    def save_func(self):
        df[self.savedata] = savelst
        df.to_excel("project\savedata.xlsx", index=False)
        self.close()
    

############################################################################################################
########################################  MAIN WINDOW   ####################################################
############################################################################################################

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        
        palette = QPalette()

        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)

        brush = QBrush(QColor(0, 0, 0))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush)

        MainWindow.setPalette(palette)
        MainWindow.showFullScreen()

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.hidden = False
        self.count = 0
        
        #날씨 이모티콘 ====================================================================
        self.weather = QLabel(self.centralwidget)
        self.weather.setGeometry(QRect(120, 50, 150,130))
        self.weather.setObjectName("weather")

        #온도 label [온도 출력]
        self.temperature = QLabel(self.centralwidget)
        self.temperature.setGeometry(QRect(80, 160, 300,130))
        self.temperature.setObjectName("temperature")
        self.temperature.setFont(QFont("맑은 고딕",20))

        #================================================================================
        #clock 이라는 이름으로 label 생성 [hello world]===================================
        self.clock = QLabel(self.centralwidget)
        self.clock.setGeometry(QRect(80,45,400,400))

        #time 이라는 이름으로 label 생성 [(오전/오후)시/분]
        self.time = QLabel(self.centralwidget)
        self.time.setGeometry(QRect(70,1300,800,60))    #(x,y, 가로, 높이)
        self.time.setObjectName("time")
        #setFont(QtGui.QFont("Font_name",Font_size))
        self.time.setFont(QFont("맑은 고딕",50)) 

        #date 이라는 이름으로 label 생성 [년/월/일]
        self.date = QLabel(self.centralwidget)
        self.date.setGeometry(QRect(290, 1250, 300, 50))
        self.date.setObjectName("date")
        self.date.setFont(QFont("맑은 고딕",20))
        #=====================================================================================
        #화장 버튼 만들기======================================================================
        self.btnSkin = QPushButton(self.centralwidget)
        self.btnSkin.setGeometry(QRect(2200,1000,50,50))
        self.btnSkin.clicked.connect(self.makeupshow)

        self.btnHide  = QPushButton(self.centralwidget)
        self.btnHide.setGeometry(QRect(2200,1100,50,50))
        self.btnHide.clicked.connect(self.facehide)
        self.btnHide.setCheckable(True)

        #얼굴 인식 칸 ====================================================================
        self.face = QLabel(self.centralwidget)
        self.face.setGeometry(QRect(800, 200, 800,1000))
        self.face.setStyleSheet('border-style: solid;''border-width: 3px;''border-color: #00FF00')
        # self.face.setBrush(QPalette.Active, QPalette.WindowText, QColor(255, 255, 255))
        self.face.setObjectName("face")
        
        self.face_make = QLabel(self.centralwidget)
        self.face_make.setGeometry(QRect(803, 250, 794,900))
        self.face_make.setObjectName("face_make")


        # 피부 =================================================================================
        self.SkinColor1 = QPushButton(self.centralwidget)
        self.SkinColor1.setGeometry(QRect(1700,1000,50,50))
        self.SkinColor1.clicked.connect(self.s_color1_start)
        self.SkinColor1.setCheckable(True)
        self.SkinColor2 = QPushButton(self.centralwidget)
        self.SkinColor2.setGeometry(QRect(1800,1000,50,50))
        self.SkinColor2.clicked.connect(self.s_color2_start)
        self.SkinColor2.setCheckable(True)
        self.SkinColor3 = QPushButton(self.centralwidget)
        self.SkinColor3.setGeometry(QRect(1900,1000,50,50))
        self.SkinColor3.clicked.connect(self.s_color3_start)
        self.SkinColor3.setCheckable(True)
        self.SkinColor4 = QPushButton(self.centralwidget)
        self.SkinColor4.setGeometry(QRect(2000,1000,50,50))
        self.SkinColor4.clicked.connect(self.s_color4_start)
        self.SkinColor4.setCheckable(True)
        self.SkinColor5 = QPushButton(self.centralwidget)
        self.SkinColor5.setGeometry(QRect(2100,1000,50,50))
        self.SkinColor5.clicked.connect(self.s_color5_start)
        self.SkinColor5.setCheckable(True)

        self.skin_result = None
        self.skin_value = False
        #입술 ==============================================================================================
        self.MouthColor1 = QPushButton(self.centralwidget)
        self.MouthColor1.setGeometry(QRect(1700,800,50,50))
        self.MouthColor1.clicked.connect(self.m_color1_start)
        self.MouthColor1.setCheckable(True)
        self.MouthColor2 = QPushButton(self.centralwidget)
        self.MouthColor2.setGeometry(QRect(1800,800,50,50))
        self.MouthColor2.clicked.connect(self.m_color2_start)
        self.MouthColor2.setCheckable(True)
        self.MouthColor3 = QPushButton(self.centralwidget)
        self.MouthColor3.setGeometry(QRect(1900,800,50,50))
        self.MouthColor3.clicked.connect(self.m_color3_start)
        self.MouthColor3.setCheckable(True)
        self.MouthColor4 = QPushButton(self.centralwidget)
        self.MouthColor4.setGeometry(QRect(2000,800,50,50))
        self.MouthColor4.clicked.connect(self.m_color4_start)
        self.MouthColor4.setCheckable(True)
        self.MouthColor5 = QPushButton(self.centralwidget)
        self.MouthColor5.setGeometry(QRect(2100,800,50,50))
        self.MouthColor5.clicked.connect(self.m_color5_start)
        self.MouthColor5.setCheckable(True)
        
        self.mouth_value = False
        self.mouth_result = None
        #눈썹 ==============================================================================================
        self.EyeColor1 = QPushButton(self.centralwidget)
        self.EyeColor1.setGeometry(QRect(1700,600,50,50))
        self.EyeColor1.clicked.connect(self.e_color1_start)
        self.EyeColor1.setCheckable(True)
        self.EyeColor2 = QPushButton(self.centralwidget)
        self.EyeColor2.setGeometry(QRect(1800,600,50,50))
        self.EyeColor2.clicked.connect(self.e_color2_start)
        self.EyeColor2.setCheckable(True)
        self.EyeColor3 = QPushButton(self.centralwidget)
        self.EyeColor3.setGeometry(QRect(1900,600,50,50))
        self.EyeColor3.clicked.connect(self.e_color3_start)
        self.EyeColor3.setCheckable(True)
        self.EyeColor4 = QPushButton(self.centralwidget)
        self.EyeColor4.setGeometry(QRect(2000,600,50,50))
        self.EyeColor4.clicked.connect(self.s_color4)
        self.EyeColor4.setCheckable(True)
        self.EyeColor5 = QPushButton(self.centralwidget)
        self.EyeColor5.setGeometry(QRect(2100,600,50,50))
        self.EyeColor5.clicked.connect(self.s_color5)
        self.EyeColor5.setCheckable(True)

        self.eyebrow_value = False
        self.eyebrow_result = None
        #볼 ==============================================================================================
        self.CheekColor1 = QPushButton(self.centralwidget)
        self.CheekColor1.setGeometry(QRect(300,700,50,50))
        self.CheekColor1.clicked.connect(self.c_color1_start)
        self.CheekColor1.setCheckable(True)
        self.CheekColor2 = QPushButton(self.centralwidget)
        self.CheekColor2.setGeometry(QRect(400,700,50,50))
        self.CheekColor2.clicked.connect(self.c_color2_start)
        self.CheekColor2.setCheckable(True)
        self.CheekColor3 = QPushButton(self.centralwidget)
        self.CheekColor3.setGeometry(QRect(500,700,50,50))
        self.CheekColor3.clicked.connect(self.c_color3_start)
        self.CheekColor3.setCheckable(True)
        self.CheekColor4 = QPushButton(self.centralwidget)
        self.CheekColor4.setGeometry(QRect(600,700,50,50))
        self.CheekColor4.clicked.connect(self.c_color4_start)
        self.CheekColor4.setCheckable(True)

        self.cheek_value = False
        self.cheek_result = None
        #눈썹 위치==============================================================================================
        self.dyxSlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.dyxSlider.setGeometry(QRect(1800,500,200,50))
        self.dyxSlider.setValue(50)
        self.dyxSlider.valueChanged.connect(self.dyxVal)
        self.xpos_UP = QPushButton(self.centralwidget)
        self.xpos_UP.setGeometry(QRect(2100,500,50,50))
        self.xpos_UP.clicked.connect(self.xpos_UPVal)
        self.xpos_UP.setText("UP")
        self.xpos_DOWN = QPushButton(self.centralwidget)
        self.xpos_DOWN.clicked.connect(self.xpos_DOWNVal)
        self.xpos_DOWN.setGeometry(QRect(1700,500,50,50))
        self.xpos_DOWN.setText("DOWN")
        self.posx = 0
        

        
        self.dyySlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.dyySlider.setGeometry(QRect(1800,400,200,50))
        self.dyySlider.setValue(50)
        self.dyySlider.valueChanged.connect(self.dyyVal)
        self.ypos_UP = QPushButton(self.centralwidget)
        self.ypos_UP.setGeometry(QRect(2100,400,50,50))
        self.ypos_UP.clicked.connect(self.ypos_UPVal)
        self.ypos_UP.setText("UP")
        self.ypos_DOWN = QPushButton(self.centralwidget)
        self.ypos_DOWN.clicked.connect(self.ypos_DOWNVal)
        self.ypos_DOWN.setGeometry(QRect(1700,400,50,50))
        self.ypos_DOWN.setText("DOWN")
        self.posy = 0


        self.lengthSlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.lengthSlider.setGeometry(QRect(1800,300,100,50))
        self.lengthSlider.valueChanged.connect(self.lengthVal)
        self.length_UP = QPushButton(self.centralwidget)
        self.length_UP.setGeometry(QRect(2100,300,50,50))
        self.length_UP.clicked.connect(self.length_UPVal)
        self.length_UP.setText("UP")
        self.length_DOWN = QPushButton(self.centralwidget)
        self.length_DOWN.clicked.connect(self.length_DOWNVal)
        self.length_DOWN.setGeometry(QRect(1700,300,50,50))
        self.length_DOWN.setText("DOWN")
        self.length = 0

        #볼 위치==============================================================================================
        self.c_dyxSlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.c_dyxSlider.setGeometry(QRect(400,600,200,50))
        self.c_dyxSlider.setValue(50)
        self.c_dyxSlider.valueChanged.connect(self.c_dyxVal)
        self.c_xpos_UP = QPushButton(self.centralwidget)
        self.c_xpos_UP.setGeometry(QRect(700,600,50,50))
        self.c_xpos_UP.clicked.connect(self.c_xpos_UPVal)
        self.c_xpos_UP.setText("UP")
        self.c_xpos_DOWN = QPushButton(self.centralwidget)
        self.c_xpos_DOWN.clicked.connect(self.c_xpos_DOWNVal)
        self.c_xpos_DOWN.setGeometry(QRect(300,600,50,50))
        self.c_xpos_DOWN.setText("DOWN")
        self.c_posx = 0
        

        
        self.c_dyySlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.c_dyySlider.setGeometry(QRect(400,500,200,50))
        self.c_dyySlider.setValue(50)
        self.c_dyySlider.valueChanged.connect(self.c_dyyVal)
        self.c_ypos_UP = QPushButton(self.centralwidget)
        self.c_ypos_UP.setGeometry(QRect(700,500,50,50))
        self.c_ypos_UP.clicked.connect(self.c_ypos_UPVal)
        self.c_ypos_UP.setText("UP")
        self.c_ypos_DOWN = QPushButton(self.centralwidget)
        self.c_ypos_DOWN.clicked.connect(self.c_ypos_DOWNVal)
        self.c_ypos_DOWN.setGeometry(QRect(300,500,50,50))
        self.c_ypos_DOWN.setText("DOWN")
        self.c_posy = 0


        self.c_widthSlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.c_widthSlider.setGeometry(QRect(400,400,100,50))
        self.c_widthSlider.valueChanged.connect(self.c_widthVal)
        self.c_width_UP = QPushButton(self.centralwidget)
        self.c_width_UP.setGeometry(QRect(700,400,50,50))
        self.c_width_UP.clicked.connect(self.c_width_UPVal)
        self.c_width_UP.setText("UP")
        self.c_width_DOWN = QPushButton(self.centralwidget)
        self.c_width_DOWN.clicked.connect(self.c_width_DOWNVal)
        self.c_width_DOWN.setGeometry(QRect(300,400,50,50))
        self.c_width_DOWN.setText("DOWN")
        self.c_width = 0

        self.c_heightSlider = QSlider(Qt.Horizontal,self.centralwidget)
        self.c_heightSlider.setGeometry(QRect(400,300,100,50))
        self.c_heightSlider.valueChanged.connect(self.c_heightVal)
        self.c_height_UP = QPushButton(self.centralwidget)
        self.c_height_UP.setGeometry(QRect(700,300,50,50))
        self.c_height_UP.clicked.connect(self.c_height_UPVal)
        self.c_height_UP.setText("UP")
        self.c_height_DOWN = QPushButton(self.centralwidget)
        self.c_height_DOWN.clicked.connect(self.c_height_DOWNVal)
        self.c_height_DOWN.setGeometry(QRect(300,300,50,50))
        self.c_height_DOWN.setText("DOWN")
        self.c_height = 0


        # ==============================================================================================================
        # 블렌딩=========================================================================================================
        self.s_Blending = QSlider(Qt.Horizontal,self.centralwidget)
        self.s_Blending.setGeometry(QRect(1800,1100,200,50))
        self.s_Blending.valueChanged.connect(self.s_Blendingval)
        self.s_UP = QPushButton(self.centralwidget)
        self.s_UP.setGeometry(QRect(2100,1100,50,50))
        self.s_UP.clicked.connect(self.s_UpVal)
        self.s_UP.setText("UP")
        self.s_DOWN = QPushButton(self.centralwidget)
        self.s_DOWN.clicked.connect(self.s_DownVal)
        self.s_DOWN.setGeometry(QRect(1700,1100,50,50))
        self.s_DOWN.setText("DOWN")
        self.s_Blending.setValue(0)
        self.s_mix = 0

        self.m_Blending = QSlider(Qt.Horizontal,self.centralwidget)
        self.m_Blending.setGeometry(QRect(1800,900,200,50))
        self.m_Blending.valueChanged.connect(self.m_Blendingval)
        self.m_UP = QPushButton(self.centralwidget)
        self.m_UP.setGeometry(QRect(2100,900,50,50))
        self.m_UP.clicked.connect(self.m_UpVal)
        self.m_UP.setText("UP")
        self.m_DOWN = QPushButton(self.centralwidget)
        self.m_DOWN.clicked.connect(self.m_DownVal)
        self.m_DOWN.setGeometry(QRect(1700,900,50,50))
        self.m_DOWN.setText("DOWN")
        self.m_Blending.setValue(0)
        self.m_mix = 0

        self.e_Blending = QSlider(Qt.Horizontal,self.centralwidget)
        self.e_Blending.setGeometry(QRect(1800,700,200,50))
        self.e_Blending.valueChanged.connect(self.e_Blendingval)
        self.e_UP = QPushButton(self.centralwidget)
        self.e_UP.setGeometry(QRect(2100,700,50,50))
        self.e_UP.clicked.connect(self.e_UpVal)
        self.e_UP.setText("UP")
        self.e_DOWN = QPushButton(self.centralwidget)
        self.e_DOWN.clicked.connect(self.e_DownVal)
        self.e_DOWN.setGeometry(QRect(1700,700,50,50))
        self.e_DOWN.setText("DOWN")
        self.eb_mix = 0

        self.c_Blending = QSlider(Qt.Horizontal, self.centralwidget)
        self.c_Blending.setGeometry(QRect(400,800,200,50))
        self.c_Blending.valueChanged.connect(self.c_Blendingval)
        self.c_UP = QPushButton(self.centralwidget)
        self.c_UP.setGeometry(QRect(700,800,50,50))
        self.c_UP.clicked.connect(self.c_UpVal)
        self.c_UP.setText("UP")
        self.c_DOWN = QPushButton(self.centralwidget)
        self.c_DOWN.clicked.connect(self.e_DownVal)
        self.c_DOWN.setGeometry(QRect(300,800,50,50))
        self.c_DOWN.setText("DOWN")
        self.c_mix = 0

        # ==============================================================================================================
        # 세이브 로드====================================================================================================
        self.savebtn = QPushButton(self.centralwidget)
        self.savebtn.setGeometry(QRect(2000,100,100,50))
        self.savebtn.setText("SAVE")
        self.savebtn.clicked.connect(self.openSaveWindow)
        self.saveWindow = SaveWindow()


        self.loadbtn = QPushButton(self.centralwidget)
        self.loadbtn.setGeometry(QRect(1800,100,100,50))
        self.loadbtn.setText("LOAD")
        self.loadbtn.clicked.connect(self.openLoadWindow)
        self.loadWindow = LoadWindow()
        self.event_loop = QEventLoop()      #이벤트 루프

        # ==============================================================================================================
        # 헬스 케어 =====================================================================================================
        self.btnHealth = QPushButton(self.centralwidget)
        self.btnHealth.setGeometry(QRect(2200,900,50,50))
        self.btnHealth.clicked.connect(self.healthcare)
        self.btnHealth.setCheckable(True)

        self.stress = QLabel(self.centralwidget)
        self.stress.setGeometry(QRect(1700, 500, 400,100))
        self.stress.setStyleSheet('color: green;'
                                  'border-style: solid;'
                                  'border-width: 5px;'
                                  'border-color: red;' 
                                  'border-radius: 50px;')
        self.stress.setFont(QFont("맑은 고딕",20,QFont.Bold))
        self.stress.setAlignment(Qt.AlignCenter)
        self.stress.hide()

        self.btnMelanoma = QPushButton(self.centralwidget)
        self.btnMelanoma.setGeometry(QRect(1700,700,400,100))
        self.btnMelanoma.clicked.connect(self.DetectMelanoma)
        self.btnMelanoma.setFont(QFont("맑은 고딕",20,QFont.Bold))
        self.btnMelanoma.setText("흑색종 탐색")
        self.btnMelanoma.hide()

        self.melanoma = QLabel(self.centralwidget)
        self.melanoma.setGeometry(QRect(1700, 900, 400,100))
        self.melanoma.setStyleSheet('color : brown;'
                                    'border-style: solid;'
                                  'border-width: 5px;'
                                  'border-color: brown;' 
                                  'border-radius: 50px;')
        self.melanoma.setFont(QFont("맑은 고딕",20,QFont.Bold))
        self.melanoma.setAlignment(Qt.AlignCenter)
        self.melanoma.hide()
        

        # ==============================================================================================================
        # 카메라, AI====================================================================================================
        self.cap = cv2.VideoCapture(0)    # 캠 저장
        self.aibtn = QPushButton(self.centralwidget)
        self.aibtn.setGeometry(QRect(2000,1200,100,50))
        self.aibtn.setText("AI추천")
        self.aibtn.clicked.connect(self.AIfunc)

        
            
        #UI 보이기
        MainWindow.setCentralWidget(self.centralwidget)
        # self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

        
    
    # def retranslateUi(self, MainWindow):
    #     _translate = QCoreApplication.translate
    #     MainWindow.setWindowTitle(_translate("MainWindow", "SmartMirror"))


    #-----------------------------------------------------------------------------------------
    # 이벤트
    # EVENT
    #-----------------------------------------------------------------------------------------
    '''def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_rect(qp)
        qp.end()

    def draw_rect(self, qp):
        qp.setBrush(QColor(180, 100, 160))
        qp.setPen(QPen(QColor(60, 60, 60), 3))
        qp.drawRect(20, 20, 100, 100)'''
    
    def healthcare(self, MainWindow):
        # # 창 띄우기
        if self.btnHealth.isChecked():
            self.stress.show()
            self.btnMelanoma.show()
            self.melanoma.show()
        else:
            self.stress.hide()
            self.btnMelanoma.hide()
            self.melanoma.hide()


        # camera = cv2.VideoCapture(0)    # 캠 저장
        # 미디어파이프의 FaceMesh와 FaceDetection 모듈을 초기화합니다.
        mp_face_detection = mp.solutions.face_detection
        mp_face_mesh = mp.solutions.face_mesh
        while self.btnHealth.isChecked():
            _, frame = self.cap.read()
            gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
                with mp_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5) as face_mesh:
                    
                    # 추출한 얼굴 영역에 FaceDetection 모듈을 적용합니다. / FaceDetection은 results 사용
                    results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                    # 추출한 얼굴 영역에 FaceMesh 모듈을 적용합니다. / 23.5.7 이전 faceMash 사용시 if results.detections: 의 results를 face_results로 변환
                    try:
                        bad_count = health.emotion_song(results, frame, gray_img)
                        if bad_count == 0:
                            self.stress.setText("스트레스지수 보통")
                            
                            
                        elif bad_count == 1:
                            self.stress.setText("스트레스지수 높음")
                            
                        else:
                            self.stress.setText("스트레스지수 매우 높음")
                            
                    except:
                        pass
            cv2.imshow('test', frame)
            cv2.waitKey(1)
        
        
    def DetectMelanoma(self, MainWindow):
        _, img = self.cap.read()
        comp = health.melanoma(img)
        # print(comp)
        if comp < 0.099: # 기준값 099
            self.melanoma.setText("점이 비대칭, 흑색종 의심")
        else:
            self.melanoma.setText("점이 대칭, 흑색종 안심")

    #시간
    def set_time(self,MainWindow):
        EvenOrAfter = "오전"
        while True:
            now=datetime.datetime.now() #현재 시각을 시스템에서 가져옴
            hour=now.hour

            if(now.hour>=12):
                EvenOrAfter="P.M."
                hour=now.hour%12

                if(now.hour==12):
                    hour=12

            else:
                EvenOrAfter="A.M."

            self.date.setText("%s년 %s월 %s일"%(now.year,now.month,now.day))
            self.time.setText(" %s %s시 %s분" %(EvenOrAfter,hour,now.minute))
            sleep(1)


    #weather (아이콘 설정 및 기온 출력)
    def weather_icon(self,MainWindow):
        #IP 기반 위도와 경도 찾기
        def get_location():
            GOOGLE_API_KEY = 'AIzaSyD_qckRmOOWxcrSop9uWlKaqkec4ccwQOs'
            url = f'https://www.googleapis.com/geolocation/v1/geolocate?key={GOOGLE_API_KEY}'
            data = {'considerIp': True, }   # 현 IP로 데이터 추출

            result = requests.post(url, data) # 해당 API에 요청을 보내며 데이터를 추출한다.

            result2 = json.loads(result.text)

            lat = result2["location"]["lat"] # 현재 위치의 위도 추출
            lng = result2["location"]["lng"] # 현재 위치의 경도 추출
            
            return lat,lng 

        while True:
            API_key = '1296f2181c5e3e22acb4fc333db31dd4'        #Openweathermap API 인증키 [https://openweathermap.org/]
            owm = OWM(API_key)
            mgr = owm.weather_manager()
            lat, lng = get_location()
            

            #위치
            #obs = mgr.weather_at_place('Seoul')              # Toponym
            #obs = mgr.weather_at_id(2643741)                      # city ID
            obs = mgr.weather_at_coords(lat,lng)      # lat/lon

            #날씨 정보 불러오기
            weather = obs.weather #날씨
            temp_dict_kelvin = weather.temperature('celsius')   # 섭씨 온도
            

            self.temperature.setText("현재 온도 %.1f ℃ " %(temp_dict_kelvin['temp']))
            
            if 'Clear' in weather.status:
                self.weather.setPixmap(QPixmap("project\weather_icon\sun.png"))

            elif "Cloudy" in weather.status:
                self.weather.setPixmap(QPixmap("project\weather_icon\clouds.png"))

            elif "Rain" in weather.status:
                self.weather.setPixmap(QPixmap("project\weather_icon\drop.png"))

            elif "Snow" in weather.status:
                self.weather.setPixmap(QPixmap("project\weather_icon\snowflake.png"))

            sleep(300)
   
   #화장결과 숨기기 / 화장결과 보이기
    def facehide(self,MainWindow):
        if self.count % 2 == 0:
            self.face.hide()
            # self.skin.hide()
            # self.mouth.hide()
            # self.eye.hide()
            self.face_make.hide()
            self.count = self.count +1
        else:
            self.face.show()
            # self.skin.show()
            # self.mouth.show()
            # self.eye.show()
            self.face_make.show()
            self.count = self.count +1
    
    #-------------------------------------------------------------------------------------------
    #화장 기능
    #-------------------------------------------------------------------------------------------
    def Make_Up(self):
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



        LIPS1_up=[ 61, 96, 89, 179, 86, 316, 403, 319, 325, 291, 
                308, 324, 318, 402, 317, 14, 87, 178, 88, 95,
                185, 40, 39, 37,0 ,267 ,269 ,270 ,409, 
                415, 310, 311, 312, 13, 82, 81, 42, 183, 78 ]
        LIPS1_down=[61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291,
                    325, 319, 403, 316, 86, 179, 89, 96]

        RIGHT_EYE_up1 = [247,30,29,27,28,56,190,  133, 173, 157, 158, 159, 160, 161 , 246, 33]
        RIGHT_EYE_up2 = [225,224,223,222,221,   133, 173, 157, 158, 159, 160, 161 , 246, 33]
        LEFT_EYE_up1 = [414,286,258,257,259,260,467,    263, 466, 388, 387, 386, 385,384, 398, 362 ]
        LEFT_EYE_up2 = [441,442,443,444,445,    263, 466, 388, 387, 386, 385,384, 398, 362 ]

        DARKCIRCLE_RIGHT= [33, 7, 163, 144, 145, 153, 154, 155, 133,  112,232,231,230,110]
        DARKCIRCLE_LEFT= [362, 382, 381, 380, 374, 373, 390, 249, 263, 339,450,451,452,341]
        
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

        map_face_mesh = mp.solutions.face_mesh

        camera = self.cap    # 캠 저장
        # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 1920)
        # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)

        face_mesh = map_face_mesh.FaceMesh(min_detection_confidence =0.5, min_tracking_confidence=0.5)

        while True:
            ret, frame = camera.read() # getting frame from camera 
            frame = cv2.resize(frame,(1920,1080))
            frame = frame[140:940, 460:1460].copy()
            copy =frame.copy()              # 카피, 자른 화면 보이게 할 시 사용
            mask = np.zeros_like(frame)          # 캠 크기와 같은 검정색으로 이루어진 화면 (마스킹 사용시 사용됨)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            results  = face_mesh.process(rgb_frame)
            
            def draw_FACE_OVAL(mask,colors, ref_img):   # 얼굴 라인
                # Inialize hair segmentation model / 머리카락 세분화 모델을 초기화합니다.
                hair_segmentation = HairSegmentation()
                
                
                blackbox = np.zeros_like(frame)          # 캠 크기와 같은 검정색으로 이루어진 화면 (마스킹 사용시 사용됨)
                
                hair_mask = hair_segmentation(frame)

                # Get dyed frame. / 염료 처리된 프레임을 가져옵니다.
            
                dyed_image = np.zeros_like(frame)
                dyed_image[:] = 255, 255, 255
                dyed_frame = dyed_image

                # Mask our dyed frame (pixels out of mask are black). / 염료 처리된 프레임에서 마스크를 적용합니다 (마스크 밖의 픽셀은 검은색).
                dyed_hair = cv2.bitwise_or(frame, dyed_frame, mask=hair_mask) ################### 이거로 #########################
                dyed_hair =~dyed_hair

                if results.multi_face_landmarks:
                    mesh_coords = landmarksDetection(frame, results, False)
                    #====== 머리 추가 =========================================================
                    addHair = mesh_coords[18][1] - mesh_coords[152][1]    # 18번매쉬.y좌표 - 0번매쉬.y좌표 / 18번을 [0, 14, 17, 18, 200, 199, 175] 중 1택 가능
                    
                    for i in [127, 162, 21, 54, 103,67, 109, 10, 338, 297, 332, 284, 251, 389, 356]:
                        mesh_coords[i] = (mesh_coords[i][0], mesh_coords[i][1] + addHair)
                    #==========================================================================

                    mask =fillPolyTrans(mask, [mesh_coords[p] for p in FACE_OVAL], colors, opacity=1 )
                    


                    # 입술 뺄 시 아래 코드 사용
                    # mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LIPS], (0,0,0), opacity=1 )  # 입술만 뺌
                    mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in CLOSE_LIP], (0,0,0), opacity=1 )   # (입술+입술 내부) 포함해서 뺌
                    # 눈 뺄 시
                    mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LEFT_EYE], (0,0,0), opacity=1 )
                    mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in RIGHT_EYE], (0,0,0), opacity=1 )
                    # # 눈썹 뺄 시
                    mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LEFT_EYEBROW], (0,0,0), opacity=1 )
                    mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in RIGHT_EYEBROW], (0,0,0), opacity=1 )
                    # masked = cv2.bitwise_and(copy, mask)
                    # # 머리
                    mask = cv2.bitwise_and(mask, dyed_hair)

                    mask_copy = mask.copy
                    mask_copy =~mask
                    # #  마스킹 하기
                    masked = cv2.bitwise_or(copy, mask_copy)
                    # cv.imshow('FACE_OVAL mask', mask) # 자른 형상 출력
                    # cv.imshow('FACE_OVAL masked', masked) # 마스킹 되는 형상 출력

                    matched = match_histograms(masked,ref_img, channel_axis= -1)
                    # out = cv2.bitwise_and(matched,mask)
                    # result = cv2.bitwise_and(copy,mask_copy)
                    # result = cv2.bitwise_or(out,result)

                    s_weighted_img = cv2.addWeighted(matched, self.s_mix/100, masked, 1-(self.s_mix/100), 0) # 두개의 이미지를 가중치에 따라서 다르게 보여줍니다.
                    
                    return s_weighted_img, mask
                
            def draw_LIPS(mask, colors, ref_img):    # 입술
                if results.multi_face_landmarks:
                    mesh_coords = landmarksDetection(frame, results, False)
                    mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LIPS], colors, opacity=1 )
                    masked = cv2.bitwise_and(copy, mask)
                    mask_copy = mask.copy
                    mask_copy =~mask
                    # #  마스킹 하기
                    masked = cv2.bitwise_or(copy, mask_copy)
                
                    matched = match_histograms(masked,ref_img, channel_axis= -1)

                    out = cv2.bitwise_and(matched,mask)
                    result = cv2.bitwise_and(copy,mask_copy)
                    result = cv2.bitwise_or(out,result)

                    m_weighted_img = cv2.addWeighted(matched, self.m_mix/100, masked, 1-(self.m_mix/100), 0) # 두개의 이미지를 가중치에 따라서 다르게 보여줍니다.
                    
                    return m_weighted_img, mask

            def overlay(image, x, y, w, h, overlay_image): # 대상 이미지 (3채널), x, y 좌표, width, height, 덮어씌울 이미지 (4채널)
                alpha = overlay_image[:, :, 3] # BGRA
                mask_image = alpha / 255 # 0 ~ 255 -> 255 로 나누면 0 ~ 1 사이의 값 (1: 불투명, 0: 완전)
                copy = image.copy()
                
                for c in range(0, 3): # channel BGR
                    copy[y:y+h, x:x+w, c] = (overlay_image[:,:, c] * mask_image) + (copy[y:y+h, x:x+w, c] * (1 - mask_image))
                    
                
                return image, copy
                

            def Blur(cam):
                #샤프닝
                kernel9 = [-1, -1, -1,
                            -1, 9, -1,
                            -1, -1, -1]
                kernel5 = [0, -1, -0,
                            -1, 5, -1,
                            0, -1, 0]
                # sharpening9 = np.array(kernel9, np.float32).reshape(3,3)
                # sharpen = cv2.filter2D(matched, -1, sharpening9) #결과 샤프닝
                # sharpen_out = cv2.bitwise_and(sharpen,mask)
                # sharpen9 = cv2.bitwise_or(sharpen_out,pre_result)

                # sharpening5 = np.array(kernel5, np.float32).reshape(3,3)
                # sharpen = cv2.filter2D(matched, -1, sharpening5) #결과 샤프닝
                # sharpen_out = cv2.bitwise_and(sharpen,mask)
                # sharpen5 = cv2.bitwise_or(sharpen_out,pre_result)
                # cv2.imshow('sharpening9', sharpen9)
                # cv2.imshow('sharpening5', sharpen5)

                #블러
                # Blur2 = cv2.blur(cam, (2,2))
                # Blur5 = cv2.blur(cam, (5,5))
                # Blur10 = cv2.blur(cam, (10,10))         #절대X

                # #가우시안 블러 10, 10 2
                sigmax, sigmay = 10,10
                GaussianBlur2 = cv2.GaussianBlur(cam, (1,1), sigmax, sigmay)
                # GaussianBlur5 = cv2.GaussianBlur(cam, (5,5), sigmax, sigmay)
                # GaussianBlur10 = cv2.GaussianBlur(cam, (9,9), sigmax, sigmay)

                # #중앙 블러
                # medianBlur2 = cv2.medianBlur(cam, 3)
                # medianBlur5 = cv2.medianBlur(cam, 5)
                # medianBlur10 = cv2.medianBlur(cam, 9)

                # # #Bilateral 블러 10
                # BilateralBler2 = cv2.bilateralFilter(cam,-1,10,5)
                # BilateralBler5 = cv2.bilateralFilter(cam,10,50,50)
                # BilateralBler10 = cv2.bilateralFilter(cam,10,75,75)


                # sharpening9 = np.array(kernel9, np.float32).reshape(3,3)
                # sharpen9 = cv2.filter2D(cam, -1, sharpening9) #결과 샤프닝

                # sharpening5 = np.array(kernel5, np.float32).reshape(3,3)
                # sharpen5 = cv2.filter2D(cam, -1, sharpening5) #결과 샤프닝
                
                # sharpen5medianBlur3 = cv2.medianBlur(sharpen5, 3)
                # sharpen9medianBlur3 = cv2.medianBlur(sharpen9, 3)

                # sharpen5medianBlur5 = cv2.medianBlur(sharpen5, 5)
                # sharpen9medianBlur5 = cv2.medianBlur(sharpen9, 5)

                # sharpen5medianBlur9 = cv2.medianBlur(sharpen5, 9)
                # sharpen9medianBlur9 = cv2.medianBlur(sharpen9, 9)

                # BilateralBler2 = cv2.bilateralFilter(sharpen5,10,50,50)
                # BilateralBler5 = cv2.bilateralFilter(sharpen9,10,50,50)
                                 
                return GaussianBlur2
            
            #================================================
            #기본상태
            if (self.skin_value == False) and (self.mouth_value == False) and (self.eyebrow_value == False) and (self.cheek_value == False):  
                img_frist = frame
                img_frist = cv2.cvtColor(img_frist, cv2.COLOR_BGR2RGB)
                h, w, c = img_frist.shape
                # print(w,',',h)
                img_frist = cv2.flip(img_frist,1)
                result_img = QImage(img_frist.data, w, h, w*c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(result_img)
                self.face_make.setPixmap(pixmap)
                sleep(0.1)  

            #화장 내의 버튼이 눌린 상태 
            else:
                img_frist = frame
                h, w, c = img_frist.shape

                skin_mask = np.zeros_like(frame)
                mouth_mask = np.zeros_like(frame)
                masked_result = np.zeros_like(frame)
                final_mask = masked_result.copy()

                if self.skin_value: #피부 버튼 눌렸을때
                    if results.multi_face_landmarks:
                        self.skin_result, mask_skin = draw_FACE_OVAL(skin_mask, utils.WHITE, self.skin_ref_img)
                        final_mask = cv2.bitwise_or(mask_skin, final_mask)
                        self.skin_result = cv2.bitwise_and(self.skin_result, mask_skin)
                    

                        
                if self.mouth_value: #입술 버튼 눌렸을때
                    if results.multi_face_landmarks:
                        self.mouth_result, mask_mouth = draw_LIPS(mouth_mask, utils.WHITE, self.mouth_ref_img)
                        final_mask = cv2.bitwise_or(mask_mouth, final_mask)
                        self.mouth_result = cv2.bitwise_and(self.mouth_result, mask_mouth)

                if self.eyebrow_value:
                    if results.multi_face_landmarks:
                        mesh_coords = landmarksDetection(frame, results, False)
                        
                        #-----------left
                        mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LEFT_EYEBROW], utils.WHITE, opacity=1 )
                        x_LEFT = [mesh_coords[p][0] for p in LEFT_EYEBROW]
                        w_LEFT = int(max(x_LEFT) - min(x_LEFT))
                        y_LEFT = [mesh_coords[p][1] for p in LEFT_EYEBROW]
                        h_LEFT = int(max(y_LEFT) - min(y_LEFT))

                        x_mid_pos_left = max(x_LEFT) - w_LEFT + self.posx 
                        y_mid_pos_left = max(y_LEFT) - h_LEFT + self.posy
                        pos_LEFT = (int(x_mid_pos_left), int(y_mid_pos_left))#(round(max(x_LEFT)-w_LEFT/2), round(max(y_LEFT)-h_LEFT/2))
                        
                        left_eyebrow = self.left_eyebrow
                        left_eyebrow = cv2.resize(left_eyebrow, (w_LEFT + self.length , h_LEFT))        
                        
                        #----------right
                        mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in RIGHT_EYEBROW], utils.WHITE, opacity=1 )
                        x_RIGHT = [mesh_coords[p][0] for p in RIGHT_EYEBROW]
                        w_RIGHT = int(max(x_RIGHT) - min(x_RIGHT))
                        y_RIGHT = [mesh_coords[p][1] for p in RIGHT_EYEBROW]
                        h_RIGHT = int(max(y_RIGHT) - min(y_RIGHT))

                        x_mid_pos_RIGHT= max(x_RIGHT) - w_RIGHT - self.posx - self.length 
                        y_mid_pos_RIGHT = max(y_RIGHT) - h_RIGHT + self.posy
                        pos_RIGHT = (int(x_mid_pos_RIGHT), int(y_mid_pos_RIGHT))

                        right_eyebrow = self.right_eyebrow
                        right_eyebrow = cv2.resize(right_eyebrow, (w_RIGHT + self.length , h_RIGHT))
                        #-----------------------------------------------
                        masked = cv2.bitwise_and(copy, mask)
                        out = cv2.bitwise_and(frame,masked)
                        
                        # final_mask = cv2.bitwise_or(mask, final_mask)
                        self.eyebrow_result = cv2.bitwise_and(out, masked)
                        # output = cv2.bitwise_or(masked, final_mask)
                    
                
                if self.cheek_value:
                    if results.multi_face_landmarks:
                        mesh_coords = landmarksDetection(frame, results, False)
                        
                        #-----------left
                        mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in LEFT_CLOWN], utils.WHITE, opacity=1 )
                        c_x_LEFT = [mesh_coords[p][0] for p in LEFT_CLOWN]
                        c_w_LEFT = int(max(c_x_LEFT) - min(c_x_LEFT))
                        c_y_LEFT = [mesh_coords[p][1] for p in LEFT_CLOWN]
                        c_h_LEFT = int(max(c_y_LEFT) - min(c_y_LEFT))

                        c_x_mid_pos_left = max(c_x_LEFT) - c_w_LEFT + self.c_posx 
                        c_y_mid_pos_left = max(c_y_LEFT) - c_h_LEFT + self.c_posy
                        c_pos_LEFT = (int(c_x_mid_pos_left), int(c_y_mid_pos_left))#(round(max(x_LEFT)-w_LEFT/2), round(max(y_LEFT)-h_LEFT/2))
                        
                        left_cheek = self.left_cheek
                        left_cheek = cv2.resize(left_cheek, (c_w_LEFT + self.c_width , c_h_LEFT + self.c_height))        
                        
                        #----------right
                        mask =utils.fillPolyTrans(mask, [mesh_coords[p] for p in RIGHT_CLOWN], utils.WHITE, opacity=1 )
                        c_x_RIGHT = [mesh_coords[p][0] for p in RIGHT_CLOWN]
                        c_w_RIGHT = int(max(c_x_RIGHT) - min(c_x_RIGHT))
                        c_y_RIGHT = [mesh_coords[p][1] for p in RIGHT_CLOWN]
                        c_h_RIGHT = int(max(c_y_RIGHT) - min(c_y_RIGHT))

                        c_x_mid_pos_RIGHT= max(c_x_RIGHT) - c_w_RIGHT - self.c_posx - self.c_width 
                        c_y_mid_pos_RIGHT = max(c_y_RIGHT) - c_h_RIGHT + self.c_posy
                        c_pos_RIGHT = (int(c_x_mid_pos_RIGHT), int(c_y_mid_pos_RIGHT))

                        right_cheek = self.right_cheek
                        right_cheek = cv2.resize(right_cheek, (c_w_RIGHT + self.c_width , c_h_RIGHT  + self.c_height))
                        #-----------------------------------------------
                        masked = cv2.bitwise_and(copy, mask)
                        out = cv2.bitwise_and(frame,masked)
                        
                        
                        # final_mask = cv2.bitwise_or(mask, final_mask)
                        self.cheek_result = cv2.bitwise_and(out, masked)
                        # output = cv2.bitwise_or(masked, final_mask)
                    
                    


                final_mask = ~final_mask
                final_mask = Blur(final_mask)
                final_mask = cv2.bitwise_and(img_frist,final_mask)
                
                

                output = final_mask.copy()
                if self.mouth_result is not None:
                    output = cv2.bitwise_or(self.mouth_result,output)
                if self.skin_result is not None:
                    output = cv2.bitwise_or(self.skin_result,output)
                if self.eyebrow_result is not None:
                    try:
                        image, copy = overlay(output, pos_LEFT[0],pos_LEFT[1], int(w_LEFT + self.length),int(h_LEFT), left_eyebrow)
                        output = cv2.addWeighted(copy, self.eb_mix/100, image, 1-(self.eb_mix/100), 0)
                    except ValueError:
                        pass

                    try:
                        image, copy = overlay(output, pos_RIGHT[0], pos_RIGHT[1], int(w_RIGHT + self.length),int(h_RIGHT), right_eyebrow)
                        output = cv2.addWeighted(copy, self.eb_mix/100, image, 1-(self.eb_mix/100), 0)
                    except ValueError:
                        pass
                if self.cheek_result is not None:
                    try:
                        image, copy = overlay(output, c_pos_LEFT[0],c_pos_LEFT[1], int(c_w_LEFT + self.c_width),int(c_h_LEFT + self.c_height), left_cheek)
                        output = cv2.addWeighted(copy, self.c_mix/100, image, 1-(self.c_mix/100), 0)
                    except ValueError:
                        pass

                    try:
                        image, copy = overlay(output, c_pos_RIGHT[0], c_pos_RIGHT[1], int(c_w_RIGHT + self.c_width),int(c_h_RIGHT + self.c_height), right_cheek)
                        output = cv2.addWeighted(copy, self.c_mix/100, image, 1-(self.c_mix/100), 0)
                    except ValueError:
                        pass


                # output = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
                # output = cv2.fastNlMeansDenoisingColoredMulti(output, 2, 5, None, 4, 7, 35)
                # output = cv2.fastNlMeansDenoisingMulti(output, 2, 5, None, 4, 7, 35)
                # output = cv2.fastNlMeansDenoisingColored(output,None,5,5,7,21)

                
                weighted_img = cv2.cvtColor(output,cv2.COLOR_BGR2RGB)
                weighted_img = cv2.flip(weighted_img,1) #반전
                # print(w,h)
                result_img = QImage(weighted_img.data, w, h, w*c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(result_img)
                self.face_make.setPixmap(pixmap)
        

            cv2.waitKey(1)
            

   #화장기능 활성화
    def makeupshow(self,MainWindow):
        if self.hidden:
            self.face.show()
            self.face_make.show()
            #피부
            self.SkinColor1.show()
            self.SkinColor2.show()
            self.SkinColor3.show()
            self.SkinColor4.show()
            self.SkinColor5.show()
            self.s_Blending.show()
            self.s_UP.show()
            self.s_DOWN.show()

            #입술
            self.m_Blending.show()
            self.m_UP.show()
            self.m_DOWN.show()
            self.MouthColor1.show()
            self.MouthColor2.show()
            self.MouthColor3.show()
            self.MouthColor4.show()
            self.MouthColor5.show()

            #눈썹
            self.e_Blending.show()
            self.e_UP.show()
            self.e_DOWN.show()
            self.dyxSlider.show()
            self.xpos_UP.show()
            self.xpos_DOWN.show()
            self.dyySlider.show()
            self.ypos_UP.show()
            self.ypos_DOWN.show()
            self.lengthSlider.show()
            self.length_UP.show()
            self.length_DOWN.show()
            self.EyeColor1.show()
            self.EyeColor2.show()
            self.EyeColor3.show()
            self.EyeColor4.show()
            self.EyeColor5.show()
            
            #볼터치
            self.c_Blending.show()
            self.c_UP.show()
            self.c_DOWN.show()
            self.c_dyxSlider.show()
            self.c_xpos_UP.show()
            self.c_xpos_DOWN.show()
            self.c_dyySlider.show()
            self.c_ypos_UP.show()
            self.c_ypos_DOWN.show()
            self.c_widthSlider.show()
            self.c_width_UP.show()
            self.c_width_DOWN.show()
            self.c_heightSlider.show()
            self.c_height_UP.show()
            self.c_height_DOWN.show()
            self.CheekColor1.show()
            self.CheekColor2.show()
            self.CheekColor3.show()
            self.CheekColor4.show()

            self.aibtn.show()
            while True:
                self.Make_Up()
                if self.btnHide.isChecked() == True:
                    break
            self.hidden = False
        else:
            self.face.hide()
            self.face_make.hide()
            #피부
            self.SkinColor1.hide()
            self.SkinColor2.hide()
            self.SkinColor3.hide()
            self.SkinColor4.hide()
            self.SkinColor5.hide()
            self.s_Blending.hide()
            self.s_UP.hide()
            self.s_DOWN.hide()

            #입술
            self.m_Blending.hide()
            self.m_UP.hide()
            self.m_DOWN.hide()
            self.MouthColor1.hide()
            self.MouthColor2.hide()
            self.MouthColor3.hide()
            self.MouthColor4.hide()
            self.MouthColor5.hide()

            #눈썹
            self.e_Blending.hide()
            self.e_UP.hide()
            self.e_DOWN.hide()
            self.dyxSlider.hide()
            self.dyySlider.hide()
            self.xpos_UP.hide()
            self.xpos_DOWN.hide()
            self.ypos_UP.hide()
            self.ypos_DOWN.hide()
            self.lengthSlider.hide()
            self.length_UP.hide()
            self.length_DOWN.hide()
            self.EyeColor1.hide()
            self.EyeColor2.hide()
            self.EyeColor3.hide()
            self.EyeColor4.hide()
            self.EyeColor5.hide()

            #볼터치
            self.c_Blending.hide()
            self.c_UP.hide()
            self.c_DOWN.hide()
            self.c_dyxSlider.hide()
            self.c_xpos_UP.hide()
            self.c_xpos_DOWN.hide()
            self.c_dyySlider.hide()
            self.c_ypos_UP.hide()
            self.c_ypos_DOWN.hide()
            self.c_widthSlider.hide()
            self.c_width_UP.hide()
            self.c_width_DOWN.hide()
            self.c_heightSlider.hide()
            self.c_height_UP.hide()
            self.c_height_DOWN.hide()
            self.CheekColor1.hide()
            self.CheekColor2.hide()
            self.CheekColor3.hide()
            self.CheekColor4.hide()
            self.aibtn.hide()
            self.hidden = True
    #AI추천 기능
    def AIfunc(self):
        _, img = self.cap.read()
        tone = personal_color.analysis(img)

        if tone == 'spring':
            self.SkinColor1.setChecked(True)
            self.s_color1_start(MainWindow)
            self.SkinColor1.setChecked(True)
            self.m_color1_start(MainWindow)
        elif tone == 'summer':
            self.SkinColor2.setChecked(True)
            self.s_color2_start(MainWindow)
            self.SkinColor2.setChecked(True)
            self.m_color2_start(MainWindow)
        elif tone == 'fall':
            self.SkinColor3.setChecked(True)
            self.s_color3_start(MainWindow)
            self.SkinColor3.setChecked(True)
            self.m_color3_start(MainWindow)
        elif tone == 'winter':
            self.SkinColor4.setChecked(True)
            self.s_color4_start(MainWindow)
            self.SkinColor4.setChecked(True)
            self.m_color4_start(MainWindow)


    def s_Blendingval(self):                      #슬라이더를 투명도 값에 연동
        self.s_mix = self.s_Blending.value()
    def s_UpVal(self):                            #UP버튼 누르면 슬라이더 값 5씩 증가
        y = self.s_Blending.value()
        y = y + 5
        self.s_Blending.setValue(y)
    def s_DownVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.s_Blending.value()
        y = y - 5
        self.s_Blending.setValue(y)

    def s_color1(self):
        # img = cv2.imread('spring_skin.png')
        # img = cv2.imread('taeyeon.jpg')
        img = cv2.imread('makeup_img\skin\spring_skin.png')
        
        self.skin_ref_img = makeup_ref_img.draw_FACE_OVAL(img, utils.WHITE)
        
        self.skin_value = True
        return self.skin_ref_img
        

    def s_color2(self):
        img = cv2.imread('makeup_img\lip\summer_lip.jpg')
        
        self.skin_ref_img = makeup_ref_img.draw_FACE_OVAL(img, utils.WHITE)
        
        self.skin_value = True
        return self.skin_ref_img
         

    def s_color3(self):
        img = cv2.imread('makeup_img\skin\\fall_skin.jpg')
        
        self.skin_ref_img = makeup_ref_img.draw_FACE_OVAL(img, utils.WHITE)
        
        self.skin_value = True
        return self.skin_ref_img
               

    def s_color4(self):
        img = cv2.imread('makeup_img\skin\winter_skin.jpg')
        
        self.skin_ref_img = makeup_ref_img.draw_FACE_OVAL(img, utils.WHITE)
        
        self.skin_value = True
        return self.skin_ref_img
          

    def s_color5(self):
        img = cv2.imread('makeup_img\skin\summer_skin.png')
        
        self.skin_ref_img = makeup_ref_img.draw_FACE_OVAL(img, utils.WHITE)
        
        self.skin_value = True
        return self.skin_ref_img
           
    def m_Blendingval(self):                      #슬라이더를 투명도 값에 연동
        self.m_mix = self.m_Blending.value()
    def m_UpVal(self):                            #UP버튼 누르면 슬라이더 값 5씩 증가
        y = self.m_Blending.value()
        y = y + 5
        self.m_Blending.setValue(y)
    def m_DownVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.m_Blending.value()
        y = y - 5
        self.m_Blending.setValue(y)

    def m_color1(self):
        img = cv2.imread('makeup_img\lip\spring_lip_orange.jpg')
        
        self.mouth_ref_img = makeup_ref_img.draw_LIPS(img, utils.WHITE)
        self.mouth_value = True
        return self.mouth_ref_img

    def m_color2(self):
        img = cv2.imread('makeup_img\lip\summer_lip.jpg')
        
        self.mouth_ref_img = makeup_ref_img.draw_LIPS(img, utils.WHITE)
        self.mouth_value = True
        return self.mouth_ref_img

    def m_color3(self):
        img = cv2.imread('makeup_img\lip\\fall_lip.png')
        
        self.mouth_ref_img = makeup_ref_img.draw_LIPS(img, utils.WHITE)
        self.mouth_value = True
        return self.mouth_ref_img

        
    def m_color4(self):
        img = cv2.imread('makeup_img\lip\winter_lip.jpg')
        
        self.mouth_ref_img = makeup_ref_img.draw_LIPS(img, utils.WHITE)
        self.mouth_value = True
        return self.mouth_ref_img
    
    def m_color5(self):
        img = cv2.imread('makeup_img\lip\winter_lip2.jpg')
        
        self.mouth_ref_img = makeup_ref_img.draw_LIPS(img, utils.WHITE)
        self.mouth_value = True
        return self.mouth_ref_img

    def e_Blendingval(self):                      #슬라이더를 투명도 값에 연동
        self.eb_mix = self.e_Blending.value()
    def e_UpVal(self):                            #UP버튼 누르면 슬라이더 값 5씩 증가
        y = self.e_Blending.value()
        y = y + 5
        self.e_Blending.setValue(y)
    def e_DownVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.e_Blending.value()
        y = y - 5
        self.e_Blending.setValue(y)

    #눈썹 x위치
    def dyxVal(self):                      #눈썹의 가로 위치 값에 연동
        self.posx = self.dyxSlider.value() - 50
    def xpos_UPVal(self):
        x = self.dyxSlider.value()
        x = x + 5
        self.dyxSlider.setValue(x)
    def xpos_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        x = self.dyxSlider.value()
        x = x - 5
        self.dyxSlider.setValue(x)

    # 눈썹 y위치
    def dyyVal(self):                      #눈썹의 세로 위치 값에 연동
        self.posy = self.dyySlider.value() - 50
    def ypos_UPVal(self):
        y = self.dyySlider.value()
        y = y + 5
        self.dyySlider.setValue(y)
    def ypos_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.dyySlider.value()
        y = y - 5
        self.dyySlider.setValue(y)
    #눈썹의 길이
    def lengthVal(self):                      #눈썹의 길이 값에 연동
        self.length = self.lengthSlider.value()
    def length_UPVal(self):
        y = self.lengthSlider.value()
        y = y + 5
        self.lengthSlider.setValue(y)
    def length_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.lengthSlider.value()
        y = y - 5
        self.lengthSlider.setValue(y)

    
    def e_color1(self):
        # self.img_right_eyebrow = cv2.imread("eyebrow2(right).png",cv2.IMREAD_UNCHANGED)       #img1, img2은 색깔넣은 합성에 사용할 부분, img3는 원본
        # self.img_left_eyebrow = cv2.imread("eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.eyebrow_value = True
        self.left_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.right_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(right).png",cv2.IMREAD_UNCHANGED)
        

    def e_color2(self):
        # self.img_right_eyebrow = cv2.imread("eyebrow2(right).png",cv2.IMREAD_UNCHANGED)       #img1, img2은 색깔넣은 합성에 사용할 부분, img3는 원본
        # self.img_left_eyebrow = cv2.imread("eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.eyebrow_value = True
        self.left_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.right_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(right).png",cv2.IMREAD_UNCHANGED)



    def e_color3(self):
        # self.img_right_eyebrow = cv2.imread("eyebrow2(right).png",cv2.IMREAD_UNCHANGED)       #img1, img2은 색깔넣은 합성에 사용할 부분, img3는 원본
        # self.img_left_eyebrow = cv2.imread("eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.eyebrow_value = True
        self.left_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.right_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(right).png",cv2.IMREAD_UNCHANGED)
        

    def e_color4(self):
        # self.img_right_eyebrow = cv2.imread("eyebrow2(right).png",cv2.IMREAD_UNCHANGED)       #img1, img2은 색깔넣은 합성에 사용할 부분, img3는 원본
        # self.img_left_eyebrow = cv2.imread("eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.eyebrow_value = True
        self.left_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.right_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(right).png",cv2.IMREAD_UNCHANGED)
        

    def e_color5(self):
        # self.img_right_eyebrow = cv2.imread("eyebrow2(right).png",cv2.IMREAD_UNCHANGED)       #img1, img2은 색깔넣은 합성에 사용할 부분, img3는 원본
        # self.img_left_eyebrow = cv2.imread("eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.eyebrow_value = True
        self.left_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(left).png",cv2.IMREAD_UNCHANGED)
        self.right_eyebrow = cv2.imread("makeup_img\eyebrown\eyebrow2(right).png",cv2.IMREAD_UNCHANGED)
        
    

    def c_Blendingval(self):                      #슬라이더를 투명도 값에 연동
        self.c_mix = self.c_Blending.value()
    def c_UpVal(self):                            #UP버튼 누르면 슬라이더 값 5씩 증가
        y = self.c_Blending.value()
        y = y + 5
        self.c_Blending.setValue(y)
    def c_DownVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.c_Blending.value()
        y = y - 5
        self.c_Blending.setValue(y)

    #볼터치 x위치
    def c_dyxVal(self):                      #눈썹의 가로 위치 값에 연동
        self.c_posx = self.c_dyxSlider.value() - 50
    def c_xpos_UPVal(self):
        x = self.c_dyxSlider.value()
        x = x + 5
        self.c_dyxSlider.setValue(x)
    def c_xpos_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        x = self.c_dyxSlider.value()
        x = x - 5
        self.c_dyxSlider.setValue(x)


    # 볼터치 y위치
    def c_dyyVal(self):                      #볼터치의 세로 위치 값에 연동
        self.c_posy = self.c_dyySlider.value() - 50
    def c_ypos_UPVal(self):
        y = self.c_dyySlider.value()
        y = y + 5
        self.c_dyySlider.setValue(y)
    def c_ypos_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.c_dyySlider.value()
        y = y - 5
        self.c_dyySlider.setValue(y)

    #볼터치의 가로
    def c_widthVal(self):                      #볼터치의 크기 값에 연동
        self.c_width = self.c_widthSlider.value()
    def c_width_UPVal(self):
        y = self.c_widthSlider.value()
        y = y + 5
        self.c_widthSlider.setValue(y)
    def c_width_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.c_widthSlider.value()
        y = y - 5
        self.c_widthSlider.setValue(y)
    #볼터치 세로
    def c_heightVal(self):                      #볼터치의 크기 값에 연동
        self.c_height = self.c_heightSlider.value()
    def c_height_UPVal(self):
        y = self.c_heightSlider.value()
        y = y + 5
        self.c_heightSlider.setValue(y)
    def c_height_DOWNVal(self):                          #DOWN버튼 누르면 슬라이더값 5씩 감소
        y = self.c_heightSlider.value()
        y = y - 5
        self.c_heightSlider.setValue(y)


    def c_color1(self):
        self.cheek_value = True
        self.left_cheek = cv2.imread("cheek\circle_100alp.png",cv2.IMREAD_UNCHANGED)
        self.right_cheek = cv2.imread("cheek\circle_100alp.png",cv2.IMREAD_UNCHANGED)

    def c_color2(self):
        self.cheek_value = True
        self.left_cheek = cv2.imread("cheek\eyeunder.png", cv2.IMREAD_UNCHANGED)
        self.right_cheek = cv2.flip(self.left_cheek, 1)         #좌우반전

    def c_color3(self):
        self.cheek_value = True
        self.left_cheek = cv2.imread("cheek\long.png", cv2.IMREAD_UNCHANGED)
        self.right_cheek = cv2.flip(self.left_cheek, 1)         #좌우반전

    def c_color4(self):
        self.cheek_value = True
        self.left_cheek = cv2.imread("cheek\short.png", cv2.IMREAD_UNCHANGED)
        self.right_cheek = cv2.flip(self.left_cheek, 1)         #좌우반전


    def openSaveWindow(self):
        skin = self.SkincolorCheck()
        mouth = self.MouthcolorCheck()
        eye = self.EyecolorCheck()
        global savelst
        savelst = [skin, mouth, eye]  
        self.saveWindow.show()
            
    
    def openLoadWindow(self):
        self.loadWindow.show()
        self.event_loop.exec_()
        a = loadlst[0]
        b = loadlst[1]
        c = loadlst[2]
        # print(a,b,c)
        if a == 'self.SkinColor1':
            self.SkinColor1.setChecked(True)
            self.s_color1_start(MainWindow)
        elif a == 'self.SkinColor2':
            self.SkinColor2.setChecked(True)
            self.s_color2_start(MainWindow)
        elif a == 'self.SkinColor3':
            self.SkinColor3.setChecked(True)
            self.s_color3_start(MainWindow)
        elif a == 'self.SkinColor4':
            self.SkinColor4.setChecked(True)
            self.s_color4_start(MainWindow)
        elif a == 'self.SkinColor5':
            self.SkinColor5.setChecked(True)
            self.s_color5_start(MainWindow)

        if b == 'self.MouthColor1':
            self.SkinColor1.setChecked(True)
            self.m_color1_start(MainWindow)
        elif b == 'self.MouthColor2':
            self.MouthColor2.setChecked(True)
            self.m_color2_start(MainWindow)
        elif b == 'self.MouthColor3':
            self.SkinColor3.setChecked(True)
            self.m_color3_start(MainWindow)
        elif b == 'self.MouthColor4':
            self.MouthColor4.setChecked(True)
            self.m_color4_start(MainWindow)
        elif b == 'self.MouthColor5':
            self.MouthColor5.setChecked(True)
            self.m_color5_start(MainWindow)

        if c == 'self.EyeColor1':
            self.EyeColor1.setChecked(True)
            self.e_color1_start(MainWindow)
        elif c == 'self.EyeColor2':
            self.e_color2_start(MainWindow)
            self.EyeColor2.setChecked(True)
        elif c == 'self.EyeColor3':
            self.EyeColor3.setChecked(True)
            self.e_color3_start(MainWindow)
        elif c == 'self.EyeColor4':
            self.EyeColor4.setChecked(True)
            self.e_color2_start(MainWindow)
        elif c == 'self.EyeColor5':
            self.EyeColor5.setChecked(True)
            self.e_color3_start(MainWindow)
    
        
        
    def SkincolorCheck(self):
        if self.SkinColor1.isChecked():
            skin = "self.SkinColor1"
            return skin
        elif self.SkinColor2.isChecked():
            skin = "self.SkinColor2"
            return skin
        elif self.SkinColor3.isChecked():
            skin = "self.SkinColor3"
            return skin
        elif self.SkinColor4.isChecked():
            skin = "self.SkinColor4"
            return skin
        elif self.SkinColor5.isChecked():
            skin = "self.SkinColor5"
            return skin

    def MouthcolorCheck(self):
        if self.MouthColor1.isChecked():
            mouth= "self.MouthColor1"
            return mouth
        elif self.MouthColor2.isChecked():
            mouth = "self.MouthColor2"
            return mouth
        elif self.MouthColor3.isChecked():
            mouth= "self.MouthColor3"
            return mouth
        elif self.MouthColor4.isChecked():
            mouth= "self.MouthColor4"
            return mouth
        elif self.MouthColor5.isChecked():
            mouth= "self.MouthColor5"
            return mouth

    def EyecolorCheck(self):
        if self.EyeColor1.isChecked():
            eye= "self.EyeColor1"
            return eye
        elif self.EyeColor2.isChecked():
            eye= "self.EyeColor2"
            return eye
        elif self.EyeColor3.isChecked():
            eye= "self.EyeColor3"
            return eye
        elif self.EyeColor4.isChecked():
            eye= "self.EyeColor4"
            return eye
        elif self.EyeColor5.isChecked():
            eye= "self.EyeColor5"
            return eye

        


    #----------------------------------------------------------------------------------------------------
    #------------------------ 쓰레드 ---------------------------------------------------------------------
    #----------------------------------------------------------------------------------------------------
    

    #Set_time을 쓰레드로 사용
    def time_start(self,MainWindow):
        thread=Thread(target=self.set_time,args=(self,))
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    #weather_icon을 쓰레드로 사용
    def weather_start(self,MainWindow):
        thread=Thread(target=self.weather_icon,args=(self,))
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    #화장 관련 UI
    def makeup_start(self,MainWindow):
        thread=Thread(target=self.makeupshow,args=(self,))
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()
    
    #피부 색깔 변경 기능들을 스레드로 사용--------------------------------------------------------------------
    def s_color1_start(self,MainWindow):
        self.SkinColor2.setChecked(False)
        self.SkinColor5.setChecked(False)
        self.SkinColor3.setChecked(False)
        self.SkinColor4.setChecked(False)
        self.SkinColor5.setChecked(False)
        # print(self.SkinColor5.isChecked())
        thread=Thread(target=self.s_color1)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def s_color2_start(self,MainWindow):
        self.SkinColor1.setChecked(False)
        self.SkinColor5.setChecked(False)
        self.SkinColor3.setChecked(False)
        self.SkinColor4.setChecked(False)
        thread=Thread(target=self.s_color2)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()
        
    def s_color3_start(self,MainWindow):
        self.SkinColor1.setChecked(False)
        self.SkinColor2.setChecked(False)
        self.SkinColor5.setChecked(False)
        self.SkinColor4.setChecked(False)
        thread=Thread(target=self.s_color3)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def s_color4_start(self,MainWindow):
        self.SkinColor1.setChecked(False)
        self.SkinColor2.setChecked(False)
        self.SkinColor3.setChecked(False)
        self.SkinColor5.setChecked(False)
        thread=Thread(target=self.s_color4)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def s_color5_start(self,MainWindow):
        self.SkinColor1.setChecked(False)
        self.SkinColor2.setChecked(False)
        self.SkinColor3.setChecked(False)
        self.SkinColor4.setChecked(False)
        thread=Thread(target=self.s_color5)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()
    
    #입술 색깔 변경 기능들을 스레드로 사용--------------------------------------------------------------------
    def m_color1_start(self,MainWindow):
        self.MouthColor2.setChecked(False)
        self.MouthColor3.setChecked(False)
        self.MouthColor4.setChecked(False)
        self.MouthColor5.setChecked(False)
        thread=Thread(target=self.m_color1)
        # thread.daemon=True #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def m_color2_start(self,MainWindow):
        self.MouthColor1.setChecked(False)
        self.MouthColor3.setChecked(False)
        self.MouthColor4.setChecked(False)
        self.MouthColor5.setChecked(False)
        thread=Thread(target=self.m_color2)
        # thread.daemon=True #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def m_color3_start(self,MainWindow):
        self.MouthColor1.setChecked(False)
        self.MouthColor2.setChecked(False)
        self.MouthColor4.setChecked(False)
        self.MouthColor5.setChecked(False)
        thread=Thread(target=self.m_color3)
        # thread.daemon=True #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def m_color4_start(self,MainWindow):
        self.MouthColor1.setChecked(False)
        self.MouthColor2.setChecked(False)
        self.MouthColor3.setChecked(False)
        self.MouthColor5.setChecked(False)
        thread=Thread(target=self.m_color4)
        # thread.daemon=True #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def m_color5_start(self,MainWindow):
        self.MouthColor1.setChecked(False)
        self.MouthColor2.setChecked(False)
        self.MouthColor3.setChecked(False)
        self.MouthColor4.setChecked(False)
        thread=Thread(target=self.m_color5)
        # thread.daemon=True #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()
    
    #눈썹
    def e_color1_start(self, MainWindow):
        self.EyeColor2.setChecked(False)
        self.EyeColor3.setChecked(False)
        self.EyeColor4.setChecked(False)
        self.EyeColor5.setChecked(False)
        thread=Thread(target=self.e_color1)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def e_color2_start(self, MainWindow):
        self.EyeColor1.setChecked(False)
        self.EyeColor3.setChecked(False)
        self.EyeColor4.setChecked(False)
        self.EyeColor5.setChecked(False)
        thread=Thread(target=self.e_color2)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def e_color3_start(self, MainWindow):
        self.EyeColor1.setChecked(False)
        self.EyeColor2.setChecked(False)
        self.EyeColor4.setChecked(False)
        self.EyeColor5.setChecked(False)
        thread=Thread(target=self.e_color3)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def c_color1_start(self, MainWindow):
        self.CheekColor2.setChecked(False)
        self.CheekColor3.setChecked(False)
        self.CheekColor4.setChecked(False)
        thread=Thread(target=self.c_color1)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()
    
    def c_color2_start(self, MainWindow):
        self.CheekColor1.setChecked(False)
        self.CheekColor3.setChecked(False)
        self.CheekColor4.setChecked(False)
        thread=Thread(target=self.c_color2)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()

    def c_color3_start(self, MainWindow):
        self.CheekColor1.setChecked(False)
        self.CheekColor2.setChecked(False)
        self.CheekColor4.setChecked(False)
        thread=Thread(target=self.c_color3)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()
        
    def c_color4_start(self, MainWindow):
        self.CheekColor1.setChecked(False)
        self.CheekColor2.setChecked(False)
        self.CheekColor3.setChecked(False)
        thread=Thread(target=self.c_color4)
        thread.daemon=False #프로그램 종료시 프로세스도 함께 종료 (백그라운드 재생 X)
        thread.start()



#-------------메인---------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()

    ui = Ui_MainWindow()

    ui.setupUi(MainWindow)
    # ui.button(MainWindow)

    ui.time_start(MainWindow) #time thread
    ui.weather_start(MainWindow) #weather thread
    ui.makeup_start(MainWindow)
    # ui.s_color1_start(MainWindow)
    # ui.m_color1_start(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())