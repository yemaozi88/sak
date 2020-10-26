import os

import librosa
import scipy
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def display_spectrogram(x, png_file=None):
    axarr = plt.subplot()
    axarr.imshow(x, aspect='auto', origin='lower', interpolation='nearest', cmap=cm.viridis)
    if not png_file == None:
        plt.savefig(png_file)


def change_sample_rate(wav_file_in, wav_file_out, sample_rate, std_out=True):
    """ change the sample rate to the desired value."""
    y, sample_rate_original = librosa.load(wav_file_in, sr=None)
    y_, _ = librosa.load(wav_file_in, sr=sample_rate)
    scipy.io.wavfile.write(wav_file_out, sample_rate, y_)
        
    if std_out:
        print('sample rate of {0} is converted from {1}[Hz] to {2}[Hz].'.format(
            os.path.basename(wav_file_out), sample_rate_original, sample_rate))
        
        
def change_sample_bit_rate(wav_file_in, wav_file_out, sample_rate=22050, bit_rate=16, channel=1):
    ''' default setting is for waveglow_vocoder '''
    command = 'sox ' + wav_file_in + ' -r ' + str(sample_rate) + ' -b ' + str(bit_rate) + ' -c ' + str(channel) + ' ' + wav_file_out
    os.system(command)
