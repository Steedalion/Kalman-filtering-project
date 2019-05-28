#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 24 09:20:46 2019

@author: csteed
"""
import kalman as kf;
import numpy as np;
import matplotlib.pyplot as plot;
import pykalman as pkal;

T = 1;

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

z = np.zeros([2,100])

tmax = len(z[1]);
x_true = np.zeros([4,tmax]);
nx = np.size(x_true,0);
x_estimate = np.zeros(np.shape(x_true));
x_priori = np.zeros(np.shape(x_true));
x_smooth = np.zeros(np.shape(x_true));
P_negative = np.zeros((tmax,nx,nx));
P_positive = np.zeros((tmax,nx,nx));

x_true[:,0] = np.array([1,1,0,1.5]);
x_estimate[:,0] = np.array(x_true[:,0]-1)
P_positive[0] = np.eye(nx)*1000;
P_negative[0] = np.eye(nx)*1;
sigmav =np.diag([1,1])*30;
sigmaW =np.diag([1,1])*1;
R = sigmav**2;
Q = sigmaW**2;

t = np.linspace(0,tmax*T,tmax)

for i in range(1,tmax):
    x_true[:,i] = F.dot(x_true[:,i-1]) +Gamma.dot(np.random.normal(0,np.sqrt(Q)).dot(np.ones([2,1]))).T    
    z[:,i] = H.dot(x_true[:,i]) + np.random.normal(0,1,2).dot(sigmav)
    
    #time update
   # x_priori[:,i] = np.dot(F,x_estimate[:,i-1]);
    #P_negative[i] = F.dot(P_positive[i-1]).dot(F.T) + Gamma.dot(sigmaW).dot(Gamma.T)
        
    K = P_negative[i].dot(H.T).dot(np.linalg.inv(H.dot(P_negative[i]).dot(H.T) + R))
    [x_priori[:,i], P_negative[i], K] = kf.timeUpdate(
            F, H, R, Q, Gamma, x_estimate[:,i-1], P_positive[i-1])
    
    #K = P_positive.dot(H.T)/((H.dot(P_positive).dot(H.T) + R))
    #P_positive[i] = (np.eye(np.size(K.dot(H),0)) - K.dot(H)).dot(P_negative[i])
    #x_estimate[:,i] = x_priori[:,i] + K.dot(z[:,i] - H.dot(x_priori[:,i]))
    [P_positive[i], x_estimate[:,i]] = kf.measurementUpdate(P_negative[i], K, x_priori[:,i],H,z[:,i])
    
#    x_smooth[:,i-1] = x_estimate[:,i-1]
#    K_smooth =  P_positive[i-1].dot(F.T).dot(np.linalg.pinv(P_negative[i]));
#    x_smooth [:,i-1] = x_estimate[:,i-1] + K_smooth.dot(x_smooth[:,i] -x_priori[:,i])

#x_smooth[:,49] = x_estimate[:,49]
#x_estimate[:,-1] = x_true[:,-1]
[P_backpass,x_backpass] = kf.backpassLib(F, x_estimate, P_filt=P_positive, x_pred=x_priori, P_pred=P_negative)

#[x_s,P_s,z] = pkal.standard._smooth(F, x_estimate.T,P_positive, x_priori.T,P_negative)

#def _smooth(transition_matrices, filtered_state_means,
#            filtered_state_covariances, predicted_state_means,
#            predicted_state_covariances)
#    
    #measurement update
    
    #print(x_priori)
    
plot.figure(1)
plot.subplot(1,2,1)
plot.title("Position")
plot.plot(z[0,:],z[1,:],'r.'
          ,x_true[0,:],x_true[2,:],'k.'
          ,x_estimate[0,:],x_estimate[2,:],'b')
plot.subplot(1,2,2)
plot.title("Velocity")
plot.plot(t,x_true[3,:],'r',t,x_estimate[3,:],'b')
plot.legend(["measurements",'true position','estimate'])

plot.figure(2)
plot.subplot(1,2,1)
plot.title("Position")
plot.plot(z[0,:],z[1,:],'r.'
          ,x_backpass[0,:],x_backpass[2,:],'b')
plot.legend(["measurments",'smoothed'])
plot.subplot(1,2,2)
plot.title("Velocity")
plot.plot(t,x_true[3,:],'r',t,x_backpass[3,:],'b')
plot.legend(["true",'smoothed'])



#random_state = np.random.RandomState(0)
#transition_matrix = F #F
#transition_offset = [0,0,0,0]
#observation_matrix = H  #H
#observation_offset = [0,0,0,0]
#transition_covariance = np.eye(4)
#observation_covariance = np.eye(4)
#initial_state_mean = x_estimate[:,0] #x0
#initial_state_covariance = P_positive[0] #P0
#
## sample from model
#kf = pkal.KalmanFilter(
#    transition_matrix, observation_matrix, transition_covariance,
#    observation_covariance, transition_offset, observation_offset,
#    initial_state_mean, initial_state_covariance,
#    random_state=random_state
#)
#
#filtered_state_estimates = kf.filter(z)[0]
#smoothed_state_estimates = kf.smooth(z)[0]

#plot.figure(1)
#plot.subplot(1,2,1)
#plot.title("Position")
#plot.plot(z[0,:],z[1,:],'r.'
#          ,filtered_state_estimates[0,:],filtered_state_estimates[2,:],'b')
#plot.subplot(1,2,2)
#plot.title("Velocity")
#plot.plot(t,x_true[3,:],'r',t,x_estimate[3,:],'b')
#plot.legend(["measurements",'estimate'])
#
#plot.figure(2)
#plot.subplot(1,2,1)
#plot.title("Position")
#plot.plot(z[0,:],z[1,:],'r.'
#          ,smoothed_state_estimates[0,:],smoothed_state_estimates[2,:],'b')
#plot.legend(["measurments",'smoothed'])
#plot.subplot(1,2,2)
#plot.title("Velocity")
#plot.plot(t,x_true[3,:],'r',t,x_backpass[3,:],'b')
#plot.legend(["true",'smoothed'])
#

