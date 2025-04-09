import random
import pickle
import os
import collections

class TicTacToeEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        """Resets the board to an empty state."""
        self.board = [" " for _ in range(9)] # Represent board as a list of 9
        self.done = False
        self.winner = None
        return tuple(self.board) # Return state as a tuple (hashable)

    def get_state(self):
        """Returns the current board state as a tuple."""
        return tuple(self.board)

    def get_available_actions(self):
        """Returns a list of indices for empty cells (valid moves)."""
        return [i for i, cell in enumerate(self.board) if cell == " "]

    def step(self, action, player):
        """Applies an action (placing a mark) and returns new state, reward, done."""
        if self.board[action] != " " or self.done:
            # Invalid move or game already finished - potentially return large negative reward
            # For simplicity here, we'll assume valid moves are always chosen by the agent
            # In a robust implementation, handle this better.
            return self.get_state(), -10, self.done # Heavy penalty for invalid move

        self.board[action] = player
        self.winner = self.check_winner()

        reward = 0
        if self.winner:
            self.done = True
            if self.winner == player: # Agent won
                reward = 1
            elif self.winner == "Draw": # Draw
                reward = 0.5
            else: # Agent lost
                reward = -1
        elif " " not in self.board: # Draw condition if no winner yet
             self.done = True
             self.winner = "Draw"
             reward = 0.5
        # else: reward = 0 # Optional: Small negative reward per step?

        return self.get_state(), reward, self.done

    def check_winner(self):
        """Checks for a win or draw condition."""
        lines = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columns
            [0, 4, 8], [2, 4, 6]             # Diagonals
        ]
        for line in lines:
            if self.board[line[0]] == self.board[line[1]] == self.board[line[2]] != " ":
                return self.board[line[0]]
        if " " not in self.board:
            return "Draw"
        return None

    def render(self):
        """Prints the board to the console."""
        print("---+---+---")
        for i in range(0, 9, 3):
            print(f" {self.board[i]} | {self.board[i+1]} | {self.board[i+2]} ")
            print("---+---+---")
        print()

