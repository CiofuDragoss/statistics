from flask import Flask, request, jsonify, session
import zipfile
import tempfile
import shutil
import os
import cv2
import numpy as np
from numpy import linalg as la
import matplotlib.pyplot as plt
import statisticss
import time
import re
import copy
import statistics
from celery import Celery
import json
import time
import traceback
import requests
app = Flask(__name__)

url_dotnet="http://localhost:5029"
app.secret_key = "lol"  
#celery pentru taskurile de procesare
app.config['broker_url'] = 'redis://localhost:6379'
app.config['result_backend'] = 'redis://localhost:6379'

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['broker_url'])
    celery.conf.update(app.config)
    return celery

celery = make_celery(app)

#dictionare pentru a manageria sesiunile
custom_sessions = {}
path_sessions={}
locked={}


#home
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "test works"})


#ruta pentru procesarea setarilor (primite din .net) 
@app.route("/processJson", methods=["POST"])
def process_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": " nu s au primit datele"}), 400
        session_id = data.get('session_id')
        settings = data.get('settings')
        if not session_id or not settings:
            return jsonify({"error": "session_id sau settings lipsesc"}), 400
        if session_id in custom_sessions:
            custom_sessions[session_id].update(settings)
        else:
            custom_sessions[session_id] = settings
        
       
        return custom_sessions[session_id], 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500



#primim de la .net sesh_id ul si verificam daca utilizatorul a trimis un zip,pentru a putea incepe procesarea
@app.route("/startProcesare",methods=["POST"])
def raspund():
    sesh_id=request.data.decode('utf-8') 
    print(path_sessions)
    if sesh_id in path_sessions:
        
        if sesh_id in locked and locked[sesh_id]:
            print("ddsada")
            return jsonify({"error": "ai deja o cerere de generat statistici in procesare!"}),400
        response = jsonify({"succes": "True"})
        response.status_code = 200
        print("asta este calea bossss " +path_sessions[sesh_id])
        celery.send_task('app.Procesare', args=[sesh_id,path_sessions[sesh_id],custom_sessions[sesh_id],url_dotnet])
        return response
    else:
        return jsonify({"error":"trebuie sa incarci si fisierul zip cu baza de date,inainte sa incepem :)"}),400

        
