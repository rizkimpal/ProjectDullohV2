import IPython
from scipy.io import wavfile
import scipy.signal
import contextlib
import sys
import wave
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display
import time
from datetime import timedelta as td
from spectrum import *
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)

sinyalName = []

def get_parameters(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        pcm_data = wf.readframes(wf.getnframes())
        return num_channels, sample_width, sample_rate, type(pcm_data)
    
def read_audio(path):
    samprate_audio, audio = wavfile.read(path)
    num_channels, samp_width, samp_rate, type= get_parameters(path)
    if num_channels!=1:
        audio = audio[:,1]
    return samprate_audio, audio

def generate_noise_sample(noise,sr_noise, length):
    MD = noise[:sr_noise*length]
    MD = np.asarray(MD, dtype=float)
    return MD
  
def plot_spectrogram(signal, path, title):
    plt.figure(figsize=(20, 4))
    librosa.display.specshow(signal, sr=44100, x_axis='time', y_axis='hz')
    plt.title(title)
    plt.colorbar()
    plt.savefig(f"media/{path}/img/{title}.png")

def plot_statistics_and_filter(mean_MD, std_MD, th, smoothing_filter,path):
    fig, ax = plt.subplots(figsize=(20,5))
    plt_mean, = ax.plot(mean_MD, label='Rata-rata noise')
    #plt_std, = ax.plot(std_noise, label='Std. power of noise')
    plt_std, = ax.plot(th, label='Threshold noise')
    ax.set_title('Threshold untuk mask')
    ax.legend()
    plt.savefig(f"media/{path}/img/Threshold untuk mask.png")
    
def removeNoise(MJ, MD,path, n_grad_freq=2, n_grad_time=4, n_fft=4096, win_length=4096, hop_length=512,
                n_std_th=1.5, prop_decrease=0, verbose=False, visual=False):
        
    # STFT pada MD
    MD_stft = librosa.stft(MD, n_fft, hop_length, win_length, window='hann')
    MD_abs = np.abs(MD_stft)
    MD_stft_db = librosa.core.amplitude_to_db(MD_abs, ref=1.0, amin=1e-20, top_db=80.0)
        
    # Hitung statistik pada MD
    mean_MD = np.mean(MD_stft_db, axis =1)
    std_MD = np.std(MD_stft_db, axis =1)
    th = mean_MD + (std_MD * n_std_th)
    # n_std_th: berapa banyak standar deviasi yang lebih keras dari rata-rata dB kebisingan
    #           (pada setiap tingkat frekuensi) yang dianggap sebagai sinyal
        
    # STFT pada MJ
    MJ_stft = librosa.stft(MJ, n_fft, hop_length, win_length, window='hann')
    MJ_abs = np.abs(MJ_stft)
    MJ_stft_db = librosa.core.amplitude_to_db(MJ_abs, ref=1.0, amin=1e-20, top_db=80.0)
        
    # Hitung nilai minimal untuk mask
    mask_gain_dB = np.min(MJ_stft_db)
    if verbose: print(noise_th, mask_gain_dB)
    
    # Buat smoothing filter untuk mask pada time dan frequency
    smoothing_filter = np.outer(np.concatenate([np.linspace(0,1, n_grad_freq + 1, endpoint=False),
                                                np.linspace(1,0, n_grad_freq + 2)])[1:-1],
                                np.concatenate([np.linspace(0,1, n_grad_time + 1, endpoint=False),
                                                np.linspace(1,0, n_grad_time + 2)])[1:-1])
    
    smoothing_filter = smoothing_filter/np.sum(smoothing_filter)
    
    # Hitung threshold untuk setiap frequency/time bin
    db_th = np.repeat(np.reshape(th, [1,len(mean_MD)]), np.shape(MJ_stft_db)[1], axis = 0).T
    
    # mask jika sinyal diatas threshold
    MJ_mask = MJ_stft_db<db_th
        
    # Operasi konvolusi mask dengan smoothing filter
    MJ_mask = scipy.signal.fftconvolve(MJ_mask, smoothing_filter,  mode='same')
    MJ_mask = MJ_mask*prop_decrease
        
    # mask sinyal
    MJ_stft_db_masked = MJ_stft_db *(1-MJ_mask) + np.ones(np.shape(mask_gain_dB))*mask_gain_dB*MJ_mask # mask real
    MJ_imag_masked = np.imag(MJ_stft)*(1-MJ_mask)
    MJ_amp = librosa.core.db_to_amplitude(MJ_stft_db_masked,ref=1.0)
    MJ_stft_amp = (MJ_amp * np.sign(MJ_stft)) + (1j * MJ_imag_masked)
        
    # Penerapan ISTFT
    recovered_signal = librosa.istft(MJ_stft_amp, 
                                     hop_length=512, 
                                     win_length=4096, 
                                     window='hann')
    recovered_STFT = librosa.stft(recovered_signal, n_fft, hop_length, win_length, window='hann')
    recovered_abs = np.abs(recovered_STFT)
    recovered_spec = librosa.core.amplitude_to_db(recovered_abs, ref=1.0, amin=1e-20, top_db=80.0)
    if verbose: print('Signal recovery:', td(seconds=time.time()-start));
    if visual: plot_spectrogram(MD_stft_db,path, title='Mic Dekat')
    if visual: plot_statistics_and_filter(mean_MD, std_MD, th, smoothing_filter,path)
    if visual: plot_spectrogram(MJ_stft_db,path, title='Mic Jauh')
    if visual: plot_spectrogram(MJ_mask,path, title='Penerapan Mask')
    if visual: plot_spectrogram(MJ_stft_db_masked,path, title='Masked signal')
    if visual: plot_spectrogram(recovered_spec,path, title='Recovered spectrogram')
    return recovered_signal

def noise_red(MJ, MD,path, prop_decrease = 0.5, verbose = False, visual = False, fft_size = 4096, iterations = 2,):
    output = removeNoise(MJ, MD,path, n_fft = fft_size, win_length = fft_size, prop_decrease = prop_decrease,
                         n_std_th=1.0, verbose=False, visual=True)
    iterations = iterations - 1
    while(iterations!=0):
        output = removeNoise(output, MD,path, n_fft = fft_size, win_length = fft_size, prop_decrease = prop_decrease, verbose=False, visual=False)
        iterations = iterations - 1
    return output

def noise_red2(MJ, MD, prop_decrease = 0.5, verbose = False, visual = False, fft_size = 4096, iterations = 6):
    output = removeNoise(MJ, MD, n_fft = fft_size, win_length = fft_size, prop_decrease = prop_decrease,
                         n_std_th=0.5, verbose=False, visual=True)
    iterations = iterations - 1
    while(iterations!=0):
        output = removeNoise(output, MD, n_fft = fft_size, win_length = fft_size, prop_decrease = prop_decrease,
                             n_std_th=0.5, verbose=False, visual=False)
        iterations = iterations - 1
    return output

def analisisFFT(sample,path,label):
    convertFromPSD = 10**(-77/20)
    x = 1
    sinyal = []
    fig, ax = plt.subplots(figsize=(20,8))
    while(x <= sample):
        AudioName = f"media/{path}/audio/New Audio background {x}.wav"  # Audio File
        fs, data = wavfile.read(AudioName)
        convertFromPSD = 10**(-70.5/20)
        dB = data*convertFromPSD
        global sinyalName
        sinyalName.append(label)
        sinyal.append(WelchPeriodogram(dB, NFFT=2048, sampling=fs,
                               label=sinyalName[x-1]))
        x += 1

    plt.ylabel('dB', size="24", font="Times New Roman")
    plt.xlim(2500, 8000)
    plt.xlabel('Frekuensi (Hz)', size=24, font="Times New Roman")
    ax.xaxis.set_major_locator(MultipleLocator(200))
    ax.yaxis.set_major_locator(MultipleLocator(5))
    ax.set_title('Analisis Frekuensi', size=72, font="Times New Roman")
    ax.legend(fontsize=18)
    plt.savefig(f'media/{path}/img/analisisFFT.png')
    return{
        print(f"successfully done from make background analisis")
    }