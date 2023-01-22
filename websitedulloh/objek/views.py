from django.shortcuts import render
from django.core.files.storage import default_storage
import record
import time
t = time.time()

def index(req):
    context = {
        "title" : "objek",
        "status":" ",
        "mic": [],
        "time": t,
        "judul": " "
    }
    context["mic"]= record.listMic()

    if "btn_record" in req.POST:
        mic1 = req.POST["mic1"]
        mic2 = req.POST["mic2"]
        judul = req.POST["name"]
        context["status"] = record.record(mic1,mic2,title="objek",label=judul)
    
    if "btn_upload" in req.POST:
        fileDekat = req.FILES["micDekat"]
        fileJauh = req.FILES["micJauh"]
        judul = req.POST["name"]
        context["judul"] = judul 

        context["status"] = record.upload(fileDekat,fileJauh,title="objek",label=judul)
        
    return render(req, "objek/index.html", context)
