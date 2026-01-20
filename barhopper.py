import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 300
BAR_Y = SCREEN_HEIGHT // 2
PLAYER_SIZE = 20
OBSTACLE_SIZE = 20 # Define obstacle size for clarity

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bar Hopper")

# Player settings (starts in the middle of the x-coordinate, on the bottom of the bar)
player = {"x": SCREEN_WIDTH // 2 - PLAYER_SIZE // 2, "y": BAR_Y + 10, "on_top": False}
player_rect = pygame.Rect(player["x"], player["y"], PLAYER_SIZE, PLAYER_SIZE)

# Bar settings
bar_length = SCREEN_WIDTH - 20 # Bar extends from x=10 to x=SCREEN_WIDTH-10

# Obstacle settings
obstacles = []
obstacle_speed = 3
obstacle_spawn_rate = 30  # Frames per obstacle
score = 0
frame_count = 0
obstacle_direction = -1   # Initial direction: -1 for left, 1 for right

# Font settings
font = pygame.font.SysFont(None, 36)

def draw_bar():
    """Draws the central bar on the screen."""
    pygame.draw.line(screen, WHITE, (10, BAR_Y), (bar_length, BAR_Y), 2)

def draw_player():
    """Draws the player square on the screen."""
    player_rect.y = player["y"]
    pygame.draw.rect(screen, RED, player_rect)

def draw_obstacles():
    """Draws all active obstacles on the screen."""
    for ob in obstacles:
        pygame.draw.rect(screen, WHITE, ob)

def check_collision():
    """Checks for collision between the player and any obstacle.
    If a collision occurs, sets the game to stop running.
    """
    global running
    for ob in obstacles:
        if player_rect.colliderect(ob):
            running = False
            break # Exit loop once a collision is detected

def remove_conflicting_obstacles():
    """Removes one of two obstacles if they exist at the same x position,
    one above and one below the bar. This prevents impossible scenarios.
    """
    # Create a map to group obstacles by their x-position
    position_map = {}
    for ob in obstacles:
        if ob.x not in position_map:
            position_map[ob.x] = [ob]
        else:
            position_map[ob.x].append(ob)

    # Iterate through x-positions to find conflicts
    for x_pos, obs_at_x in position_map.items():
        top_ob = None
        bottom_ob = None
        for ob in obs_at_x:
            if ob.y < BAR_Y: # Obstacle is above the bar
                top_ob = ob
            elif ob.y > BAR_Y: # Obstacle is below the bar
                bottom_ob = ob

        # If both a top and bottom obstacle exist at the same x, remove one randomly
        if top_ob and bottom_ob:
            obstacles.remove(random.choice([top_ob, bottom_ob]))

def update_obstacles():
    """Updates obstacle positions, spawns new obstacles,
    and handles score/speed progression.
    """
    global score, obstacle_speed, obstacle_direction, frame_count

    # Move existing obstacles
    for ob in obstacles:
        ob.x += obstacle_speed * obstacle_direction

    # Remove obstacles that have moved off-screen
    # The condition depends on the direction of movement
    if obstacle_direction == -1: # Moving left
        obstacles[:] = [ob for ob in obstacles if ob.x > -OBSTACLE_SIZE]
    else: # Moving right
        obstacles[:] = [ob for ob in obstacles if ob.x < SCREEN_WIDTH]

    # Spawn new obstacles based on spawn rate
    if frame_count % obstacle_spawn_rate == 0:
        # Determine spawn X position based on current direction
        spawn_x = SCREEN_WIDTH if obstacle_direction == -1 else 0 - OBSTACLE_SIZE

        # Determine spawn Y positions (above or below the bar)
        # These are fixed relative to BAR_Y
        pos_above_bar = BAR_Y - OBSTACLE_SIZE - 10
        pos_below_bar = BAR_Y + 10

        # Randomly decide to spawn 1 or 2 obstacles
        num_to_spawn = random.randint(1, 2)
        spawned_positions = [] # To ensure unique y positions if spawning 2

        for _ in range(num_to_spawn):
            # Randomly choose between above or below the bar
            if random.choice([True, False]) and pos_above_bar not in spawned_positions:
                new_y = pos_above_bar
            elif pos_below_bar not in spawned_positions:
                new_y = pos_below_bar
            else: # If one position is already taken or not chosen, use the other
                new_y = pos_above_bar if pos_below_bar in spawned_positions else pos_below_bar

            obstacles.append(pygame.Rect(spawn_x, new_y, OBSTACLE_SIZE, OBSTACLE_SIZE))
            spawned_positions.append(new_y) # Track spawned positions

        score += 1 # Increment score for each spawn cycle

        # Remove conflicting obstacles immediately after spawning
        remove_conflicting_obstacles()

        # Reverse direction and potentially increase speed based on score
        if score > 0 and score % 25 == 0:
            obstacle_direction *= -1 # Reverse movement direction
            # You might want to reset obstacle_speed or adjust it differently here
            # if the game becomes too fast too quickly.
            # For now, speed increases every 5 points, so this just reverses direction.

        # Speed up the obstacles every 5 points
        if score > 0 and score % 5 == 0:
            obstacle_speed += 1

def draw_score():
    """Displays the current score on the screen."""
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Toggle player position between top and bottom of the bar
                player["on_top"] = not player["on_top"]
                player["y"] = BAR_Y - PLAYER_SIZE if player["on_top"] else BAR_Y + 10
            if event.key == pygame.K_q: # Allow quitting with 'q' key
                running = False

    # Game logic updates
    update_obstacles()
    check_collision()

    # Drawing
    screen.fill(BLACK)
    draw_bar()
    draw_player()
    draw_obstacles()
    draw_score()

    # Update the display
    pygame.display.flip()

    # Control game speed
    pygame.time.delay(30) # Roughly 33 FPS (1000ms / 30ms)
    frame_count += 1

# Quit pygame
pygame.quit()
