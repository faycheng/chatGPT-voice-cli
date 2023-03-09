import queue
import time
import threading

from conf import settings
import azure.cognitiveservices.speech as speechsdk



class Recognizer:
    __instance = None

    @staticmethod
    def get():
        if Recognizer.__instance == None:
            Recognizer()
        return Recognizer.__instance

    def __init__(self):
        if Recognizer.__instance != None:
            raise Exception("a singleton can not be initiated multiple times")
        else:
            speech_config = speechsdk.SpeechConfig(subscription=settings.azure_key, region=settings.azure_region)
            speech_config.speech_recognition_language = settings.language
            audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
            speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            Recognizer.__instance = speech_recognizer


class Synthesizer:
    __instance = None

    @staticmethod
    def get():
        if Synthesizer.__instance == None:
            Synthesizer()
        return Synthesizer.__instance

    def __init__(self):
        if Synthesizer.__instance != None:
            raise Exception("a singleton can not be initiated multiple times")
        else:
            speech_config = speechsdk.SpeechConfig(subscription=settings.azure_key, region=settings.azure_region)
            speech_config.speech_recognition_language = settings.language
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            Synthesizer.__instance = synthesizer
            synthesizer.speak_text(" ")


def init():
    Recognizer()
    Synthesizer()


def get_recognizer():
    return Recognizer.get()


def get_synthesizer():
    return Synthesizer.get()


def synthesize_and_speak(q):
    futures = queue.Queue()
    streams = [None for i in range(1000)]
    futures_lock = threading.Lock()
    streams_lock = threading.Lock()

    def handle_interrupt(func):
        def inner():
            try:
                func()
            except KeyboardInterrupt:
                return
        return inner

    def synthesize():
        while True:
            try:
                future_tuple = futures.get(timeout=10)
                if type(future_tuple[0]) == str:
                    idx = future_tuple[1]
                    streams[idx] = "IM_EOF"
                    return
            except queue.Empty:
                return
            stream = speechsdk.speech.AudioDataStream(future_tuple[0].get())
            idx = future_tuple[1]
            with streams_lock:
                streams[idx] = stream

    t1 = threading.Thread(target=synthesize)
    t2 = threading.Thread(target=synthesize)
    t3 = threading.Thread(target=synthesize)

    t1.start()
    t2.start()
    t3.start()
    idx = 0

    def speak():
        idx = 0
        while True:
            with streams_lock:
                stream = streams[idx]
            if stream is None:
                time.sleep(0.01)
                continue
            if stream == "IM_EOF":
                return
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                stream.save_to_wav_file(f.name)
                from playsound import playsound
                playsound(f.name)
            idx += 1

    speaker = threading.Thread(target=speak)
    speaker.start()
    while True:
        try:
            text = q.get(timeout=10)
            if text == "IM_EOF":
                futures.put_nowait(["IM_EOF", idx])
                futures.put_nowait(["IM_EOF", idx])
                futures.put_nowait(["IM_EOF", idx])
                t1.join()
                t2.join()
                t3.join()
                speaker.join()
                return
            ssml = construct_ssml(text)
            future = get_synthesizer().speak_ssml_async(ssml)
            with futures_lock:
                futures.put_nowait([future, idx])
                idx += 1
        except queue.Empty:
            t1.join()
            t2.join()
            t3.join()
            speaker.join()
            return


def construct_ssml(text, speed=100):
    ssml = '''<speak version="1.0" xmlns="https://www.w3.org/2001/10/synthesis" xml:lang="en-US">
      <voice name="en-US-AIGenerate1Neural">
        <prosody rate="-{}.00%">
      {}
        </prosody>
      </voice>
    </speak>'''
    return ssml.format(100 - speed, text)
