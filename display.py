import os

import librosa
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from IPython.display import Audio
import IPython

def disp_wav(wav_file, sampling_rate=22050, offset=None, duration=None):
    '''
    duration: how long will be read [s]. 
            when not specified, everything will be read (default). 
    '''
    assert os.path.exists(wav_file), '{} does not exist.'.format(wav_file)
    if (offset == None) and (duration == None):
        y, _ = librosa.load(wav_file, sr=sampling_rate)
    else:
        y, _ = librosa.load(wav_file, sr=sampling_rate, offset=offset, duration=duration)
    IPython.display.display(Audio(y, rate=sampling_rate))


def disp_spectrogram(x, png_file=None):
    axarr = plt.subplot()
    axarr.imshow(x, aspect='auto', origin='lower', interpolation='nearest', cmap=cm.viridis)
    if not png_file == None:
        plt.savefig(png_file)