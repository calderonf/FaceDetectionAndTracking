#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 20:20:36 2020

@author: Francisco Calderon

Este modulo implementa llamados de estructuras de seguimiento\n 
puede ser llamado desde esta misma carpeta o invocado como un modulo aparte\n


Para generar la documentacion del modulo ejecute desde una terminal en el directorio raiz del modulo:\n

  python -m pydoc -w TrackerUtils\n
  
  A continuacion se listan prerequisitos o 'modulos',  clases y funciones implementadas.\n
"""
import cv2
import rectUtils as ru
import random


def createTrackerByName(tracker_type):
    
    if tracker_type == 'BOOSTING':
        tracker = cv2.TrackerBoosting_create()
    elif tracker_type == 'MIL':
        tracker = cv2.TrackerMIL_create()
    elif tracker_type == 'KCF':
        tracker = cv2.TrackerKCF_create()
    elif tracker_type == 'TLD':
        tracker = cv2.TrackerTLD_create()
    elif tracker_type == 'MEDIANFLOW':
        tracker = cv2.TrackerMedianFlow_create()
    elif tracker_type == 'GOTURN':
        tracker = cv2.TrackerGOTURN_create()
    elif tracker_type == 'MOSSE':
        tracker = cv2.legacy_TrackerMOSSE.create() # nota se añade legacy.
    elif tracker_type == "CSRT":
        tracker = cv2.TrackerCSRT_create()
    else:
        print("ERROR tracker no identificado se selecciona MOSSE")
        tracker = cv2.TrackerMOSSE_create()
    return tracker

class RealTracker:
    def __init__(self,ID,trackerType='MOSSE',ObjClass="Object",TTL=3,assigned=False):
        self.ID=ID
        self.trackerType=trackerType
        self.ObjClass=ObjClass# TODO que la clase sea la moda del las clases en el tiempo
        self.MaxTTL=TTL
        self.TTL=TTL
        self.assigned=assigned
        self.iou=1
        self.colour=(int(random.uniform(0,255)),int(random.uniform(0,255)),int(random.uniform(0,255)))
        
        self.path=[]
        self.algotrack=createTrackerByName(self.trackerType)
    
    def init(self,image,rect):
        self.detect=rect
        self.path.append(rect)
        self.iou=1
        return self.algotrack.init(image,tuple(rect))
    
    
    def reInit(self,image,rect):
        self.detect=rect
        #self.path[-1]=rect#compensa la ultima vista del path a la nueva deteccion genera outliers en paths
        self.iou=1
        return self.algotrack.init(image,tuple(rect))
    
    def update(self,frame):
        ok, bbox = self.algotrack.update(frame)
        if ok:
            self.path.append(bbox)
            self.iou=ru.iou(self.detect,bbox)
        else:# if not ok means the detection is lost
            self.path.append(self.path[-1])
            self.iou=0
        return ok,bbox
    
    def drawPath(self,image,verboso=False,scale=3):
        if len(self.path)>1:
            pt=(int((self.path[0][0]+self.path[0][2]/2)*scale),int((self.path[0][1]+self.path[0][3]/2)*scale))
            cv2.circle(image,pt,2,self.colour,-1)
            pt=(int((self.path[-1][0]+self.path[-1][2]/2)*scale),int((self.path[-1][1]+self.path[-1][3]/2)*scale))
            cv2.circle(image,pt,2,self.colour,-1)
            for ptr in range(1,len(self.path)):
                pt1=(int((self.path[ptr-1][0]+self.path[ptr-1][2]/2)*scale),int((self.path[ptr-1][1]+self.path[ptr-1][3]/2))*scale)
                pt2=(int((self.path[ptr][0]+self.path[ptr][2]/2)*scale),int((self.path[ptr][1]+self.path[ptr][3]/2))*scale)
                cv2.line(image,pt1,pt2,self.colour,thickness=1, lineType=8, shift=0)
    
        

class RealMultiTracker:
    def __init__(self,trackerType='MOSSE'):
        self.trackers=[]
        self.trackerType=trackerType
        
    def add(self,image,rect,ID,ObjClass="Object",TTL=3,assigned=False):
        tr=RealTracker(ID,trackerType=self.trackerType,ObjClass=ObjClass,TTL=TTL,assigned=assigned)
        tr.init(image,rect)
        self.trackers.append(tr)

    def update(self,frame):
        detections=[]
        for tr in self.trackers:
            ok,box=tr.update(frame)
            detections.append(box)
        return detections
        

    def reInitByID(self,ID,image,rect):
        for tr in self.trackers:
            found=False
            if tr.ID==ID:
                tr.init(image,rect)
                found=True
        if not found:
            return False
        else:
            return True
        
    def reInitByDetectedBox(self,detection,image,pc=0.3,assingAverage=False):
        """
        A la funcion le entra una de las detecciones del clasificador y la imagen actual, 
        la funcion busca esta deteccion en la lista de objetos siendo seguidos.
        refresca el mas probable y lo marca reseteando su TTL,
        Si encuentra el objeto retorna True
        Si no encuentra el objeto retorna False
        
        si retorna False este objeto debe tomarse como una deteccion nueva al final de la funcion 
        
        assingAverage genera movimientos bruscos en la deteccion
        
        """
        if len(self.trackers)>0:
            weights=[]
            for tr in self.trackers:
                if tr.assigned:# si ya esta asignado marquelo para no asignacion dando peso en 0
                    weights.append(-1)
                else:
                    weights.append(ru.iou(tr.path[-1],detection))
            #con la lista de pesos hallar el máximo y ese reiniciarlo y marcarlo
            maxidx=weights.index(max(weights))
            if weights[maxidx]>pc:#si el iou es menor a este valor pc no se asigna a ninguno para que se marque como nuevo
                if assingAverage:
                    self.trackers[maxidx].reInit(image,ru.promediarRect(detection,self.trackers[maxidx].path[-1]))
                else:
                    self.trackers[maxidx].reInit(image,self.trackers[maxidx].path[-1])
                self.trackers[maxidx].assigned=True
                self.trackers[maxidx].TTL=self.trackers[maxidx].MaxTTL
                return True
            else:
                return False
        else:
            return False# si no hay tracks para procesar fijo la deteccion es una deteccion nueva
              
            
           
    def processTTL(self):
        """
        La funcion disminuye en 1 el valor de TODOS los Time To Live (TTL) de la clase traking
        
        """
        for tr in self.trackers:
            tr.TTL=tr.TTL-1
            tr.assigned=False
                
    def deleteTTL(self,verbose=True):
        """
        La funcion busca TODOS los tracks con TTL en 0 o menor y los elimina.
        
        """
        li=list(range(len(self.trackers)))
        li.reverse()
        for i in li:
           if self.trackers[i].TTL<=0:#si el TTL llegó a 0 o menos
               borrado=self.trackers.pop(i)
               if verbose:
                   print ("borrando por TTL ID",borrado.ID, "TTL",borrado.TTL)
               break
    
    def deleteSurplusTracks(self,pc=0.1,verbose=True):
        """
        la funcion borra los tracks que estan siguiendo un mismo objeto, toma solo el objeto con menor error a su deteccion siendo seguido, da la opcion de concatenar los paths o de tomar el path mas largo.
        
        """
        rects=len(self.trackers)
        li=list(range(0,rects,1))
        li.reverse()
        for i in li:
            rects=len(self.trackers)
            lj=list(range(0,rects,1))
            lj.reverse()
            for j in lj:
                if not i==j:
                    try:
                        ri=self.trackers[i].path[-1]
                        rj=self.trackers[j].path[-1]
                        if ru.rectContenidos(ri,rj,pc=pc):#Si estan contenidos elimine el mas pequeño ya se garantiza que son normales los rectangulos
                            if self.trackers[i].iou>self.trackers[j].iou:#si tiene menos error i elimine j
                                if len(self.trackers[j].path)>len(self.trackers[i].path):# si el path  de j es mayor que el de i, conserve el de j
                                    del self.trackers[i].path[:]
                                    self.trackers[i].path=self.trackers[j].path.copy()
                                    self.trackers[i].colour=self.trackers[j].colour
                                del self.trackers[j]
                            else:# si no elimine i
                                if len(self.trackers[i].path)>len(self.trackers[j].path):# si el path  de i es mayor que el de j, conserve el de i
                                    del self.trackers[j].path[:]
                                    self.trackers[j].path=self.trackers[i].path.copy()
                                    self.trackers[j].colour=self.trackers[i].colour
                                del self.trackers[i]
                    except:
                        print ("TODO: ver problema de indice en path, los paths deben tener siempre tamaño pero no lo tenia")
        
    def procesDetections(self,image,detectionlist,currID,pc=0.3,TTL=3,assingAverage=True):#TODO añadir una lista extra con el nombre de la clase de cada objeto
        """
        Esta funcion procesa una lista de detecciones, por cada deteccion nueva busca si existe un track y lo asigna, si 
        la deteccion nueva no es asignada a un track, crea un track nuevo.
        
        al final procesa el TTL y borra los tracks que cumplieron el TTL
        retorna el current ID para que sea asignado al contador externo.  
        """
        self.processTTL()
        for det in detectionlist:
            assigneddet=self.reInitByDetectedBox(det,image,pc=pc,assingAverage=assingAverage)
            if not assigneddet:
                self.add(image,det,currID,ObjClass="Object",TTL=TTL,assigned=True)#se marca como asignado ya, para que no se le asigne una deteccion en el siguiente bucle 
                currID+=1
        self.deleteTTL()
        self.deleteSurplusTracks()
        return currID
    
    def drawPaths(self,image,verboso=False,scale=3):
        for tr in self.trackers:
            tr.drawPath(image,verboso=verboso,scale=scale)
    
    def reurnIdCentralPtTam(self,scale=3):
        ls=[]
        for tr in self.trackers:
            ls.append((tr.ID, ((tr.path[-1][0]*scale+tr.path[-1][2]*scale/2),(tr.path[-1][1]*scale+tr.path[-1][3]*scale/2)),tr.path[-1][2]*scale*tr.path[-1][3]*scale))
        return ls
        
        
if __name__ == '__main__':
    import sys
    from random import randint
    import  camutils as cu
    
     
    # Create a video capture object to read videos
    cap = cv2.VideoCapture(0)
    cu.setfourccmjpg(cap)
    cu.setRes1080pFPS30(cap)
     
    # Read first frame
    success, frame = cap.read()
    # quit if unable to read the video file
    if not success:
        print('Failed to read video')
        sys.exit(1)
    else:
        ## Select boxes
        bboxes = []
        colors = [] 
         
        # OpenCV's selectROI function doesn't work for selecting multiple objects in Python
        # So we will call this function in a loop till we are done selecting all objects
        while True:
          # draw bounding boxes over objects
          # selectROI's default behaviour is to draw box starting from the center
          # when fromCenter is set to false, you can draw box starting from top left corner
          bbox = cv2.selectROI('MultiTracker BOX SELECT ENTER Q exit', frame)
          bboxes.append(bbox)
          colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
          print("Press q to quit selecting boxes and start tracking")
          print("Press any other key to select next object")
          k = cv2.waitKey(0) & 0xFF
          if (k == 113 or k==ord("Q")):  # q is pressed
            break
         
        print('Selected bounding boxes {}'.format(bboxes))
        cv2.destroyWindow('MultiTracker BOX SELECT ENTER Q exit')
        
        
        # Specify the tracker type
        trackerType = "MOSSE"   
         
        # Create MultiTracker object
        multiTracker = RealMultiTracker(trackerType=trackerType)
         
        # Initialize MultiTracker 
        ID=0
        
        
        ID=multiTracker.procesDetections(frame,bboxes,ID)
        
        """
        for bbox in bboxes:
          multiTracker.add(frame, bbox,ID)
          ID=ID+1
        """
          
          # Process video and track objects
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
           
            # get updated location of objects in subsequent frames
            boxes = multiTracker.update(frame)
             
            # draw tracked objects
            i=0
            for newbox in boxes:
                p1 = (int(newbox[0]), int(newbox[1]))
                p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
                cv2.rectangle(frame, p1, p2, colors[i], 2, 1)
                i=i+1
                 
            # show frame
            cv2.imshow('MultiTracker', frame)
               
            # quit on ESC button
            if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
                break
            
        cap.release()
        cv2.destroyAllWindows()
            
            
        
    
    
    
    
    
