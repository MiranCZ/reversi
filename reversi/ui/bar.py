import pygame

class Bar:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.percentage = 0.5
    
    def render(self, surface):
        pygame.draw.rect(surface, "#000000", pygame.Rect(self.x, self.y, self.width, self.height), 0, 15)
        pygame.draw.rect(surface, "#ffffff", pygame.Rect(self.x, self.y, self.width, self.height * self.percentage), 0, 15)
        pygame.draw.rect(surface, "#B08968", pygame.Rect(self.x, self.y, self.width, self.height), 12, 15)
