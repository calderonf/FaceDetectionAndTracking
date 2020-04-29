#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 06:57:21 2020

@author: francisco
"""
import cv2
import glob

def cargarImagenes(pathIm="images/"):
    pathsMascarasP=glob.glob(pathIm+"mascaraP*.png")
    pathsGlobosP=glob.glob(pathIm+"P*.jpg")
    pathsMascarasR=glob.glob(pathIm+"mascaraP*.png")
    pathsGlobosR=glob.glob(pathIm+"R*.jpg")
    globosP=[]
    masksP=[]
    globosR=[]
    masksR=[]
    if len(pathsMascarasP)==len(pathsGlobosP) and len(pathsMascarasR)==len(pathsGlobosR)and len(pathsMascarasP)==len(pathsGlobosR)  :# si hay un numero de imagenes iguales
        pathsMascarasP.sort()
        pathsGlobosP.sort()
        pathsMascarasR.sort()
        pathsGlobosR.sort()
        tam=len(pathsMascarasP)
        for idx in range(tam):
            globosP.append(cv2.imread(pathsGlobosP[idx], cv2.IMREAD_COLOR))
            masksP.append(cv2.imread(pathsMascarasP[idx], cv2.IMREAD_GRAYSCALE))
            globosR.append(cv2.imread(pathsGlobosR[idx], cv2.IMREAD_COLOR))
            masksR.append(cv2.imread(pathsMascarasR[idx], cv2.IMREAD_GRAYSCALE))
    else:
        print (pathsGlobosP)
        print (pathsMascarasP)
        print (pathsGlobosR)
        print (pathsMascarasR)
        print (" La canidad de globos debe ser la misma que de mascaras deben llamarse mascara#.png y globo#.png sensible a minuscula donde # es un consecutivo" )
        tam=0
    return (tam, globosP, masksP,globosR, masksR)
    

if __name__ == '__main__':
    
    tam, globos, masks,globosR, masksR=cargarImagenes()
    if tam>0:
        for tt in range(tam):
            cv2.imshow("globosp",globos[tt])
            cv2.imshow("masksp",masks[tt])
            cv2.imshow("globosr",globosR[tt])
            cv2.imshow("masksr",masksR[tt])
            cv2.waitKey(2000)
    else:
        print("sin imagenes a mostrar")
    
    cv2.destroyAllWindows()
    
    
def filtTam(tx,ty,tw,th,imgw=1920,imgh=1080):
    """
    para evitar copiar por fuera de la imagen
    
    """
    if tw>imgw:
        print("error tw>imgw")
        return 0,0,0,0
        
    if th>imgh:
        print("error th>imgh")
        return 0,0,0,0
    
    x1=tx-tw/2
    y1=ty-th/2
    x2=x1+tw
    y2=y1+th
    
    if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
        return int(x1),int(y1),int(tw),int(th)
    
    if x1<0:
        x1=(tx-tw/2)-x1
        y1=ty-th/2
        x2=x1+tw
        y2=y1+th
        if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
            return int(x1),int(y1),int(tw),int(th)
    if y1<0:  
        y1=(ty-th/2)-y1
        y2=y1+th
        if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
            return int(x1),int(y1),int(tw),int(th) 
        
    if x2>=imgw:  
        restarx=x2-imgw+1# el +1 es pr si es 1920 toca que sea 1919 se le resta 1
        x1=(tx-tw/2)-restarx
        y1=(ty-th/2)
        x2=x1+tw
        y2=y1+th
        if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
            return int(x1),int(y1),int(tw),int(th)  
        if y1<0:  
            y1=(ty-th/2)-y1
            y2=y1+th
            if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
                return int(x1),int(y1),int(tw),int(th) 
        
    if y2>=imgh:  
        restary=y2-imgh+1# el +1 es pr si es 1080 toca que sea 1079 se le resta 1
        y1=(ty-th/2)-restary
        y2=y1+th
        if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
            return int(x1),int(y1),int(tw),int(th) 
        
        if x1<0:
            x1=(tx-tw/2)-x1
            x2=x1+tw
            if x1>=0 and y1>=0 and x2<imgw and y2<imgh:
                return int(x1),int(y1),int(tw),int(th)
        
    print ("error no deberia llegar acá el tamaño es:")
    print(tx,ty,tw,th)
    print ("la salida es:")
    
    print(x1,y1,tw,th)