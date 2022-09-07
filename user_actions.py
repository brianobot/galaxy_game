# this is only activated if the user's platform matches PC based platform
from kivy.uix.relativelayout import RelativeLayout
# from Galaxy.main import MainWidget


def _on_keyboard_down(self, keyboard, keycode, text, modifier):
    if keycode[1] == 'd' or keycode[1] == 'right':
        self.current_speed_x -= self.SPEED_x
    if keycode[1] == 'a' or  keycode[1] =='left':
        self.current_speed_x += self.SPEED_x
    return True

def _on_keyboard_up(self, keyboard, keycode):
    self.current_speed_x = 0 

def on_touch_down(self, touch):
    if not self.state_game_over and self.state_game_started:
        if touch.x > self.width/2:
            # print('going Right')
            self.current_speed_x -= self.SPEED_x
        if touch.x < self.width/2:
            # print('banking left')
            # self.current_offset_x -= self.width*self.V_SPACING
            self.current_speed_x += self.SPEED_x 
    return super(RelativeLayout, self).on_touch_down(touch)

def on_touch_up(self, touch):
    # print('UP!')
    self.current_speed_x = 0
    return True
