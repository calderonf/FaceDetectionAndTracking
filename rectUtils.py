#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 12:41:52 2020

@author: francisco


rect1AreNormal means that the rectangle notation is (x, y, w, h)
rect not normal means                          that (x1,x2,y1,y2)
"""


def bb_intersection_over_union(boxA, boxB):#probada OJO que la entrada son los puntos del rectangulo, no el de arriba a la izquierda + el tamaño
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
    if interArea == 0:
        return 0
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
    boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou

def rectTam2Puntos(r1):#probada pasa de x,y,w,h a x1,y1,x2,y2
    return list((r1[0],r1[1],r1[0]+r1[2],r1[1]+r1[3]))

def rectPuntos2Tam(r1):#          pasa de  x1,y1,x2,y2 a x,y,w,h
    return list((r1[0],r1[1],r1[2]-r1[0],r1[3]-r1[1]))


def iou(r1,r2,rect1AreNormal=True,rect2AreNormal=True):#probada NOrmal notation
    if rect1AreNormal:
        rr1=rectTam2Puntos(r1)
    else:
        rr1=r1
    if rect2AreNormal:
        rr2=rectTam2Puntos(r2)
    else:
        rr2=r2
    return bb_intersection_over_union(rr1,rr2)

def rectContenidos(r1,r2,pc=0.7,rect1AreNormal=True,rect2AreNormal=True):#Rectanguos entran en notacion de (p1,p2) no (p,tam)
    iouu=iou(r1,r2,rect1AreNormal=rect1AreNormal,rect2AreNormal=rect2AreNormal)
    if iouu>pc:
        return True
    else:
        return False

def promediarRect(r1,r2):#probada da igual para ambas notaciones de rectangulo
    return list((round((r1[0]+r2[0])/2),round((r1[1]+r2[1])/2),round((r1[2]+r2[2])/2),round((r1[3]+r2[3])/2)))


def listOfRect_Puntos2Tam(rectlist):
    ret=[]
    for r in rectlist:
        ret.append(rectPuntos2Tam(r))
    return ret
    

def RemoverMenorRectContenido(rects,pc=0.7,verbose=False,rectsAreNormal=True):#probada
    ret=[]
    for i in range(0,len(rects),1):
        for j in range(i+1,len(rects),1):
            #print(rects[i],"vs",rects[j]) 
            if rectsAreNormal:
                ri=rects[i]
                rj=rects[j]
            else:
                ri=rectPuntos2Tam(rects[i])
                rj=rectPuntos2Tam(rects[j])
            if rectContenidos(ri,rj,pc=pc):#Si estan contenidos elimine el mas pequeño ya se garantiza que son normales los rectangulos
                if ri[2]*ri[3]>rj[2]*rj[3]:#es mas grande i
                    ret.append(ri)
                else:
                    ret.append(rj)
    for r in ret:
        try:
            rects.remove(r)
        except:
            if verbose:
                print("error depurado")
    return rects

def promediarDetecciones(lr1,lr2,pc=0.7,rectsAreNormal=True):
    lr1=RemoverMenorRectContenido(lr1,rectsAreNormal=rectsAreNormal)
    lr2=RemoverMenorRectContenido(lr2,rectsAreNormal=rectsAreNormal)
    if len(lr1)==0:
        if len(lr2)==0:
            return []
        else:
            return lr2
    retorno=[]
    li=list(range(len(lr1)))
    li.reverse()
    
    for i in li:
        lj=list(range(len(lr2)))
        lj.reverse()
        for j in lj:
           if rectContenidos(lr1[i],lr2[j],pc=pc):#Si estan contenidos agregue el promedio
               retorno.append(promediarRect(lr1[i],lr2[j]))
               # y eliminelos de las listas
               lr1.pop(i)
               lr2.pop(j)
               break
    #si se salva el contenido de la lista es por que no tiene par y sebe ser adicionado
    retorno.extend(lr1)
    retorno.extend(lr2)
    retorno=RemoverMenorRectContenido(retorno)
    return retorno           
               
def nuevasDetecciones(tracker,detections,pc=0.5):
    if len(tracker)==0:
        if len(detections)==0:
            return []
        else:
            return detections
    retorno=[]
    li=list(range(len(tracker)))
    li.reverse()
    
    for i in li:
        lj=list(range(len(detections)))
        lj.reverse()
        for j in lj:
           if rectContenidos(tracker[i],detections[j],pc=pc):#Si estan contenidos agregue el promedio
               #retorno.append(promediarRect(tracker[i],lr2[j]))
               # y eliminelos de las listas
               tracker.pop(i)
               detections.pop(j)
               break
    #si se salva el contenido de la lista es por que no tiene par y sebe ser adicionado
    #retorno.extend(tracker)
    retorno.extend(detections)
    retorno=RemoverMenorRectContenido(retorno)
    return retorno 


    
    
    
            
if __name__ == '__main__':
    
    lr1=[[ 696  ,222 ,1125  ,651], [1299   ,93 ,1743  ,537],[117 ,369 ,639 ,891],[1250 ,1500 ,639 ,891]]
    lr2=[[ 681  ,204 ,1128  ,651],[ 1302   ,84 ,1761  ,543],[ 84 ,345 ,654 ,915],[ 681  ,204 ,1128  ,651],[ 696  ,222 ,1125  ,651],[1 ,1 ,50 ,50]]

    print ("Promedio de ",lr1[0],"con ",lr2[0],"Es ",promediarRect(lr1[0],lr2[0]))
    rects=[]
    rects.extend(lr1)
    rects.extend(lr2)
    print ("antes")
    print(rects)
    res=RemoverMenorRectContenido(rects)
    print("Despues")
    print(res)
    
    for idx in range(0,len(lr1)):
        print(iou(lr1[idx],lr2[idx]))

    print("Promediar las detecciones")
    ret=promediarDetecciones(lr1,lr2)
    print(ret)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
