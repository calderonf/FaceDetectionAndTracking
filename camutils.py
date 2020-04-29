#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 10:27:31 2020

@author: francisco
"""


import numpy as np
import cv2 as cv

def countCameras():
    import platform
    import os
    if platform.system()=="Linux":
        data=os.popen("ls /dev/video*").read()
        return(data.count("\n"))
    else:
        print("Unsupported OS")
        return 0
    
def getCameraLocations():
    import platform
    import os
    if platform.system()=="Linux":
        data=os.popen("ls /dev/video*").read()
        return(data[1:-1].split("\n"))
    else:
        print("Unsupported OS")
        return 0

def decode_fourcc(v):
    v = int(v)
    return "".join([chr((v >> 8 * i) & 0xFF) for i in range(4)])


def getInfoCapture(cap,camtype="USB"):
    if camtype=="USB":
        """
        Docuemntacion:
            https://docs.opencv.org/4.1.0/d4/d15/group__videoio__flags__base.html#gaeb8dd9c89c10a5c63c139bf7c4f5704d
            https://docs.opencv.org/4.1.0/dc/dfc/group__videoio__flags__others.html
            
        """
        fps = cap.get(cv.CAP_PROP_FPS)
        focus = int(min(cap.get(cv.CAP_PROP_FOCUS) , 255))  # ceil focus to C_LONG as Python3 int can go to +inf
        fourcc = decode_fourcc(cap.get(cv.CAP_PROP_FOURCC))
        w=int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        h=int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print ("Se encuentra camara de ",cap.getBackendName()," con propiedades: FPS=" ,fps," Foco=",focus," FOURCC=",fourcc, " Resolucion=",w,"X",h)
        return fps,focus,fourcc,w,h

def setMaxRes(cap):
    """
    documentacion
    https://es.wikipedia.org/wiki/Resoluci%C3%B3n_de_pantalla#/media/Archivo:Vector_Video_Standards2.svg
    
    """
    #try VGA
    res="VGA"
    w=640
    h=480
    res1=cap.set(cv.CAP_PROP_FRAME_WIDTH,w)
    res2=cap.set(cv.CAP_PROP_FRAME_HEIGHT,h)
    if res1 and res2:
        w=int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        h=int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("se configura resolucion ",res,"Queda en ",w,"X",h)
    else:
        print("falla en fijar resolucion ",res)
    
    
    #try HD720
    res="HD720"
    w=1280
    h=720
    res1=cap.set(cv.CAP_PROP_FRAME_WIDTH,w)
    res2=cap.set(cv.CAP_PROP_FRAME_HEIGHT,h)
    if res1 and res2:
        w=int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        h=int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("se configura resolucion ",res,"Queda en ",w,"X",h)
    else:
        print("falla en fijar resolucion ",res)
    
    #try HD
    res="HD1080"
    w=1920
    h=1080
    res1=cap.set(cv.CAP_PROP_FRAME_WIDTH,w)
    res2=cap.set(cv.CAP_PROP_FRAME_HEIGHT,h)
    if res1 and res2:
        w=int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        h=int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        print("se configura resolucion ",res,"Queda en ",w,"X",h)
    else:
        print("falla en fijar resolucion ",res)


def setMaxFPS(cap):
    res="5"
    fps=5
    res1=cap.set(cv.CAP_PROP_FPS,fps)
    if res1:
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar FPS en ",res)
        
    res="10"
    fps=10
    res1=cap.set(cv.CAP_PROP_FPS,fps)
    if res1:
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar FPS en ",res)
        
    res="15"
    fps=15
    res1=cap.set(cv.CAP_PROP_FPS,fps)
    if res1:
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar FPS en ",res)
        
    res="20"
    fps=20
    res1=cap.set(cv.CAP_PROP_FPS,fps)
    if res1:
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar FPS en ",res)
           
    res="29.97"
    fps=29.97
    res1=cap.set(cv.CAP_PROP_FPS,fps)
    if res1:
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar FPS en ",res)
        
    res="30"
    fps=30
    res1=cap.set(cv.CAP_PROP_FPS,fps)
    if res1:
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar FPS en ",res)


def setfourccmjpg(cap):
    oldfourcc = decode_fourcc(cap.get(cv.CAP_PROP_FOURCC))
    codec = cv.VideoWriter_fourcc(*'MJPG')
    
    print ("Cambiando codec de ",oldfourcc, "a MJPG...")
    
    res=cap.set(cv.CAP_PROP_FOURCC,codec)
    if res:
        print("codec queda en ",decode_fourcc(cap.get(cv.CAP_PROP_FOURCC)))
    else:
        print("Al parecer no se logra cambiar, codec queda en ",decode_fourcc(cap.get(cv.CAP_PROP_FOURCC)))
    

def setRes1080pFPS30(cap):
    
    res="HD1080"
    w=1920
    h=1080
    fps=30
    res1=cap.set(cv.CAP_PROP_FRAME_WIDTH,w)
    res2=cap.set(cv.CAP_PROP_FRAME_HEIGHT,h)
    res3=cap.set(cv.CAP_PROP_FPS,fps)
    if res1 and res2 and res3:
        w=int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
        h=int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv.CAP_PROP_FPS))
        print("se configura resolucion ",res,"Queda en ",w,"X",h)
        print("se configura FPS en ",res," Queda en ",fps)
    else:
        print("falla en fijar resolucion o FPS",res)