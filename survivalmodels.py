# Survival models

import numpy as np
    
def survival(n,t):
    coeff = np.array([8.81848, 9.41225, 11.96006, 10.72095, 11.02082, 10.31950, 9.26393, 13.99271, 13.73019, 13.97148, 15.44454, 14.84630, 8.88931])
    
    st = np.exp(-1*np.exp(-(coeff[n-1]))*t)
    return st