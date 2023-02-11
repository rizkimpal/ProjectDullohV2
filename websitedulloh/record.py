import pyaudio
import wave
import numpy as np
from scipy.io import wavfile
import audio as aud

sample = 0
def listMic():

    p = pyaudio.PyAudio()
    micArr = []
    num_devices = p.get_device_count()
    #print("Daftar mikrofon yang tersedia:")
    for i in range(num_devices):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            micArr.append([f"{i}", f"{info['name']}"])
    print(f"tersedia microphone sejumlah:  {i}")
    return(micArr)

def record(mice1,mice2,title,label):
    p = pyaudio.PyAudio()

    #get index for microphone 
    mic1_index = int(mice1)
    mic2_index = int(mice2)
    
    mic1_info = p.get_device_info_by_index(mic1_index)
    mic2_info = p.get_device_info_by_index(mic2_index)

    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record 44100 samples per second
    seconds = 15  # Record for 5 seconds

    status = "Recording" #Status Record
    print(status)
    # Initialize arrays to store the recorded data
    frames1 = []
    frames2 = []

    # Open a connection to microphone 1
    mic1 = p.open(format=sample_format,
            channels=channels,
            rate=fs,
            frames_per_buffer=chunk,
            input_device_index=mic1_index,  # Use the selected microphone
            input=True)

    # Open a connection to microphone 2
    mic2 = p.open(format=sample_format,
            channels=channels,
            rate=fs,
            frames_per_buffer=chunk,
            input_device_index=mic2_index,  # Use the selected microphone
            input=True)

    # Record data from microphone 1
    for i in range(0, int(fs / chunk * seconds)):
        data = mic1.read(chunk)
        frames1.append(data)

    # Record data from microphone 2
    for i in range(0, int(fs / chunk * seconds)):
        data = mic2.read(chunk)
        frames2.append(data)

    # Stop and close the streams
    mic1.stop_stream()
    mic1.close()
    mic2.stop_stream()
    mic2.close()

    # Terminate the PortAudio interface
    p.terminate()

    status = "Finished Recording, saving....."
    print(status)

    # Save the recorded data as WAV files
    wf = wave.open(f"media/{title}/audio/voiceDekat.wav", 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames1))
    wf.close()

    wf = wave.open(f"media/{title}/audio/voiceJauh.wav", 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames2))
    wf.close()

    status = "Audio Saved"
    getNewAudio(title,label)
    aud.analisisFFT(sample,title,label)
    return(status)

def upload(short,long,title,label):
    p = pyaudio.PyAudio()
    with open(f'media/{title}/audio/voiceDekat.wav', 'wb') as destination:
        for chunk in short.chunks():
            destination.write(chunk)
        print(f"Audio Dekat saved ")
    with open(f'media/{title}/audio/voiceJauh.wav', 'wb') as destination:
        for chunk in long.chunks():
            destination.write(chunk)
        print(f"Audio Jauh saved ")
    
    status = "Audio dekat dan jauh sudah tersimpan"
    status = "Audio Saved"
    getNewAudio(title,label)
    aud.analisisFFT(sample,title,label)
    return(status)

#fungsi mendapatkan audio baru 
def getNewAudio(Title,label):

    MJ_BG = f"media/{Title}/audio/voiceDekat.wav"
    MD_BG = f"media/{Title}/audio/voiceJauh.wav"
        
    sr_MJ_BG, MJ_BG = aud.read_audio(MJ_BG)
    sr_noise, MD_BG = aud.read_audio(MD_BG)

    MJ_BG = MJ_BG.astype(float)
    MD_BG = aud.generate_noise_sample(MD_BG,sr_noise, 2)

    output_BG = aud.noise_red(MJ_BG, MD_BG,Title, fft_size=4096, iterations=3)
    if(label == "background"):
        db = wavfile.write(f'media/{Title}/audio/New Audio {label}.wav', 44100, output_BG.astype(np.int16))
        status = "background sudah terinput"
    else:
        global sample
        sample += 1
        db = wavfile.write(f'media/{Title}/audio/New Audio {sample}.wav', 44100, output_BG.astype(np.int16))
        MJ_BG = f"media/background/audio/New Audio background.wav"
        MD_BG = f"media/{Title}/audio/New Audio {sample}.wav"
        sr_MJ_BG, MJ_BG = aud.read_audio(MJ_BG)
        sr_noise, MD_BG = aud.read_audio(MD_BG)

        MJ_BG = MJ_BG.astype(float)
        MD_BG = aud.generate_noise_sample(MD_BG,sr_noise, 2)

        output_BG = aud.noise_red(MJ_BG, MD_BG,Title, fft_size=4096, iterations=3)
        db = wavfile.write(f'media/final/audio/Final Audio {sample}.wav', 44100, output_BG.astype(np.int16))
        status = f"success membuat final audio dengan nama Final Audio {sample}.wav"
    return(status)