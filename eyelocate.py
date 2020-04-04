#By: Owen Dolan

import cv2
import dlib
from djitellopy import Tello
import time

class telloTrack(object):

    def __init__(self):
            self.tello = Tello()

    def telloflightcheck(self):
        if not self.tello.connect():
            print("Tello not connected")
            return
        else: return True

    def startupdrone(self):
        if self.telloflightcheck()== True:
            self.tello.takeoff()

    def telloFly(self, direction):
        #just gets battery; seems to help change blinking light to green
        self.tello.get_battery()

        time.sleep(5)
        #self.tello.move_up(50)

        if self.telloflightcheck() == True:
            #checks if drone needs to move to center itself in the frame
            if direction == "Right":
                self.tello.rotate_clockwise(20)
            if direction == "Left":
                self.tello.rotate_counter_clockwise(20)
        else:
            print("Drone Not connected: Direction Command Not Accepted")

    def getEye(self):
        #gets video stream from webcam
        cap = cv2.VideoCapture(0)

        #loads in dlib haar cascade that tracks face with facial mapping landmarks
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

        #gets face coordinates to help locate eye
        def midpoint(p1 ,p2):
            return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

        showstream = False
        looking = "Not Found"

        #starts flying the drone if it is connected
        self.startupdrone()

        #forever loop that performs functions on livestream video data
        while True:

            if showstream == True:
                print("got here")
                frame_read = self.tello.get_frame_read()
                frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
                newframe = frame_read.frame
                cv2.imshow('Owen Tello Stream', newframe)

            _, frame = cap.read()
            #grayscales the image for computation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:

                #finds the landmarks on the webcam video feed
                landmarks = predictor(gray, face)
                left_point = (landmarks.part(36).x, landmarks.part(36).y)
                right_point = (landmarks.part(39).x, landmarks.part(39).y)
                center_top = midpoint(landmarks.part(37), landmarks.part(38))
                center_bottom = midpoint(landmarks.part(41), landmarks.part(40))

                #draws green lines along axis of eyes
                cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
                cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

                #calculates roi image view based off of dlib landmarks
                xdist = abs(left_point[0]-right_point[0])
                ydist = abs(center_top[1]-center_bottom[1])

                #this is the small image shown calculation grayscale version
                smalleye = gray[center_top[1]:center_top[1]+ydist, left_point[0]:left_point[0]+xdist]
                tinyeyelook = frame[center_top[1]:center_top[1] + ydist, left_point[0]:left_point[0] + xdist]

                #gets middle of eye regardless of where pupil is looking and draws red dot there
                eyemidx = int((left_point[0]+right_point[0])/2)
                eyemidy = int((center_top[1]+center_bottom[1])/2)
                cv2.circle(frame, (eyemidx, eyemidy), 2, (20, 40, 255), -1)

                #searches for circles in the eye for iris
                eyeball = cv2.HoughCircles(smalleye, cv2.HOUGH_GRADIENT, 1, 200, param1=200, param2=1, minRadius=5,maxRadius=35)

                #Draws the circles within the eye
                try:
                    for i in eyeball[0, :]:
                        # draw the center of the circle as a prediction within small eye image
                        cv2.circle(tinyeyelook, (i[0], i[1]), 2, (255, 255, 255), 3)
                        eyedisfromcent = int((eyemidx-left_point[0])-i[0])
                        #print(eyedisfromcent)

                        if eyedisfromcent>15:
                            print("Right")
                            looking = "Right"
                            #self.telloFly("Right")

                        if eyedisfromcent<-15:
                            print("Left")
                            looking = "Left"
                            #self.telloFly("Left")

                        if eyedisfromcent>-15 or eyedisfromcent<15:
                            print("Straight")
                            #looking = "Straight"

                except Exception as e:
                    pass

                #resize eye
                smalllook = cv2.resize(tinyeyelook, (int(tinyeyelook.shape[1] * 5), int(tinyeyelook.shape[0] * 5)),interpolation=cv2.INTER_AREA)
                frame[0:smalllook.shape[0], 0:smalllook.shape[1]] = smalllook

            #displays and flips the two live video streams
            final = cv2.flip(frame, 1)

            #Displaying onscreen stats for GUI
            cv2.putText(final, "Direction Looking: "+looking, (930, 130), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (200, 0, 0),3, cv2.LINE_AA)
            if self.telloflightcheck() == True:
                cv2.putText(final, "Tello Connected", (930, 155), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(200, 0, 0), 3, cv2.LINE_AA)
            else:
                cv2.putText(final, "Tello Not Connected", (930, 155), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1,(200, 0, 0), 3, cv2.LINE_AA)

            #cv2.imshow("Frame", final)

            #this will resize the large cv2 display to fit in tkinter window
            width = int(final.shape[1] * 90 / 100)
            height = int(final.shape[0] * 90 / 100)
            dim = (width, height)
            smallfinal = cv2.resize(final, dim, interpolation=cv2.INTER_AREA)
            cv2.imshow('Webcam', smallfinal)

            key = cv2.waitKey(1)
            if key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        if self.telloflightcheck() == True:
            self.tello.land()

def main():
    dude = telloTrack()
    dude.getEye()


if __name__ == '__main__':
    main()
