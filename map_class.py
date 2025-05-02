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
BLUE = (0, 0, 255) # Player color
GREY = (128, 128, 128) # Wall color

# --- Wall Class ---
class Wall(pygame.sprite.Sprite):
    """ Represents an obstacle/wall on the map """
    def __init__(self, x, y, width, height):
        super().__init__() # Call the parent class (Sprite) constructor

        # Create the wall's visual representation (a grey rectangle)
        self.image = pygame.Surface([width, height])
        self.image.fill(GREY)

        # Get the rectangle that defines the sprite's boundaries and position
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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

        # Set the initial position (adjust if needed based on map)
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2

        # Store movement vectors (how much to change x and y each frame)
        self.change_x = 0
        self.change_y = 0

        # List of sprites we can bump against
        self.wall_list = None # Will be set later

    def update(self):
        """ Update the player's position, handling collisions """

        # --- Horizontal Movement & Collision ---
        # Move left/right first
        self.rect.x += self.change_x

        # Check for collisions after horizontal movement
        # *** UNCOMMENT THIS SECTION TO ENABLE COLLISION ***
        # block_hit_list = pygame.sprite.spritecollide(self, self.wall_list, False)
        # for block in block_hit_list:
        #     # If moving right, snap to the left side of the block hit
        #     if self.change_x > 0:
        #         self.rect.right = block.rect.left
        #     # If moving left, snap to the right side of the block hit
        #     elif self.change_x < 0:
        #         self.rect.left = block.rect.right
        #     # Optional: Stop horizontal movement immediately on hit
        #     # self.stop_x()

        # --- Vertical Movement & Collision ---
        # Move up/down next
        self.rect.y += self.change_y

        # Check for collisions after vertical movement
        # *** UNCOMMENT THIS SECTION TO ENABLE COLLISION ***
        # block_hit_list = pygame.sprite.spritecollide(self, self.wall_list, False)
        # for block in block_hit_list:
        #     # If moving down, snap to the top side of the block hit
        #     if self.change_y > 0:
        #         self.rect.bottom = block.rect.top
        #     # If moving up, snap to the bottom side of the block hit
        #     elif self.change_y < 0:
        #         self.rect.top = block.rect.bottom
        #     # Optional: Stop vertical movement immediately on hit
        #     # self.stop_y()


        # --- Boundary Checking (Screen edges) ---
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

    # --- Movement Methods (Unchanged) ---
    def go_left(self): self.change_x = -PLAYER_SPEED
    def go_right(self): self.change_x = PLAYER_SPEED
    def go_up(self): self.change_y = -PLAYER_SPEED
    def go_down(self): self.change_y = PLAYER_SPEED
    def stop_x(self): self.change_x = 0
    def stop_y(self): self.change_y = 0

