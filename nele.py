import os
import sys
import array
import random
import wave
import tempfile

import numpy as np
import librosa
from pystoi import stoi
from pysiib import SIIB
from . import signal_processing as sp


# Calculation of amp
def calc_amp(wf):
    buffer = wf.readframes(wf.getnframes())
    amptitude = (np.frombuffer(buffer, dtype="int16")).astype(np.float64)
    return amptitude


# calculation of RMS
def calc_rms(amp):
    return np.sqrt(np.mean(np.square(amp), axis=-1))


# Synthesize waveforms of any size
def calc_adjusted_rms(clean_rms, snr=0):
    a = float(snr) / 20
    noise_rms = clean_rms / (10**a) 
    return noise_rms


# A series of processes in one
def add_noise(wav_clean_path, wav_noise_path, wav_mix_path, snr=0):
    # open wav file
    clean_wav = wave.open(wav_clean_path, "r")
    noise_wav = wave.open(wav_noise_path, "r")
                    
    # Calculation of amp
    clean_amp = calc_amp(clean_wav)
    noise_amp = calc_amp(noise_wav)
                                    
    # Calculation of RMS
    start = random.randint(0, len(noise_amp)-len(clean_amp))
    clean_rms = calc_rms(clean_amp)
    split_noise_amp = noise_amp[start: start + len(clean_amp)]
    noise_rms = calc_rms(split_noise_amp)
                                                            
    # Synthesize waveforms of any size
    adjusted_noise_rms = calc_adjusted_rms(clean_rms, snr)
           
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


def create_noise_mask(
    wav_clean_path, wav_noise_path, wav_noise_mask_path, 
    sampling_frequency=44100, randomize=True):
    '''
    Args:
        randomize (binary): if the start position of the input should be randomized.
    '''

    # load signal from wav files.
    wav_clean = sp.load_wav(wav_clean_path)
    wav_noise = sp.load_wav(wav_noise_path)

    # triple the length of noise file.
    wav_noise3 = np.r_[wav_noise, wav_noise, wav_noise]
 
    if randomize:
        mask_start = random.choice(np.arange(len(wav_noise)))
    else:
        #mask_start = 100000
        mask_start = 0
    noise_mask = wav_noise3[mask_start:mask_start+len(wav_clean)]

    librosa.output.write_wav(wav_noise_mask_path, noise_mask, sampling_frequency)


def add_noise2(
    wav_clean_path, 
    wav_noise_path, 
    wav_mixed_path, 
    wav_noise_out_path=None, 
    snr=0, 
    sampling_frequency=44100, 
    randomize=True):
    '''
    re-implement add noise function using librosa and sak. 
    '''
    # load signal from wav files.
    signal_clean = sp.load_wav(wav_clean_path)
    signal_noise = sp.load_wav(wav_noise_path)

    # if the length of signal and noise does not match
    # make noise mask.
    if not len(signal_noise) == len(signal_clean):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        create_noise_mask(
            wav_clean_path, 
            wav_noise_path, 
            temp_file.name, 
            sampling_frequency=sampling_frequency, randomize=randomize)
        signal_noise = sp.load_wav(temp_file.name)
        os.remove(temp_file.name)

    # calculate average rms. 
    rms_clean = np.mean(sp.calc_rms(signal_clean))
    rms_noise = np.mean(sp.calc_rms(signal_noise))

    # energy_noise = energy_signal / exp(SNR / 20)
    a = float(snr) / 20
    rms_noise_desired = rms_clean / (10**a)

    # adjust rms of noise and add to signal_clean.
    signal_noise_desired = signal_noise * rms_noise_desired / rms_noise
    signal_mixed = signal_clean + signal_noise_desired

    # output the signal.
    librosa.output.write_wav(wav_mixed_path, signal_mixed, sampling_frequency)
    if not wav_noise_out_path==None:
        librosa.output.write_wav(wav_noise_out_path, signal_noise_desired, sampling_frequency)


def calc_stoi_file(wav_clean_path, wav_mixed_path, sampling_frequency=44100):
    # load signal from wav files.
    signal_clean = sp.load_wav(wav_clean_path)
    signal_mixed = sp.load_wav(wav_mixed_path)
    
    # calculate stoi
    stoi_score = stoi(signal_clean, signal_mixed, sampling_frequency, extended=False)

    return stoi_score


def calc_siib_file(wav_clean_path, wav_mixed_path, sampling_frequency=44100):
    '''
    Optional Parameters:
        gauss (bool): Use SIIB^Gauss.
        use_MI_Kraskov (bool): Use C-implementation for SIIB calculation.
            This is not valid for SIIB^Gauss mode.
        window_length (float):
        window_shift (float):
        window (str):
        delta_dB (float)): VAD threshold
    '''
    # load signal from wav files.
    signal_clean = sp.load_wav(wav_clean_path)
    signal_mixed = sp.load_wav(wav_mixed_path)

    # calculate SIIB
    siib_score = SIIB(signal_clean, signal_mixed, sampling_frequency, gauss=True)

    return siib_score
