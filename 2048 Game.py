import pygame
import random
import math

pygame.init()

FPS = 60

Width, Height = 650, 650
Rows = 4
Cls = 4
Rect_Hieght = Height // Rows
Rect_Width = Width // Cls

outline_colour = (187, 173, 160)
outline_thickness = 10
Background_colour = (205, 192, 180)
Font_colour = (119, 110, 101)

Font = pygame.font.SysFont("comicsans", 60, bold=True)
Move_vel = 30

WINDOW = pygame.display.set_mode((Width,Height))
pygame.display.set_caption("2048")

class Tile:
    COLOUR = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),
    ]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * Rect_Width
        self.y = row * Rect_Hieght

    def get_colour(self):
        colour_index = int(math.log2(self.value)) - 1
        colour = self.COLOUR[colour_index]
        return colour 

    def draw(self, window) :
        colour = self.get_colour()
        pygame.draw.rect(window, colour, (self.x, self.y, Rect_Width, Rect_Hieght))

        text = Font.render(str(self.value), 1, Font_colour)
        window.blit(
            text, 
            (
                self.x + (Rect_Width / 2 - text.get_width() / 2),
                self.y + (Rect_Hieght / 2 - text.get_height() / 2),
            ),
        )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / Rect_Hieght)
            self.col = math.ceil(self.x / Rect_Width)
        else:
            self.row = math.floor(self.y / Rect_Hieght)
            self.col = math.floor(self.x / Rect_Width)
        

    def move(self, delta):
        self.x += delta[0]
        self.y  += delta[1]
    

def draw_grid(window):
    for row in range(1, Rows):
        y = row * Rect_Hieght
        pygame.draw.line(window, outline_colour, (0, y),(Width, y), outline_thickness)

    for col in range(1, Cls):
        x = col * Rect_Width
        pygame.draw.line(window, outline_colour, (x, 0),(x, Height), outline_thickness)

    pygame.draw.rect(window, outline_colour, (0, 0, Width, Height), outline_thickness)

def draw(window, tiles):
    window.fill(Background_colour)

    for tile in tiles.values():
        tile.draw(window)
    
    draw_grid(window)

    pygame.display.update()

def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, Rows)
        col = random.randrange(0, Cls)

        if f"{row}{col}" not in tiles:
            break
    return row, col


def generate_tiles():
    tiles = {}
    for i in range(2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-Move_vel, 0)
        boundry_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + Move_vel
        move_check = (
            lambda tile, next_tile: tile.x > next_tile.x + Rect_Width + Move_vel
        )
        ceil = True

    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (Move_vel, 0)
        boundry_check = lambda tile: tile.col == Cls - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - Move_vel
        move_check = (
            lambda tile, next_tile: tile.x + Rect_Width + Move_vel < next_tile.x
        )
        ceil = False

    elif direction == "up":
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -Move_vel)
        boundry_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + Move_vel
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + Rect_Hieght + Move_vel
        )
        ceil = True
    elif direction == "down":
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, Move_vel)
        boundry_check = lambda tile: tile.row == Rows - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - Move_vel
        move_check = (
            lambda tile, next_tile: tile.y + Rect_Hieght + Move_vel < next_tile.y 
        )
        ceil = False

    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundry_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (tile.value == next_tile.value and tile not in blocks and next_tile not in blocks):
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue
            tile.set_pos(ceil)
            updated = True
        updated_tiles(window, tiles, sorted_tiles)

    return end_move(tiles)

def end_move(tiles):
    if len(tiles) == 16:
        return "Lost"
    
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2, 4]), row, col)
    return "Continue"

def updated_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile

    draw(window, tiles)  

def main(window):
    clock = pygame.time.Clock()
    run = True 

    tiles = generate_tiles()


    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, "left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, "right")
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, "up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, "down")


        draw(window, tiles)

    pygame.quit()
    
if __name__ == "__main__":
    main(WINDOW)