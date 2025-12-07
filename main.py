# main.py
import tkinter as tk
from src.common.constants import GameConfig
from src.common.enums import GameMode
from src.ui.setup import get_game_settings
from src.ui.game_canvas import GameCanvas
from src.utils.debug import DebugLogger
from src.simulation.runner import ScenarioSimulationRunner
from src.strategies.ai import (
    AggressiveAnticipationStrategy,
    NoisyAdaptiveAggressiveStrategy,
    SafeFoodSeekingStrategy,
    SuperiorAdaptiveStrategy
)
import pandas as pd

def setup_game_window(root: tk.Tk, config: GameConfig) -> None:
    """Setup the main game window and center it on screen."""
    root.title("Chain Duel")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - config.WINDOW_WIDTH) // 2
    y = (screen_height - config.WINDOW_HEIGHT) // 2
    root.geometry(f'{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}+{x}+{y}')

def create_controls_label(root: tk.Tk, mode: GameMode, config: GameConfig) -> None:
    """Create and display the controls help text."""
    controls_text = "Controls: Arrow Keys (Green) | R: Restart | ESC: Quit" if mode == GameMode.PLAYER_VS_AI else "Controls: R: Restart | ESC: Quit"
    controls = tk.Label(
        root,
        text=controls_text,
        bg=config.BACKGROUND_COLOR,
        fg=config.TEXT_COLOR
    )
    controls.pack(side='bottom')

def run_interactive_mode(mode: GameMode, strategy1, strategy2, debug: DebugLogger, runner=None) -> None:
    """Run the game in interactive mode (with visual display)."""
    root = tk.Tk()
    config = GameConfig()
    
    setup_game_window(root, config)
    
    # Create and setup game canvas
    game = GameCanvas(root, mode, config, strategy1, strategy2, debug)
    game.pack(expand=True, fill='both')
    create_controls_label(root, mode, config)

    def on_closing(event=None):  # Accepte aussi un event pour ESC
        debug.log("Game closing")
        debug.close()
        root.destroy()
        if runner:
            runner.run()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.bind("<Escape>", on_closing)  # Ajoute ceci pour gérer ESC
    debug.log("Starting main game loop")
    root.mainloop()

def run_simulation_mode(strategy1, strategy2, num_runs: int) -> None:
    """Run the game in simulation mode (batch processing or visual simulation)."""
    choice = input("\nVisualiser la simulation ? (y/n): ").lower()
    if choice == 'y':
        # Mode graphique comme un vrai match IA vs IA
        debug = DebugLogger(False)
        run_interactive_mode(GameMode.AI_VS_AI, strategy1, strategy2, debug)
    else:
        # Mode batch sans interface
        print("\nStarting simulation...")
        runner = ScenarioSimulationRunner(strategy1.__class__, strategy2.__class__, num_runs)
        runner.run_parallel()


def run_game_mode(mode: GameMode, strategy1, strategy2, debug_enabled: bool, num_runs: int = None) -> None:
    if mode == GameMode.SIMULATION:
        if num_runs == 1:
            debug = DebugLogger(False)
            debug.log("Starting single visual simulation (IA vs IA)")
            runner = ScenarioSimulationRunner(strategy1.__class__, strategy2.__class__, num_runs=1, silent=True)
            run_interactive_mode(GameMode.AI_VS_AI, strategy1, strategy2, debug, runner=runner)

        else:
            print("\nStarting batch simulation...")
            runner = ScenarioSimulationRunner(strategy1.__class__, strategy2.__class__, num_runs, silent=True)
            runner.run_parallel()

    else:
        debug = DebugLogger(debug_enabled)
        debug.log("Starting normal game mode")

        # IA vs IA avec affichage du rapport à la fin
        if mode == GameMode.AI_VS_AI:
            runner = ScenarioSimulationRunner(strategy1.__class__, strategy2.__class__, num_runs=1, silent=True)
        else:
            runner = None

        run_interactive_mode(mode, strategy1, strategy2, debug, runner=runner)


def run_all_matchups():
    strategies = [
        AggressiveAnticipationStrategy,
        NoisyAdaptiveAggressiveStrategy,
        SafeFoodSeekingStrategy,
        SuperiorAdaptiveStrategy
    ]

    results = []

    for strat1 in strategies:
        for strat2 in strategies:
            print(f"\nRunning: {strat1.__name__} vs {strat2.__name__}")
            runner = ScenarioSimulationRunner(strat1, strat2, num_runs=10000, silent=True)
            runner.run_parallel()

            
            #LANCEMENT 

            wins1 = runner.stats['wins1']
            wins2 = runner.stats['wins2']
            draws = runner.stats.get('draws', 0)
            total = wins1 + wins2 + draws

            results.append({
                'Player 1': strat1.__name__,
                'Player 2': strat2.__name__,
                'Wins P1': wins1,
                'Wins P2': wins2,
                'Draws': draws,
                '% P1': f"{wins1 / total * 100:.1f}%",
                '% P2': f"{wins2 / total * 100:.1f}%",
                '% Draws': f"{draws / total * 100:.1f}%"
            })

    df = pd.DataFrame(results)
    print(df.to_string(index=False))


def main():
    settings = get_game_settings()

    # Mode batch pour tous les match-ups
    if settings == "all_matchups":
        run_all_matchups()
        return

    if len(settings) == 5:  # Simulation mode
        mode, strategy1, strategy2, _, num_runs = settings
        run_game_mode(mode, strategy1, strategy2, False, num_runs)
    else:  # Interactive modes
        mode, strategy1, strategy2, enable_debug = settings
        run_game_mode(mode, strategy1, strategy2, enable_debug)

if __name__ == "__main__":
    main()
