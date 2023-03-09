import time
import fire
import queue
import prompt_toolkit
import threading
import sys

from prompt_toolkit.input import create_input
from prompt_toolkit.keys import Keys

from chatgpt import ChatBot
from speech_recognition import get_recognizer
from speech_recognition import get_synthesizer

bot = ChatBot()


class AiBotFire(object):
    @staticmethod
    def __ask_and_speak(prompt, need_speak=True):
        print_queue = queue.Queue()
        synthesize_queue = queue.Queue()
        speak_queue = queue.Queue()

        def print_answer():
            while True:
                try:
                    text = print_queue.get(timeout=3)
                    sys.stdout.write(text)
                    sys.stdout.flush()
                except queue.Empty:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return

        def synthesize_answer():
            if not need_speak:
                return
            current = []
            cnt = 1
            while True:
                try:
                    word = synthesize_queue.get(timeout=3)
                    current.append(word)

                    def endswith(text):
                        symbols = [",", ".", "?", "!", "'", '"']
                        for symbol in symbols:
                            if text.endswith(symbol):
                                return True

                    if endswith(word):
                        threshold = cnt * 16
                        if threshold > 128:
                            threshold = 128
                        if len(current) < threshold:
                            continue
                        speak_queue.put_nowait("".join(current))
                        current = []
                        cnt += 1
                        continue
                except queue.Empty:
                    if current:
                        speak_queue.put_nowait(" ".join(current))
                    speak_queue.put_nowait("IM_EOF")
                    return

        def speak_answer():
            from speech_recognition import synthesize_and_speak
            synthesize_and_speak(speak_queue)

        printer_thread = threading.Thread(target=print_answer)
        synthesizer_thread = threading.Thread(target=synthesize_answer)
        speaker_thread = threading.Thread(target=speak_answer)
        printer_thread.start()
        synthesizer_thread.start()
        speaker_thread.start()
        for word in bot.ask(prompt):
            print_queue.put_nowait(word)
            synthesize_queue.put_nowait(word)
        printer_thread.join()
        synthesizer_thread.join()
        speaker_thread.join()

    @staticmethod
    def text_conversation():
        from speech_recognition import init
        init()
        while True:
            prompt = prompt_toolkit.prompt("you:")
            AiBotFire.__ask_and_speak(prompt, True)

    @staticmethod
    def voice_conversation():
        from speech_recognition import init
        init()

        recognizer = get_recognizer()
        synthesizer = get_synthesizer()

        def recognize_and_answer():
            data = []
            import sys
            def handle_final_result(evt):
                data.append(evt.result.text)
                sys.stdout.write(evt.result.text)
                sys.stdout.flush()

            recognizer.recognized.connect(handle_final_result)
            recognizer.start_continuous_recognition()
            input = create_input()
            while True:
                press_enter = False
                for key_press in input.read_keys():
                    print(key_press.key)
                    if key_press.key == Keys.Escape:
                        recognizer.stop_continuous_recognition()
                        return
                    if key_press.key == Keys.ControlJ:
                        press_enter = True
                        break
                if press_enter is True:
                    break
            recognizer.stop_continuous_recognition()
            print_queue = []
            synthesize_queue = []
            speak_queue = []
            import threading
            print_lock = threading.Lock()
            synthesize_lock = threading.Lock()
            speak_lock = threading.Lock()

            def print_answer():
                while True:
                    with print_lock:
                        for word in print_queue:
                            sys.stdout.write(word)
                            sys.stdout.flush()
                        print_queue.clear()
                    time.sleep(0.01)

            def synthesize_answer():
                while True:
                    current = []
                    speak = False
                    with synthesize_lock:
                        for word in synthesize_queue:
                            current.append(word)
                            if word.endswith(",") or word.endswith(".") or word.endswith("?"):
                                speak = True
                                break
                        if len(current) > 0 and speak:
                            synthesize_queue = synthesize_queue[len(current):]
                    if current:
                        with speak_lock:
                            speak_queue.append(synthesizer.speak_text_async(" ".join(current)))
                    time.sleep(0.01)

            def speak_answer():
                while True:
                    with speak_lock:
                        if not speak_queue:
                            time.sleep(0.01)
                            continue
                        head = speak_queue[0]
                        speak_queue.remove(head)
                        head.get()

            printer_thread = threading.Thread(target=print_answer)
            synthesizer_thread = threading.Thread(target=synthesize_answer)
            speaker_thread = threading.Thread(target=speak_answer)
            printer_thread.start()
            synthesizer_thread.start()
            speaker_thread.start()
            for word in bot.ask(" ".join(data)):
                print_queue.append(word)
                synthesize_queue.append(word)
            printer_thread.join()
            synthesizer_thread.join()
            speaker_thread.join()

        print("Speak into your microphone.")
        while True:
            recognize_and_answer()


def main():
    fire.Fire(AiBotFire)


if __name__ == '__main__':
    fire.Fire(AiBotFire)
