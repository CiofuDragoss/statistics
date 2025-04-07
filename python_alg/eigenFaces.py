import os
import pandas as pd
import cv2
import numpy as np
from numpy import linalg as la
import matplotlib.pyplot as plt
import statistics
import time
import re
import matplotlib.pyplot as plt
import copy



def proc_eigen_cod(A,k,person_pics,alg_type):
    medie=[]
    if alg_type in["eigen","eigen-class"]:
        medie=np.mean(A,axis=1)
        B=A.copy()
        A=(A.T-medie).T
        L=np.dot(A.T,A)
        d,v=np.linalg.eig(L)
        d=np.argsort(d)[::-1]
        v=np.dot(A,v)
        print(v.shape)
        HQPB=np.zeros((len(A),k))
        for i in range(k):
            HQPB[:,i]=v[:,d[i]]
        if alg_type=="eigen":
            proiectii=np.dot(A.T,HQPB)
        else:
            RC=np.zeros((10304,len(A[0])//person_pics))
            for i in range(0,len(A[0]),person_pics):
                RC[:,(i+1)//person_pics]=np.mean(A[:,i:i+person_pics],1)
        
            proiectii=np.dot(RC.T,HQPB)
        A=B
        
    elif alg_type=="cod":
        #initialize
        B=A.copy()
        #init HQPB
        HQPB=np.zeros((len(A),k))
        #init u si v
        u= np.dot(A,np.ones(((len(A[0])),1)))
        v = np.dot(A.T,np.ones(((len(A)),1)))
        u=u/np.linalg.norm(u)
        v=v/np.linalg.norm(v)
        #start
        for i in range(k):
            #componenente u si v new(x=z/q)--> z  first, q second
            u_first_comp=np.dot(B,v)
            u_second_comp=np.linalg.norm(u_first_comp,2)
            v_first_comp=np.dot(B.T,u)
            v_second_comp=np.linalg.norm(v_first_comp,2)
            
            # v si u new
            
            u=u_first_comp/u_second_comp
            
            v=v_first_comp/v_second_comp
            #elementele sigma (a*b)/c
            
            a=u_second_comp
            b=v_second_comp
            c=np.dot(u.T,np.dot(B,v))
            #sigma
            sigma=(a*b)/c
            #new matrix
            B-=sigma*np.dot(u,v.T)
            #fill HQPB
            HQPB[:,i]=u.T
        proiectii=np.dot(A.T,HQPB)
        
    else:
        raise ValueError("Nu este valid parametrul alg_type")
    
    return proiectii,HQPB,medie

def proc_eigen_test(T,HQPB,medie=[]):
    T_copy=T.copy()
    print("asta e media ",medie)
    if len(medie)==0:
        proiectiiT=np.dot(T.T,HQPB)
    else:
        T=(T.T-medie).T
        proiectiiT=np.dot(T.T,HQPB)
    
    T=T_copy.copy()
    return proiectiiT



    
    
    

"""
A=create_training_matrix(10304,80,40,project_folder,10)[0]
T=create_training_matrix(10304,80,40,project_folder,10)[1]
proiectiiA,HQPB,medie=proc_eigen_cod(A, 20, 8,"cod")
print("sahdsadsa",proc_eigen_test(T,HQPB,medie).shape)
print("sahdsadsa",proiectiiA.shape)
print("sahdsadsa",HQPB.shape)
poza_test=T[:,3]
poza_test=np.dot(poza_test,HQPB)
print(poza_test.shape)
print("rezultatul :",NN(proiectiiA.T,poza_test,'1'))
"""






        


