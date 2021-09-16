import numpy as np
import scipy.stats as st

def confidence_interval(a):
    c1, c2 = st.t.interval(0.95, len(a)-1, loc=np.mean(a), scale=st.sem(a))
    h = c2 - np.mean(a)
    return h
