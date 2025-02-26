import pygame
from core.gamemanager import GameManager
import math
from ui.button import Button
from ui.bar import Bar

# fixes weird windows resize issue
# from: https://stackoverflow.com/a/32063729
try:
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

pygame.display.init()
pygame.font.init()

game_display = pygame.display.set_mode(((pygame.display.Info().current_w, pygame.display.Info().current_h)), pygame.FULLSCREEN|pygame.SCALED)
clock = pygame.time.Clock()
pygame.display.set_caption("Reversi")
font = pygame.font.Font('ui/Mont-HeavyDEMO.otf', 40)
font_stopwatch = pygame.font.Font('ui/Mont-HeavyDEMO.otf', 80)
font_stopwatch_victory = pygame.font.Font('ui/Mont-HeavyDEMO.otf', 60)
running = True

size = 960
width, height = pygame.display.get_surface().get_size()
rect_y = height/2 - size/2
rect_x = width/2 - size/2

delta_time = 0
seconds = 0
minutes = 0
minutes_ten = 0
seconds_ten = 0

player_turn = False
game_ended = False

button = None

bar = Bar(rect_x - 250, rect_y, 100, size)

def set_player_turn(value):
    global player_turn
    player_turn = value

def on_game_ended():
    global game_ended
    game_ended = True

gamemanager = GameManager(True, False, set_player_turn, on_game_ended, bar)
board = gamemanager.game.board

def draw_text(text, font, text_color, x, y):
    text_output = font.render(text, True, text_color)
    text_rect = text_output.get_rect(center = (x, y))
    game_display.blit(text_output, text_rect)

def draw_scoreboard():
    width, height = pygame.display.get_surface().get_size()
    rect_y = height/2 - size/2
    rect_x = width/2 - size/2

    if gamemanager.is_white_playing():
        pygame.draw.rect(game_display, "#B08968", pygame.Rect(rect_x + size + 50, size / 2 - 60, 200, 150), 0, 15)
        pygame.draw.rect(game_display, "#DDB892", pygame.Rect(rect_x + size + 260, size / 2 - 60, 200, 150), 0, 15)
    elif gamemanager.is_black_playing():
        pygame.draw.rect(game_display, "#DDB892", pygame.Rect(rect_x + size + 50, size / 2 - 60, 200, 150), 0, 15)
        pygame.draw.rect(game_display, "#B08968", pygame.Rect(rect_x + size + 260, size / 2 - 60, 200, 150), 0, 15)

    draw_text("Black", font, (0, 0, 0), rect_x + size + 150, size / 2 - 30)
    draw_text("White", font, (0, 0, 0), rect_x + size + 360, size / 2 - 30)

    draw_text(str(board.get_b_sutry()), font_stopwatch, (0, 0, 0), rect_x + size + 150, size / 2 + 40)
    draw_text(str(board.get_w_sutry()), font_stopwatch, (0, 0, 0), rect_x + size + 360, size / 2 + 40)

def draw_board():
    width, height = pygame.display.get_surface().get_size()
    rect_y = height/2 - size/2
    rect_x = width/2 - size/2

    pygame.draw.rect(game_display, "#DDB892", pygame.Rect(rect_x, rect_y, size, size), 0, 15)
    pygame.draw.rect(game_display, "#7f5539", pygame.Rect(rect_x - 5, rect_y - 5, size + 10, size + 10), 10, 15)

    number_y = size
    for i in range(7):
        number_y -= size / 8
        pygame.draw.line(game_display, "#7f5539", (rect_x - 4, rect_y + number_y), (rect_x + size, rect_y + number_y), width = 10)
    
    number_x = size
    for i in range(7):
        number_x -= size / 8
        pygame.draw.line(game_display, "#7f5539", (rect_x + number_x, rect_y), (rect_x + number_x, rect_y + size), width = 10)

def draw_disks():
    valid_moves = gamemanager.game.get_moves_for_now_player()

    for row in range(8):
        for column in range(8):
            if board.board[row][column] == "W":
                disk_color = "#ffffff"
            elif board.board[row][column] == "B":
                disk_color = "#000000"
            elif board.board[row][column] == ".":
                if (row, column) in valid_moves and not gamemanager.game.natahu.is_bot:
                    pygame.draw.circle(game_display, "#B08968", (rect_x + (row * size / 8) + size / 16 + 1, rect_y + (column * size / 8) + size / 16 + 1), 25)
                continue
            
            pygame.draw.circle(game_display, disk_color, (rect_x + (row * size / 8) + size / 16 + 1, rect_y + (column * size / 8) + size / 16 + 1), 50)

def rnd(x):
    if x % 1 >= 0.5:
        return math.ceil(x)
    return math.floor(x)

def reset():
    global delta_time, seconds, minutes, minutes_ten, seconds_ten, game_ended, gamemanager, board, button
    delta_time = 0
    seconds = 0
    minutes = 0
    minutes_ten = 0
    seconds_ten = 0
    gamemanager = GameManager(True, False, set_player_turn, on_game_ended, bar)
    board = gamemanager.game.board
    game_ended = False
    button = None
    bar.percentage = 0.5

def victory_screen():
    global button

    overlay = pygame.Surface(pygame.display.get_surface().get_size())
    overlay.set_alpha(180)
    overlay.fill("black")
    game_display.blit(overlay, (0, 0))

    pygame.draw.rect(game_display, "#E6CCB2", pygame.Rect(width / 2 - 350, height / 2 - 200, 700, 400), 0, 10)

    if gamemanager.game.winner() == "W":
        draw_text("White won!", font_stopwatch, "#000000", width / 2, height / 2 - 130)
    elif gamemanager.game.winner() == "B":
        draw_text("Black won!", font_stopwatch, "#000000", width / 2, height / 2 - 130)
    else:
        draw_text("Tie!", font_stopwatch, "#000000", width / 2, height / 2 - 130)
    draw_text(f"Game took: {minutes_ten}{minutes}:{seconds_ten}{seconds}", font_stopwatch_victory, "#000000", width / 2 , height / 2 - 30)

    button = Button(width / 2 - 300, height / 2, 300, 100, "#DDB892", "#B08968", "Play again", font, reset)
    button.render(game_display)


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONUP:
            cursor_position = event.pos
            
            if pygame.Rect(rect_x, rect_y, size, size).collidepoint(cursor_position):
                x = rnd((cursor_position[0] - 1 - size / 16 - rect_x) / (size / 8))
                y = rnd((cursor_position[1] - 1 - size / 16 - rect_y) / (size / 8))
                
                if player_turn:
                    gamemanager.on_player_move(x, y)
            
            if button is not None:
                button.on_click(cursor_position)

    delta_time += clock.tick() / 1000

    game_display.fill("#E6CCB2")
    draw_board()
    draw_scoreboard()
    draw_disks()
    bar.render(game_display)

    gamemanager.tick()

    pygame.draw.rect(game_display, "#DDB892", pygame.Rect(rect_x + size + 50, size / 2 + 100, 410, 200), 0, 15)
    draw_text(f"{minutes_ten}{minutes}:{seconds_ten}{seconds}", font_stopwatch, (0, 0, 0), rect_x + size + 50 + 205, size / 2 + 30 + 175)
    
    if game_ended == False:
        if delta_time > 1:
            seconds += 1
            delta_time = 0

            if seconds == 10:
                seconds_ten += 1
                seconds = 0
            if seconds_ten == 6:
                seconds_ten = 0
                seconds = 0
                minutes += 1
            if minutes == 10:
                minutes_ten += 1
                minutes = 0
    
    if game_ended:
        victory_screen()
    
    pygame.display.flip()

pygame.quit()