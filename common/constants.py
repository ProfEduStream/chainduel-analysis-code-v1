# src/common/constants.py
from dataclasses import dataclass
from .enums import Direction

# Constants for grid dimensions
GRID_WIDTH = 51
GRID_HEIGHT = 25

# --- Default Initial Positions ---
DEFAULT_SNAKE1_POSITION = [(6, 12), (5, 12)] #[(24 - i, GRID_HEIGHT // 2) for i in range(2)]  # Exemple: [(6,12), (5,12)]
DEFAULT_SNAKE2_POSITION = [(44, 12), (45, 12)] #[(GRID_WIDTH - 24 + i, GRID_HEIGHT // 2) for i in range(2)]  # Exemple: [(44,12), (45,12)]
DEFAULT_SNAKE1_DIRECTION = Direction.RIGHT
DEFAULT_SNAKE2_DIRECTION = Direction.LEFT

#################### A MODIFIER POUR LES SIMULATIONS ####################
CASE = 1  # Modifiable à 1, 2, 3, ou 4 selon le scénario

#####CAS 1
#CUSTOM_SNAKE1_POSITION = [(6, 12), (5, 12)]
#CUSTOM_SNAKE2_POSITION = [(44, 12), (45, 12)] #cas initial, positions symétriques par rapport à la coinbase

#####CAS 2
#CUSTOM_SNAKE1_POSITION = [(25, 12), (24, 12), (23, 12)]
#CUSTOM_SNAKE2_POSITION = [(27, 12), (28, 12)] #commence par faire haut gauche bas, donc 1 case de retard (2D, même ligne)

#####CAS 3
#CUSTOM_SNAKE1_POSITION = [(25, 12), (24, 12), (23, 12)]
#CUSTOM_SNAKE2_POSITION = [(26, 11), (27, 11)] #commence par faire haut gauche, donc 2 cases de retard (1D 1H)

#####CAS 4
#CUSTOM_SNAKE1_POSITION = [(25, 12), (24, 12), (23, 12)]
#CUSTOM_SNAKE2_POSITION = [(27, 10), (28, 10)] #commence par faire haut haut gauche, donc 3 cases de retard et deux lignes en haut & une de retard en horizontal


if CASE == 1:
    CUSTOM_SNAKE1_POSITION = [(6, 12), (5, 12)]
    CUSTOM_SNAKE2_POSITION = [(44, 12), (45, 12)] #cas initial, positions symétriques par rapport à la coinbase
    STARTING_SCORE_SNAKE1 = 50000
    STARTING_SCORE_SNAKE2 = 50000
    SNAKE1_LENGTH = 2
    SNAKE2_LENGTH = 2
    
elif CASE == 2:
    CUSTOM_SNAKE1_POSITION = [(25, 12), (24, 12), (23, 12)]
    CUSTOM_SNAKE2_POSITION = [(27, 12), (28, 12)] #commence par faire haut gauche bas, donc 1 case de retard (2D, même ligne)
    STARTING_SCORE_SNAKE1 = 52000
    STARTING_SCORE_SNAKE2 = 50000
    SNAKE1_LENGTH = 3
    SNAKE2_LENGTH = 2
    
elif CASE == 3:
    CUSTOM_SNAKE1_POSITION = [(25, 12), (24, 12), (23, 12)]
    CUSTOM_SNAKE2_POSITION = [(26, 11), (27, 11)] #commence par faire haut gauche, donc 2 cases de retard (1D 1H)    
    STARTING_SCORE_SNAKE1 = 52000
    STARTING_SCORE_SNAKE2 = 50000
    SNAKE1_LENGTH = 3
    SNAKE2_LENGTH = 2
    
elif CASE == 4:
    CUSTOM_SNAKE1_POSITION = [(25, 12), (24, 12), (23, 12)]
    CUSTOM_SNAKE2_POSITION = [(27, 10), (28, 10)] #commence par faire haut haut gauche, donc 3 cases de retard et deux lignes en haut & une de retard en horizontal
    STARTING_SCORE_SNAKE1 = 52000
    STARTING_SCORE_SNAKE2 = 50000
    SNAKE1_LENGTH = 3
    SNAKE2_LENGTH = 2
    
else:
    raise ValueError("CASE invalide dans constants.py")

CUSTOM_SNAKE1_DIRECTION = Direction.RIGHT
CUSTOM_SNAKE2_DIRECTION = Direction.LEFT


@dataclass
class GameConfig:
    # Window settings
    WINDOW_WIDTH: int = 1020  # 51 * 20
    WINDOW_HEIGHT: int = 500  # 25 * 20 + score bar
    GRID_SIZE: int = 20
    
    # Game settings
    FPS: int = 15
    #INITIAL_SNAKE_LENGTH: int = 2
    #STARTING_SCORE: int = 50000
    WINNING_SCORE: int = 100000
    SCORE_BAR_HEIGHT: int = 30
    
    # Colors
    GRID_COLOR: str = '#333333'
    SNAKE1_COLOR: str = '#005eff'  # Blue
    SNAKE2_COLOR: str = '#ff1a1a'  # Red
    SCORE_BAR_BG: str = '#444444'
    SCORE_BAR1_COLOR: str = '#003d99'  # Darker blue
    SCORE_BAR2_COLOR: str = '#990000'  # Darker red
    FOOD_COLOR: str = 'yellow'
    BACKGROUND_COLOR: str = 'black'
    TEXT_COLOR: str = 'white'
    
    
    #GRID_COLOR: str = '#333333'
    #SNAKE1_COLOR: str = '#2ecc71'  # Green
    #SNAKE2_COLOR: str = '#e67e22'  # Orange
    #SCORE_BAR_BG: str = '#444444'
    #SCORE_BAR1_COLOR: str = '#1a8045'  # Darker green
    #SCORE_BAR2_COLOR: str = '#b35c00'  # Darker orange
    #FOOD_COLOR: str = 'yellow'
    #BACKGROUND_COLOR: str = 'black'
    #TEXT_COLOR: str = 'white'
    
    # Font settings
    SCORE_FONT: tuple = ('Arial', 16, 'bold')
    GAMEOVER_FONT: tuple = ('Arial', 24, 'bold')
    
    @property
    def GRID_WIDTH(self) -> int:
        return 51
    
    @property
    def GRID_HEIGHT(self) -> int:
        return 25
        
    def calculate_points(self, snake_length: int) -> int:
        """Calculate points based on snake length: 2000 * 2^(L-2)"""
        if snake_length <= 4:
            return int(2000 * (2 ** (snake_length - 2)))
        elif 5 <= snake_length <= 7:
            return 8000
        else:  # snake_length >= 8
            return 16000
