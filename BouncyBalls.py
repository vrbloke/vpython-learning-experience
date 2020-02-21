from vpython import *
import random

## TO DO LIST
# 1. Figure out why balls are able to gain infinite energy by colliding with stationary balls
# 2. Fix division by zero errors (jesus christ i dont wanna do this)
# 3. Alter bounce function so it can be used for colliding with both walls and balls

# Variables
dt = 1/60
gravitational_acceleration = 9.81
origin = vector(0, 0, 0)
randomness_range = 15
precision_coefficient = 0.05

## CLASSES
# VelocitySphere: like normal sphere but has physics (affected by gravity and can bounce)
class VelocitySphere(sphere):
    def __init__(self, position, radius, color, velocity = vector(0,0,0)):
        super().__init__(pos=position, radius=radius, color=color)
        self.velocity = velocity
        self.hpos = position

    # Randomizes velocity for excitement and wonder
    def random_velocity(self):
        self.velocity = vector.random() * random.random() * randomness_range
        self.velocity.z = 0

    # Predicts the sphere's movement according to its velocity
    def predict_movement(self):
        self.hpos = self.pos + self.velocity

    # Moves the sphere according to its velocity
    def move(self):
        self.pos = self.pos + self.velocity

    # Changes the sphere's velocity as dictated by gravity
    def apply_gravity(self, gravitational_acceleration):
        self.velocity = self.velocity + gravitational_acceleration * dt * vector(0, -1, 0)

    # Bounce off walls
    def bounce(self, x, y):
        self.velocity.x = self.velocity.x * x
        self.velocity.y = self.velocity.y * y

# Frame: 4 boxes framing the scene
class Frame:
    def __init__(self, position, length, height):
        self.pos = position
        self.length = length
        self.height = height

        # Create the 4 boxes
        self.wallR = box(pos = self.pos + vector(self.length/2, 0, 0), size = vector(self.length/20, self.height, 5), color = color.red)
        self.wallL = box(pos = self.pos + vector(-self.length/2, 0, 0), size = vector(self.length/20, self.height, 5), color = color.red)
        self.wallD = box(pos = self.pos + vector(0, -self.height/2, 0), size = vector(self.length, self.height/20, 5), color = color.red)
        self.wallU = box(pos = self.pos + vector(0, self.height/2, 0), size = vector(self.length, self.height/20, 5), color = color.red)
        self.fullbox = compound([self.wallR, self.wallL, self.wallD, self.wallU])

## FUNCTIONS
def create_ball(position, radius, color, velocity, list):
    ball = VelocitySphere(position, radius, color, velocity)
    list.append(ball)

def create_random_ball(radius, color, frame, list):
    position = vector(random.random() * (frame.length/2 - frame.length/20), random.random() * (frame.height/2 - frame.height/20), 0)
    ball = VelocitySphere(position, radius, color)
    ball.random_velocity()
    list.append(ball)

def randomize_velocities():
    for object in velocityspheres:
        object.random_velocity()

def create_random_ball_click():
    create_random_ball(10, color.green, frame, velocityspheres)

# Create lists to hold like objects
velocityspheres = []

# Scene information
scene.bind('click', randomize_velocities)
button = canvas(width = 230, height = 130)
button.bind('click', create_random_ball_click)
buttonbox = box(length = 200, height = 100)
buttontext = label(text = "Add ball", align = "center", color = color.black, height = 30)
scene.select()
scene.caption = """Press any mouse button to randomize the balls' velocities.
Press the white button to add a new ball.
WARNING: Adding too many balls will eventually cause the scene to freeze. I'll fix this later."""

# Create the frame
frame = Frame(origin, 390, 300)

# Create necessary balls
random.seed()
for i in range(3):
    create_random_ball(10, color.green, frame, velocityspheres)

# Start simulation
while True:
    rate(60)
    # Movement of balls occurs in three main stages:
    # 1. Predict the ball's movement if affected only by gravity
    # 2. Correct the movement if collisions occur or otherwise necessary
    # 3. Repredict movement until no corrections are necessary
    # 4. Actually move the ball
    for ball in velocityspheres:
        # Apply gravity
        ball.apply_gravity(gravitational_acceleration)

        # Predict movement
        ball.predict_movement()

        # Bounce off walls if necessary
        if ball.hpos.x + ball.radius > frame.length/2 - frame.wallR.length/2: # Beyond wallR
            ball.pos.x = frame.length/2 - frame.wallR.length/2 - ball.radius
            ball.bounce(-1, 1)
            ball.hpos = ball.pos
            continue
        if ball.hpos.x - ball.radius < -frame.length/2 + frame.wallL.length/2: # Beyond wallL
            ball.pos.x = -frame.length/2 + frame.wallL.length/2 + ball.radius
            ball.bounce(-1, 1)
            ball.hpos = ball.pos
            continue
        if ball.hpos.y + ball.radius > frame.height/2 - frame.wallU.height/2: # Beyond wallU
            ball.pos.y = frame.height/2 - frame.wallU.height/2 - ball.radius
            ball.bounce(1, -1)
            ball.hpos = ball.pos
            continue
        if ball.hpos.y - ball.radius < -frame.height/2 + frame.wallD.height/2: # Beyond wallD
            ball.pos.y = -frame.height/2 + frame.wallD.height/2 + ball.radius
            ball.bounce(1, -1)
            ball.hpos = ball.pos
            continue

        # Detect collision with other balls and collide if necessary
        for ball_b in velocityspheres:
            if ball_b is ball:
                continue
            axis = ball.hpos - ball_b.pos
            if mag(axis) <= ball.radius + ball_b.radius:
                velocity = ball.velocity
                velocity_b = ball_b.velocity
                # Calculate the angles
                angle_velocity_axis = acos(dot(velocity, axis) / (mag(velocity) * mag(axis)))
                angle_to_rotate = pi/2 - angle_velocity_axis
                angle_to_rotate_b = acos(dot(velocity_b, axis) / (mag(velocity_b) * mag(axis)))
                # Rotate the velocities
                ## velocity
                velocity.x = velocity.x * cos(angle_to_rotate) + velocity.y * sin(angle_to_rotate)
                velocity.y = velocity.y * sin(angle_to_rotate) - velocity.x * sin(angle_to_rotate)
                ## velocity_b
                velocity_b.x = velocity_b.x * cos(angle_to_rotate_b) + velocity_b.y * sin(angle_to_rotate_b)
                velocity_b.y = velocity_b.y * sin(angle_to_rotate_b) - velocity_b.x * sin(angle_to_rotate_b)
                # Switch magnitudes
                if mag(velocity) == 0:
                    velocity = velocity_b
                    velocity_b = vector(0, 0, 0)
                elif mag(velocity_b) == 0:
                    velociby_b = velocity
                    velocity = vector(0, 0, 0)
                else:
                    helper = mag(velocity_b) / mag(velocity)
                    velocity_b = velocity_b * mag(velocity)/mag(velocity_b)
                    velocity = velocity * helper
                # Offset
                ball.predict_movement()
                while mag(ball.hpos - ball_b.pos) <= ball.radius + ball_b.radius:
                    ball.pos = ball.pos + hat(axis) * (ball.radius + ball_b.radius) * precision_coefficient
                    ball.predict_movement()
                ball.hpos = ball.pos

        # Move
        ball.move()
