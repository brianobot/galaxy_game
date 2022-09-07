from kivy.config import Config
from kivy.uix.relativelayout import RelativeLayout
Config.set('graphics', 'width', '900') #setting the application window width
Config.set('graphics', 'height', '400') #setting the application window height

import kivy
kivy.require('1.9.0')
from kivy.app import App
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ObjectProperty, StringProperty
from kivy.graphics.vertex_instructions import Line
from kivy.graphics import Quad, Color, Triangle
from kivy.properties import Clock
from kivy.core.window import Window
from kivy import platform
from random import choice
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
import time

Builder.load_file("menu.kv")

# the root widget , for creating the whole GUI
class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_Perspective #module containing important transformation functions
    from user_actions import _on_keyboard_down, _on_keyboard_up, on_touch_down, on_touch_up 

    menuwidget = ObjectProperty()
    score_menu = StringProperty()
    
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    menu_title = StringProperty("G   A   L   A   X   Y")
    menu_button = StringProperty("START")

    V_NB_LINES = 8 #number of vertical lines in the game window
    V_SPACING = .2 #percentage spacing of the vertical lines with respect to game window
    vertical_lines = [] #list holding ref to all vertical lines in the game screen

    H_NB_LINES = 15 #number of horizontal lines in the game
    H_SPACING = .25  # percentage spacing of the horizontal lines with respec to game width
    horizontal_lines = [] # list holding ref to all horozontal lines in the game screen

    current_offset_y = 0  # diff between declared lines and drawn line in y axis
    #testing exponential speed 
    SPEED = 4  # vertical speed of grids, downwards speed
    current_loop = 0

    SPEED_x = 12 # horizontal speed
    current_offset_x = 0    # diff betweem declared lines and drawn lines in x axis

    current_speed_x = 0 # instantaneous speed on x axis

    NB_TILES = 15 #number of tiles to be used in the display
    tiles = [] #this is a variable to hold the tile list reference
    tile = None #for testing of a single tile display (uncomment tile variable and comment tiles variable if you want to test single tile)
    tiles_coordinates = [] #list to all the generate tiles coordinate

    ti_x, ti_y = 1, 4

    ship = None
    SHIP_WIDTH = .1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04

    ship_coordinates = [(0,0),(0,0),(0,0)]

    state_game_over = False
    state_game_started = False

    sound_begin = None
    sound_galaxy = None
    game_soundtrack = None
    gameover_sound = None
    gameimpact = None

  
    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        self.init_audio()
        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_close, self)
            self._keyboard.bind(on_key_down=self._on_keyboard_down)
            self._keyboard.bind(on_key_up=self._on_keyboard_up)
        Clock.schedule_interval(self.update, 1/60 )

    def init_audio(self):
        self.sound_begin = SoundLoader.load(r"audio\begin.wav")
        self.sound_galaxy = SoundLoader.load(r"audio\galaxy.wav")
        self.game_soundtrack = SoundLoader.load(r"audio\t.mp3")
        self.gameover_sound = SoundLoader.load(r"audio\gameover_voice.wav")
        self.gameimpact = SoundLoader.load(r"audio\gameover_impact.wav")
        self.encourage = SoundLoader.load(r"audio\emma.wav")

    def reset_game(self):
        self.current_offset_y = 0
        self.current_loop = 0

        self.current_offset_x = 0    # diff betweem declared lines and drawn lines in x axis
        self.current_speed_x = 0

        self.tiles_coordinates = []
        self.score_menu = "SCORE:" + str(self.current_loop)
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()

        self.state_game_over = False

    
    def is_desktop(self):
        if platform in ['win', 'macosx', 'linux']:
            return True
        return False

    def keyboard_close(self): 
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None  

    def init_ship(self):
        with self.canvas:
            Color(0,.5,1)
            self.ship = Triangle()  

    def update_ship(self):
        center_x = self.width/2
        base_y = self.SHIP_BASE_Y * self.height #base of the ship with ref to window height
        ship_width = self.SHIP_WIDTH * self.width # ship's width with ref to window's width
        ship_height = self.SHIP_HEIGHT * self.height   # ship's height with ref to window's width
        '''
            2

        1       3
        point 1, 2 and 3 denote the ships vertices forming the triangle points
        '''
        self.ship_coordinates[0] = center_x - ship_width/2, base_y
        self.ship_coordinates[1] = center_x, base_y + ship_height
        self.ship_coordinates[2] = center_x + ship_width/2, base_y

        xmin, ymin = self.ship_coordinates[0] # points tuple for point 1
        xcent, ycent =  self.ship_coordinates[1] # points tuple for point 2
        xmax, ymax = self.ship_coordinates[2] # points tuple for point 3

        x1, y1 = self.transform(xmin, ymin) #transform them to align with the current plane
        x2, y2 = self.transform(xcent, ycent) #do same as above
        x3, y3 = self.transform(xmax, ymax) # do same as above
        self.ship.points = [x1, y1, x2, y2, x3, y3] #update the triangle points with new values

    def check_ship_collision(self):
        for i in range(len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_loop + 3:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tiles_from_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tiles_from_coordinates(ti_x+1, ti_y+1)
        for i in range(0,3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <=ymax:
                return True
        return False

    def init_vertical_lines(self):

        with self.canvas:
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def init_horizontal_lines(self):
        with self.canvas:
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def get_line_x_from_index(self, index):
        center_line_x = self.perspective_point_x #centre of the game screen 
        spacing = self.width  * self.V_SPACING #spacing between vertical lines
        offset = index - 0.5 #find out why i am subtracting 0.5 from index
        line_x = center_line_x + offset*spacing + self.current_offset_x #calculating x value based on offset, spacing anf current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_SPACING * self.height  #finds the spacing between the horizontal lines
        line_y = index * spacing_y - self.current_offset_y  #calculates the exact position of the horizontal line
        return line_y

    def init_tiles(self):
        with self.canvas:
            Color(1,1,1,1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        pre_fill_num = 20 #variable holding the number of straight line tp pre-fill the track before bending starts/cud possibily be linked with level
        for i in range(pre_fill_num):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0 

        start_index = -int(self.V_NB_LINES/2) + 1
        end_index = start_index + self.V_NB_LINES - 1

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_loop:
                del self.tiles_coordinates[i]

        if len(self.tiles_coordinates) > 0:
            last_coordinates = self.tiles_coordinates[-1]
            last_y = last_coordinates[1] + 1
            last_x = last_coordinates[0]

        # print("foo1")

        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            start_index = -int(self.V_NB_LINES/2) + 1 #find the index of the left most vertical line    
            end_index = start_index + self.V_NB_LINES - 1   #finds the index of the right most vertical line
            
            g = choice([0,1,2]) #generates random values between 0 and 2, including boundary values

            if last_x <= start_index:   #if the last generate tile was on the start index force the g to only go forward or left
                g = choice([0,1])
            if last_x + 1 >= end_index:   #same thing as for start index above # NOTE the plus 1 i used is an hack to make it work as expected
                #bug will be fixed with subsequent version release
                g = choice([0,2])

            self.tiles_coordinates.append((last_x,last_y))  #create a new tiles coordinates in the tiles_coordinates list
            #check value of random variable...
            # 0 means go straight -- create new tile at current x axis, but at current y plus 1
            # 1 means go right -- create new tile at current x axis + y and current y axis and the new current x axis and current y axis plus 1
            # 2 means go left -- do the same thing as 1 but in the opposite directions   
            
            if g == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            elif g == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1

        # print("foo2")

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            x, y = self.tiles_coordinates[i]
            xmin, ymin = self.get_tiles_from_coordinates(x, y) 
            xmax, ymax = self.get_tiles_from_coordinates(x+1, y+1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            self.tiles[i].points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def get_tiles_from_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_vertical_lines(self):
        start_index = -int(self.V_NB_LINES/2) + 1 #manipulated to allocate the lines on both sides of the central line
        for i in range(start_index, start_index+self.V_NB_LINES): 
            line_x = self.get_line_x_from_index(i) #refer to function for more details

            x1, y1 = self.transform(line_x, 0) #transform base of line to specified plane
            x2, y2 = self.transform(line_x, self.height)  #transform top of line to specified plane
            self.vertical_lines[i].points = [x1, y1, x2, y2] #reset the points of the line in the vertical line list

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES/2) + 1 #find the index of the left most vertical line    
        end_index = start_index + self.V_NB_LINES - 1   #find the index of the rightmost vertical line

        xmin = self.get_line_x_from_index(start_index) #constraint the width of the horizontal line to a left limit
        xmax = self.get_line_x_from_index(end_index)  #constraint the width of the horizontal line to a right limit
        
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)

            x1, y1 = self.transform(xmin, line_y)   #do neccessary transformation bla bla bla
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2] #reset the position of the lines to correct values

    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines() #reset the vertical lines into correct positions
        self.update_horizontal_lines()  #reset the horizontal lines into correct positions
        self.update_tiles()
        self.update_ship()
        speed_y = (self.SPEED * self.height)/200 #very interesting hack ...to allow speed to look constant despite window's height
        
        if not self.state_game_over and self.state_game_started:
            self.current_offset_y += speed_y*time_factor

            spacing_y = self.H_SPACING * self.height
            
            while self.current_offset_y > spacing_y:
                self.current_offset_y -= spacing_y
                self.current_loop += 1
                if self.current_loop%100 == 0:
                    self.encourage.play()
                self.score_menu = "SCORE:" + str(self.current_loop)
                self.generate_tiles_coordinates()

            speed_x = (self.SPEED_x * self.width)/200 #very interesting hack ...to allow speed to look constant despite window's width
            self.current_offset_x += self.current_speed_x*time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.game_soundtrack.stop()
            self.state_game_over = True
            self.menu_title = "G  a  m  e    O  v  e  r"
            self.menu_button = "RESTART"
            self.menuwidget.opacity = 1
            print("Game Over DUDE!")
            self.gameimpact.play()
            self.gameover_sound.play()

    def on_menu_button_pressed(self):
        #method to control game starting
        # self.sound_galaxy.play()
        # time.sleep(2)
        self.reset_game()
        self.sound_begin.play()
        self.state_game_started = True
        self.menuwidget.opacity = 0
        self.game_soundtrack.play()

    
# the main class which subclasses the app resposible for instantiating the application window
class GalaxyApp(App):
    sound = None
    def on_start(self):
        self.title = "Brian's Game"
        self.sound = SoundLoader.load(r"audio\galaxy.wav")
        self.sound.play()
 
# the program engine, prevent the script from auto-execution, if it was imported
if __name__ == "__main__":
    GalaxyApp().run()
