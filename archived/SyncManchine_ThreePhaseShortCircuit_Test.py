# Leo Fitzgerald
# Phyton code plotting Synchronous Machine Three Phase Short Circuit Fault Response
# 15th September 2024

# This was derived from lecturers notes by Dr. Brian Johnston at University of Idaho Power System Lectuer

import math 
import numpy as np
import matplotlib.pyplot as plt

def Iass():
    """Calculate subtransient current."""
    return (Eass / (complex(0,Xdss) + complex(0,X_tran)))
  
def Ias():
    """Calculate transient current."""
    return (Eas / (complex(0,Xds) + complex(0,X_tran)))

def Iss():
    """Calculate steady state current."""
    return (Ea / (complex(0,Xd) + complex(0,X_tran)))

def Idcoffsetmax():
    """Calculate maximum direct current."""
    return math.sqrt(2) * (Eass/ ((complex(0,Xdss) + complex(0,X_tran))))

def Iss_time(t):
    """Calculate steady state current."""
    return (math.sqrt(2) * abs(Iss()) * np.cos(oemega * t)) 

def Itransient(t):
    """Calculate transient current."""
    return np.exp(-t/Tds) * math.sqrt(2) * abs(Ias()) * np.cos(oemega * t)

def Isubtransient(t):
    """Calculate subtransient current."""
    return np.exp(-t/Tdss) * math.sqrt(2) * abs(Iass()) * np.cos(oemega * t)

def fullsymresponse(t): ########## need to verify = incomplete / issues
    '''Calculate full symmetrical response.'''
    return math.sqrt(2)*Eass * (1/(Xd + X_tran)) +\
    ((1/(Xds+X_tran)) - (1/(Xd+X_tran))) * np.exp(-t/Tds) +\
    ((1/(Xdss+X_tran)) - (1/(Xds+X_tran))) * (np.exp(-t/Tdss)) * np.cos(oemega * t)                    

'''Plot the three currents.'''
# def plot(t, Iss_time, Itransient, Isubtransient):
#     plt.plot(t, Iss_time(t))
#     plt.plot(t, Itransient(t))
#     plt.plot(t, Isubtransient(t))
#     plt.legend(["Iss_time", "Itransient", "Isubtransient"])
#     plt.xlim(0,0.8)
#     plt.show()

##################Generator Parameters##################
pu = 1
S_rated = 20 # MVA
VLL     = 13.8
Xdss    = 0.145
Xds     = 0.240
Xd      = 1.100
oemega = math.pi*2*50

X2      = Xdss
X_tran  = 0.0
V_term  = 1.0
Tdss    = 0.035 #sec
Tds     = 1     # sec
Ta      = 0.2   # sec

L2 = (X2/oemega) * ((VLL**2)/S_rated)
Ra = (L2/Ta)

Eass    = V_term
Eas     = V_term
Ea      = V_term
##################Generator Parameters##################

Ibase = S_rated * math.pow(10,6) / (1.732 * VLL * math.pow(10,3))
t = np.arange(0, 2, 0.00001) # start, stop, step

# plot(t, Iss_time, Itransient, Isubtransient)  # Call the plot function



def plot_subplots(t, Iss_time, Itransient, Isubtransient, fullsymresponse):
    plt.figure(figsize=(10, 8))

    # Plot all currents
    plt.subplot(4, 1, 1)
    plt.plot(t, Iss_time(t))
    plt.plot(t, Itransient(t))
    plt.plot(t, Isubtransient(t))
    plt.legend(["Iss_time", "Itransient", "Isubtransient"], loc="upper right")
    plt.xlim(0,0.8)
    # plt.show()

    # Subplot 1: Iss_time
    plt.subplot(4, 1, 4)
    plt.plot(t, Iss_time(t),color='blue')
    plt.title("Iss_time")
    plt.legend(["Iss_time"])
    plt.xlim(0, 0.8)

    # Subplot 2: Itransient
    plt.subplot(4, 1 ,3)
    plt.plot(t, Itransient(t), color='orange')
    plt.title("Itransient")
    plt.legend(["Itransient"])
    plt.xlim(0, 0.8)

    # Subplot 3: Isubtransient
    plt.subplot(4, 1, 2)
    plt.plot(t, Isubtransient(t), color='green')
    plt.title("Isubtransient")
    plt.legend(["Isubtransient"])
    plt.xlim(0, 0.8)

    # # Subplot 4: Full symmetrical response
    # plt.subplot(5, 1, 4)
    # plt.plot(t, fullsymresponse(t), color='orange')
    # plt.title("Full Symmetrical Response")
    # plt.legend(["Full Symmetrical Response"])
    # plt.xlim(0, 0.8)

    plt.tight_layout()
    plt.show()

plot_subplots(t, Iss_time, Itransient, Isubtransient, fullsymresponse)  # Call the plot function