# Ruta pentru procesare zip
@app.route("/processZip", methods=["POST"])
def processZip():
    print(request.files)
    print(request.form)
    try:
        if 'file' not in request.files:
            return jsonify({"error":"Nu ai incarcat fisier"}),400
        database=request.files['file']
        session_id = request.form.get('session_id')
        if not session_id:
            print("loool2")
            return jsonify({"error": "session_id invalid sau nu nu ai setat parametrii"}), 400
        if session_id in locked and locked[session_id]:
            
            return jsonify({"error": "ai deja o cerere de generat statistici in procesare!"}),400
        print("loool3") 
        custom_temp_root = r"C:\Users\drago\Desktop\app_final\app\wwwroot"
        temp_dir = tempfile.mkdtemp(prefix=f"server_temp_", dir=custom_temp_root)
        database_path=os.path.join(temp_dir,database.filename)
        database.save(database_path)
        with zipfile.ZipFile(database_path,'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        try:
            settings={}
            settings['rezolutie'],settings['nr_persoane'],settings['nr_poze']=validate_and_get_arg(os.path.join(temp_dir, os.path.splitext(database.filename)[0]))
            if session_id in custom_sessions:
                custom_sessions[session_id].update(settings)
            else:
                custom_sessions[session_id] = settings
        except Exception as e:
            shutil.rmtree(temp_dir)
            return jsonify({"error": f"databaseul nu este valid -> {str(e)}"}),400

        if session_id in path_sessions:
            
            path=path_sessions.pop(session_id)
            
            shutil.rmtree(os.path.dirname(path))

        path_sessions[session_id]=os.path.join(temp_dir, os.path.splitext(database.filename)[0])
        return jsonify("am reusit"),200
        
        
    except Exception as e :
        print(str(e))
        return jsonify({"error": str(e)}), 500
        



#helper pentru validate_and_get
def get_image_resolution(image_path):
    
    img = cv2.imread(image_path)
    if img is not None:
        return img.shape[1]* img.shape[0] 
    else:
        raise ValueError(f"Folderul nu contine doar imagini")
    
#validare+extragere date necesare pentru rularea algoritmului/statisticilor
#get datele pe care le dorim + valideaza data_base
def validate_and_get_arg(path):

    if not path:
        raise ValueError("Calea este goala")
    persoane=0
    poze_per_folder=None
    img_rez=None

    for root,dirs,files in os.walk(path):
        if root==path:
            persoane=len(dirs)
        if poze_per_folder is None and root!=path:
            poze_per_folder=len(files)
        elif poze_per_folder is not None:
            if poze_per_folder!=len(files):
                print(f"poze init {poze_per_folder} si eroarea {len(files)}")
                raise ValueError("Nu avem acelasi nr de poze in fiecare folder")

        for file in files:
            file_path=os.path.join(root,file)
            rezolutie=get_image_resolution(file_path)
            if img_rez is None:
                img_rez=rezolutie
            elif img_rez!=rezolutie:
                raise ValueError("Pozele au rezolutii diferite")
    if poze_per_folder==None or persoane==0 or rezolutie==None:
        raise ValueError("Atentie fisierul tau zip trebuie sa fie de forma: date.zip/date/folder_pers/poze!Arhiva Sa aiba \
                         acelasi nume cu folderul bazei de date ce contine  folderele cu poze ale claselor/persoanelor!")
    
    return img_rez,persoane,poze_per_folder

#procesam setarile ,cheile pt dictionar sunt->(rezolutie,nr_persoane,nr_poze,Alg,Norme,Training,K,Fantome,Optiuni)
@celery.task(name='app.Procesare', bind=True)
def process_settings(self,sesh_id,path,settings,url):
    path_csv=None
    path_grafice=None
    try:
            rez = int(settings["rezolutie"])
            nr_clase = int(settings["nr_persoane"])
            nr_poze_per_cls = int(settings["nr_poze"])
            alg = settings["Alg"]
            training = int(settings["Training"]) // 10
            k = int(settings["K"])
            fantome = int(settings["Fantome"])
            norme = settings["Norme"]
            optiuni = settings["Optiuni"]

            # Setam argumentele booleene
            csv_bool = "csv" in optiuni
            plot_bool = "plot" in optiuni
            time_bool = "time" in optiuni

            # Obținem vectorii normelor, opțiunilor, k/fantome și training
            norm_vector = [norm for norm in norme]
            k_vector = [i for i in range(3, k + 1, 2)]
            proc_vector = [i for i in range(5, training + 1, 1)]
            f_vector = [i for i in range(20, fantome + 1, 20)]
            print("asta e fantome vector: ",f_vector)
            start_timp=time.time()
            # Începem procesarea (funcția statistics_iterate poate dura mult)
            try:
                if alg in ["K-NN","NN"]:
                    path_grafice,path_csv = statisticss.statistics_iterate(rez, nr_clase, path, nr_poze_per_cls, alg, k_vector, proc_vector, norm_vector, csv_bool, time_bool, plot_bool)
                else:
                    path_grafice,path_csv = statisticss.statistics_iterate(rez, nr_clase, path, nr_poze_per_cls, alg, f_vector, proc_vector, norm_vector, csv_bool, time_bool, plot_bool)
            except Exception:
                pass
            print("asta este calea bossss din celery" +path)
            timp=time.time()-start_timp
            timp=f"{timp:.2f}"
            date = {
            "path_grafice": path_grafice,
            "path_csv": path_csv,
            "timp": timp,
           
        }
            

            
            webhook_url = url+"/get_date/Webhook/proc_grafice"
            cookies = {'ASP.NET_SessionId': sesh_id}
            headers = {"Content-Type": "application/json"}
            print(path_grafice)
            print(path_csv)
            response = requests.post(webhook_url,cookies=cookies, json=date, headers=headers)
            return path_grafice,path_csv,timp
    except Exception as e:
        webhook_url = url+"/get_date/Webhook/grafice"
        cookies = {'ASP.NET_SessionId': sesh_id}
        headers = {"Content-Type": "application/json"}
                
        
        requests.post(webhook_url,cookies=cookies, json={"mesaj": "Eroare undeva:\n" + "".join(traceback.format_exception(type(e), e, e.__traceback__))}, headers=headers)
        

if __name__ == "__main__":
    # Setam apl să ruleze local pe portul 5030
    app.run(debug=True, host="0.0.0.0", port=5030)







    #teste si debugging celery

@celery.task(name='app.test')
def test(sesh_id):
    time.sleep(5)
    return 3


