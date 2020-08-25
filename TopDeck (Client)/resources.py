
import pygame
from pygame.locals import *

class Resources:

    def __init__(self):
        self.images = {}
        self.fonts = {}
        pygame.init() #incase the pygame module was not already initialized

    def get_image(self, file_name):
        if file_name in self.images.keys():
            return self.images[file_name]
        else:
            image = pygame.image.load(file_name)
            self.images[file_name] = image
            return self.images[file_name]

    def get_card_image(self, file_name, card_size):
        if file_name in self.images.keys():
            return self.images[file_name]
        else:
            image = pygame.image.load(file_name)
            image = pygame.transform.scale(image, card_size)
            self.images[file_name] = image
            return self.images[file_name]

    def get_font(self, file_name, size=13):
        if file_name in self.fonts.keys():
            return self.fonts[file_name]
        else:
            font = pygame.font.Font(file_name, size)
            self.fonts[file_name] = font
            return self.fonts[file_name]
    '''
    def get_font(self, file_name, size):
        if file_name in self.fonts.keys():
            return self.fonts[file_name]
        else:
            font = pygame.font.Font(file_name, size)
            self.fonts[file_name] = font
            return self.fonts[file_name]
    '''