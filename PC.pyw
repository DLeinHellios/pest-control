#!/usr/bin/env python3
# Pest Control - Battle for the Lawn
#   Requires Python 3 and Pygame library

import pygame as pg
import os, sys
from random import randint



class Window:
    def __init__(self):
        '''Create screen surface object'''
        self.screen = pg.display.set_mode((650,625))
        self.rect = self.screen.get_rect()
        pg.display.set_icon(pg.image.load(os.path.join("img", "icon.png")))
        pg.display.set_caption("Pest Control | Battle for the Lawn")



class Unit:
    def __init__(self, coords, image, active):
        '''Define a single unit'''
        self.coords = coords
        self.image = image
        self.active = active
        self.rect = self.image.get_rect()
        self.rect.top = 30 + (64 * self.coords[1])
        self.rect.left = 69 + (64 * self.coords[0])

    def draw(self, window, selected_coords):
        '''Draws a single unit'''
        if selected_coords == self.coords:
            window.screen.blit(self.active, self.rect)
        else:
            window.screen.blit(self.image, self.rect)



class Player:
    def __init__(self, team):
        '''Initialize empty player object'''
        self.units = [] # Holds player's unit objects
        self.image = pg.image.load(os.path.join("img", "units", "P"+str(team) + ".png")).convert_alpha()
        self.active = pg.image.load(os.path.join("img", "units", "P"+str(team) + "_S.png")).convert_alpha()
        self.rect = self.image.get_rect()


    def get_unit_coords(self):
        '''Returns all currently-occupied tile coordinates'''
        ally_coords = []
        for unit in self.units:
            ally_coords.append(unit.coords)

        return ally_coords


    def check_adjacent(self, center):
        '''Calculates and returns coordinates adjacent to center value'''
        adjacent_coords = []
        for u in self.units:
            if u.coords == center or (abs(center[0] - u.coords[0]) <= 1 and abs(center[1] - u.coords[1]) <= 1):
                adjacent_coords.append(u.coords)

        return adjacent_coords


    def add_units(self, coords_list):
        '''Accepts list of coordinates, generates units at those coordinates'''
        for u in range(len(coords_list)):
            self.units.append(Unit(coords_list[u], self.image, self.active))


    def remove_units(self, coords_list):
        '''Accepts lists of coordinates, removes units found, returns coordinates of removed units'''
        removed_coords = []
        units_copy = self.units.copy()
        for i in units_copy:
            if i.coords in coords_list:
                self.units.remove(i)
                removed_coords.append(i.coords)

        return removed_coords


    def move_unit(self, old_coords, new_coords, opponent):
        '''Conducts move action of a single unit'''
        self.add_units([new_coords]) # Add new unit
        self.remove_units([old_coords]) # Remove old unit
        self.add_units(opponent.remove_units(opponent.check_adjacent(new_coords))) # Handle opponent conversion


    def copy_unit(self, new_coords, opponent):
        '''Conducts copy unit of a single unit'''
        self.add_units([new_coords]) # Add new unit
        self.add_units(opponent.remove_units(opponent.check_adjacent(new_coords))) # Handle unit conversion


    def draw_units(self, window, selected_coords):
        '''Draws all living units'''
        for unit in self.units:
            unit.draw(window, selected_coords)



class Tile:
    def __init__(self, coords, image):
        '''Create individual tile object at specified coordinates'''
        self.coords = coords
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.top = 30 + (64 * self.coords[1])
        self.rect.left = 69 + (64 * self.coords[0])


    def draw(self, window):
        '''Draws a single tile'''
        window.screen.blit(self.image, self.rect)



class Board:
    def __init__(self, player1, player2):
        '''Create object containing all tile objects and board variables'''
        self.tileImage = pg.image.load(os.path.join("img", "tiles", "tile.gif")).convert()
        self.copyImage = pg.image.load(os.path.join("img", "tiles", "copy.png")).convert_alpha()
        self.moveImage = pg.image.load(os.path.join("img", "tiles", "move.png")).convert_alpha()

        self.moveTiles = []
        self.copyTiles = []
        self.turn_rect = self.tileImage.get_rect()

        # Populate Tiles
        self.tiles = []
        for tileX in range(8):
            for tileY in range(8):
                self.tiles.append(Tile((tileX,tileY), self.tileImage))

        # Populate units
        player1.add_units([(0,0),(0,7)])
        player2.add_units([(7,0),(7,7)])


    def check_turn_tiles(self, center, all_units):
        '''Accepts a single unit and list of all unit coords, returns valid move and copy coords'''
        move, copy = [],[]
        for tile in self.tiles:
            if tile.coords in all_units:
                continue
            if abs(center[0] - tile.coords[0]) <= 1 and abs(center[1] - tile.coords[1]) <= 1:
                copy.append(tile.coords)
            elif abs(center[0] - tile.coords[0]) <= 2 and abs(center[1] - tile.coords[1]) <= 2:
                move.append(tile.coords)

        return move,copy


    def set_turn_tiles(self, center, all_units):
        '''Populates tiles for valid unit move/copy actions'''
        self.moveTiles, self.copyTiles = self.check_turn_tiles(center, all_units)


    def convert_position(self, position):
        '''Converts pixel position to tile position'''
        sel_tile = None
        for tile in self.tiles:
            if tile.rect.collidepoint(position):
                sel_tile = tile.coords

        return sel_tile


    def draw(self, window):
        '''Draws all board tiles'''
        for tile in self.tiles:
           tile.draw(window)


    def draw_turn_tiles(self, window, selected):
        '''Draws all valid move/copy indicators if unit is selected'''
        if selected != None:
            for tile in self.copyTiles:
                self.turn_rect.top = 30 + (64 * tile[1])
                self.turn_rect.left = 69 + (64 * tile[0])
                window.screen.blit(self.copyImage, self.turn_rect)

            for tile in self.moveTiles:
                self.turn_rect.top = 30 + (64 * tile[1])
                self.turn_rect.left = 69 + (64 * tile[0])
                window.screen.blit(self.moveImage, self.turn_rect)



