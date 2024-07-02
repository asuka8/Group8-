from gtts import gTTS
import pygame
import time
from datetime import datetime
import os

def text_to_speech(text, lang):
    tts = gTTS(text=text, lang=lang, slow = False)
    
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    audio_file = f'./guide_voice_{timestamp}.mp3'
    tts.save(audio_file)
    
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    
    time.sleep(0.5)
    os.remove(audio_file)
