from typing import Tuple, List, Dict, Any
from tqdm import tqdm
from datetime import datetime
import os
import random
import statistics
import ast
import multiprocessing

from ..common.enums import Direction
from ..core.snake import Snake
from ..core.game_state import GameState
from ..common.constants import GameConfig
#################### A MODIFIER POUR LES SIMULATIONS ####################
from ..common.constants import (
    CUSTOM_SNAKE1_POSITION,
    CUSTOM_SNAKE2_POSITION,
    CUSTOM_SNAKE1_DIRECTION,
    CUSTOM_SNAKE2_DIRECTION
)
from ..common.constants import (
    DEFAULT_SNAKE1_POSITION,
    DEFAULT_SNAKE2_POSITION,
    DEFAULT_SNAKE1_DIRECTION,
    DEFAULT_SNAKE2_DIRECTION
)
from ..common.constants import (
    SNAKE1_LENGTH,
    SNAKE2_LENGTH,
    STARTING_SCORE_SNAKE1,
    STARTING_SCORE_SNAKE2
)

class InitialPosition:
    def __init__(self, x: int, y: int, direction: Direction, description: str):
        self.x = x
        self.y = y
        self.direction = direction
        self.description = description

class ScenarioSimulationRunner:
    def run_parallel(self, num_processes: int = None):
        import time

        num_processes = 8
        snake2_pos = InitialPosition(
            x=self.config.GRID_WIDTH - 7,
            y=self.config.GRID_HEIGHT // 2,
            direction=Direction.LEFT,
            description="Standard position"
        )

        start_time = time.time()

        # 💡 Choix entre séquentiel et multiprocessing en fonction du nombre de simulations
        if self.num_runs <= 100000:  # Seuil à ajuster selon tes besoins
            print("\n🔹 Petit volume détecté : exécution séquentielle...")
            results_iter = []
            with tqdm(total=self.num_runs, desc="Simulations Progress", dynamic_ncols=True, unit="sim") as progress_bar:
                for _ in range(self.num_runs):
                    results_iter.append(self.run_single_game_wrapper(snake2_pos))
                    progress_bar.update(1)
        else:
            print("\n🔹 Lancement en mode multiprocessing...")
            with multiprocessing.Pool(processes=num_processes) as pool:
                results_iter = pool.imap_unordered(
                    self.run_single_game_wrapper,
                    [snake2_pos] * self.num_runs,
                    chunksize=50
                )
                results_iter = tqdm(results_iter, total=self.num_runs, desc="Simulations Progress", dynamic_ncols=True, unit="sim")

        # 📝 Traitement des résultats
        for final_state, is_draw in results_iter:
            score1, length1 = final_state[0]
            score2, length2 = final_state[1]

            if score1 >= self.config.WINNING_SCORE:
                self.stats['wins1'] += 1
            elif score2 >= self.config.WINNING_SCORE:
                self.stats['wins2'] += 1
            elif is_draw:
                self.stats['draws'] = self.stats.get('draws', 0) + 1

        total_time = time.time() - start_time
        time_per_sim = total_time / self.num_runs
        sim_per_sec = self.num_runs / total_time

        # 📊 Affichage des résultats
        total_games = self.num_runs
        wins1 = self.stats['wins1']
        wins2 = self.stats['wins2']
        draws = self.stats.get('draws', 0)

        print("\n===== 📊 Résultats des Simulations =====")
        print(f"🏆 Joueur 1 : {wins1} victoires ({wins1 / total_games * 100:.1f}%)")
        print(f"🏆 Joueur 2 : {wins2} victoires ({wins2 / total_games * 100:.1f}%)")
        print(f"🤝 Matchs nuls : {draws} ({draws / total_games * 100:.1f}%)")
        print(f"⏱️ Temps total : {total_time:.2f} secondes")
        print(f"📈 Temps moyen par simulation : {time_per_sim:.4f} secondes")
        print("==========================================\n")


    def run_single_game_wrapper(self, snake2_pos):
        return self.run_single_game(snake2_pos)
    
    def __init__(self, strategy1_class, strategy2_class, num_runs: int, silent: True):
        self.strategy1_class = strategy1_class  # <-- stocke la classe, pas l'instance
        self.strategy2_class = strategy2_class
        self.num_runs = num_runs
        self.silent = silent
        self.save_results = False
        self.config = GameConfig()
        
        self.sim_dir = 'scenario_simulations'
        os.makedirs(self.sim_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_dir = os.path.join(self.sim_dir, f'sim_{timestamp}')
        os.makedirs(self.run_dir, exist_ok=True)
        
        self.results_file = os.path.join(self.run_dir, 'results.txt')
        self.stats_file = os.path.join(self.run_dir, 'stats.txt')
        
        self.stats = {
            'wins1': 0,
            'wins2': 0,
            'avg_score1': [],
            'avg_score2': [],
            'max_length1': [],
            'max_length2': [],
            'game_lengths': [],
            'strategy1_name': strategy1_class.__name__,
            'strategy2_name': strategy2_class.__name__,
            'position_stats': {}
        }

    def init_specific_scenario(self, snake2_pos: InitialPosition) -> GameState:
        food = self._place_food(CUSTOM_SNAKE1_POSITION, CUSTOM_SNAKE2_POSITION)
        
        state = GameState(
        #################### A MODIFIER POUR LES SIMULATIONS ####################
            snake1=CUSTOM_SNAKE1_POSITION.copy(),
            snake2=CUSTOM_SNAKE2_POSITION.copy(),
            food_position=food,
            grid_width=self.config.GRID_WIDTH,
            grid_height=self.config.GRID_HEIGHT,
            score1=STARTING_SCORE_SNAKE1,
            score2=STARTING_SCORE_SNAKE2
        )
        
        return state

    def _place_food(self, snake1_body: List[Tuple[int, int]], snake2_body: List[Tuple[int, int]]) -> Tuple[int, int]:
        # Si la position des serpents correspond au cas spécifique, on place la food au centre
        if snake1_body == [(6, 12), (5, 12)] and snake2_body == [(44, 12), (45, 12)]:
            return (25, 12)
        # Sinon comportement normal
        while True:
            x = random.randint(0, self.config.GRID_WIDTH - 1)
            y = random.randint(0, self.config.GRID_HEIGHT - 1)
            if (x, y) not in snake1_body and (x, y) not in snake2_body:
                return (x, y)


    def run_single_game(self, snake2_pos: InitialPosition) -> Tuple[str, bool]:
        # Création des instances fraîches UNE SEULE FOIS par partie
        strategy1 = self.strategy1_class()
        strategy2 = self.strategy2_class()

        game_state = self.init_specific_scenario(snake2_pos)

        snake1 = Snake(game_state.snake1.copy(), CUSTOM_SNAKE1_DIRECTION)
        snake2 = Snake(game_state.snake2.copy(), CUSTOM_SNAKE2_DIRECTION)

        history = []
        # Supposons que max_steps soit initialisé en haut
        max_steps = 10000
        is_draw = False

        while True:
            direction1 = strategy1.get_next_move(game_state, 1)
            direction2 = strategy2.get_next_move(game_state, 2)

            next_head1 = (snake1.head[0] + direction1.value[0], snake1.head[1] + direction1.value[1])
            next_head2 = (snake2.head[0] + direction2.value[0], snake2.head[1] + direction2.value[1])

            hit_wall1 = not (0 <= next_head1[0] < game_state.grid_width and 0 <= next_head1[1] < game_state.grid_height)
            hit_wall2 = not (0 <= next_head2[0] < game_state.grid_width and 0 <= next_head2[1] < game_state.grid_height)

            snake1_body = set(snake1.body[:-1])
            snake2_body = set(snake2.body[:-1])

            collide1 = next_head1 in snake1_body or next_head1 in snake2.body
            collide2 = next_head2 in snake2_body or next_head2 in snake1.body

            head_on_collision = next_head1 == next_head2


            if head_on_collision:
                # Reset Snake1
                game_state.snake1 = DEFAULT_SNAKE1_POSITION.copy()
                snake1 = Snake(game_state.snake1, DEFAULT_SNAKE1_DIRECTION)
                snake1.body = DEFAULT_SNAKE1_POSITION.copy()

                # Reset Snake2
                game_state.snake2 = DEFAULT_SNAKE2_POSITION.copy()
                snake2 = Snake(game_state.snake2, DEFAULT_SNAKE2_DIRECTION)
                snake2.body = DEFAULT_SNAKE2_POSITION.copy()
            else:
                if hit_wall1 or collide1:
                    game_state.snake1 = DEFAULT_SNAKE1_POSITION.copy()
                    snake1 = Snake(game_state.snake1, DEFAULT_SNAKE1_DIRECTION)
                    snake1.body = DEFAULT_SNAKE1_POSITION.copy()
                else:
                    snake1.set_direction(direction1)
                    snake1.move(game_state.grid_width, game_state.grid_height, snake2)

                if hit_wall2 or collide2:
                    game_state.snake2 = DEFAULT_SNAKE2_POSITION.copy()
                    snake2 = Snake(game_state.snake2, DEFAULT_SNAKE2_DIRECTION)
                    snake2.body = DEFAULT_SNAKE2_POSITION.copy()
                else:
                    snake2.set_direction(direction2)
                    snake2.move(game_state.grid_width, game_state.grid_height, snake1)

            game_state.snake1 = snake1.body
            game_state.snake2 = snake2.body

            # Nourriture
            if snake1.head == game_state.food_position:
                points = self.config.calculate_points(len(snake1.body))
                snake1.grow()
                game_state.score1 = game_state.score1 + points
                game_state.score2 = max(0, game_state.score2 - points)    # Pas de score négatif
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)

            elif snake2.head == game_state.food_position:
                points = self.config.calculate_points(len(snake2.body))
                snake2.grow()
                game_state.score2 = game_state.score2 + points 
                game_state.score1 = max(0, game_state.score1 - points)    # Pas de score négatif
                game_state.food_position = self._place_food(game_state.snake1, game_state.snake2)

            history.append(([game_state.score1, len(snake1.body)], [game_state.score2, len(snake2.body)]))

            # === FIN DE PARTIE ? ===
            if game_state.score1 >= self.config.WINNING_SCORE:
                winner = 1
                break
            elif game_state.score2 >= self.config.WINNING_SCORE:
                winner = 2
                break
            elif len(history) >= max_steps:
                is_draw = True
                break

        #print(f"FIN DE PARTIE : score1={game_state.score1}, score2={game_state.score2}, steps={len(history)}")
        final_state = ([game_state.score1, len(snake1.body)], [game_state.score2, len(snake2.body)])
        return final_state, is_draw



    def run(self):
        center_y = self.config.GRID_HEIGHT // 2
        snake2_start_pos = InitialPosition(
            x=self.config.GRID_WIDTH - 7,
            y=center_y,
            direction=Direction.LEFT,
            description="Standard position"
        )

        pos_key = f"Position {snake2_start_pos.description}"
        self.stats['position_stats'][pos_key] = {
            'wins1': 0,
            'wins2': 0,
            'avg_score1': [],
            'avg_score2': [],
        }

        print(f"\nRunning simulations for Snake 2 {snake2_start_pos.description}")
        for _ in tqdm(range(self.num_runs), desc="Progress"):
            final_state, is_draw = self.run_single_game(snake2_start_pos)
            score1, length1 = final_state[0]
            score2, length2 = final_state[1]


            if not self.silent:
                self.stats['avg_score1'].append(score1)
                self.stats['avg_score2'].append(score2)
                self.stats['max_length1'].append(length1)
                self.stats['max_length2'].append(length2)

                self.stats['position_stats'][pos_key]['avg_score1'].append(score1)
                self.stats['position_stats'][pos_key]['avg_score2'].append(score2)

            if score1 >= self.config.WINNING_SCORE:
                self.stats['wins1'] += 1
                self.stats['position_stats'][pos_key]['wins1'] += 1

            elif score2 >= self.config.WINNING_SCORE:
                self.stats['wins2'] += 1
                self.stats['position_stats'][pos_key]['wins2'] += 1

            elif is_draw:
                #print(f"🟡 DRAW | max_steps atteint | Score1: {score1} | Score2: {score2} | Steps: {len(states)}")
                self.stats['draws'] = self.stats.get('draws', 0) + 1
                self.stats['position_stats'][pos_key]['draws'] = self.stats['position_stats'][pos_key].get('draws', 0) + 1

        if not self.silent and self.save_results:
            self.save_and_print_report()

    def save_and_print_report(self):
        with open(self.stats_file, 'w') as f:
            f.write(f"=== Specific Scenario Simulation Report ===\n")
            f.write(f"Strategies: {self.stats['strategy1_name']} vs {self.stats['strategy2_name']}\n")
            f.write(f"Total Games: {self.num_runs}\n\n")
            
            f.write("Overall Results:\n")
            total_games = self.num_runs
            f.write(f"Player 1: {self.stats['wins1']} ({self.stats['wins1']/total_games*100:.1f}%)\n")
            f.write(f"Player 2: {self.stats['wins2']} ({self.stats['wins2']/total_games*100:.1f}%)\n")
            if 'draws' in self.stats:
                    f.write(f"Nuls: {self.stats['draws']} ({self.stats['draws']/total_games*100:.1f}%)\n\n")
            
            f.write("Results by Starting Position:\n")
            for pos_key, pos_stats in self.stats['position_stats'].items():
                f.write(f"\n{pos_key}:\n")
                f.write(f"  Wins P1: {pos_stats['wins1']}\n")
                f.write(f"  Wins P2: {pos_stats['wins2']}\n")
                f.write(f"  Avg Score P1: {statistics.mean(pos_stats['avg_score1']):,.0f}\n")
                f.write(f"  Avg Score P2: {statistics.mean(pos_stats['avg_score2']):,.0f}\n")
            
            f.write("\nOverall Statistics:\n")
            f.write(f"Average Game Length: {statistics.mean(self.stats['game_lengths']):.1f} steps\n")
            f.write(f"Max Snake Lengths - P1: {max(self.stats['max_length1'])}, P2: {max(self.stats['max_length2'])}\n")
        
        print(f"\nResults saved to: {self.run_dir}")
        with open(self.stats_file, 'r') as f:
            print(f.read())
