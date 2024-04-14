import speech_recognition as sr


def detect_keyword(keywords):

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                print("Listening for keyword...")
                audio = recognizer.listen(source=source, timeout=3, phrase_time_limit=3)
                text = recognizer.recognize_google(audio, language="en-IN")
                print("Heard:", text)
                for keyword in keywords:
                    if keyword in text.lower():
                        print("Keyword detected:", keyword)
                        return keyword
            except sr.WaitTimeoutError:
                print("Timeout occurred. Listening again...")
            except sr.UnknownValueError:
                print("Could not understand audio")
            except sr.RequestError as e:
                print("Could not request results; {0}".format(e))


