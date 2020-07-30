import os

import librosa

from IPython.display import Audio
import IPython

def disp_wav(wav_file, sampling_rate=22050):
    assert os.path.exists(wav_file), '{} does not exist.'.format(wav_file)
    y, _ = librosa.load(wav_file)
    IPython.display.display(Audio(y, rate=sampling_rate))