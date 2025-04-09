# Tic Tac Toe AI & GUI 🎮🤖

Welcome to the Tic Tac Toe AI & GUI project! This project consists of two main components: an AI agent that learns to play Tic Tac Toe using Q-learning, and a graphical user interface (GUI) built with wxPython to interact with the game.

## Features ✨

- **AI Agent**: Uses Q-learning to learn optimal strategies for playing Tic Tac Toe.
- **GUI**: A user-friendly interface to play against the AI or watch AI vs AI matches.
- **Training**: Train the AI agents to improve their gameplay over multiple episodes.

## How to Use 🛠️

### Prerequisites

Ensure you have Python installed on your system. You can download it from [python.org](https://www.python.org/).

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the AI Training 🏋️‍♂️

To train the AI agents, run the following command:

```bash
python tic_tac_toe_ai.py
```

This will train two AI agents (X and O) over a specified number of episodes.

### Running the GUI 🖥️

To start the GUI and play Tic Tac Toe, run:

```bash
python tic_tac_toe_gui.py
```

- **Play against AI**: Click on the board to make your move. The AI will respond automatically.
- **Watch AI vs AI**: Use the menu option to watch trained agents play against each other.

## Dependencies 📦

- `wxPython`: For creating the GUI.
- `pickle`: For saving and loading the Q-table.
- `collections`: For managing the Q-table with defaultdict.

## Contributing 🤝

Feel free to fork this repository and submit pull requests. We welcome contributions that improve the AI, GUI, or overall functionality.

## License 📄

This project is licensed under the MIT License.

## Built with Cursor 🖥️✨

This project was developed using [Cursor](https://www.cursor.so/) (Licensed). 🚀

## AI Technology Used 🤖🧠

This project employs a Q-learning algorithm, a type of reinforcement learning, to develop the AI agent for playing Tic Tac Toe. The Q-learning algorithm enables the agent to learn optimal strategies by interacting with the environment and receiving feedback in the form of rewards.

### Why Q-learning?
- **Exploration and Exploitation**: Q-learning balances exploration of new strategies and exploitation of known strategies to maximize rewards.
- **Model-Free**: It does not require a model of the environment, making it versatile and easy to implement.

### Libraries Used
- **Collections**: Utilized for managing the Q-table with `defaultdict`, which stores the state-action values.
- **Pickle**: Used for saving and loading the Q-table, allowing the AI to retain learned strategies across sessions.

### Why Call it AI?
The term "AI" is used because the agent autonomously learns and improves its gameplay through experience, mimicking intelligent behavior. It makes decisions based on learned data, adapting to different game scenarios without explicit programming for each possible move.

Enjoy playing Tic Tac Toe with AI! 🎉 
