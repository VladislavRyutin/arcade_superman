# Basic arcade shooter
#

# Imports
from dataclasses import dataclass
import arcade
import random
import arcade.gui as gui
import database as db
import os
import sys

from pyglet.image import load as pyglet_load
# Constants

DATABASE = db.DataBase()
# Classes

def resource_path(relative_path):
  try:
  # PyInstaller creates a temp folder and stores path in _MEIPASS
      base_path = sys._MEIPASS
  except Exception:
      base_path = os.path.abspath(".")

  return os.path.join(base_path, relative_path)

class FlyingSprite(arcade.Sprite):
    """Base class for all flying sprites
    Flying sprites include enemies and clouds
    """

    def update(self):
        """Update the position of the sprite
        When it moves off screen to the left, remove it
        """

        # Move the sprite
        super().update()

        # Remove us if we're off screen
        if self.right < 0:
            self.remove_from_sprite_lists()


class Level(arcade.View):
    """Space Shooter side scroller game
    Player starts on the left, enemies appear on the right
    Player can move anywhere, but not off screen
    Enemies fly to the left at variable speed
    Collisions end the game
    """

    def __init__(self,scaling, userName):
      """Initialize the game"""
      super().__init__()
      self.userName = userName
      self.scaling = scaling
      # Setup the empty sprite lists
      self.enemies_list = arcade.SpriteList()
      self.all_sprites = arcade.SpriteList()
      self.scores = 0
      self.enemy_velocity = None
      self.player_velocity = 250
      self.background = None
      self.speed_up = 250
      self.is_speed_up = False
      self.level = None

    def setup(self):
        """Get the game ready to play"""        

        self.missle_url = resource_path("images/missile.png")
        self.collision_sound_url = resource_path("sounds/Collision.wav")
        self.rising_sound_url = resource_path("sounds/Rising_putter.wav")
        self.falling_sound_url = resource_path("sounds/Falling_putter.wav")

        # Setup the player
        self.jet_url = resource_path("images/superman.png")
        self.background_sound_url = resource_path("sounds/Apoxode_-_Electric_1.wav")

        self.player = arcade.Sprite(self.jet_url, 0.3)
        self.player.center_y = self.window.height / 2
        self.player.left = 10
        self.all_sprites.append(self.player)

    
        arcade.schedule(self.add_score, 1.0)

        # Load our background music
        # Sound source: http://ccmixter.org/files/Apoxode/59262
        # License: https://creativecommons.org/licenses/by/3.0/
        
        self.background_music = arcade.load_sound(
            self.background_sound_url
        )

        # Load our other sounds
        # Sound sources: Jon Fincher
        
        self.collision_sound = arcade.load_sound(self.collision_sound_url)
        
        self.move_up_sound = arcade.load_sound(self.rising_sound_url)
        
        self.move_down_sound = arcade.load_sound(self.falling_sound_url)

        # Start the background music
        self.media_player = arcade.play_sound(self.background_music)

        # Unpause everything and reset the collision timer
        self.paused = False
        self.collided = False
        self.collision_timer = 0.0

    def add_score(self, delta_time: float):
      self.scores+=10

    def add_enemy(self, delta_time: float):
        """Adds a new enemy to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """

        # First, create the new enemy sprite
        
        enemy = FlyingSprite(self.missle_url, self.scaling)

        # Set its position to a random height and off screen right
        enemy.left = random.randint(self.window.width, self.window.width + 10)
        enemy.top = random.randint(10, self.window.height - 10)

        # Set its speed to a random speed heading left
        enemy.velocity = self.enemy_velocity

        # Add it to the enemies list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

    def on_key_press(self, symbol: int, modifiers: int):
        """Handle user keyboard input
        Q: Quit the game
        P: Pause the game
        I/J/K/L: Move Up, Left, Down, Right
        Arrows: Move Up, Left, Down, Right

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if symbol == arcade.key.Q:
            # Quit immediately
            self.on_exit()

        
        if modifiers & arcade.key.MOD_SHIFT:
          if self.player.change_x > 0:
            self.player.change_x = self.player_velocity + self.speed_up
          if self.player.change_x < 0:
            self.player.change_x = -(self.player_velocity + self.speed_up)
          if self.player.change_y > 0:
            self.player.change_y = self.player_velocity + self.speed_up
          if self.player.change_y < 0:
            self.player.change_y = -( self.player_velocity + self.speed_up)


        if symbol == arcade.key.P:
            self.paused = not self.paused

        if symbol == arcade.key.I or symbol == arcade.key.UP:            
            self.player.change_y = self.player_velocity
            
            arcade.play_sound(self.move_up_sound)

        if symbol == arcade.key.K or symbol == arcade.key.DOWN:
            self.player.change_y = -self.player_velocity
            arcade.play_sound(self.move_down_sound)

        if symbol == arcade.key.J or symbol == arcade.key.LEFT:
            self.player.change_x = -self.player_velocity

        if symbol == arcade.key.L or symbol == arcade.key.RIGHT:
            self.player.change_x = self.player_velocity
          
    def on_key_release(self, symbol: int, modifiers: int):
        """Undo movement vectors when movement keys are released

        Arguments:
            symbol {int} -- Which key was pressed
            modifiers {int} -- Which modifiers were pressed
        """
        if (
            symbol == arcade.key.I
            or symbol == arcade.key.K
            or symbol == arcade.key.UP
            or symbol == arcade.key.DOWN
        ):
            self.player.change_y = 0

        if (
            symbol == arcade.key.J
            or symbol == arcade.key.L
            or symbol == arcade.key.LEFT
            or symbol == arcade.key.RIGHT
        ):
            self.player.change_x = 0
        
        if not (modifiers & arcade.key.MOD_SHIFT):          
          if self.player.change_x > 0:
            self.player.change_x = self.player_velocity
          if self.player.change_x < 0:
            self.player.change_x = -self.player_velocity
          if self.player.change_y > 0:
            self.player.change_y = self.player_velocity
          if self.player.change_y < 0:
            self.player.change_y = -self.player_velocity

    def on_update(self, delta_time: float):
        """Update the positions and statuses of all game objects
        If we're paused, do nothing
        Once everything has moved, check for collisions between
        the player and the list of enemies

        Arguments:
            delta_time {float} -- Time since the last update
        """

        # Did we collide with something earlier? If so, update our timer
        if self.collided:
            self.collision_timer += delta_time
            # If we've paused for two seconds, we can quit
            if self.collision_timer > 1.0:
                self.on_exit()
            # Stop updating things as well
            return

        # If we're paused, don't update anything
        if self.paused:
            return

        # Did we hit anything? If so, end the game
        if self.player.collides_with_list(self.enemies_list):
            self.collided = True
            self.collision_timer = 0.0
            arcade.play_sound(self.collision_sound)

        # Update everything
        for sprite in self.all_sprites:
            sprite.center_x = int(
                sprite.center_x + sprite.change_x * delta_time
            )
            sprite.center_y = int(
                sprite.center_y + sprite.change_y * delta_time
            )
        # self.all_sprites.update()

        # Keep the player on screen
        if self.player.top > self.window.height:
            self.player.top = self.window.height
        if self.player.right > self.window.width:
            self.player.right = self.window.width
        if self.player.bottom < 0:
            self.player.bottom = 0
        if self.player.left < 0:
            self.player.left = 0

    def on_exit(self):
      arcade.unschedule(self.add_score)
      arcade.unschedule(self.add_enemy)
      DATABASE.createConn()
      DATABASE.addScore(self.userName,self.scores, self.level)
      DATABASE.closeConn()
      arcade.stop_sound(self.media_player)
      stat_view = StatMenu(self.scaling)
      self.window.show_view(stat_view)

    def on_draw(self):
        """Draw all game objects"""
        self.clear()
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            self.background)
        self.all_sprites.draw()
        arcade.draw_text(
            f"{self.userName} : {self.scores}",
            self.window.width-30 - (len(self.userName)*15),
            self.window.height-30,
            arcade.color.BLACK,
            15,
            anchor_x="center",
        )

    def on_show_view(self):
      self.setup()

class Level1(Level):
  def __init__(self,scaling, userName):
    super().__init__(scaling,userName)
  
  def setup(self):
    # Set the background color
    
    self.enemy_velocity = (-150,0)
    self.background = arcade.load_texture("./images/background3.jpg")
    self.level = 1

    # Spawn a new enemy every second
    arcade.schedule(self.add_enemy, 1.0)

    super().setup()

class Level2(Level):
  def __init__(self,scaling, userName):
    super().__init__(scaling,userName)
  
  def setup(self):
    # Set the background color
    
    self.enemy_velocity = (-350,0)
    self.background = arcade.load_texture("./images/background2.jpg")
    self.level = 2


    # Spawn a new enemy every second
    arcade.schedule(self.add_enemy, 0.5)

    super().setup()

class Level3(Level):
  def __init__(self,scaling, userName):
    super().__init__(scaling,userName)
  
  def setup(self):
    # Set the background color
    
    self.enemy_velocity = (-650,0)
    self.background = arcade.load_texture("./images/background1.jpg")
    self.level = 3

    # Spawn a new enemy every second
    arcade.schedule(self.add_enemy, 0.1)
    super().setup()


class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()

class MainMenu(arcade.View):    
  def __init__(self,scaling):
    super().__init__()
    
    self.background = arcade.load_texture("./images/шапка.jpg")
    self.scaling = scaling  
    self.level1_button = None
    self.level2_button = None
    self.level3_button = None
    self.label = None
    self.input_field = None
    self.submit_button = None
    self.back_button = None
    self.stat_button = None
    self.manager = None
    self.v_box = None
       

  def setup(self):   

    arcade.get_window().set_icon(pyglet_load(resource_path('images/superman.ico')))

    arcade.set_background_color(arcade.color.BEIGE)    
    
    self.level1_button = None
    self.level2_button = None
    self.level3_button = None
    # Create a text label
    self.label = gui.UILabel(
        text="Введите свое имя:",
        text_color=arcade.color.WHITE,
        width=300,
        height=40,
        font_size=24,
        font_name="Kenney Future")

    # Create an text input field
    self.input_field = gui.UIInputText(
      text_color=arcade.color.WHITE,
      font_size=24,
      width=200,
      text='Name')

    # Create a button
    self.submit_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Submit',
      width=130)
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    self.submit_button.on_click = self.on_click 

    # Create a button
    self.back_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Back',
      width=130)
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    self.back_button.on_click = self.on_clickBack 

    # Create a button
    self.stat_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Show leaderboard',
      width=130)
    
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    self.stat_button.on_click = self.on_click1 

    self.manager = gui.UIManager()
    self.manager.enable()
    self.v_box = gui.UIBoxLayout()    
    self.v_box.add(self.label)
    self.v_box.add(self.input_field.with_space_around(bottom=10))
    self.v_box.add(self.submit_button.with_space_around(bottom=10))
    self.v_box.add(self.stat_button.with_space_around(bottom=10))
    self.v_box.add(QuitButton(text="Quit",width=130))
    
    self.manager.add(
        gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box)
    )
    

  def update_text(self):
      print(f"updating the label with input text '{self.input_field.text}'")
      self.label.text = self.input_field.text    

  def on_click(self, event):
    # Create a button
    self.manager = gui.UIManager()
    self.manager.enable()     
    
    self.level1_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Level1',
      width=130)
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    self.level1_button.on_click = self.on_clickLevel1 

    self.level2_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Level2',
      width=130)
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    self.level2_button.on_click = self.on_clickLevel2 

    self.level3_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Level3',
      width=130)
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    self.level3_button.on_click = self.on_clickLevel3 

    self.v_box = gui.UIBoxLayout()
    self.v_box.add(self.level1_button.with_space_around(bottom=10))
    self.v_box.add(self.level2_button.with_space_around(bottom=10))
    self.v_box.add(self.level3_button.with_space_around(bottom=10))
    self.v_box.add(self.back_button.with_space_around(bottom=10))
    self.manager.add(
      arcade.gui.UIAnchorWidget(
          anchor_x="center_x",
          anchor_y="center_y",
          child=self.v_box)
    )
    
  def on_click1(self, event):
      stat_view = StatMenu(self.scaling)
      self.window.show_view(stat_view)

  def on_clickLevel1(self,event):
    game_view = Level1(self.scaling,self.input_field.text)
    self.window.hide_view()
    self.window.show_view(game_view)
    
  def on_clickLevel2(self,event):
    game_view = Level2(self.scaling,self.input_field.text)
    self.window.hide_view()
    self.window.show_view(game_view)
    
  def on_clickLevel3(self,event):
    game_view = Level3(self.scaling,self.input_field.text)
    self.window.hide_view()
    self.window.show_view(game_view)
      
  def on_clickBack(self,event):
    menu_view = MainMenu(self.scaling)
    self.window.hide_view()
    self.window.show_view(menu_view)

  def on_draw(self):
      arcade.start_render()
      arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            self.background)
      self.manager.draw()

  def on_show_view(self):
    """Called when switching to this view."""
    self.setup()

class StatMenu(arcade.View):    
  def __init__(self,scaling):
    super().__init__()
    self.scaling = scaling
    self.manager = gui.UIManager()
    self.manager.enable()

    arcade.set_background_color(arcade.color.BEIGE)
    
    self.label = arcade.gui.UILabel(
        text="Leaderboard",
        text_color=arcade.color.DARK_RED,
        font_size=20,
        font_name="Kenney Future")

    # Create a text label
    self.textArea1 = gui.UITextArea(
        text="Level 1:",
        text_color=arcade.color.DARK_RED,
        width=300,
        height=self.window.height*0.9,
        multiline = True,
        font_size=20,
        font_name="Kenney Future")
      
    self.textArea2 = gui.UITextArea(
        text="Level 2:",
        text_color=arcade.color.DARK_RED,
        width=300,
        height=self.window.height*0.9,
        multiline = True,
        font_size=20,
        font_name="Kenney Future")
      
    self.textArea3 = gui.UITextArea(
        text="Level 3:",
        text_color=arcade.color.DARK_RED,
        width=300,
        height=self.window.height*0.9,
        multiline = True,
        font_size=20,
        font_name="Kenney Future")

    
    # Create a button
    back_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Back')
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    back_button.on_click = self.on_click 
    
    self.v_box = gui.UIBoxLayout()
    self.h_box = gui.UIBoxLayout(vertical=False)
    self.h_box.add(self.textArea1)
    self.h_box.add(gui.UISpace(width=30))
    self.h_box.add(self.textArea2)
    self.h_box.add(gui.UISpace(width=30))
    self.h_box.add(self.textArea3)
    self.v_box.add(self.label)
    self.v_box.add(self.h_box.with_space_around(bottom=0))
    self.v_box.add(back_button)
    
    self.manager.add(
        arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box)
    )

  def update_text(self):
    
      DATABASE.createConn()
      self.scores1 = DATABASE.getAllScores(1)
      self.scores2 = DATABASE.getAllScores(2)
      self.scores3 = DATABASE.getAllScores(3)
      DATABASE.closeConn()
      str = "Level 1:\n"
      for score in self.scores1:
        str+=f"{score[0]} - {score[1]}\n"
      
      self.v_box.children[1].children[0].children[0].doc.text = str
      str = "Level 2:\n"
      for score in self.scores2:
        str+=f"{score[0]} - {score[1]}\n"
      
      self.v_box.children[1].children[0].children[2].doc.text = str

      str = "Level 3:\n"
      for score in self.scores3:
        str+=f"{score[0]} - {score[1]}\n"
      
      self.v_box.children[1].children[0].children[4].doc.text = str
      

  def on_click(self, event):
      menu_view = MainMenu(self.scaling)
      self.window.show_view(menu_view)

      
  def on_draw(self):
      arcade.start_render()
      self.manager.draw()

  def on_show_view(self):
    """Called when switching to this view."""
    arcade.set_background_color(arcade.color.WHITE)
    self.update_text()