class UI:
    def __init__(self):
        '''Creates object to manage UI elements'''
        self.bg = pg.image.load(os.path.join("img","ui","bg.png"))

        self.turn_indicator = {
            "1":pg.image.load(os.path.join("img","ui","turn_1.png")).convert_alpha(),
            "2":pg.image.load(os.path.join("img","ui","turn_2.png")).convert_alpha()}
        self.indicator_rect = self.turn_indicator["1"].get_rect()
        self.indicator_rect.center= (325,585)

        self.unit_counts = [0,0,0,0] # P1 tens, P1 ones, P2 tens, P1 ones
        self.unit_counter = [
            pg.image.load(os.path.join("img","ui","n0.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n1.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n2.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n3.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n4.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n5.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n6.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n7.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n8.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","n9.png")).convert_alpha()]

        self.counter_rects = {
            "1-0":self.unit_counter[0].get_rect(), # P1 tens
            "1-1":self.unit_counter[0].get_rect(), # P1 ones
            "2-0":self.unit_counter[0].get_rect(), # P2 tens
            "2-1":self.unit_counter[0].get_rect()} # P2 ones

        self.counter_rects["1-0"].center = (41,595)  # P1 tens
        self.counter_rects["1-1"].center = (95,595)  # P1 ones
        self.counter_rects["2-0"].center = (555,595) # P2 tens
        self.counter_rects["2-1"].center = (609,595) # P2 ones


    def update_counts(self, player1, player2):
        '''Counts units on both player teams and formats for count images'''
        self.unit_counts[0] = len(player1.units) // 10
        self.unit_counts[1] = len(player1.units) % 10
        self.unit_counts[2] = len(player2.units) // 10
        self.unit_counts[3] = len(player2.units) % 10


    def draw(self, window, turn, game_over):
        '''Draws all UI'''
        window.screen.blit(self.bg,window.rect)

        window.screen.blit(self.unit_counter[self.unit_counts[0]],self.counter_rects["1-0"])
        window.screen.blit(self.unit_counter[self.unit_counts[1]],self.counter_rects["1-1"])
        window.screen.blit(self.unit_counter[self.unit_counts[2]],self.counter_rects["2-0"])
        window.screen.blit(self.unit_counter[self.unit_counts[3]],self.counter_rects["2-1"])

        if not game_over:
            window.screen.blit(self.turn_indicator[str(turn)],self.indicator_rect)


