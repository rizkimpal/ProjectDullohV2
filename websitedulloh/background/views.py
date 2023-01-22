from django.shortcuts import render
import record
import time

def index(req):

    t = time.time()
    
    context = {
        "title":"background",
        "judul":"background",
        "status":" ",
        "mic": [],
        "time" : t
    }
    context["mic"]= record.listMic()
    if "btn_record" in req.POST:
        mic1 = req.POST["mic1"]
        mic2 = req.POST["mic2"]
        context["status"] = record.record(mic1,mic2,title="background",label="background")
        context["mic"]= record.listMic()
    
    if "btn_upload" in req.POST:
        fileDekat = req.FILES["micDekat"]
        fileJauh = req.FILES["micJauh"]
        context["mic"]= record.listMic()
        
        context["status"] = record.upload(fileDekat,fileJauh,title="background",label="background")
    return render(req, 'background/index.html',context)