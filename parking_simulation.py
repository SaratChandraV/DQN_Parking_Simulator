import pygame
import numpy as np
import math
import time

class parkingSim():
    def __init__(self) -> None:
        # Constants
        self.WIDTH, self.HEIGHT = 800, 600
        self.MAX_RAY_DISTANCE = 200
        self.NO_OF_RAYS = 8
        self.BOUNDARY_COLOR = (64, 224, 208)
        self.MIN_DISTANCE = 50

        # Parking lane constants
        self.PARKING_LANE_LINE_WIDTH = 5
        self.PARKING_LANE_COLOR = (255, 255, 0)
        self.PARKING_LANE_WIDTH = 160
        self.PARKING_LANE_HEIGHT = 160

        # Car Constants
        self.CAR_WIDTH = self.PARKING_LANE_WIDTH - 60
        self.CAR_HEIGHT = self.PARKING_LANE_HEIGHT + 10
        self.CAR_COLOR = (255, 255, 255)

        # Player car constants
        self.PLAYER_CAR_COLOR = (0, 0, 255)
        self.PLAYER_ANGLE_STEP = math.radians(5)
        self.PLAYER_STEP = 5
        self.ACTIONS_LIST = ["front_only", "front_left", "front_right", "back_only", "back_left", "back_right"]

        # Player Position Variables
        self.PLAYER_X = 400
        self.PLAYER_Y = 300
        self.PLAYER_ANGLE = math.radians(0)
        self.prev_distance = math.inf

        # Other variables
        self.CENTER_X = 0
        self.CENTER_Y = 0

        self.no_of_actions = len(self.ACTIONS_LIST)

        self.screen = None

        self.upper_row = None
        self.lower_row = None
        self.row_choice = None

        self.cars_list = []

        self.is_recording = False

    def move(self, x, y, angle, command):
        # Calculate the direction vector based on the angle
        direction_vector = (math.cos(angle), math.sin(angle))

        new_angle = angle

        if command == "front_only":
            # Move forward in the direction of the vector
            x += self.PLAYER_STEP * direction_vector[0]
            y += self.PLAYER_STEP * direction_vector[1]

        elif command == "front_left":
            # Rotate anti-clockwise by a small angle and move forward
            new_angle = angle - self.PLAYER_ANGLE_STEP  # Rotate by 5 degrees
            new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
            x += self.PLAYER_STEP * new_direction_vector[0]
            y += self.PLAYER_STEP * new_direction_vector[1]

        elif command == "front_right":
            # Rotate clockwise by a small angle and move forward
            new_angle = angle + self.PLAYER_ANGLE_STEP  # Rotate by 5 degrees
            new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
            x += self.PLAYER_STEP * new_direction_vector[0]
            y += self.PLAYER_STEP * new_direction_vector[1]

        elif command == "back_only":
            # Move backward in the opposite direction
            x -= self.PLAYER_STEP * direction_vector[0]
            y -= self.PLAYER_STEP * direction_vector[1]

        elif command == "back_left":
            # Rotate anti-clockwise by a small angle and move backward
            new_angle = angle - self.PLAYER_ANGLE_STEP  # Rotate by 5 degrees
            new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
            x -= self.PLAYER_STEP * new_direction_vector[0]
            y -= self.PLAYER_STEP * new_direction_vector[1]

        elif command == "back_right":
            # Rotate clockwise by a small angle and move backward
            new_angle = angle + self.PLAYER_ANGLE_STEP  # Rotate by 5 degrees
            new_direction_vector = (math.cos(new_angle), math.sin(new_angle))
            x -= self.PLAYER_STEP * new_direction_vector[0]
            y -= self.PLAYER_STEP * new_direction_vector[1]

        return x, y, new_angle

    def calculate_distance(self, x1, y1, x2, y2):
        # Calculate the squared differences
        x_diff = x2 - x1
        y_diff = y2 - y1

        # Calculate the squared Euclidean distance
        distance_squared = x_diff ** 2 + y_diff ** 2

        # Take the square root to get the actual Euclidean distance
        distance = math.sqrt(distance_squared)

        return distance

    def bounding_rectangle(self, points):
        # Calculate the bounding rectangle around a set of points

        # Find the minimum and maximum coordinates
        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_y = min(point[1] for point in points)
        max_y = max(point[1] for point in points)

        left = min_x
        top = min_y
        width = max_x - min_x
        height = max_y - min_y

        return top, left, width, height

    def rotate_rectangle(self, center, width, height, angle):
        """
        Rotate a rectangle by a specified angle.

        Args:
            center (tuple): Center of the rectangle as (x, y).
            width (float): Width of the rectangle.
            height (float): Height of the rectangle.
            angle (float): Rotation angle in radians.

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
    def points_outside_screen(self, points, screen_width, screen_height):
        for x, y in points:
            if x < 0 or x > screen_width or y < 0 or y > screen_height:
                return True
        return False

    def _get_action(self, index):
        return self.ACTIONS_LIST[index]

    def get_action_sample(self):
        return np.random.choice(self.no_of_actions)

    def onDestroy(self):
        pygame.display.quit()
        pygame.quit()

    def set_things(self):
        # Randomly select the upper and lower parking lane configurations
        self.upper_row = np.random.choice(2, size=5)
        self.lower_row = np.random.choice(2, size=5)

        # Randomly choose one row for parking
        self.row_choice = np.random.choice(2)

        if self.row_choice == 0:
            if np.sum(self.upper_row) == 5:
                self.upper_row[np.random.choice(5)] = 0
            _temp = (self.upper_row == 0) * np.arange(1, 6)
            _index = np.random.choice(_temp[_temp > 0])
            self.CENTER_X = (_index - 1) * self.PARKING_LANE_WIDTH + int(self.PARKING_LANE_WIDTH / 2)
            self.CENTER_Y = int(self.PARKING_LANE_HEIGHT / 2)
        
        if self.row_choice == 1:
            if np.sum(self.lower_row) == 5:
                self.lower_row[np.random.choice(5)] = 0
            _temp = (self.lower_row == 0) * np.arange(1, 6)
            _index = np.random.choice(_temp[_temp > 0])
            self.CENTER_X = (_index - 1) * self.PARKING_LANE_WIDTH + int(self.PARKING_LANE_WIDTH / 2)
            self.CENTER_Y = self.HEIGHT - int(self.PARKING_LANE_HEIGHT / 2)

        for i in range(0, 5):
            if self.upper_row[i] == 0:
                continue
            rect = pygame.Rect((i) * self.PARKING_LANE_WIDTH + 30, 5, self.CAR_WIDTH, self.CAR_HEIGHT)
            self.cars_list.append(rect)

        for i in range(0, 5):
            if self.lower_row[i] == 0:
                continue
            rect = pygame.Rect((i) * self.PARKING_LANE_WIDTH + 30, self.HEIGHT - self.CAR_HEIGHT - 5, self.CAR_WIDTH, self.CAR_HEIGHT)
            self.cars_list.append(rect)

    def _get_state(self):
        # Clear the screen
        self.screen.fill(color=(0, 0, 0))

        # Draw the upper and lower parking lanes
        for i in range(1, 5):
            pygame.draw.line(surface=self.screen, color=self.PARKING_LANE_COLOR,
                             start_pos=(i * self.PARKING_LANE_WIDTH, 0),
                             end_pos=(i * self.PARKING_LANE_WIDTH, self.PARKING_LANE_HEIGHT),
                             width=self.PARKING_LANE_LINE_WIDTH
                             )

        for i in range(1, 5):
            pygame.draw.line(surface=self.screen, color=self.PARKING_LANE_COLOR,
                             start_pos=(i * self.PARKING_LANE_WIDTH, self.HEIGHT - self.PARKING_LANE_HEIGHT),
                             end_pos=(i * self.PARKING_LANE_WIDTH, self.HEIGHT),
                             width=self.PARKING_LANE_LINE_WIDTH
                             )

        # Draw boundaries
        pygame.draw.line(surface=self.screen, color=self.BOUNDARY_COLOR, start_pos=(0, 0), end_pos=(0, self.HEIGHT),
                         width=self.PARKING_LANE_LINE_WIDTH)
        pygame.draw.line(surface=self.screen, color=self.BOUNDARY_COLOR, start_pos=(0, 0), end_pos=(self.WIDTH, 0),
                         width=self.PARKING_LANE_LINE_WIDTH)
        pygame.draw.line(surface=self.screen, color=self.BOUNDARY_COLOR, start_pos=(0, self.HEIGHT),
                         end_pos=(self.WIDTH, self.HEIGHT), width=self.PARKING_LANE_LINE_WIDTH)
        pygame.draw.line(surface=self.screen, color=self.BOUNDARY_COLOR, start_pos=(self.WIDTH, 0),
                         end_pos=(self.WIDTH, self.HEIGHT), width=self.PARKING_LANE_LINE_WIDTH)

        # Draw other cars
        for car_rect in self.cars_list:
            pygame.draw.rect(surface=self.screen, color=self.CAR_COLOR, rect=car_rect)

        # Calculate ray distances from the player's car
        ray_distances = [self.MAX_RAY_DISTANCE for x in range(0, self.NO_OF_RAYS)]
        for i in range(0, self.NO_OF_RAYS):
            _theta = i * 2 * math.pi / self.NO_OF_RAYS + self.PLAYER_ANGLE
            for j in range(0, self.MAX_RAY_DISTANCE):
                _point_x = int(self.PLAYER_X + j * math.cos(_theta))
                _point_y = int(self.PLAYER_Y + j * math.sin(_theta))
                if _point_x < 0 or _point_x >= self.WIDTH or _point_y < 0 or _point_y >= self.HEIGHT:
                    pass
                else:
                    _point = (_point_x, _point_y)
                    pixel_at = self.screen.get_at(_point)
                    if pixel_at == self.BOUNDARY_COLOR or pixel_at == self.CAR_COLOR:
                        break
                    else:
                        ray_distances[i] = j
                        if i == 0:
                            self.screen.set_at(_point, (0, 255, 0))
                        else:
                            self.screen.set_at(_point, (150, 150, 150))

        # Draw the player's car
        player_poly_points = self.rotate_rectangle(center=(self.PLAYER_X, self.PLAYER_Y), width=self.CAR_HEIGHT,
                                                   height=self.CAR_WIDTH, angle=self.PLAYER_ANGLE)
        pygame.draw.polygon(surface=self.screen, color=self.PLAYER_CAR_COLOR, points=player_poly_points)

        # Draw the target parking location
        pygame.draw.circle(self.screen, (255, 0, 0), (self.CENTER_X, self.CENTER_Y), 5)

        # Draw a line from the player's car to the target parking location
        pygame.draw.line(self.screen, (255, 10, 10), (self.PLAYER_X, self.PLAYER_Y), (self.CENTER_X, self.CENTER_Y))

        # Update the display
        pygame.display.flip()

        # Return the state as a list of ray distances and car positions
        return ray_distances + [self.PLAYER_X, self.PLAYER_Y, self.CENTER_X, self.CENTER_Y, self.PLAYER_ANGLE]

    def step(self, action):
        if self.is_recording:
            time.sleep(1/120)
        reward = 1
        obs = None
        terminated = False
        truncated = False

        action_name = self.ACTIONS_LIST[action]

        # Move the player's car based on the chosen action
        self.PLAYER_X, self.PLAYER_Y, self.PLAYER_ANGLE = self.move(self.PLAYER_X, self.PLAYER_Y, self.PLAYER_ANGLE, action_name)

        # Update the game state
        obs = self._get_state()

        # Calculate a bounding rectangle for the player's car
        player_poly_points = self.rotate_rectangle(center=(self.PLAYER_X, self.PLAYER_Y), width=self.CAR_HEIGHT, height=self.CAR_WIDTH, angle=self.PLAYER_ANGLE)
        player_rect_top, player_rect_left, player_rect_width, player_rect_height = self.bounding_rectangle(player_poly_points)
        player_rect = pygame.Rect(player_rect_left, player_rect_top, player_rect_width, player_rect_height)

        # Check for termination conditions
        if self.points_outside_screen(player_poly_points, self.WIDTH, self.HEIGHT):
            terminated = True
            reward = -100

        for car in self.cars_list:
            if player_rect.colliderect(car):
                terminated = True
                reward = -100

        # Calculate the current distance from the player's car to the target parking location
        current_distance = self.calculate_distance(self.PLAYER_X, self.PLAYER_Y, self.CENTER_X, self.CENTER_Y)

        if current_distance < self.prev_distance:
            reward = 1
        else:
            reward = -5

        if current_distance < self.MIN_DISTANCE:
            truncated = True
            reward = 1000

        self.prev_distance = current_distance

        return obs, reward, terminated, truncated

    def reset(self):
        pygame.init()
        # Player Position Variables
        self.PLAYER_X = 400
        self.PLAYER_Y = 300
        self.PLAYER_ANGLE = math.radians(0)
        self.prev_distance = math.inf

        # Other variables
        self.CENTER_X = 0
        self.CENTER_Y = 0

        self.cars_list = []

        # Initialize the Pygame screen
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Parking Lanes")

        # Initialize the game environment
        self.set_things()

        # Return the initial state
        return self._get_state()

# Testing Loop
# ps = parkingSim()
# ps.reset()
# running = True
# while running:
#     ob, re, te, tr = ps.step(action=np.random.choice(ps.no_of_actions))
#     print(ob, re, te, tr)
#     if te or tr:
#         running = False