class Game:
    def __init__(self):
        '''Top-level object for managing game function'''
        self.start()


    def start(self):
        '''Sets game variables to initial values'''
        self.ui = UI()
        self.player1 = Player(1)
        self.player2 = Player(2)
        self.board = Board(self.player1, self.player2)

        self.turn = randint(1,2) # Current player turn
        self.selected = None
        self.game_over = False
        self.ui.update_counts(self.player1,self.player2)


    def check_valid_moves(self, player):
        '''Accepts player int, returns bool indicating if player has viable moves'''
        all_units = self.player1.get_unit_coords() + self.player2.get_unit_coords()
        valid_moves = False

        if player == 1:
            for unit in self.player1.get_unit_coords():
                move, copy = self.board.check_turn_tiles(unit, all_units)
                if len(move) or len(copy) > 0:
                    valid_moves = True
                    break

        elif player == 2:
            for unit in self.player2.get_unit_coords():
                move, copy = self.board.check_turn_tiles(unit, all_units)
                if len(move) or len(copy) > 0:
                    valid_moves = True
                    break

        return valid_moves


    def check_game_over(self):
        '''Reads game object conditions and updates self.game_over flag'''
        if len(self.player1.units) + len(self.player2.units) == len(self.board.tiles):
            self.game_over = True # Board full

        elif len(self.player1.units) == 0 or len(self.player2.units) == 0:
            self.game_over = True # One player has no units

        elif self.turn == 1:
            if not self.check_valid_moves(2):
                self.game_over = True # Player 2 can take no action

        elif self.turn == 2:
            if not self.check_valid_moves(1):
                self.game_over = True # Player 1 can take no action


    def flip_turn(self):
        '''Flip player turn after player action'''
        self.selected = None
        self.ui.update_counts(self.player1,self.player2)
        self.check_game_over()

        if self.turn == 1:
            self.turn = 2
        elif self.turn == 2:
            self.turn = 1


    def select(self, coords):
        '''Selects unit and prepares for unit action'''
        self.selected = None
        all_units = self.player1.get_unit_coords() + self.player2.get_unit_coords()

        if self.turn == 1:
            for unit in self.player1.units:
                if unit.coords == coords:
                    self.selected = coords
                    self.board.set_turn_tiles(coords, all_units)

        elif self.turn == 2:
            for unit in self.player2.units:
                if unit.coords == coords:
                    self.selected = coords
                    self.board.set_turn_tiles(coords, all_units)


    def action(self, coords):
        '''Conducts unit action following unit selection'''
        if self.selected != None and coords in self.board.copyTiles:
            if self.turn == 1:
                self.player1.copy_unit(coords, self.player2)
                self.flip_turn()

            elif self.turn == 2:
                self.player2.copy_unit(coords, self.player1)
                self.flip_turn()

        elif self.selected != None and coords in self.board.moveTiles:
            if self.turn == 1:
                self.player1.move_unit(self.selected, coords, self.player2)
                self.flip_turn()

            elif self.turn == 2:
                self.player2.move_unit(self.selected, coords, self.player1)
                self.flip_turn()

        else:
            self.select(coords) # Select another unit


    def keydown_event(self, event):
        '''Handles keypress event'''
        if event.key == pg.K_ESCAPE:
            sys.exit()

        #elif event.key == pg.K_r:
                #self.start() # Manual game reset


    def mouse_event(self, event):
        '''Handles mouse-click event'''
        sel_tile = self.board.convert_position(pg.mouse.get_pos())

        if event.button == 1:
            # Left-click
            self.action(sel_tile)


    def events(self):
        '''Sorts events into specific handlers'''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            elif event.type == pg.KEYDOWN:
                self.keydown_event(event)

            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_event(event)


    def check_winner(self):
        '''Checks player unit counts and returns int of winner (tie returns 0)'''
        if len(self.player1.units) > len(self.player2.units):
            winner = 1
        elif len(self.player1.units) < len(self.player2.units):
            winner = 2
        else:
            winner = 0

        return winner


    def update(self):
        '''Reads self.game_over flag and returns state value'''
        new_state = 1
        if self.game_over:
            self.check_winner()
            new_state = 2

        return new_state


    def draw(self, window):
        '''Top-level drawing of all game objects'''
        self.ui.draw(window, self.turn, self.game_over)
        self.board.draw(window)
        self.player1.draw_units(window, self.selected)
        self.player2.draw_units(window, self.selected)
        self.board.draw_turn_tiles(window, self.selected)



class Results:
    def __init__(self):
        '''Object to manage game over specific functions'''
        self.overlay = [
            pg.image.load(os.path.join("img","ui","overlay_0.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","overlay_1.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","overlay_2.png")).convert_alpha()]
        self.overlay_rect = self.overlay[0].get_rect()
        self.button = [
            pg.image.load(os.path.join("img","ui","replay_0.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","replay_1.png")).convert_alpha(),
            pg.image.load(os.path.join("img","ui","replay_2.png")).convert_alpha()]
        self.button_rect = self.button[0].get_rect()

        self.overlay_rect.topleft = (69,30)
        self.button_rect.center = (325,585)

        self.replay = False


    def events(self):
        '''Conducts events on game over screen'''
        for event in pg.event.get():
            if event.type == pg.QUIT:
                sys.exit()

            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    sys.exit()
                elif event.key == pg.K_RETURN:
                    self.replay = True

            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and self.button_rect.collidepoint(pg.mouse.get_pos()):
                    self.replay = True


    def update(self, game):
        '''Updates state if replay flag is flipped, starting new game'''
        new_state = 2
        if self.replay:
            new_state = 1
            self.replay = False
            game.start()

        return new_state


    def draw(self, window, game):
        game.draw(window)
        window.screen.blit(self.overlay[game.check_winner()], self.overlay_rect)
        window.screen.blit(self.button[game.check_winner()], self.button_rect)



# =========================================
def main():
    # Setup
    window = Window()
    game = Game()
    results = Results()
    clock = pg.time.Clock()
    state = 1

    while True:
        # Main game loop
        if state == 1:
            # Game Active
            game.events()
            state = game.update()
            game.draw(window)

        elif state == 2:
            results.events()
            state = results.update(game)
            results.draw(window, game)

        pg.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    main()
