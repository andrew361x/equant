import wave
import pyaudio


class PlayAudio(object):
    '''播放音频文件'''
    _audioDict = {
        'Signal' : r'./audio/Fail.wav',
        'Fail'   : r'./audio/Fail.wav',
    }
    
    def __init__(self):
        pass
        
    @staticmethod
    def play(audioType):
        if audioType not in PlayAudio._audioDict:
            return
            
        #open a wav format music
        f = wave.open(PlayAudio._audioDict[audioType],"rb")
        #instantiate PyAudio
        p = pyaudio.PyAudio()
        #open stream
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                        channels = f.getnchannels(),
                        rate = f.getframerate(),
                        output = True)
                        
        #read data
        data = f.readframes(1024)
         
        #paly stream
        while data != b'':
            stream.write(data)
            data = f.readframes(1024)
         
        #stop stream
        stream.stop_stream()
        stream.close()
        
        #close PyAudio
        p.terminate()