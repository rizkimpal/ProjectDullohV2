from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'background.html')
def objek(request):
    return render(request, 'objek.html')
def analisisFFT(request):
    return render(request, 'analisisFFT.html')