class QLearningAgent:
    def __init__(self, player_mark, learning_rate=0.1, discount_factor=0.9, exploration_rate=1.0, exploration_decay=0.999, min_exploration_rate=0.01):
        self.player_mark = player_mark
        self.q_table = collections.defaultdict(lambda: collections.defaultdict(float)) # Q[state][action] -> value
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = exploration_rate
        self.epsilon_decay = exploration_decay
        self.min_epsilon = min_exploration_rate

    def choose_action(self, state, available_actions):
        """Chooses an action based on epsilon-greedy strategy."""
        if not available_actions:
            return None # Should not happen if game logic is correct

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(available_actions) # Explore
        else:
            # Exploit: Choose the best known action
            state_q_values = self.q_table[state]
            # Filter Q-values for available actions only
            available_q_values = {action: state_q_values.get(action, 0.0) for action in available_actions}
            if not available_q_values: # If no Q-values known for this state's actions
                 return random.choice(available_actions)
            # Find the action(s) with the maximum Q-value among available actions
            max_q = max(available_q_values.values())
            best_actions = [action for action, q in available_q_values.items() if q == max_q]
            return random.choice(best_actions) # Break ties randomly

    def update_q_table(self, state, action, reward, next_state, next_available_actions):
        """Updates the Q-value for the state-action pair."""
        if not next_available_actions:
             max_next_q = 0 # Terminal state
        else:
             next_state_q_values = self.q_table[next_state]
             available_next_q = [next_state_q_values.get(act, 0.0) for act in next_available_actions]
             max_next_q = max(available_next_q) if available_next_q else 0

        current_q = self.q_table[state][action]
        new_q = current_q + self.lr * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q

    def decay_exploration(self):
        """Reduces the exploration rate."""
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def save_q_table(self, filename="q_table.pkl"):
        """Saves the Q-table to a file."""
        # Convert defaultdicts to regular dicts for pickling if needed, though pickle handles them
        with open(filename, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
        print(f"Q-table saved to {filename}")

    def load_q_table(self, filename="q_table.pkl"):
        """Loads the Q-table from a file."""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                loaded_dict = pickle.load(f)
                # Convert back to nested defaultdict
                self.q_table = collections.defaultdict(lambda: collections.defaultdict(float))
                for state, actions in loaded_dict.items():
                    self.q_table[state] = collections.defaultdict(float, actions)
            print(f"Q-table loaded from {filename}")
        else:
            print("No existing Q-table found, starting fresh.")

# --- Training and Visualization ---
def train(env, agent_x, agent_o, num_episodes):
    stats = {"X": 0, "O": 0, "Draw": 0}
    print_interval = num_episodes // 10

    for episode in range(num_episodes):
        state = env.reset()
        done = False
        current_agent = agent_x
        other_agent = agent_o
        last_move = {} # Store the last (state, action) for the opponent's update

        while not done:
            available_actions = env.get_available_actions()
            action = current_agent.choose_action(state, available_actions)

            if action is None: # Should not happen in TicTacToe if logic is right
                break

            next_state, reward, done = env.step(action, current_agent.player_mark)

            # Update the Q-table for the *current* agent
            next_available_actions = env.get_available_actions()
            current_agent.update_q_table(state, action, reward, next_state, next_available_actions)

            # Update the Q-table for the *previous* agent (opponent) based on the reward they received *implicitly*
            # Opponent's reward is the negative of the current player's reward (win=1 -> loss=-1)
            opponent_reward = -reward if reward != 0.5 else reward # Draws are neutral (0.5)
            if current_agent.player_mark in last_move:
                prev_state, prev_action = last_move[current_agent.player_mark]
                # The 'next_state' for the opponent *was* the current 'state' before the current agent moved
                # The 'next_available_actions' for the opponent *were* the current 'available_actions'
                other_agent.update_q_table(prev_state, prev_action, opponent_reward, state, available_actions)

            # Store state and action for the potential update on the next turn
            last_move[other_agent.player_mark] = (state, action)

            state = next_state

            if done:
                # Final update for the agent that made the last move leading to game end
                current_agent.update_q_table(state, action, reward, next_state, []) # No next actions
                # Final update for the opponent based on the last state
                opponent_reward = -reward if reward != 0.5 else reward
                if current_agent.player_mark in last_move:
                     prev_state, prev_action = last_move[current_agent.player_mark]
                     other_agent.update_q_table(prev_state, prev_action, opponent_reward, state, []) # No next actions

                winner = env.winner
                if winner in stats:
                    stats[winner] += 1
                break # Exit while loop
            else:
                # Switch agents
                current_agent, other_agent = other_agent, current_agent

        # Decay exploration rate after each episode
        agent_x.decay_exploration()
        agent_o.decay_exploration()

        if (episode + 1) % print_interval == 0:
            print(f"Episode {episode + 1}/{num_episodes} - Stats (X wins, O wins, Draws): {stats['X']}, {stats['O']}, {stats['Draw']} - Epsilon: {agent_x.epsilon:.4f}")
            # Reset stats for the next interval if desired, or keep cumulative
            # stats = {"X": 0, "O": 0, "Draw": 0}

    return stats

def play_game(env, agent_x, agent_o):
    """Plays one game between two agents with rendering and zero exploration."""
    state = env.reset()
    done = False
    current_agent = agent_x
    original_epsilon_x = agent_x.epsilon
    original_epsilon_o = agent_o.epsilon
    agent_x.epsilon = 0 # Force exploitation
    agent_o.epsilon = 0 # Force exploitation

    print("--- Starting Playback Game ---")
    env.render()

    while not done:
        available_actions = env.get_available_actions()
        action = current_agent.choose_action(state, available_actions)

        if action is None:
            print(f"Agent {current_agent.player_mark} cannot find a move (Should not happen).")
            break

        print(f"Agent {current_agent.player_mark} chooses action: {action}")
        state, reward, done = env.step(action, current_agent.player_mark)
        env.render()

        if done:
            print(f"--- Game Over! Winner: {env.winner} ---")
            break
        else:
            current_agent = agent_o if current_agent == agent_x else agent_x

    # Restore original exploration rates
    agent_x.epsilon = original_epsilon_x
    agent_o.epsilon = original_epsilon_o

if __name__ == "__main__":
    env = TicTacToeEnv()
    agent_x = QLearningAgent("X")
    agent_o = QLearningAgent("O", exploration_decay=0.999) # O can have slightly different params if needed

    # --- Parameters ---
    LOAD_TABLES = False # Set to True to load pre-trained tables
    SAVE_TABLES = True  # Set to True to save tables after training
    Q_TABLE_X_FILE = "q_table_x.pkl"
    Q_TABLE_O_FILE = "q_table_o.pkl"
    NUM_EPISODES = 10000
    PLAY_AFTER_TRAINING = False # Set to True to watch a game after training

    if LOAD_TABLES:
        agent_x.load_q_table(Q_TABLE_X_FILE)
        agent_o.load_q_table(Q_TABLE_O_FILE)
        # If loading, maybe skip training or train fewer episodes
        # NUM_EPISODES = 1000 # Example: Fewer episodes if loading

    if NUM_EPISODES > 0:
        print(f"Starting training for {NUM_EPISODES} episodes...")
        final_stats = train(env, agent_x, agent_o, NUM_EPISODES)
        print("Training finished.")
        print("Final Stats (X wins, O wins, Draws):", final_stats)
    else:
        print("Skipping training as NUM_EPISODES is 0.")

    if SAVE_TABLES:
        agent_x.save_q_table(Q_TABLE_X_FILE)
        agent_o.save_q_table(Q_TABLE_O_FILE)

    if PLAY_AFTER_TRAINING:
        play_game(env, agent_x, agent_o) 