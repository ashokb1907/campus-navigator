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
        # This could later be replaced with an image using pygame.image.load()
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
    # These methods set the speed components based on input
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
        print("Warning: No joysticks detected. Connect a controller to move.")
        # You could add keyboard fallback controls here if desired

    # --- Sprite Management ---
    # This group will hold all sprites for easy updating and drawing
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
        # Check for all events happening (button presses, joystick moves, etc.)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: # User clicked the close button
                running = False

            # --- Joystick Input Handling ---
            # Check if a joystick is connected before processing joystick events
            if joysticks:
                # Analog stick movement
                if event.type == pygame.JOYAXISMOTION:
                    # Axis 0: Usually Left/Right (-1 to 1)
                    # Axis 1: Usually Up/Down (-1 to 1)
                    # Note: Axis numbers might vary between controllers
                    if event.axis == 0: # Horizontal axis
                        # Apply deadzone to ignore slight stick drift
                        if math.fabs(event.value) > JOYSTICK_DEADZONE:
                            if event.value < 0:
                                player.go_left()
                            else:
                                player.go_right()
                        else: # Stick is centered horizontally
                            player.stop_x()
                    elif event.axis == 1: # Vertical axis
                        # Apply deadzone
                        if math.fabs(event.value) > JOYSTICK_DEADZONE:
                            if event.value < 0: # Up is usually negative
                                player.go_up()
                            else: # Down is usually positive
                                player.go_down()
                        else: # Stick is centered vertically
                            player.stop_y()

                # D-Pad (Hat) movement
                elif event.type == pygame.JOYHATMOTION:
                    # Hat value is a tuple (x, y)
                    # x: -1 (left), 0 (center), 1 (right)
                    # y: -1 (down), 0 (center), 1 (up) -- Note: Y is often inverted!
                    hat_x, hat_y = event.value

                    # Horizontal D-pad
                    if hat_x == -1:
                        player.go_left()
                    elif hat_x == 1:
                        player.go_right()
                    else: # Center X
                        # Only stop if not also moving via analog stick
                        # (This check might be refined later if needed)
                        if player.change_x != 0 and not any(j.get_axis(0) for j in joysticks if math.fabs(j.get_axis(0)) > JOYSTICK_DEADZONE):
                             player.stop_x()


                    # Vertical D-pad (Inverted Y)
                    if hat_y == 1:
                        player.go_up()
                    elif hat_y == -1:
                        player.go_down()
                    else: # Center Y
                         # Only stop if not also moving via analog stick
                         if player.change_y != 0 and not any(j.get_axis(1) for j in joysticks if math.fabs(j.get_axis(1)) > JOYSTICK_DEADZONE):
                            player.stop_y()

                # --- Optional: Add button press handling here later ---
                # elif event.type == pygame.JOYBUTTONDOWN:
                #     print(f"Button {event.button} pressed")
                # elif event.type == pygame.JOYBUTTONUP:
                #     print(f"Button {event.button} released")

        # --- Game Logic ---
        # Update the state of all sprites (calls player.update())
        all_sprites_list.update()

        # --- Drawing Code ---
        # Fill the screen background (white)
        screen.fill(WHITE)

        # Draw all the sprites onto the screen
        all_sprites_list.draw(screen)

        # --- Update Screen ---
        # Flip the display to show the newly drawn frame
        pygame.display.flip()

        # --- Frame Rate Control ---
        # Limit the game to 60 frames per second
        clock.tick(60)

    # --- End of Game Loop ---
    # Uninitialize Pygame modules and exit
    pygame.quit()
    sys.exit()

# --- Script Entry Point ---
# This ensures main() runs only when the script is executed directly
if __name__ == "__main__":
    main()
