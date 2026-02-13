import pyttsx3

engine = pyttsx3.init()

voices = engine.getProperty("voices")

print(voices[2].id)

engine.setProperty("voice", voices[1].id)


engine.setProperty("rate", 128)
print(voices[3])
engine.setProperty("voice", voices[3].id)

engine.say("Your Voice generated")

engine.save_to_file('Необязательно быть великим, чтобы начать, но нужно начать, чтобы стать великим..', 'russian_test_irina.mp3')

engine.runAndWait()