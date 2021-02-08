import os
import sys
import array
import random
import wave
import numpy as np


# Calculation of amp
def cal_amp(wf):
    buffer = wf.readframes(wf.getnframes())
    amptitude = (np.frombuffer(buffer, dtype="int16")).astype(np.float64)
    return amptitude

# Calculation of RMS
def cal_rms(amp):
    return np.sqrt(np.mean(np.square(amp), axis=-1))

# Synthesize waveforms of any size
def cal_adjusted_rms(clean_rms, snr=0):
    a = float(snr) / 20
    noise_rms = clean_rms / (10**a) 
    return noise_rms

# A series of processes in one
def add_noise(wav_clean_path, wav_noise_path, wav_mix_path, snr=0):
    # open wav file
    clean_wav = wave.open(wav_clean_path, "r")
    noise_wav = wave.open(wav_noise_path, "r")
                    
    # Calculation of amp
    clean_amp = cal_amp(clean_wav)
    noise_amp = cal_amp(noise_wav)
                                    
    # Calculation of RMS
    start = random.randint(0, len(noise_amp)-len(clean_amp))
    clean_rms = cal_rms(clean_amp)
    split_noise_amp = noise_amp[start: start + len(clean_amp)]
    noise_rms = cal_rms(split_noise_amp)
                                                            
    # Synthesize waveforms of any size
    adjusted_noise_rms = cal_adjusted_rms(clean_rms, snr)
           
    adjusted_noise_amp = split_noise_amp * (adjusted_noise_rms / noise_rms) 
    mixed_amp = (clean_amp + adjusted_noise_amp)
                                                                                    
    # Normalized so as not to crack the sound
    if (mixed_amp.max(axis=0) > 32767):
        mixed_amp = mixed_amp * (32767/mixed_amp.max(axis=0))
        clean_amp = clean_amp * (32767/mixed_amp.max(axis=0))
        adjusted_noise_amp = adjusted_noise_amp * (32767/mixed_amp.max(axis=0))
                                                                                                                            
    # output noisy file
    noisy_wave = wave.Wave_write(wav_mix_path)
    noisy_wave.setparams(clean_wav.getparams())
    noisy_wave.writeframes(array.array('h', mixed_amp.astype(np.int16)).tostring() )
    noisy_wave.close()
