import pyaudio
import wave

#variable untuk menyimpan text
array = []

# Buat objek PyAudio
p = pyaudio.PyAudio()

# Dapatkan jumlah perangkat audio yang tersedia
num_devices = p.get_device_count()

# Tampilkan daftar mikrofon yang tersedia
print("Daftar mikrofon yang tersedia:")
for i in range(num_devices):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        array.append(f"{i}: {info['name']}")
        print(array)

# Pilih mikrofon 1
mic1_index = int(input("Pilih mikrofon 1 (masukkan nomor): "))
mic1_info = p.get_device_info_by_index(mic1_index)

# Pilih mikrofon 2
mic2_index = int(input("Pilih mikrofon 2 (masukkan nomor): "))
mic2_info = p.get_device_info_by_index(mic2_index)

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 1
fs = 44100  # Record 44100 samples per second
seconds = 5  # Record for 5 seconds

# Initialize arrays to store the recorded data
frames1 = []
frames2 = []

print('Recording')

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

print('Finished recording')

# Save the recorded data as WAV files
wf = wave.open("mic1.wav", 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames1))
wf.close()

wf = wave.open("mic2.wav", 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames2))
wf.close()

