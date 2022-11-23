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


class SpaceShooter(arcade.View):
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
        self.clouds_list = arcade.SpriteList()
        self.all_sprites = arcade.SpriteList()
        self.scores = 0

    def setup(self):
        """Get the game ready to play"""

        # Set the background color
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Setup the player
        self.jet_url = resource_path("images/superman.png")
        self.background_sound_url = resource_path("sounds/Apoxode_-_Electric_1.wav")
        self.cloud_url = resource_path("images/cloud.png")
        self.missle_url = resource_path("images/missile.png")
        self.collision_sound_url = resource_path("sounds/Collision.wav")
        self.rising_sound_url = resource_path("sounds/Rising_putter.wav")
        self.falling_sound_url = resource_path("sounds/Falling_putter.wav")

        self.player = arcade.Sprite(self.jet_url, 0.3)
        self.player.center_y = self.window.height / 2
        self.player.left = 10
        self.all_sprites.append(self.player)

        # Spawn a new enemy every second
        arcade.schedule(self.add_enemy, 1.0)

        # Spawn a new cloud every 3 seconds
        arcade.schedule(self.add_cloud, 3.0)

        
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
        enemy.velocity = (random.randint(-200, -50), 0)

        # Add it to the enemies list
        self.enemies_list.append(enemy)
        self.all_sprites.append(enemy)

    def add_cloud(self, delta_time: float):
        """Adds a new cloud to the screen

        Arguments:
            delta_time {float} -- How much time has passed since the last call
        """
        # First, create the new cloud sprite
        
        cloud = FlyingSprite(self.cloud_url, self.scaling)

        # Set its position to a random height and off screen right
        cloud.left = random.randint(self.window.width, self.window.width + 10)
        cloud.top = random.randint(10, self.window.height - 10)

        # Set its speed to a random speed heading left
        cloud.velocity = (random.randint(-50, -20), 0)

        # Add it to the enemies list
        self.clouds_list.append(cloud)
        self.all_sprites.append(cloud)

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

        if symbol == arcade.key.P:
            self.paused = not self.paused

        if symbol == arcade.key.I or symbol == arcade.key.UP:
            self.player.change_y = 250
            arcade.play_sound(self.move_up_sound)

        if symbol == arcade.key.K or symbol == arcade.key.DOWN:
            self.player.change_y = -250
            arcade.play_sound(self.move_down_sound)

        if symbol == arcade.key.J or symbol == arcade.key.LEFT:
            self.player.change_x = -250

        if symbol == arcade.key.L or symbol == arcade.key.RIGHT:
            self.player.change_x = 250

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
      arcade.unschedule(self.add_cloud)
      DATABASE.createConn()
      DATABASE.addScore(self.userName,self.scores)
      DATABASE.closeConn()
      arcade.stop_sound(self.media_player)
      stat_view = StatMenu(self.scaling)
      self.window.show_view(stat_view)

    def on_draw(self):
        """Draw all game objects"""
        self.clear()
        arcade.start_render()
        self.all_sprites.draw()
        arcade.draw_text(
            self.scores,
            self.window.width-30,
            self.window.height-30,
            arcade.color.BLACK,
            15,
            anchor_x="center",
        )

    def on_show_view(self):
      self.setup()

class QuitButton(arcade.gui.UIFlatButton):
    def on_click(self, event: arcade.gui.UIOnClickEvent):
        arcade.exit()

class MainMenu(arcade.View):    
  def __init__(self,scaling):
    super().__init__()
    self.scaling = scaling
    self.manager = gui.UIManager()
    self.manager.enable()
  

    arcade.get_window().set_icon(pyglet_load(resource_path('images/superman.ico')))

    arcade.set_background_color(arcade.color.BEIGE)
    
    # Create a text label
    self.label = arcade.gui.UILabel(
        text="Введите свое имя:",
        text_color=arcade.color.DARK_RED,
        width=300,
        height=40,
        font_size=24,
        font_name="Kenney Future")

    # Create an text input field
    self.input_field = gui.UIInputText(
      color=arcade.color.DARK_BLUE_GRAY,
      font_size=24,
      width=200,
      text='Name')

    # Create a button
    submit_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Submit',
      width=130)
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    submit_button.on_click = self.on_click 

    # Create a button
    stat_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Show leaderboard',
      width=130)
    
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    stat_button.on_click = self.on_click1 
    
    self.v_box = gui.UIBoxLayout()
    self.v_box.add(self.label.with_space_around(bottom=0))
    self.v_box.add(self.input_field.with_space_around(bottom=10))
    self.v_box.add(submit_button.with_space_around(bottom=10))
    self.v_box.add(stat_button.with_space_around(bottom=10))
    self.v_box.add(QuitButton(text="Quit",width=130))
    
    self.manager.add(
        arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box)
    )


  def update_text(self):
      print(f"updating the label with input text '{self.input_field.text}'")
      self.label.text = self.input_field.text    

  def on_click(self, event):
      
      #DATABASE.createConn()
      #DATABASE.addScore(self.userName,self.scores)
      #DATABASE.closeConn()
      #self.database = db.DataBase('base/base.json')
      #self.database.addUser(self.input_field.text)
      game_view = SpaceShooter(self.scaling,self.input_field.text)
      self.window.show_view(game_view)

  def on_click1(self, event):
      
      stat_view = StatMenu(self.scaling)
      self.window.show_view(stat_view)

      
  def on_draw(self):
      arcade.start_render()
      self.manager.draw()

  def on_show_view(self):
    """Called when switching to this view."""
    arcade.set_background_color(arcade.color.WHITE)


class StatMenu(arcade.View):    
  def __init__(self,scaling):
    super().__init__()
    self.scaling = scaling
    self.manager = gui.UIManager()
    self.manager.enable()

    arcade.set_background_color(arcade.color.BEIGE)
    
    # Create a text label
    self.textArea = arcade.gui.UITextArea(
        text="Leaderboard:",
        text_color=arcade.color.DARK_RED,
        width=300,
        height=self.window.height*0.9,
        multiline = True,
        font_size=24,
        font_name="Kenney Future")

    
    # Create a button
    back_button = gui.UIFlatButton(
      color=arcade.color.DARK_BLUE_GRAY,
      text='Back')
    # --- Method 2 for handling click events,
    # assign self.on_click_start as callback
    back_button.on_click = self.on_click 
    
    self.v_box = gui.UIBoxLayout()
    self.v_box.add(self.textArea.with_space_around(bottom=0))
    self.v_box.add(back_button)
    
    self.manager.add(
        arcade.gui.UIAnchorWidget(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.v_box)
    )

  def update_text(self):
    
      DATABASE.createConn()
      self.scores = DATABASE.getAllScores()
      DATABASE.closeConn()
      str = "Leaderboard:\n"
      for score in self.scores:
        str+=f"{score[0]} - {score[1]}\n"
      self.v_box.children[0] = arcade.gui.UITextArea(
        text=str,
        text_color=arcade.color.DARK_RED,
        width=300,
        height=self.window.height*0.9,
        multiline = True,
        font_size=24,
        font_name="Kenney Future")
      

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



