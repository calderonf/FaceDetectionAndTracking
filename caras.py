#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 09:15:01 2020

@author: Francisco Calderon
"""
from __future__ import print_function
import  camutils as cu
import rectUtils as ru
import TrackerUtils as tu
import cargaMascaras as cm
import platform

import numpy as np
import cv2
import math

from common import clock, draw_str



CAMERANUM=1  # cambiar aqui el numero de la camara
show_params=False #modo verboso en pantalla

focusTB=False
focusTrackBar=False

FullScreen=True

detectar=5
fps=30
segundosTTL=2
TTL=round((fps/detectar)*segundosTTL)
scale=3
ID=0
dt=0
dt2=0



def detect(img, cascade):
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
    if len(rects) == 0:
        return []
    rects[:,2:] += rects[:,:2]
    return ru.listOfRect_Puntos2Tam(list(rects))

def draw_rects(img, rects, color,escala):
    for r in rects:
        cv2.rectangle(img, (r[0]*escala, r[1]*escala), ((r[0]+r[2])*escala, (r[1]+r[3])*escala), color, 2)
    """
    for i, newbox in enumerate(boxes):
        p1 = (int(newbox[0]), int(newbox[1]))
        p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
        cv2.rectangle(vis, p1, p2, (0,255,0), 2, 1)
    """





# Specify the tracker type
trackerType = "MOSSE"   
 
# Create MultiTracker object
multiTracker = tu.RealMultiTracker(trackerType=trackerType)
boxes=[]
font = cv2.FONT_HERSHEY_SIMPLEX
color = (0, 255, 0)

#mask loader
tamglobos, globos, masks,globosr, masksr=cm.cargarImagenes()
mostrarMascaras=True

if tamglobos>0:
    if mostrarMascaras:
        for tt in range(tamglobos):
            cv2.imshow("masks",masks[tt])
            cv2.imshow("globos",globos[tt])
            cv2.waitKey(500)
else:
    print("sin mascaras a mostrar")
    exit()
cv2.destroyAllWindows()



if platform.system()=="Linux":
    cap = cv2.VideoCapture(CAMERANUM)

elif platform.system()=='Windows':
    cap = cv2.VideoCapture((cv2.CAP_DSHOW)+CAMERANUM)

else:
    print("Unsupported OS")
    exit()

if FullScreen:
    cv2.namedWindow('Video', cv2.WINDOW_FREERATIO)
    cv2.setWindowProperty('Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
if not cap.isOpened():
    print("ERROR! Unable to open camera")
else:
    cv2.namedWindow("Video")
    print ("Antes")
    fps,focus,fourcc,w,h=cu.getInfoCapture(cap)
    
    if focusTB:
        cap.set(cv2.CAP_PROP_AUTOFOCUS, False)  # Known bug: https://github.com/opencv/opencv/pull/5474
        cap.set(cv2.CAP_PROP_FOCUS, 0 )
        if focusTrackBar:
            cv2.createTrackbar("Focus", "Video", focus, 100, lambda v: cap.set(cv2.CAP_PROP_FOCUS, v ))
    
    
    pathToData=cv2.data.haarcascades
    cascade_fn = "haarcascade_frontalface_default.xml"
    #nested_fn  = "haarcascade_frontalface_alt.xml"
    nested_fn  = "haarcascade_profileface.xml"
    

    cascade = cv2.CascadeClassifier(cv2.samples.findFile(pathToData+cascade_fn))
    cascade2 = cv2.CascadeClassifier(cv2.samples.findFile(pathToData+nested_fn))
    #cu.setMaxFPS(cap)
    #cu.setMaxRes(cap)
    cu.setfourccmjpg(cap)
    cu.setRes1080pFPS30(cap)
    
    print ("Despues")
    fps,focus,fourcc,w,h=cu.getInfoCapture(cap)
    
    fotograma=0
    while True:
        _status, im = cap.read()
        if im is None:
            print ("no se abre camara indice no existe o error en hardware")
            break
        
        img=cv2.flip(im, +1)#puede hacerse desde guvcview en modo control, para que no gaste proceso en CPU TODO
        if fourcc == "MJPG":
            #img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
            imglR=cv2.resize(img,(640,360))
            gray = cv2.cvtColor(imglR, cv2.COLOR_BGR2GRAY)
            
        elif fourcc == "YUYV":
            imglR=cv2.resize(img,(640,360))
            gray = cv2.cvtColor(imglR, cv2.COLOR_BGR2GRAY)
        elif fourcc == "NV12":# guindowsq
            imglR=cv2.resize(img,(640,360))
            gray = cv2.cvtColor(imglR, cv2.COLOR_BGR2GRAY)
        else:
            if not platform.system()=='Windows':
                print("Unsupported format in capture check ",fourcc)
                break
            else:
                imglR=cv2.resize(img,(640,360))
                gray = cv2.cvtColor(imglR, cv2.COLOR_BGR2GRAY)
        
        if show_params:
            cv2.putText(img, "Mode: {}".format(fourcc), (15, 40), font, 1.0, color)
            cv2.putText(img, "FPS: {}".format(fps), (15, 80), font, 1.0, color)
        
        vis = img.copy()
        if (fotograma % detectar) == 0:
            t = clock()
            rects = detect(gray, cascade)
            #draw_rects(vis, rects, (0, 255, 0))
            rects2 = detect(gray, cascade2)
            #draw_rects(vis, rects2, (255, 255, 0))
            ret=ru.promediarDetecciones(rects,rects2)
            if show_params:
                draw_rects(vis, np.array(ret, dtype=np.int32), (0, 255, 0),scale)
            dt = clock() - t
            if show_params:
                draw_str(vis, (20, 20), 'time Detection: %.1f ms' % (dt*1000))
                draw_str(vis, (200, 20), 'time Tracking: %.1f ms' % (dt2*1000))
            boxes = multiTracker.update(imglR)
            
            if show_params:
                draw_rects(vis, np.array(boxes, dtype=np.int32), (255, 255, 255),scale)
                multiTracker.drawPaths(vis)
            ID=multiTracker.procesDetections(imglR,ret,ID,TTL=TTL)
            
        else:
            # get updated location of objects in subsequent frames
            
            t = clock()
            boxes = multiTracker.update(imglR)
            #print (boxes)
                    # draw tracked objects
                    
            if show_params:
                draw_rects(vis, np.array(boxes, dtype=np.int32), (255, 255, 255),scale)
            dt2 = clock() - t
            if show_params:
                draw_str(vis, (20, 20), 'time Detection: %.1f ms' % (dt*1000))
                draw_str(vis, (200, 20), 'time Tracking: %.1f ms' % (dt2*1000))
                multiTracker.drawPaths(vis)
                
        
        #For Fun
        caritas=multiTracker.reurnIdCentralPtTam()
        
        for face in caritas:
            #tamglobos, globos, masks
            globoid=face[0]%tamglobos
            tamcara=face[2]
            #despejando que la relacion de aspecto debe ser 640/480 y que el area debe ser la misma.
            caraw=int((math.sqrt((640/480)*tamcara)))
            carah=int((math.sqrt((480/640)*tamcara)))
            
            tx=int(face[1][0]+caraw*0.8)
            ty=int(face[1][1])-int(carah*1/1.618)
            
            imgglob=cv2.ximgproc.guidedFilter(globos[globoid],globos[globoid],3,0.1)
            imgmask=cv2.ximgproc.guidedFilter(masks[globoid],masks[globoid],3,0.1)
            
            globopegar	=	cv2.resize(	imgglob, (caraw,carah),cv2.INTER_NEAREST)
            mascarapegar	=	cv2.resize(	imgmask, (caraw,carah),cv2.INTER_NEAREST)
            x,y,w,h=cm.filtTam(tx,ty,caraw,carah)
            impegar=vis[y:y+h,x:x+w, :]
            cv2.copyTo(globopegar, mascarapegar,impegar)
            vis[y:y+h,x:x+w, :]=impegar# creo que esta linea sobra la copia es por referencia creo.
            """
            if show_params:
                cv2.imshow("recorte", impegar)
            """
        
        
        
        
        cv2.imshow("Video", vis)
        k = cv2.waitKey(1)
        fotograma+=1
    
        if k == 27:
            break
    
    print('Done')
    cv2.destroyAllWindows()
    cap.release()
