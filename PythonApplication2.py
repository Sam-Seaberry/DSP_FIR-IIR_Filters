import numpy as np
import wave, sys, math
import PySimpleGUI as gui


def convolve(data,fir, window):
  convolve = np.convolve(data,fir, mode='full') #conmvolves wav data with fir text in mode "full" which gives a output of array size M+N-1 
  #length = len(data)+len(fir)-1
  #y = [0]*length
  #z=0
  #for i in range(2,len(data)):
  #  for x in range(0,len(fir)):
  #     y[x+z] = y[x+z]+data[i-x]*fir[x] convolution using for loops very long exicution time 
  #  
  #z = z+1

  
  
  return (convolve[window:] - convolve[:-window]) / window #windows used to remove unnessisary data 

def conv(data, kernal): #second covolution fuction not used but more optimised than the one above
    y = [0]*(len(kernal)+len(data)-1)

    for i in range((len(kernal)-1), len(data)):
        for k in range(0,len(kernal)):
            j = i-1
            y[i] = y[i]+data[j]*kernal[k]
    for i in range(0,(len(kernal)-1)):
        k=0
        for j in range(i,0):
            k = k+1
            y[i] = y[i] + data[j]*kernal[k]
    return y


def get_data(raw, frames, channeln, samplewidth, interleaved = True):

    if samplewidth == 2:
        dtype = np.int16 # signed 2-byte short
    else:
        raise ValueError("Not Compatable format")

    data = np.frombuffer(raw, dtype=dtype) #converting bytes to int
    data.shape = (frames, channeln) 
    data = data.T
    

    return data

def firfilter(filename,impulse):

    fir = [float(x) for x in open(impulse).read().split()] #reads each line and splits into array of floats 
    fir = list(map(float,fir)) #creates a mapped list so np.convolve can be used 

    wav = wave.open(filename, 'r')
    samplerate = wav.getframerate()
    width = wav.getsampwidth()
    channeln = wav.getnchannels()
    frames = wav.getnframes()

    
    signal = wav.readframes(frames*channeln)
    wav.close()
    data = get_data(signal, frames, channeln, width, True)

    window = 512 #window defined 

    filtered = convolve(data[0],fir, window).astype(data.dtype)#only first channel of data used 
    #filt = conv(data[0],fir)

    wav_out = wave.open("fin.wav", "w")
    wav_out.setparams((1, width, samplerate, frames, wav.getcomptype(), wav.getcompname())) #set perameters of output wav file 
    wav_out.writeframes(filtered.tobytes('C')) #write filtered data to wav file 
    wav_out.close()

def zp(data, pole, zero, e, f): #zero pole placement 
    y = [0]*len(data)
    out = [0]*len(data)

    x = -2*zero*np.array(data) 
    y = e*np.array(data)
    out = np.array(y)*np.array(x)

    for i in range(2,len(data)):
        out[i] = out[i]-2*pole*out[i-1]-f*out[i-2]
        
        
        #y[i] = y[i]-2*zeroreal[0]*filter[i-1]+e1*filter[i-2]+2*polereal[0]*y[i-1]-f1*y[i-2] full iir function 

    out = out[2048:] - out[:-2048] / 2048
    return out

def IIR():

    wav = wave.open('test_2.wav', 'r')
    samplerate = wav.getframerate()
    width = wav.getsampwidth()
    channeln = wav.getnchannels()
    frames = wav.getnframes()

    
    signal = wav.readframes(frames*channeln)
    wav.close()
    data = get_data(signal, frames, channeln, width, True)

    txt = open('IIR', "r")
    iir = [line.strip().split() for line in txt.readlines()] #reads and creates list from pole zero file 

   
    zeroreal = [float(x) for x in np.array(iir[1:17])] # find the real/imaginary poles and zeros 
    zeroimag = [float(x) for x in np.array(iir[19:35])]

    polereal = [float(x) for x in np.array(iir[37:53])]
    poleimag = [float(x) for x in np.array(iir[55:71])]

    e1 = zeroreal[0]*zeroreal[0] + zeroimag[0]*zeroimag[0] 
    f1 = polereal[0]*polereal[0] + poleimag[0]*poleimag[0]

    e = [0]*16
    f = [0]*16
    out = [0]*957952



    for i in range(0,2):
        e[i] = zeroreal[i]*zeroreal[i] + zeroimag[i]*zeroimag[i]
        f[i] = polereal[i]*polereal[i] + poleimag[i]*poleimag[i]
        d = zp(data[0],polereal[i],zeroreal[i],e[i],f[i])
        out =  out + d
        
        
    
    filtering = out.astype(data.dtype)
    filtered = zp(data[0],polereal[0],zeroreal[0],e1,f1).astype(data.dtype)


    wav_out = wave.open("fin3.wav", "w")
    wav_out.setparams((1, width, samplerate, frames, wav.getcomptype(), wav.getcompname()))
    wav_out.writeframes(filtering.tobytes('C'))
    wav_out.close()




def GUI():
    layout = [  [gui.Text('Fir Impulse reponse', size=(20,1)), gui.Input(key='-Impulse-'), gui.FileBrowse()],
            [gui.Text('Wav File', size=(20,1)), gui.Input(key='-Fir-'), gui.FileBrowse()],
            [gui.Text('IIR Poles and Zeros', size=(20,1)), gui.Input(key='-Poles-'), gui.FileBrowse()],
            [gui.Text('Wav File', size=(20,1)), gui.Input(key='-IIR-'), gui.FileBrowse()],
            [gui.Button('Fir'), gui.Button('IIR'), gui.Button('Exit')]  ]

    window = gui.Window('Window Title', layout)

    while True:             # Event Loop
        event, values = window.read()
        #print(event, values)
        if event in (None, 'Exit'):
            break
        if event == 'Fir':
            firfilter(values['-Fir-'], values['-Impulse-'])
        if event == 'IIR':
            print("not yet")

    window.close()
    
GUI();    



