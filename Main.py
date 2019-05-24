#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 16:33:55 2019

@author: csteed
"""

import cv2
import numpy as np
from collections import deque

greenLower = (6, 120, 100)
greenUpper =  (64, 255, 255)

greenLower = (8, 12, 20)
greenUpper =  (70, 255, 100)

fps=30;
period=1/fps;

video = cv2.VideoCapture('Blue_ball_straight.mp4')
#video = cv2.VideoCapture('ball_video.mp4')
frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
frameWidth = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
frameHeight = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

buf = np.empty((frameCount, frameHeight, frameWidth, 3), np.dtype('uint8'))

fc = 0
ret = True

while (fc < frameCount  and ret):
    ret, buf[fc] = video.read()
    fc += 1

points = deque(maxlen=len(buf))

video.release() 
i=0; 
while (i<len(buf)):
    
    currentFrame = buf[i];
    i=i+1;
    
    
    blurred = cv2.GaussianBlur(currentFrame, (11, 11), 0);
    hsv = cv2.cvtColor(blurred, cv2.COLOR_RGB2HSV);
    mask = cv2.inRange(hsv, greenLower, greenUpper);
    mask = cv2.erode(mask, None, iterations=2);
    mask = cv2.dilate(mask, None, iterations=2);
    ballContours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE);

    ballContours = ballContours[-2]; #extracting contours;

    
    if len(ballContours) > 0:
        largestContour = max(ballContours, key=cv2.contourArea);
        ((circleX, circleY),circleRadius) = cv2.minEnclosingCircle(largestContour);
        cv2.circle(currentFrame, (int(circleX),int(circleY)), int(circleRadius),(0,255,255),2)
        points.appendleft((int(circleX),int(circleY)))
        #print("points: ",points);
    #Draw trail line    
    for j in range(1,len(points)):
        cv2.line(currentFrame,points[j - 1], points[j], (0,0,255), 3)
        
    cv2.namedWindow('frame 10');
    cv2.imshow('frame 10', currentFrame);
    cv2.namedWindow('edited')
    cv2.imshow('edited', hsv)
    cv2.namedWindow('mask')
    cv2.imshow('mask', mask)
    keyPressed = cv2.waitKey(200)
    if (keyPressed == ord('q')):
        break;
    if (keyPressed == ord('p')):
        cv2.waitKey(0);
cv2.destroyAllWindows()



print("Filter entered")

import numpy as np;
import matplotlib.pyplot as plot;
import kalman as kf; 
    
def backPass(F, P_neg, P_pos, x_neg, x_pos):
    
    x_new = np.zeros(np.shape(x_pos));
    x_new[:,-1] = x_pos[:,-1]
    P_new = np.zeros(np.shape(P_neg));
    P_new[-1] = P_pos[-1]
    t = np.size(x_pos,1);
    
    for i in range(t-1,0,-1):
        L = P_pos[i-1].dot(F.T).dot(np.linalg.inv(P_neg[i]));
        x_new[:,i-1] = x_pos[:,i-1] + L.dot(x_new[:,i]-x_neg[:,i]);
        P_new[i-1] = P_pos[i-1] + L.dot(P_new[i]-P_neg[i]).dot(L.T);
    return (P_new,x_new);

T = 1/30;   
F = np.array([[1, T],[0, 1]]);np.zeros(np.shape(F));
F = np.block([
        [F, np.zeros(np.shape(F))],
        [np.zeros(np.shape(F)),F]
        ]);    
Gamma = np.array([[pow(T,2)/2],[T]]);
Gamma = np.block([
        [Gamma, np.zeros(np.shape(Gamma))],
        [np.zeros(np.shape(Gamma)),Gamma]
        ]);    
H = np.array([[1,0,0,0],[0,0,1,0]]);   
z = np.array(points).T
tmax = len(z[1]);
x_true = np.zeros([4,tmax]);
x_estimate = np.zeros(np.shape(x_true));   
x_estimate[:,0] = np.array([z[0][0],1,z[1][0],0])   
pk = np.eye(np.size(x_true,0));
R = 0.002;
Q = np.eye(2)*0.000001;    
t = np.linspace(0,tmax*T,tmax)

for i in range(1,tmax):
    x_true[:,i] = F.dot(x_true[:,i-1]) +Gamma.dot(np.random.normal(0,np.sqrt(Q)).dot(np.ones([2,1]))).T    
    #z[:,i] = H.dot(x_true[:,i]) +np.random.normal(0,np.sqrt(R))
    
    #time update
    x_priori = np.dot(F,x_estimate[:,i-1]);
    pk = F.dot(pk).dot(F.T) + Gamma.dot(Q).dot(Gamma.T)
    K = pk.dot(H.T).dot(np.linalg.inv(H.dot(pk).dot(H.T) + R))
    #K = pk.dot(H.T)/((H.dot(pk).dot(H.T) + R))
    #measurement update
    [pk,x_estimate[:,i]] = kf.measurementUpdate(pk,K,x_priori,H,z[:,i])
    
#[P_backpass,x_backpass] = backPass(F,P_negative,P_positive,x_priori,x_estimate)
plot.figure(1)
plot.subplot(1,2,1)
plot.title("Position")
plot.plot(z[0,:],z[1,:],'r.'
          ,x_estimate[0,:],x_estimate[2,:],'b')
plot.legend(["measurements",'position estimate'])

plot.subplot(1,2,2)
plot.title("Velocity")
plot.plot(t,x_estimate[1,:],'b',
          t,x_estimate[3,:],'r')
    
