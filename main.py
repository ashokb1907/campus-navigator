import pygame
import sys
import math # Needed for joystick deadzone calculation

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SIZE = 30
PLAYER_SPEED = 5
JOYSTICK_DEADZONE = 0.4 # Threshold below which joystick motion is ignored

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255) # Player color for now

# --- Player Class ---
class Player(pygame.sprite.Sprite):
    """ Represents the player character """
    def __init__(self):
        super().__init__() # Call the parent class (Sprite) constructor

        # Create the player's visual representation (a blue square for now)
        self.image = pygame.Surface([PLAYER_SIZE, PLAYER_SIZE])
        self.image.fill(BLUE)

        # Get the rectangle that defines the sprite's boundaries and position
        self.rect = self.image.get_rect()

        # Set the initial position (center of the screen)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2

        # Store movement vectors (how much to change x and y each frame)
        self.change_x = 0
        self.change_y = 0

    def update(self):
        """ Update the player's position based on the current movement vectors """
        # Move left/right
        self.rect.x += self.change_x
        # Move up/down
        self.rect.y += self.change_y

        # --- Boundary Checking ---
        # Prevent the player from moving off the screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    # --- Movement Methods ---
    def go_left(self):
        """ Set horizontal speed to move left """
        self.change_x = -PLAYER_SPEED

    def go_right(self):
        """ Set horizontal speed to move right """
        self.change_x = PLAYER_SPEED

    def go_up(self):
        """ Set vertical speed to move up """
        self.change_y = -PLAYER_SPEED

    def go_down(self):
        """ Set vertical speed to move down """
        self.change_y = PLAYER_SPEED

    def stop_x(self):
        """ Stop horizontal movement """
        self.change_x = 0

    def stop_y(self):
        """ Stop vertical movement """
        self.change_y = 0

# --- Main Function ---
def main():
    """ Main program function """
    pygame.init() # Initialize all Pygame modules

    # --- Screen Setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Campus Navigator Challenge - Phase 1")

    # --- Controller Setup ---
    joysticks = []
    # Check for available joysticks and initialize them
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        print(f"Detected Joystick {i}: {joystick.get_name()}")

    if not joysticks:
        print("No joysticks detected. Using keyboard controls.")
    else:
        print("Joystick detected. Keyboard controls also available.")


    # --- Sprite Management ---
    all_sprites_list = pygame.sprite.Group()

    # --- Create Player Instance ---
    player = Player()
    all_sprites_list.add(player) # Add the player to the sprite group

    # --- Game Loop Variables ---
    running = True # Controls the main game loop
    clock = pygame.time.Clock() # Used to control game frame rate

    # -------- Main Program Loop -----------
    while running:
        # --- Event Processing ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # User clicked the close button
                running = False

            # --- Joystick Input Handling ---
            if joysticks:
                # Analog stick movement
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0: # Horizontal axis
                        if math.fabs(event.value) > JOYSTICK_DEADZONE:
                            if event.value < 0: player.go_left()
                            else: player.go_right()
                        else: player.stop_x()
                    elif event.axis == 1: # Vertical axis
                        if math.fabs(event.value) > JOYSTICK_DEADZONE:
                            if event.value < 0: player.go_up()
                            else: player.go_down()
                        else: player.stop_y()

                # D-Pad (Hat) movement
                elif event.type == pygame.JOYHATMOTION:
                    hat_x, hat_y = event.value
                    # Horizontal D-pad
                    if hat_x == -1: player.go_left()
                    elif hat_x == 1: player.go_right()
                    else:
                         # Stop only if not also moving via analog stick's X axis
                         is_analog_x_active = any(math.fabs(j.get_axis(0)) > JOYSTICK_DEADZONE for j in joysticks)
                         if not is_analog_x_active:
                              player.stop_x()

                    # Vertical D-pad (Inverted Y)
                    if hat_y == 1: player.go_up()
                    elif hat_y == -1: player.go_down()
                    else:
                         # Stop only if not also moving via analog stick's Y axis
                         is_analog_y_active = any(math.fabs(j.get_axis(1)) > JOYSTICK_DEADZONE for j in joysticks)
                         if not is_analog_y_active:
                              player.stop_y()

            # --- Keyboard Input Handling (Fallback / Alternative) ---
            if event.type == pygame.KEYDOWN: # A key is pressed down
                if event.key == pygame.K_LEFT:
                    player.go_left()
                elif event.key == pygame.K_RIGHT:
                    player.go_right()
                elif event.key == pygame.K_UP:
                    player.go_up()
                elif event.key == pygame.K_DOWN:
                    player.go_down()
                elif event.key == pygame.K_ESCAPE: # Allow quitting with Esc key
                    running = False

            elif event.type == pygame.KEYUP: 
                # A key is released
                # Stop movement only if the released key corresponds to the current direction
                # and no other movement key in that axis is still pressed
                # (This prevents stopping if holding Left then press/release Right)
                # A simpler approach is just to stop if the key matches the direction,
                # assuming only one key/direction is primary at a time for keyboard.

                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop_x()
                elif event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop_x()
                elif event.key == pygame.K_UP and player.change_y < 0:
                    player.stop_y()
                elif event.key == pygame.K_DOWN and player.change_y > 0:
                    player.stop_y()


        # --- Game Logic ---
        all_sprites_list.update() # Calls the update() method on all sprites

        # --- Drawing Code ---
        screen.fill(WHITE) # Draw the background
        all_sprites_list.draw(screen) # Draw all sprites

        # --- Update Screen ---
        pygame.display.flip()

        # --- Limit frames per second ---
        clock.tick(60) # 60 FPS

    # Close the window and quit.
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
