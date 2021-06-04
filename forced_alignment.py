import os
import sys
import shutil
import tempfile

import textgrids
import pandas as pd

lexicon_txt    = r'/home/common/db/audio_corpora/Librispeech/librispeech-lexicon.txt'
acoustic_model = r'/home/akikun/projects/mfa/english.zip'

def forced_alignment(wav_path, 
                     lab_path, 
                     mfa_dir, 
                     lexicon_txt=lexicon_txt, 
                     acoustic_model=acoustic_model):
    #temp_dir = r'/home/akikun/projects/auto_eval/tts_en/temp'
    #os.makedirs(temp_dir)
    temp_dir = tempfile.mkdtemp()
    shutil.copy(wav_path, os.path.join(temp_dir, os.path.basename(wav_path)))
    shutil.copy(lab_path, os.path.join(temp_dir, os.path.basename(lab_path)))

    # forced-alignment
    command = ('mfa align ' + temp_dir 
                + ' ' + lexicon_txt 
                + ' ' + acoustic_model
                + ' ' + mfa_dir)
    os.system(command)

    # read the result.
    speaker = os.path.basename(temp_dir)
    shutil.rmtree(temp_dir)

    textgrid_path = os.path.join(mfa_dir, 
        speaker + '-' + os.path.basename(wav_path).replace('.wav', '.TextGrid'))
    os.path.exists(textgrid_path)
 
    grid = textgrids.TextGrid(textgrid_path)
    os.rename(textgrid_path, textgrid_path.replace(speaker + '-', ''))
    
    return grid


def grid2df(grid):
    text = []
    xmin = []
    xmax = []
    for line in grid['phones']:
        text.append(line.text)
        xmin.append(line.xmin)
        xmax.append(line.xmax)
    df = pd.DataFrame({
        'phones': text,
        'start': xmin,
        'end': xmax        
    })
    return df