from django.shortcuts import render
import pyaudio
import wave

def index(req):
    context = {
        "status":" ",
        "mic": []
    }
    p = pyaudio.PyAudio()
    num_devices = p.get_device_count()
    print("Daftar mikrofon yang tersedia:")
    for i in range(num_devices):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            context["mic"].append([f"{i}", f"{info['name']}"])
        print(context["mic"])

    if "btn_record" in req.GET:

        context["status"] = "Recording"
        print(context["status"])
        mic1_info = p.get_device_info_by_index(1)
        mic2_info = p.get_device_info_by_index(5)

        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record 44100 samples per second
        seconds = 15  # Record for 5 seconds

        # Initialize arrays to store the recorded data
        frames1 = []
        frames2 = []

        # Open a connection to microphone 1
        mic1 = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input_device_index=1,  # Use the selected microphone
                input=True)

        # Open a connection to microphone 2
        mic2 = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input_device_index=5,  # Use the selected microphone
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

        context["status"] = "Finished Recording, saving....."
        print(context["status"])

        # Save the recorded data as WAV files
        wf = wave.open(f"audio/mic1.wav", 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames1))
        wf.close()

        wf = wave.open(f"audio/mic2.wav", 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames2))
        wf.close()

        context["status"] = "Audio Saved"
        print(context["status"])

    return render(req, "coba.html", context)
# Create your views here.
