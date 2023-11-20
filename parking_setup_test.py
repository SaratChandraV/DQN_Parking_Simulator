# pending
# 1. write the check that ensures it the car gets parked within some tolerance of an angle.
import pygame
import sys
import numpy as np
import time
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
MAX_RAY_DISTANCE = 200
NO_OF_RAYS = 20
BOUNDARY_COLOR = (64, 224, 208)
CENTER_X = 0
CENTER_Y = 0

#Parking lane constants
PARKING_LANE_LINE_WIDTH = 5
PARKING_LANE_COLOR = (255,255,0)
PARKING_LANE_WIDTH = 160
PARKING_LANE_HEIGHT = 160

#Car Constants
CAR_WIDTH = PARKING_LANE_WIDTH - 60
CAR_HEIGHT = PARKING_LANE_HEIGHT + 10
CAR_COLOR = (255,255,255)

#Player car constants
PLAYER_CAR_COLOR = (0,0,255)
PLAYER_ANGLE_STEP = math.radians(5)
PLAYER_STEP = 5
ACTIONS_LIST = ["front_only","front_left","front_right","back_only","back_left","back_right"]

#Player Position Variables
PLAYER_X = 400
PLAYER_Y = 300
PLAYER_ANGLE = math.radians(0)

def calculate_distance(x1, y1, x2, y2):
    # Calculate the squared differences
    x_diff = x2 - x1
    y_diff = y2 - y1

    # Calculate the squared Euclidean distance
    distance_squared = x_diff**2 + y_diff**2

    # Take the square root to get the actual Euclidean distance
    distance = math.sqrt(distance_squared)

    return distance

def bounding_rectangle(points):

    min_x = min(point[0] for point in points)
    max_x = max(point[0] for point in points)
    min_y = min(point[1] for point in points)
    max_y = max(point[1] for point in points)

    left = min_x
    top = min_y
    width = max_x - min_x
    height = max_y - min_y

    return top, left, width, height

def move(x, y, angle, command):

    # Calculate the direction vector based on the angle
    direction_vector = (math.cos(angle), math.sin(angle))

    new_angle = angle

    if command == "front_only":
        # Move forward in the direction of the vector
        x += PLAYER_STEP * direction_vector[0]
        y += PLAYER_STEP * direction_vector[1]

    elif command == "front_left":
        # Rotate anti-clockwise by a small angle and move forward
        new_angle = angle - PLAYER_ANGLE_STEP  # Rotate by 10 degrees
        new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
        x += PLAYER_STEP * new_direction_vector[0]
        y += PLAYER_STEP * new_direction_vector[1]

    elif command == "front_right":
        # Rotate clockwise by a small angle and move forward
        new_angle = angle + PLAYER_ANGLE_STEP  # Rotate by 10 degrees
        new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
        x += PLAYER_STEP * new_direction_vector[0]
        y += PLAYER_STEP * new_direction_vector[1]

    elif command == "back_only":
        # Move backward in the opposite direction
        x -= PLAYER_STEP * direction_vector[0]
        y -= PLAYER_STEP * direction_vector[1]

    elif command == "back_left":
        # Rotate anti-clockwise by a small angle and move backward
        new_angle = angle - PLAYER_ANGLE_STEP  # Rotate by 10 degrees
        new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
        x -= PLAYER_STEP * new_direction_vector[0]
        y -= PLAYER_STEP * new_direction_vector[1]

    elif command == "back_right":
        # Rotate clockwise by a small angle and move backward
        new_angle = angle + PLAYER_ANGLE_STEP  # Rotate by 10 degrees
        new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
        x -= PLAYER_STEP * new_direction_vector[0]
        y -= PLAYER_STEP * new_direction_vector[1]

    return x, y, new_angle

