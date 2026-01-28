import pygame

class AudioPlayer:
    def __init__(self, path):
        pygame.mixer.init()
        self.path = path
        self.playing = False

    def play(self):
        if not self.playing:
            pygame.mixer.music.load(self.path)
            pygame.mixer.music.play(-1)
            self.playing = True

    def stop(self):
        if self.playing:
            pygame.mixer.music.stop()
            self.playing = False
