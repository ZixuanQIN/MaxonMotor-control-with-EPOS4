# -*- coding: utf-8 -*-
"""
@author: QIN ZIXUAN, Tokyo Institute of Technology
e-mail: qin.z.aa@m.titech.ac.jp
"""

import clr
import ctypes
import time
import sys
clr.AddReference('EposCmd.Net')
EposCmd64 = ctypes.CDLL('.\EposCmd64.dll')
from EposCmd.Net.VcsWrapper import Device
import re

# parameters
errorCode = 0
nodeID = 1
baudrate = 1000000
timeout = 500
absolute = False #as opposed to relative
immediately = True #does not wait for execution of previous command
pos0 = 0
delta_angle = 0 # record the change of angle

class Motor:
    def _init_(self, angle, direction, velocity, acceleration, deceleration, pos, actualPos, actualVel):
        self.angle = angle
        self.direction = direction
        self.velocity = velocity
        self.acceleration = acceleration
        self.deceleration = deceleration
        self.pos = pos
        self.actualPos = actualPos
        self.actualVel = actualVel
        
def connection():
    errorCode = 0
    Device.Init()
    keyHandle, error = Device.VcsOpenDevice('EPOS4', 'MAXON SERIAL V2', 'USB', 'USB0', errorCode) #opens EPOS
    if keyHandle == 0:
        print("Please turn on Power Supply!\n")
    return keyHandle

def initial(name):
    name.angle = 0
    name.direction = 0
    name.velocity = 5000 #rpm profile speed
    name.acceleration = 100000 #rpm/s, up to 1e7 would be possible
    name.deceleration = 100000 #rpm/s
    name.pos = 1000000000
    return name

# start
def settings(keyHandle, name):
    Device.VcsSetProtocolStackSettings(keyHandle, baudrate, timeout, errorCode) #set baudrate
    Device.VcsClearFault(keyHandle, nodeID, errorCode) #clear all faults

    Device.VcsActivateProfilePositionMode(keyHandle, nodeID, errorCode) #activate profile position mode
    Device.VcsSetPositionProfile(keyHandle, nodeID, name.velocity, name.acceleration, name.deceleration, errorCode) #set profile parameters
    Device.VcsSetEnableState(keyHandle, nodeID, errorCode) #enable device
    
def start(name, delta_angle):
    # angle limit
    if name.angle > 75 or name.angle < -75:
        print("Angle is out of range!!!\n")
    else:
        keyHandle = connection()
        name.actualPos = (Device.VcsGetPositionIs(keyHandle, nodeID, name.pos, errorCode))[1]
        name.actualVel = (Device.VcsGetVelocityIs(keyHandle, nodeID, name.velocity, errorCode))[1]
        settings(keyHandle, name)
        
        a = 60
        delay = a/6/name.velocity
                
        # delta angle calculation
        if name.angle > 0:
            name.direction = 1
        elif name.angle < 0:
            name.direction = -1
        else:
            name.direction = 0
        
        delta_angle += name.direction * name.angle
        # ANGLE, name.direction, delta_angle = DELTA_ANGLE(ANGLE, name.direction, delta_angle)
                
        # continue
        timewait = 40 * abs(name.angle)
        pos1 = name.direction * name.pos #put in a big number, bigger than the desired end position

        name.actualPos = (Device.VcsGetPositionIs(keyHandle, nodeID, pos1, errorCode))[1]
        name.actualVel = (Device.VcsGetVelocityIs(keyHandle, nodeID, name.velocity, errorCode))[1]
            
        Device.VcsSetEnableState(keyHandle, nodeID, errorCode) #enable device 
                
        Device.VcsMoveToPosition(keyHandle, nodeID, pos1, absolute, immediately, errorCode)
        time.sleep(delay)
        Device.VcsWaitForTargetReached(keyHandle, nodeID, timewait, errorCode)
        name.actualPos = (Device.VcsGetPositionIs(keyHandle, nodeID, pos1, errorCode))[1]
        name.actualVel = (Device.VcsGetVelocityIs(keyHandle, nodeID, name.velocity, errorCode))[1]
        Device.VcsSetDisableState(keyHandle, nodeID, errorCode)
        
        