def rotate_rectangle(center, width, height, angle):
    """
    Rotate a rectangle by a specified angle.

    Args:
        center (tuple): Center of the rectangle as (x, y).
        width (float): Width of the rectangle.
        height (float): Height of the rectangle.
        angle (float): Rotation angle in degrees.

    Returns:
        list of tuples: Coordinates of the rotated rectangle as [(x1, y1), (x2, y2), (x3, y3), (x4, y4)].
    """
    # Convert the angle to radians
    angle_rad = angle

    # Calculate half-width and half-height
    half_width = width / 2
    half_height = height / 2

    # Calculate the coordinates of the rectangle's corners
    x1 = center[0] - half_width
    y1 = center[1] - half_height

    x2 = center[0] + half_width
    y2 = center[1] - half_height

    x3 = center[0] + half_width
    y3 = center[1] + half_height

    x4 = center[0] - half_width
    y4 = center[1] + half_height

    # Initialize an empty list for the rotated rectangle
    rotated_rectangle = []

    for x, y in [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]:
        # Translate the rectangle so that the center is at the origin (0,0)
        translated_x = x - center[0]
        translated_y = y - center[1]

        # Apply the rotation transformation
        rotated_x = translated_x * math.cos(angle_rad) - translated_y * math.sin(angle_rad)
        rotated_y = translated_x * math.sin(angle_rad) + translated_y * math.cos(angle_rad)

        # Translate the rectangle back to its original position
        rotated_x += center[0]
        rotated_y += center[1]

        rotated_rectangle.append((rotated_x, rotated_y))

    return rotated_rectangle

# Function to check if points are outside the screen boundaries
def points_outside_screen(points, screen_width, screen_height):
    for x, y in points:
        if x < 0 or x > screen_width or y < 0 or y > screen_height:
            return True
    return False


# Create the display window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Parking Lanes")

upper_row = np.random.choice(2,size=5)
lower_row = np.random.choice(2,size=5)

row_choice = np.random.choice(2)

if np.sum(upper_row == 0) == 0:
    if np.sum(lower_row == 0) == 0:
        row_choice = 0
        upper_row[np.random.choice(5)] = 1
    else:
        row_choice = 1

if np.sum(lower_row == 0) == 0:
    if np.sum(upper_row == 0) == 0:
        row_choice = 1
        lower_row[np.random.choice(5)] = 1
    else:
        row_choice = 0

if row_choice == 0:
    _temp = (upper_row == 0) * np.arange(1,6)
    _index = np.random.choice(_temp[_temp > 0])
    CENTER_X = (_index - 1) * PARKING_LANE_WIDTH + int(PARKING_LANE_WIDTH / 2)
    CENTER_Y = int(PARKING_LANE_HEIGHT  / 2)
else:
    _temp = (lower_row == 0) * np.arange(1,6)
    _index = np.random.choice(_temp[_temp > 0])
    CENTER_X = (_index - 1) * PARKING_LANE_WIDTH + int(PARKING_LANE_WIDTH / 2)
    CENTER_Y = HEIGHT - int(PARKING_LANE_HEIGHT  / 2)


count = 0

prev_distance = math.inf

