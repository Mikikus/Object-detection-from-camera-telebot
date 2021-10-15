import cv2
import numpy as np
import telebot
from threading import Thread
from tkinter import *
from tkinter import messagebox
import os

class UserInfo:
    isPersonHere = False
    role = ""
    token = ""
    camera = ""

user = UserInfo()

root = Tk()
root.title("Configuration")

class Settings:
    role_entry = Entry(textvariable=user.role)
    token_entry = Entry(textvariable=user.token)
    camera_entry = Entry(textvariable=user.camera)

settings = Settings()

#basic inputs and configuration window
def completeInfo():
    user.role = str(settings.role_entry.get())
    user.token = str(settings.token_entry.get())
    user.camera = str(settings.camera_entry.get())
    root.quit()

def setPassToString():
    user.isCameraLinkString = True

def setPassToInteger():
    user.isCameraLinkString = False

def onClose():
    os._exit(0)

def setSettingsWindow():
    role_label = Label(text="Введите роль:")
    token_label = Label(text="Введите токен:")
    camera_label = Label(text="Камера:")

    role_label.grid(row=0, column=0, sticky="w")
    token_label.grid(row=1, column=0, sticky="w")
    camera_label.grid(row=2, column=0, sticky="w")

    settings.role_entry.grid(row=0, column=1, padx=5, pady=5)
    settings.token_entry.grid(row=1, column=1, padx=5, pady=5)
    settings.camera_entry.grid(row=2, column=1, padx=5, pady=5)

    message_button = Button(text="OK", command=completeInfo)
    message_button.grid(row=4, column=1, padx=5, pady=5, sticky="e")

    exit_button = Button(text="Выход", command=onClose)
    exit_button.grid(row=4, column=0, padx=5, pady=5, sticky="e")

    user.isCameraLinkString = BooleanVar()
    user.isCameraLinkString.set(1)

    root.protocol('WM_DELETE_WINDOW', onClose)
    root.mainloop()
    if (user.camera == "") and user.role == "" or user.token == "":
        messagebox.showinfo("Неверное заполнение", "Заполните все поля!")
        setSettingsWindow()

setSettingsWindow()
root.destroy()

#Declare bot
bot = telebot.TeleBot(user.token)

#Message handler

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/speaker":
        if user.isPersonHere:
            bot.send_message(message.from_user.id, "Да, " + user.role + " здесь.")
        else:
            bot.send_message(message.from_user.id, user.role + " еще не здесь.")

#Polling all the time for messages
if __name__ == '__main__':
    def pol():
        bot.polling(none_stop=True, interval=0)

#onChange trackBar
if __name__ == '__main__':
    def nothing(*arg):
        pass

#Open video from webcam/source
if user.camera.isdigit():
    cap = cv2.VideoCapture(int(user.camera))
else:
    cap = cv2.VideoCapture(user.camera)


if not cap.isOpened():
    messagebox.showinfo("Ошибка", "Не удалось открыть видео")
    onClose()

#Settings window and trackbars
if __name__ == '__main__':
    def createTrackBar():
        cv2.namedWindow("Control HSV", cv2.WINDOW_AUTOSIZE)

        cv2.createTrackbar("Low H", "Control HSV", 0, 255, nothing)
        cv2.createTrackbar("High H", "Control HSV", 255, 255, nothing)

        cv2.createTrackbar("Low S", "Control HSV", 0, 255, nothing)
        cv2.createTrackbar("High S", "Control HSV", 255, 255, nothing)

        cv2.createTrackbar("Low V", "Control HSV", 0, 255, nothing)
        cv2.createTrackbar("High V", "Control HSV", 255, 255, nothing)

        cv2.createTrackbar("Area", "Control HSV", 0, 10000, nothing)


if __name__ == '__main__':
    def processVideo():
        createTrackBar()
        moved = False
        while True:
            # Read frames and convert to HSV
            flag, frameBGR = cap.read()
            if not flag:
                os._exit(0)

            frameHSV = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2HSV)

            #Get trackbar positions
            lowH = cv2.getTrackbarPos("Low H", "Control HSV")
            highH = cv2.getTrackbarPos("High H", "Control HSV")

            lowS = cv2.getTrackbarPos("Low S", "Control HSV")
            highS = cv2.getTrackbarPos("High S", "Control HSV")

            lowV = cv2.getTrackbarPos("Low V", "Control HSV")
            highV = cv2.getTrackbarPos("High V", "Control HSV")

            h_min = np.array((lowH, lowS, lowV), np.uint8)
            h_max = np.array((highH, highS, highV), np.uint8)

            #Threshold image
            frameThresholded = cv2.inRange(frameHSV, h_min, h_max)

            #Dilate thresholded image
            kernel = np.ones((5, 5), 'uint8')
            frameThresholded = cv2.dilate(frameThresholded, kernel)

            # Creating contour to color
            contours, hierarchy = cv2.findContours(frameThresholded,
                                                   cv2.RETR_TREE,
                                                   cv2.CHAIN_APPROX_SIMPLE)

            for pic, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                area_value = cv2.getTrackbarPos("Area", "Control HSV")
                if (area > area_value):
                    x, y, w, h = cv2.boundingRect(contour)
                    frameBGR = cv2.rectangle(frameBGR, (x, y),
                                               (x + w, y + h),
                                               (0, 0, 255), 5)
                    user.isPersonHere = True
                else:
                    user.isPersonHere = False

            #display windows
            cv2.imshow("Thresholded", frameThresholded)
            cv2.imshow("Original", frameBGR)

            if not moved:
                cv2.moveWindow("Thresholded", 900, 300)
                cv2.moveWindow("Original", 410, 300)
                cv2.moveWindow("Control HSV", 90, 300)
                moved = True

            if cv2.waitKey(10) == 27:
                break

#Parallel start of video and bot
thread1 = Thread(target=processVideo)
thread2 = Thread(target=pol)

#Start threads
thread1.start()
thread2.start()

#Stop threads
thread1.join()
thread2.join()

#Close all
cap.release()
cv2.destroyAllWindows()