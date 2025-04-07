import os
import pandas as pd
import cv2
import numpy as np
from numpy import linalg as la
import matplotlib
import matplotlib.pyplot as plt
import statistics
import time
import re
import matplotlib.pyplot as plt
import copy
import eigenFaces
import traceback
import requests
#folosim backend AGG pentru a putea rula fara probleme in threaduri secundare.
matplotlib.use("AGG")

def test():
    time.sleep(20)
    return 3


def extrage_numar(s):
    numar = ''
    
    for caracter in reversed(s):
        if caracter.isdigit():
            numar = caracter + numar
        else:
            break
    for caracter in s:
        if caracter.isdigit():
            numar += caracter
        else:
            break
    return int(numar) if numar else None

def create_training_matrix(resolution,training,nr_pers,project_folder,poze_in_folder):
    poze_test_nr = poze_in_folder-training
    poze_antrenare=training
    
    training_matrix = np.zeros((resolution, nr_pers * (poze_in_folder - poze_test_nr))) 
    testing_matrix = np.zeros((resolution, poze_test_nr*nr_pers)) 
    test_files = []
    
    for i in range(poze_in_folder-poze_antrenare):
        index=poze_in_folder-i
        test_files.append(f"{index}.pgm")
   
    for root, dirs, files in os.walk(project_folder):
        for file in files:
            file_path=""
            if file.lower().endswith("pgm"):
                
                    
                file_path = os.path.join(root, file)
                poza=cv2.imread(file_path,0)
                poza=np.array(poza)
                poza=poza.reshape(-1,)
                
                if os.path.basename(file_path) not in test_files:
                    
                    training_matrix[:,(poze_antrenare*(extrage_numar(root)-1))+(extrage_numar(file)-1)]=poza
                    
                    
                    
                else:
                    testing_matrix[:,(poze_test_nr*(extrage_numar(root)-1))+extrage_numar(file)-poze_antrenare-1]=poza
                    
                    
    
    
    return training_matrix,testing_matrix
                        
def cosinus(vector, poza):
    return np.dot(vector, poza) / (la.norm(vector) * la.norm(poza))

def NN(A, poza, norma: str):
    
    
    z = np.zeros(A.shape[1])
    
    if norma == "1":
        
        for i in range(len(z)):
            
            z[i] = la.norm(A[:, i] - poza, ord=1)
    
    elif norma == "2":
        
        for i in range(len(z)):
            z[i] = la.norm(A[:, i] - poza)
    
    elif norma == "infinit":
        
        for i in range(len(z)):
            z[i] = la.norm(A[:, i] - poza, ord=np.inf)
    
    elif norma== "cos":
        
        for i in range(len(z)):
            z[i] = cosinus(A[:, i], poza)
        return np.argmax(z)  
    
    else:
        raise ValueError("nu e buna normaa.")
    return np.argmin(z) 
    
