import pygame

class Button:
    def __init__(self, x, y, width, height, color, hover_color, text, font, on_click_function):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text = text
        self.font = font
        self.on_click_function = on_click_function
    
    def render(self, surface):
        pygame.draw.rect(surface, self.color, pygame.Rect(self.x + self.width / 2, self.y + self.height / 2, self.width, self.height), 0, 15)
        
        if pygame.Rect(self.x + self.width / 2, self.y + self.height / 2, self.width, self.height).collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, self.hover_color, pygame.Rect(self.x + self.width / 2, self.y + self.height / 2, self.width, self.height), 0, 15)

        text_render = self.font.render(self.text, True, "#000000")
        text_rect = text_render.get_rect(center = (self.x + self.width, self.y + self.height)) # fix me
        surface.blit(text_render, text_rect)
    
    def on_click(self, cursor_position):
        if pygame.Rect(self.x + self.width / 2, self.y + self.height / 2, self.width, self.height).collidepoint(cursor_position):
            self.on_click_function()
    
