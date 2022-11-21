import arcade_game as ag


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Arcade Superman"

SCALING = 2.0


# Create a new Space Shooter window
window = ag.arcade.Window(int(SCREEN_WIDTH * SCALING), int(SCREEN_HEIGHT * SCALING), SCREEN_TITLE)
main_menu = ag.MainMenu(SCALING)
window.show_view(main_menu)
# Setup to play
# Run the game
ag.arcade.run()


  