def K_NN(A,poza,norma:str,k,poze_antrenare):
    
    z = np.zeros(A.shape[1])
    
    if norma == "1":
        
        for i in range(len(z)):
    
            z[i] = la.norm(A[:, i] - poza, ord=1)
    
    elif norma == "2":
        
        for i in range(len(z)):
            z[i] = la.norm(A[:, i] - poza)
    
    elif norma == "infinit":
        
        for i in range(len(z)):
            z[i] = la.norm(A[:, i] - poza, ord=np.inf)
    
    elif norma== "cos":
        
        for i in range(len(z)):
            
            z[i] = cosinus(A[:, i], poza)
        return statistics.mode((np.argsort(-z)[:k])//poze_antrenare)
    else:
        raise ValueError("nu e buna normaa.")
    
    return statistics.mode((np.argsort(z)[:k])//poze_antrenare)


        

def csv(lista_csv,dataframes,alg,proc_vector,output_path,k=True):
    try:
        output_dir = output_path
        
        for i in range(len(dataframes)):
            if k:
                nume_fisier=f'statisitici alg {alg} procentaj antrenare{proc_vector[i]}.csv'
            else:
                nume_fisier=f"statistici NN.csv"
            
            path=os.path.join(os.path.dirname(output_dir),nume_fisier)
            print("asta e output_dir",os.path.dirname(output_dir) )
            df=dataframes[i]
            df.to_csv(path)
            print("bagam in lista")
            
            lista_csv.append(path)
    except Exception as e:
        print(str(e))
        return e
def lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,axaY,output_path,time=False):
    try:
        if alg=="NN":
            if time:
                fig, ax = plt.subplots()
                ax.plot(norm_vector, axaY, marker='o',color='red')
                ax.set_xlabel('norma')
                ax.set_ylabel('Timp_mediu')
                ax.set_title(f'alg:{alg} Procent Antrenare: {proc*10}%')
                ax.grid(True)
                plot_file=f"{output_path}_plot{len(lista_grafice)}.png"
                fig.savefig(plot_file)
                plt.close(fig)
                lista_grafice.append(plot_file)
            else:
                fig, ax = plt.subplots()
                ax.plot(norm_vector, axaY, marker='o',color='green')
                ax.set_xlabel('Norma')
                ax.set_ylabel('Recunoastere')
                ax.set_title(f'alg:{alg} Procent Antrenare: {proc*10}%')
                ax.grid(True)
                plot_file=f"{output_path}_plot{len(lista_grafice)}.png"
                fig.savefig(plot_file)
                plt.close(fig)
                lista_grafice.append(plot_file)
            
        else:     
            if time:
            
                
                    fig, ax = plt.subplots()
                    if isinstance(axaY[0], (int, float)):
                        ax.plot(k_vector,axaY, marker='o',label=f'timp',color='red')
                    else:
                        for i,axa in enumerate(axaY):
                            ax.plot(norm_vector, axa, linestyle='--',marker='o', label=f'k= {k_vector[i]}')
                    ax.legend()
                    ax.set_xlabel('k')
                    if alg=="K-NN":
                        ax.set_ylabel('Timp mediu pt fiecare k')
                    else:
                        ax.set_ylabel('Timp pre-proc')
                    ax.set_title(f'Alg:{alg} Procent Antrenare:{proc*10}%,grafic Timp pre-proc')
                    ax.grid(True)
                    plot_file=f"{output_path}_plot{len(lista_grafice)}.png"
                    fig.savefig(plot_file)
                    plt.close(fig)
                    lista_grafice.append(plot_file)
            else:
                
                for i in range(len(axaY)):
                    k=k_vector[i]
                    fig, ax = plt.subplots()
                    ax.plot(norm_vector,np.array(axaY)[i,:], marker='o')
                    ax.set_xlabel('Norma')
                    ax.set_ylabel('Recunoastere')
                    ax.set_title(f'Alg:{alg} Procent Antrenare:{proc*10}% si k este{k}')
                    
                    ax.grid(True)
                    plot_file=f"{output_path}_plot{len(lista_grafice)}.png"
                    fig.savefig(plot_file)
                    plt.close(fig)
                    lista_grafice.append(plot_file)
    except Exception as e:
        print(str(e))
        return e
def statistics_iterate(rez,nr_pers,project_folder,poze_in_folder,alg,k_vector,proc_vector,norm_vector=["2"],download_csv=False,timp=False,plot=False):
    
        print("ok let go")
        rec_list_NN=[]
        lista_grafice=[]
        lista_csv=[]
        lista_grafice_time=[]
        dataframes = []
        for proc in proc_vector:
            
            poze_test_nr = poze_in_folder-proc
            poze_antrenare=proc
            A=create_training_matrix(rez,proc,nr_pers,project_folder,poze_in_folder)[0]
            T=create_training_matrix(rez,proc,nr_pers,project_folder,poze_in_folder)[1]
            total_time_results=[]
            rec_keep_results=[]
            tt_list=[]
            rec_list=[]
            print("hopppp")
            if alg=="NN":
                print("ok start nn")
                for norm in norm_vector:
                        rec_keep=0
                        total_time=0
                        for i in range(T.shape[1]):
                        
                            test_poza=T[:,i]
                            start_time=time.time()
                            rezultat=NN(A, test_poza, norm)
                            end_time=time.time()-start_time
                            total_time+=end_time
                            index_pers = i // poze_test_nr
                            
                            start_interval = (index_pers) * poze_antrenare
                            end_interval = (index_pers+1) * poze_antrenare - 1
                            
                            if start_interval <= rezultat <= end_interval:
                                rec_keep+=1
                        total_time=total_time/T.shape[1]
                        total_time_results.append(total_time)
                        rec_keep=rec_keep/T.shape[1]
                        rec_keep_results.append(rec_keep)
                
                        print("procent antrenare",proc)
                        print(norm)
                        print(total_time)
                        print(rec_keep)
                        
                rec_list_NN.append(rec_keep_results)
                
                if plot:
                    if timp:
                        lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,total_time_results,project_folder,True)
                    lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,rec_keep_results,project_folder)
            elif alg=="K-NN":
                    
                    
                for k in k_vector:
                    total_time_results.clear()
                    rec_keep_results.clear()
                    for norm in norm_vector:
                        rec_keep=0
                        total_time=0
                        for i in range(T.shape[1]):
                            test_poza=T[:,i]
                            start_time=time.time()
                            rezultat=K_NN(A, test_poza, norm,k,poze_antrenare)
                            end_time=time.time()-start_time
                            total_time+=end_time
                            index_pers = i // poze_test_nr
                            start_interval = (index_pers) * poze_antrenare
                            end_interval = (index_pers+1) * poze_antrenare - 1
                            
                            if start_interval <= rezultat*poze_antrenare <= end_interval:
                                rec_keep+=1
                        total_time=total_time/T.shape[1]
                        total_time_results.append(total_time)
                        rec_keep=rec_keep/T.shape[1]
                        rec_keep_results.append(rec_keep)
                        print('procent', proc)
                        print('norma',norm)
                        print('timp',total_time)
                        print('rata rec',rec_keep)
                        print('k este', k)
                    
                    
                    tt_list.append(copy.deepcopy(total_time_results)) 
                    rec_list.append(copy.deepcopy(rec_keep_results)) 
                if plot:
                    if timp:
                        lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,tt_list,project_folder,True)
                    
                    lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,rec_list,project_folder)
                if download_csv:
                    df=pd.DataFrame(rec_list,columns=[f"norma {norm_vector[i]}" for i in range(len(norm_vector))],index=[f"k {k_vector[i]}" for i in range(len(k_vector))]) 
                    
                        
                    info=[f"alg: {alg}, proc: {proc*10}"]+[np.nan]*(len(df)-1)
                    print(f"suntem in else si lungimea df este {len(df)} iar lungimea info este {len(info)}")
                    df['info fisier']=info
                        
                    dataframes.append(df)
            elif alg in ["eigen","cod","eigen-class"]:
                total_time_results.clear()
                for k in k_vector:
                    rec_keep_results.clear()
                    start_time=time.time()
                    processed_A=A.copy()
                    processed_T=T.copy()
                    processed_A,HQPB,medie=eigenFaces.proc_eigen_cod(processed_A, k,proc , alg)
                    processed_T=eigenFaces.proc_eigen_test(processed_T,HQPB,medie)
                    print(f"size {processed_T.shape} a lu T, size a lu A {processed_A.T.shape} size a lu HQPB {HQPB.shape}")
                    end_time=time.time()-start_time
                    total_time_results.append(end_time)
                    for norm in norm_vector:
                        rec_keep=0
                        total_time=0
                        for i in range(processed_T.T.shape[1]):
                            test_poza=processed_T.T[:,i]
                            rezultat=NN(processed_A.T, test_poza, norm)
                            index_pers = i // poze_test_nr
                            start_interval = (index_pers) * poze_antrenare
                            end_interval = (index_pers+1) * poze_antrenare - 1
                            if alg=="eigen-class":
                                if start_interval <= rezultat*poze_antrenare <= end_interval:
                                    rec_keep+=1
                            else:
                                if start_interval <= rezultat <= end_interval:
                                    rec_keep+=1
                        print("asta e t pt care am eroare",T.shape)
                        rec_keep=rec_keep/T.shape[1]
                        rec_keep_results.append(rec_keep)
                        print('procent', proc)
                        print('norma',norm)
                        print('timp',total_time)
                        print('rata rec',rec_keep)
                        print('k este', k)
                        
                    
                    
                    rec_list.append(copy.deepcopy(rec_keep_results)) 
                if plot:
                    if timp:
                        lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,total_time_results,project_folder,True)
                    
                    
                    lista_cu_grafice(lista_grafice,proc,alg,k_vector,norm_vector,rec_list,project_folder)
                
                if download_csv:
                    df=pd.DataFrame(rec_list,columns=[f"norma {norm_vector[i]}" for i in range(len(norm_vector))],index=[f"k {k_vector[i]}" for i in range(len(k_vector))]) 
                    
                        
                    info=[f"alg: {alg}, proc: {proc*10}"]+[np.nan]*(len(df)-1)
                    df['info fisier']=info
                    dataframes.append(df)
            
            else:
                raise ValueError("algoritm invalid ,alg valizi:cod,eigen,eigen-class,NN,K-NN")
        if download_csv:      
            proc_vector_up=[i*10 for i in proc_vector]
            if alg=="NN":
                
                df=pd.DataFrame(rec_list_NN,columns=[f"norma {norm_vector[i]}" for i in range(len(norm_vector))],index=[f"proc {proc_vector[i]*10}" for i in range(len(proc_vector))]) 
                info=[f"alg: {alg}, proc: {proc*10}"]+[np.nan]*(len(proc_vector)-1)
                dataframes.append(df)
                print(len(dataframes))
                csv(lista_csv,dataframes,alg,proc_vector_up,project_folder,False)
                print("ooooooooooooook")
                
            else:
                csv(lista_csv,dataframes,alg,proc_vector_up,project_folder)
            
        print("asta e rek keep:",rec_list_NN)
        return lista_grafice,lista_csv