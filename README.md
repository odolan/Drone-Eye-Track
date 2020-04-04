# Drone-Eye-Track

This project uses pretrained facial landmarks to determine the users left eye. Using the calculated zone, the program applies the open-cv hough circle detector to look for the individuals pupil. While this program can be addapted to use the eye tracking for any purpose, I used the DJI tello drone API to allow eye movements to control the direction or any flight attribute for the drone. 

Please contact me if you have any questions on usage. 

Additional files needed: https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat 

example of the GUI that shows the eye tracking
![Image Failed to Load](exampleImage.png)

