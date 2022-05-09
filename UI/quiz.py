import cv2
import threading
import random

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5 import QtGui

from instance import Instance
from UI.result import Result


form_quiz = uic.loadUiType("./UI/quiz.ui")[0]


class QuizWindow(QDialog, QWidget, form_quiz):
    def __init__(self):
        super(QuizWindow, self).__init__()
        self.initUi()

        self.btn_learn.clicked.connect(self.btn_learing_function)
        self.btn_quiz.clicked.connect(self.btn_quiz_function)
        self.btn_mode.clicked.connect(self.btn_mode_function)
        self.progressBar.valueChanged.connect(self.printValue)
        self.btn_pass.clicked.connect(self.btn_pass_function)

        self.progressBar.setRange(0, 10)
        self.progressBar.reset()
        self.timerVar = QTimer()
        self.timerVar.setInterval(1000)
        self.timerVar.timeout.connect(self.progressBarTimer)
        # self.timerVar.start()

        self.running = False
        self.start()

        self.page = 3
        self.page_cur = 0
        self.lb_page_all.setText(str(self.page))
        self.lb_page.setText("")

        self.select_words()
        self.nth_quiz = -1

    def initUi(self):
        self.setupUi(self)

    def btn_learing_function(self):
        self.running = False
        self.page_reset()
        Instance.window.changeWindow("quiz", "learning")

    def btn_quiz_function(self):
        self.page_reset()
        Instance.window.changeWindow("quiz", "quiz")

    def btn_mode_function(self):
        self.running = False
        self.page_reset()
        Instance.window.changeWindow("quiz", "mode")

    def btn_pass_function(self):
        if self.page_cur == 0:
            self.page_cur = 1
            self.progressBar.reset()
            self.btn_pass.setText("다음 단어로")
            self.lb_page.setText(str(self.page_cur))
            self.timerVar.start()
            self.nth_quiz += 1
            self.lb_question.setText(self.selected_words[self.nth_quiz])
        else:
            self.next_word()

    def select_words(self):
        self.selected_words = random.sample(
            list(Result.quiz_words.keys())[1:], 3)
        Result.words = self.selected_words
        Result.check = [False for i in range(len(self.selected_words))]

    def progressBarTimer(self):
        self.time = self.progressBar.value()
        self.time += 1
        self.progressBar.setValue(self.time)
        self.lb_ncount.setText(str(10-self.progressBar.value()))

        # ProgressBar의 값이 최댓값 이상이 되면 Timer를 중단시켜 ProgressBar의 값이 더이상 증가하지 않게 합니다.
        if self.time > self.progressBar.maximum():
            self.next_word()

    def page_reset(self):
        self.page_cur = 0
        self.timerVar.stop()
        self.progressBar.reset()
        self.lb_page.setText("")
        self.btn_pass.setText("시작")
        self.nth_quiz = -1
        self.select_words()
        self.lb_question.setText("단어")

    def next_word(self):
        if self.page_cur == self.page:  # 단어 퀴즈 끝나면
            self.page_reset()
            Instance.window.changeWindow("quiz", "note")
        else:
            self.time = 0
            self.progressBar.setValue(self.time)
            self.page_cur += 1
            self.lb_page.setText(str(self.page_cur))
            self.lb_ncount.setText("10")
            self.nth_quiz += 1
            self.lb_question.setText(self.selected_words[self.nth_quiz])

    def printValue(self):
        # print(self.progressBar.value())
        return

    def camera_run(self):
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.lb_camera.resize(width, height)
        while self.running:
            ret, img = cap.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                h, w, c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c,
                                    QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.lb_camera.setPixmap(pixmap)
            else:
                #QtWidgets.QMessageBox.about(win, "Error", "Cannot read frame.")
                print("cannot read frame.")
                break
        cap.release()

    def start(self):
        self.running = True
        th = threading.Thread(target=self.camera_run)
        th.start()