# --- Main Function ---
def main():
    """ Main program function """
    pygame.init() # Initialize all Pygame modules

    # --- Screen Setup ---
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Campus Navigator Challenge - Aston Map")

    # --- Controller Setup (Unchanged) ---
    joysticks = []
    for i in range(pygame.joystick.get_count()):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)
        print(f"Detected Joystick {i}: {joystick.get_name()}")
    if not joysticks: print("No joysticks detected. Using keyboard controls.")
    else: print("Joystick detected. Keyboard controls also available.")

    # --- Sprite Management ---
    all_sprites_list = pygame.sprite.Group()
    wall_list = pygame.sprite.Group() # Group specifically for walls

    # --- Create Walls ---
    # Define wall coordinates [x, y, width, height] based on Aston Map PDF
    # *** THESE ARE ESTIMATES - ADJUST AS NEEDED ***
    wall_coords = [
        # Borders (optional, but good practice)
        [0, 0, SCREEN_WIDTH, 10],         # Top border
        [0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10], # Bottom border
        [0, 10, 10, SCREEN_HEIGHT - 20],  # Left border
        [SCREEN_WIDTH - 10, 10, 10, SCREEN_HEIGHT - 20], # Right border

        # Main Building Complex (Approx area 1, 2, 3) - Large, slightly left of center
        [180, 80, 200, 180],

        # Aston Business School / Conf Center (5) - Right of Main Building
        [400, 150, 150, 100],

        # Library (6) - South of ABS
        [420, 270, 120, 80],

        # Vision Sciences / Medical / Audiology (9) - South East area
        [450, 380, 150, 120],

        # Woodcock Sports Centre (10) - South East, below Vision Sci
        [480, 510, 180, 80],

        # EBRI (14) - Top Right area
        [500, 80, 100, 80],

        # Engineering Academy (16) - Far Top Right
        [650, 100, 120, 150],

        # Student Union (4) - Between Main Bldg and ABS
        [385, 100, 50, 40],

        # MLK Centre (15) - South West, near bottom road
        [150, 450, 80, 80],

        # Accommodation Blocks (Approx area 18, 19) - West side
        [50, 150, 100, 250],

        # Accommodation Block (Approx area 22) - Far West, near Coleshill St
        [20, 350, 80, 150],

        # Accommodation Blocks (Approx area 20, 21) - South West
        [250, 480, 150, 100],

        # Shops Area (39) - West of Main Building
        [120, 100, 50, 80],

    ]

    # Create Wall objects from coordinates and add to groups
    for coords in wall_coords:
        wall = Wall(coords[0], coords[1], coords[2], coords[3])
        wall_list.add(wall)
        all_sprites_list.add(wall) # Add walls to the main drawing group too

    # --- Create Player Instance ---
    player = Player()
    player.wall_list = wall_list # Give the player a reference to the walls
    all_sprites_list.add(player)

    # --- Game Loop Variables ---
    running = True
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while running:
        # --- Event Processing (Unchanged) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            # Joystick Input
            if joysticks:
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        if math.fabs(event.value) > JOYSTICK_DEADZONE:
                            if event.value < 0: player.go_left()
                            else: player.go_right()
                        else: player.stop_x()
                    elif event.axis == 1:
                        if math.fabs(event.value) > JOYSTICK_DEADZONE:
                            if event.value < 0: player.go_up()
                            else: player.go_down()
                        else: player.stop_y()
                elif event.type == pygame.JOYHATMOTION:
                    hat_x, hat_y = event.value
                    if hat_x == -1: player.go_left()
                    elif hat_x == 1: player.go_right()
                    else:
                         is_analog_x_active = any(math.fabs(j.get_axis(0)) > JOYSTICK_DEADZONE for j in joysticks)
                         if not is_analog_x_active: player.stop_x()
                    if hat_y == 1: player.go_up()
                    elif hat_y == -1: player.go_down()
                    else:
                         is_analog_y_active = any(math.fabs(j.get_axis(1)) > JOYSTICK_DEADZONE for j in joysticks)
                         if not is_analog_y_active: player.stop_y()
            # Keyboard Input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: player.go_left()
                elif event.key == pygame.K_RIGHT: player.go_right()
                elif event.key == pygame.K_UP: player.go_up()
                elif event.key == pygame.K_DOWN: player.go_down()
                elif event.key == pygame.K_ESCAPE: running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0: player.stop_x()
                elif event.key == pygame.K_RIGHT and player.change_x > 0: player.stop_x()
                elif event.key == pygame.K_UP and player.change_y < 0: player.stop_y()
                elif event.key == pygame.K_DOWN and player.change_y > 0: player.stop_y()

        # --- Game Logic ---
        all_sprites_list.update() # Calls update() on player and walls

        # --- Drawing Code ---
        screen.fill(WHITE) # Draw the background
        all_sprites_list.draw(screen) # Draw player and walls

        # --- Update Screen ---
        pygame.display.flip()

        # --- Limit frames per second ---
        clock.tick(60)

    # Close the window and quit.
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