# Main loop
running = True
while running:
    time.sleep(1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(color=(0,0,0))

    reward = 1

    for i in range(1,5):
        pygame.draw.line(surface=screen,color=PARKING_LANE_COLOR,
                         start_pos=(i*PARKING_LANE_WIDTH,0),
                         end_pos=(i*PARKING_LANE_WIDTH,PARKING_LANE_HEIGHT),
                         width=PARKING_LANE_LINE_WIDTH
                         )
    
    for i in range(1,5):
        pygame.draw.line(surface=screen,color=PARKING_LANE_COLOR,
                         start_pos=(i*PARKING_LANE_WIDTH,HEIGHT - PARKING_LANE_HEIGHT),
                         end_pos=(i*PARKING_LANE_WIDTH,HEIGHT),
                         width=PARKING_LANE_LINE_WIDTH
                         )
    
    
    cars_list = []

    pygame.draw.line(surface=screen,color=BOUNDARY_COLOR,start_pos=(0,0),end_pos=(0,HEIGHT),width=PARKING_LANE_LINE_WIDTH)
    pygame.draw.line(surface=screen,color=BOUNDARY_COLOR,start_pos=(0,0),end_pos=(WIDTH,0),width=PARKING_LANE_LINE_WIDTH)
    pygame.draw.line(surface=screen,color=BOUNDARY_COLOR,start_pos=(0,HEIGHT),end_pos=(WIDTH,HEIGHT),width=PARKING_LANE_LINE_WIDTH)
    pygame.draw.line(surface=screen,color=BOUNDARY_COLOR,start_pos=(WIDTH,0),end_pos=(WIDTH,HEIGHT),width=PARKING_LANE_LINE_WIDTH)
    
    for i in range(0,5):
        if upper_row[i] == 0:
            continue
        rect = pygame.Rect((i) * PARKING_LANE_WIDTH + 30,5,CAR_WIDTH,CAR_HEIGHT)
        
        car_rect = pygame.draw.rect(surface=screen,color=CAR_COLOR,rect=rect)

        cars_list.append(rect)

    for i in range(0,5):
        if lower_row[i] == 0:
            continue
        rect = pygame.Rect((i) * PARKING_LANE_WIDTH + 30,HEIGHT - CAR_HEIGHT - 5,CAR_WIDTH,CAR_HEIGHT)
        
        car_rect = pygame.draw.rect(surface=screen,color=CAR_COLOR,rect=rect)

        cars_list.append(rect)

    ray_distances = [MAX_RAY_DISTANCE for x in range(0,NO_OF_RAYS)]
    for i in range(0,NO_OF_RAYS):
        _theta = i * 2 * math.pi / NO_OF_RAYS + PLAYER_ANGLE
        for j in range(0,MAX_RAY_DISTANCE):
            _point_x = int(PLAYER_X + j * math.cos(_theta))
            _point_y = int(PLAYER_Y + j * math.sin(_theta))
            if _point_x < 0 or _point_x >= WIDTH or _point_y < 0 or _point_y >= HEIGHT:
                pass
            else:
                _point = (_point_x,_point_y)
                pixel_at = screen.get_at(_point)
                if pixel_at == BOUNDARY_COLOR or pixel_at == CAR_COLOR:
                    break
                else:
                    ray_distances[i] = j
                    screen.set_at(_point,(150,150,150))

    player_poly_points = rotate_rectangle(center=(PLAYER_X,PLAYER_Y),width=CAR_HEIGHT,height=CAR_WIDTH,angle=PLAYER_ANGLE)

    player_poly = pygame.draw.polygon(surface=screen,color=PLAYER_CAR_COLOR,points=player_poly_points)

    player_rect_top, player_rect_left, player_rect_width, player_rect_height  = bounding_rectangle(player_poly_points)

    player_rect = pygame.Rect(player_rect_left, player_rect_top, player_rect_width, player_rect_height)

    pygame.draw.circle(screen,(255,0,0),(CENTER_X,CENTER_Y),5)

    pygame.draw.line(screen,(255,10,10),(PLAYER_X,PLAYER_Y),(CENTER_X,CENTER_Y))

    PLAYER_X, PLAYER_Y, PLAYER_ANGLE = move(PLAYER_X,PLAYER_Y,PLAYER_ANGLE,np.random.choice(ACTIONS_LIST))

    if points_outside_screen(player_poly_points,WIDTH,HEIGHT):
        running = False
        reward = -100

    for car in cars_list:
        if player_rect.colliderect(car):
            reward = -100
            running = False

    current_distance = calculate_distance(PLAYER_X,PLAYER_Y,CENTER_X,CENTER_Y)

    if current_distance < 20 :
        running = False

    if current_distance <= prev_distance:
        reward = 1
    else:
        reward = -1

    prev_distance = current_distance

    print(count,reward)

    pygame.display.flip()

# Quit pygame
pygame.quit()
sys.exit()