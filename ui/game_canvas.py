from __future__ import annotations
import tkinter as tk
from typing import Tuple, Optional, List, Dict, Any
import time
import random
from src.utils.debug import DebugLogger
from src.common.enums import GameMode, Direction
from src.common.types import GameState
from src.common.constants import GameConfig
#################### A MODIFIER POUR LES SIMULATIONS ####################
from src.common.constants import CUSTOM_SNAKE1_POSITION, CUSTOM_SNAKE2_POSITION, CUSTOM_SNAKE1_DIRECTION, CUSTOM_SNAKE2_DIRECTION
from src.common.constants import DEFAULT_SNAKE1_POSITION, DEFAULT_SNAKE2_POSITION, DEFAULT_SNAKE1_DIRECTION, DEFAULT_SNAKE2_DIRECTION
from src.common.constants import STARTING_SCORE_SNAKE1, STARTING_SCORE_SNAKE2



Position = Tuple[int, int]

class GameCanvas(tk.Canvas):
    def __init__(self, 
                 master: tk.Tk,
                 mode: GameMode,
                 config: GameConfig = None,
                 strategy1: Optional[Any] = None,
                 strategy2: Optional[Any] = None,
                 debug: Optional[DebugLogger] = None) -> None:
        # Initialize configuration
        self.config = config or GameConfig()
        
        # Setup canvas
        super().__init__(
            master,
            width=self.config.WINDOW_WIDTH,
            height=self.config.WINDOW_HEIGHT + self.config.SCORE_BAR_HEIGHT,
            bg=self.config.BACKGROUND_COLOR,
            highlightthickness=0
        )
        
        # Game settings
        self.mode = mode
        self.strategy1 = strategy1
        self.strategy2 = strategy2
        self.debug = debug or DebugLogger(False)
        
        # Canvas dimensions
        self.width = self.config.WINDOW_WIDTH
        self.height = self.config.WINDOW_HEIGHT
        self.cell_size = self.config.GRID_SIZE
        self.grid_width = self.config.GRID_WIDTH
        self.grid_height = self.config.GRID_HEIGHT
        
        # Game state initialization
        self.last_move_time = time.time()
        self.after_id = None
        self.is_paused = False
        
        # Initialize game and start updates
        self.init_game_state()
        self.step_counter = 0
        self.bind_all('<Key>', self.handle_keypress)
        self.start_game_loop()
    
    def start_game_loop(self) -> None:
        """Start or restart the game update loop."""
        if self.after_id:
            self.after_cancel(self.after_id)
        self.after_id = self.after(16, self.update_game)

    def init_game_state(self) -> None:
        """Initialize or reset the game state."""
        self.game_over = False
        self.winner = None
        self.score1 = STARTING_SCORE_SNAKE1
        self.score2 = STARTING_SCORE_SNAKE2
        #################### A MODIFIER POUR LES SIMULATIONS ####################
        self.snake1 = CUSTOM_SNAKE1_POSITION.copy()
        self.snake2 = CUSTOM_SNAKE2_POSITION.copy()
        self.direction1 = CUSTOM_SNAKE1_DIRECTION
        self.direction2 = CUSTOM_SNAKE2_DIRECTION
        self.food_pos = self._place_food()
        assert self.food_pos is not None, "Erreur critique : self.food_pos est None"


    def handle_keypress(self, event: tk.Event) -> None:
        """Handle keyboard input for player controls and game management."""
        key = event.keysym
        
        if key == 'r':
            self.init_game_state()
            self.step_counter = 0
            self.start_game_loop()
            return
        if key == 'Escape':
            if self.after_id:
                self.after_cancel(self.after_id)
            self.master.destroy()
            return
        if key == 'space':
            self.is_paused = not self.is_paused  # Bascule entre pause et reprise
            return
    
        if not self.game_over and self.mode == GameMode.PLAYER_VS_AI:
            key_to_direction = {
                'Up': Direction.UP,
                'Down': Direction.DOWN,
                'Left': Direction.LEFT,
                'Right': Direction.RIGHT
            }
            if key in key_to_direction:
                new_dir = key_to_direction[key]
                if not Direction.opposite(new_dir) == self.direction1:
                    self.direction1 = new_dir

    def _place_food(self) -> Position:
        # Si la position des serpents correspond au cas spécifique, on place la food au centre
        if self.snake1 == [(6, 12), (5, 12)] and self.snake2 == [(44, 12), (45, 12)]:
            return (25, 12)
        # Sinon comportement normal
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake1 and (x, y) not in self.snake2 and (x, y) != (self.grid_width // 2, self.grid_height // 2):
                return (x, y)


    def move_snake(self, snake: List[Position], direction: Direction) -> Tuple[List[Position], bool]:
        """Move a snake in the specified direction. Returns (new_positions, hit_wall)"""
        if not snake:  # Safety check
            return snake, False
            
        head_x, head_y = snake[0]
        dx, dy = direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if not (0 <= new_head[0] < self.grid_width and 0 <= new_head[1] < self.grid_height):
            return snake, True
        
        # Check if food is collected
        if new_head == self.food_pos:
            return [new_head] + snake, False  # Grow snake
        
        return [new_head] + snake[:-1], False  # Move without growing

    def reset_snake(self, snake_id: int) -> None:
        """Reset a snake to its starting position and initial direction."""
        if snake_id == 1:
            self.snake1 = DEFAULT_SNAKE1_POSITION.copy()
            self.direction1 = DEFAULT_SNAKE1_DIRECTION
        else:
            self.snake2 = DEFAULT_SNAKE2_POSITION.copy()
            self.direction2 = DEFAULT_SNAKE2_DIRECTION
        
    def check_collisions(self) -> None:
        """Check and handle all types of collisions."""
        if not self.snake1 or not self.snake2:  # Safety check
            return
            
        head1 = self.snake1[0]
        head2 = self.snake2[0]
        
        # Wall collisions are now handled during move_snake
        
        # Self collisions
        if head1 in self.snake1[1:]:
            self.reset_snake(1)
            
        if head2 in self.snake2[1:]:
            self.reset_snake(2)
        
        # Head-to-head collision
        if head1 == head2:
            self.reset_snake(1)
            self.reset_snake(2)
            return
        
        # Head to body collisions
        if head1 in self.snake2:
            self.reset_snake(1)
            
        if head2 in self.snake1:
            self.reset_snake(2)

    def update_game(self) -> None:
        """Main game update logic."""
        current_time = time.time()
        speed_threshold = 0.001 if self.mode == GameMode.SIMULATION else 0.1
        if current_time - self.last_move_time >= speed_threshold:  # Game speed control
            if not self.game_over:
                if self.is_paused:
                    self.after_id = self.after(16, self.update_game)
                    return
                # Get AI moves
                if self.mode in [GameMode.AI_VS_AI, GameMode.PLAYER_VS_AI]:
                    state = GameState(
                        snake1=self.snake1.copy(),
                        snake2=self.snake2.copy(),
                        food_position=self.food_pos,
                        grid_width=self.grid_width,
                        grid_height=self.grid_height,
                        score1=self.score1,
                        score2=self.score2
                    )
                    
                    if self.mode == GameMode.AI_VS_AI and self.strategy1:
                        self.direction1 = self.strategy1.get_next_move(state, 1)
                    if self.strategy2:
                        self.direction2 = self.strategy2.get_next_move(state, 2)

                # Move snakes and handle food collection
                old_len1 = len(self.snake1)
                old_len2 = len(self.snake2)
                self.step_counter += 1
                
                # Handle wall collisions during movement
                new_snake1, hit_wall1 = self.move_snake(self.snake1, self.direction1)
                new_snake2, hit_wall2 = self.move_snake(self.snake2, self.direction2)
                
                if hit_wall1:
                    self.reset_snake(1)
                else:
                    self.snake1 = new_snake1
                    
                if hit_wall2:
                    self.reset_snake(2)
                else:
                    self.snake2 = new_snake2
                
                # Handle food collection and scoring
                if self.snake1[0] == self.food_pos:
                    points = self.config.calculate_points(len(self.snake1)-1)
                    self.score1 += points
                    self.score2 = max(0, self.score2 - points)
                    if self.score1 >= self.config.WINNING_SCORE:
                        self.game_over = True
                        self.winner = "Blue"
                    self.food_pos = self._place_food()

                elif self.snake2[0] == self.food_pos:
                    points = self.config.calculate_points(len(self.snake2)-1)
                    self.score2 += points
                    self.score1 = max(0, self.score1 - points)
                    if self.score2 >= self.config.WINNING_SCORE:
                        self.game_over = True
                        self.winner = "Red"
                    self.food_pos = self._place_food()
                
                self.check_collisions()
                self.last_move_time = current_time
        
        self.draw_game()
        self.create_text(
            self.width // 2,
            self.height - 20,
            text=f"Steps: {self.step_counter}",
            fill="white",
            font=("Arial", 12)
        )
        self.after_id = self.after(16, self.update_game)

    def draw_score_bar(self) -> None:
        """Draw the score distribution bar."""
        bar_height = self.config.SCORE_BAR_HEIGHT - 6
        bar_y = self.height + 3
        total_width = self.width - 100
        
        # Calculate proportions
        score_span = self.config.WINNING_SCORE
        score1_width = max(0, min(total_width, (self.score1 / score_span) * total_width))
        score2_width = max(0, min(total_width, (self.score2 / score_span) * total_width))
        
        # Background bar
        self.create_rectangle(
            50, bar_y,
            50 + total_width, bar_y + bar_height,
            fill=self.config.SCORE_BAR_BG
        )
        
        # Score bars
        self.create_rectangle(
            50, bar_y,
            50 + score1_width, bar_y + bar_height,
            fill=self.config.SCORE_BAR1_COLOR
        )
        self.create_rectangle(
            50 + total_width - score2_width, bar_y,
            50 + total_width, bar_y + bar_height,
            fill=self.config.SCORE_BAR2_COLOR
        )

    def draw_game(self) -> None:
        """Render the game state."""
        self.delete('all')
            
        if self.game_over:
            self.create_text(
                self.width // 2,
                self.height // 2,
                text=f"Game Over!\n{self.winner} Wins!\nScore: {max(self.score1, self.score2):,} \nLength: {self.step_counter} \nPress R to restart",
                fill='white',
                font=('Arial', 24, 'bold'),
                justify='center'
            )
            self.draw_score_bar()
            return
        
        # Draw grid
        for i in range(0, self.width + 1, self.cell_size):
            self.create_line(i, 0, i, self.height, fill=self.config.GRID_COLOR)
        for i in range(0, self.height + 1, self.cell_size):
            self.create_line(0, i, self.width, i, fill=self.config.GRID_COLOR)
        
        # Draw snakes
        for snake_positions, head_color, base_color in [
            (self.snake1, self.config.SNAKE1_COLOR, '#164a29'),
            (self.snake2, self.config.SNAKE2_COLOR, '#a65602')
        ]:
            # Draw body
            for x, y in snake_positions[1:]:
                self.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=base_color, outline=''
                )
            # Draw head
            if snake_positions:
                x, y = snake_positions[0]
                self.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=head_color, outline=''
                )
        
        # Draw food
        food_x, food_y = self.food_pos
        self.create_oval(
            food_x * self.cell_size + 2, food_y * self.cell_size + 2,
            (food_x + 1) * self.cell_size - 2, (food_y + 1) * self.cell_size - 2,
            fill=self.config.FOOD_COLOR
        )
        
        # Draw scores
        self.create_text(
            100, 20,
            text=f'Blue: {self.score1:,}',
            fill=self.config.SNAKE1_COLOR,
            font=self.config.SCORE_FONT
        )
        self.create_text(
            self.width - 100, 20,
            text=f'Red: {self.score2:,}',
            fill=self.config.SNAKE2_COLOR,
            font=self.config.SCORE_FONT
        )
        
        # Draw score bar
        self.draw_score_bar()
