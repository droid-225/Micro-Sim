"""
Simulation-wide constants and configuration defaults.
"""

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Simulation area offsets (sidebar reserved for controls)
SIMULATION_WIDTH = 900
SIMULATION_HEIGHT = WINDOW_HEIGHT
PANEL_WIDTH = WINDOW_WIDTH - SIMULATION_WIDTH

# Particle defaults
PARTICLE_RADIUS = 12
POSITIVE_PARTICLE_MASS = 1836.0 # 1863:1 irl raio
NEGATIVE_PARTICLE_MASS = 1.0
PARTICLE_SPEED_RANGE = (-30, 30)  # pixels per second initial velocity
PARTICLE_MIN_DISTANCE = PARTICLE_RADIUS * 2

# Physics constants
COULOMB_CONSTANT = 6000.0
DAMPING = 0.99  # mild damping to keep system stable
MAX_FORCE = 2000.0  # clamp extreme forces to maintain stability
RESTITUTION = 0.5  # energy retention for elastic collisions
BOND_FORCE_THRESHOLD = 1000.0  # minimum attractive force magnitude to bond
REPULSION_MULTIPLIER = 10.0  # amplify repulsion for like charges
MIN_CHARGE_STRENGTH = 1.0
MAX_CHARGE_STRENGTH = 100.0
MIN_TIME_SCALE = 0.25
MAX_TIME_SCALE = 10.0

# UI defaults
DEFAULT_CHARGE_STRENGTH = 1.0
DEFAULT_MAX_PARTICLES = 150
DEFAULT_SPAWN_COUNT = 1
DEFAULT_ZOOM = 1.0
DEFAULT_TIME_SCALE = 1.0

# Colors
COLOR_BACKGROUND = (12, 12, 20)
COLOR_PANEL_BG = (32, 32, 44)
COLOR_PANEL_BORDER = (64, 64, 80)
COLOR_TEXT = (230, 230, 240)
COLOR_BUTTON = (70, 90, 140)
COLOR_BUTTON_HOVER = (90, 110, 170)
COLOR_SLIDER_TRACK = (80, 80, 120)
COLOR_SLIDER_HANDLE = (200, 200, 220)
COLOR_POSITIVE = (60, 120, 220) 
COLOR_NEGATIVE = (220, 80, 80)
COLOR_NEUTRAL = (200, 200, 200)

# Fonts
FONT_NAME = "freesansbold.ttf"
FONT_SIZE = 16

