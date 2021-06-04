import os

import librosa
import soundfile as sf
import scipy
import numpy as np


## this function not only change the sampling rate, but also change the bit rate.
## shouldn't be used.
# def change_sample_rate(wav_file_in, wav_file_out, sample_rate, std_out=True):
#     """ change the sample rate to the desired value."""
#     y, sample_rate_original = librosa.load(wav_file_in, sr=None)
#     y_, _ = librosa.load(wav_file_in, sr=sample_rate)
#     scipy.io.wavfile.write(wav_file_out, sample_rate, y_)
        
#     if std_out:
#         print('sample rate of {0} is converted from {1}[Hz] to {2}[Hz].'.format(
#             os.path.basename(wav_file_out), sample_rate_original, sample_rate))
        
        
def change_sample_bit_rate(wav_in_path, wav_out_path, sample_rate=22050, bit_rate=16, channel=1):
    ''' default setting is for waveglow_vocoder '''
    command = ('sox ' + wav_in_path 
                + ' -r ' + str(sample_rate) 
                + ' -b ' + str(bit_rate) 
                + ' -c ' + str(channel) 
                + ' ' + wav_out_path)
    os.system(command)


def trim_silB_silE_sox(wav_in_path, wav_out_path, duration_threshold=1, volume_threshold=0.1):
    '''
    trim silB (silence - begin) and silE (silence - end) using sox

    Args:
        wav_in_path: wav file to be trimmed.
        
        wav_out_path: wav file which is trimmed.
        
        duration_threshold: trim silence (anything less than {volume_threshold}%) 
            until we encounter sound lasting more than {duration_threshold} seconds in duration. 
            default value = 1
            
        volume_threshold: used to indicate what sample value you should treat as silence. 
            For digital audio, a value of 0 may be fine but for audio recorded from analog, 
            you may wish to increase the value to account for background noise.
            default value = 0.1
                
    '''
    command = ('sox ' + wav_in_path + ' ' + wav_out_path
                + ' silence 1 '
                + str(duration_threshold) + ' ' + str(volume_threshold)
                + '% reverse silence 1 '
                + str(duration_threshold) + ' ' + str(volume_threshold) 
                + '% reverse')
    os.system(command)


def calc_silB_silE(lab_path):
    '''
    lab_path: htk formatted label file.
    '''
    unit = 10 ** 7 # 100 ns = 100 x 10^(-9) = 10^(-7)
    with open(lab_path) as f:
        lines = f.read().split('\n')
    lines = [line.split() for line in lines if len(line.split()) == 3]

    # get the length of silB.
    pau = []
    for line in lines:
        if line[2] == 'pau':
            pau.append(line)
            break
    silB = [int(pau[0][0])/unit, 
            int(pau[-1][1])/unit]

    pau = []
    for line in reversed(lines):
        if line[2] == 'pau':
            pau.append(line)
            break
    silE = [int(pau[-1][0])/unit, 
            int(pau[0][1])/unit]
    
    return silB, silE


def trim_silB_silE_lab(wav_in_path, wav_out_path, lab_path):
    silB, silE = calc_silB_silE(lab_path)
    trim_start = silB[1]
    trim_duration = silE[0] - silB[1]
    #sox {wav_in_path} {wav_out_path} trim {trim_start} {trim_duration}
    command = ('sox ' + wav_in_path + ' ' + wav_out_path
                + ' trim '
                + str(trim_start) + ' ' + str(trim_duration)
                )
    os.system(command)


def load_wav(wav_path, sampling_rate=44100):
    signal, _ = librosa.load(wav_path, sr=sampling_rate)
    return signal


def get_length(wav_path):
    return librosa.get_duration(filename=wav_path)


def calc_rms(signal, frame_length=2048, hop_length=512, center=True):
    rms = librosa.feature.rms(
        signal, 
        frame_length=frame_length, 
        hop_length=hop_length, 
        center=True)
    return rms.T


def calc_zero_crossings(signal, frame_length=2048, hop_length=512, center=True):
    zero_crossings = librosa.feature.zero_crossing_rate(
        signal, 
        frame_length=frame_length, 
        hop_length=hop_length, 
        center=True)
    return zero_crossings.T


def normalize_rms(signal, rms_target=0.02):
    rms = calc_rms(signal)
    rms_mean = np.mean(rms[np.nonzero(rms)])
    a = rms_target / rms_mean
    return signal * a


def normalize_rms_file(wav_in_path, wav_out_path, rms_target=0.02, sampling_frequency=44100):
    wav_in  = load_wav(wav_in_path)
    wav_out = normalize_rms(wav_in, rms_target)

    #maxv = np.iinfo(np.int16).max
    #librosa.output.write_wav(wav_out_path, wav_out.astype(np.int16), sampling_frequency)
    sf.write(wav_out_path, wav_out, sampling_frequency)