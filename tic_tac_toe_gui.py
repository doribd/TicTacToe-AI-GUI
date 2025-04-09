import wx
import pickle
import os
import time
import threading
import collections # Needed for defaultdict in loaded Q-table

# --- Try to import the QLearningAgent --- #
try:
    # This assumes tic_tac_toe_ai.py is in the same directory
    from tic_tac_toe_ai import QLearningAgent
except ImportError:
    print("ERROR: Could not import QLearningAgent.")
    print("Ensure 'tic_tac_toe_ai.py' is in the same directory.")
    # Fallback: Define a dummy class if import fails, so GUI can still load
    class QLearningAgent:
        def __init__(self, *args, **kwargs):
            print("WARNING: Using dummy QLearningAgent class.")
        def load_q_table(self, *args, **kwargs):
            print("WARNING: Cannot load Q-table (dummy agent).")
            self.q_table = None # Indicate failure
        def choose_action(self, *args, **kwargs):
            return None # Dummy agent cannot choose action

class TicTacToeFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Tic Tac Toe (WxPython) - AI Capable", size=(350, 400))
        self.panel = wx.Panel(self)
        self.current_player = "X"
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.game_over = False
        self.ai_playback_active = False
        self.ai_thread = None

        self._create_menu()
        self._create_widgets()
        self._create_sizers()

        self.load_ai_agents() # Load AI agents on startup
        self.Center()

    def _create_menu(self):
        menu_bar = wx.MenuBar()
        ai_menu = wx.Menu()
        watch_ai_item = ai_menu.Append(wx.ID_ANY, "Watch AI vs AI", "Watch trained agents play against each other")
        menu_bar.Append(ai_menu, "&AI")
        self.SetMenuBar(menu_bar)
        self.Bind(wx.EVT_MENU, self.on_watch_ai, watch_ai_item)

    def _create_widgets(self):
        # Status Label
        self.status_label = wx.StaticText(self.panel, label=f"Player {self.current_player}'s turn")
        font = self.status_label.GetFont()
        font.PointSize += 2
        self.status_label.SetFont(font)

        # Game Board Buttons
        for r in range(3):
            for c in range(3):
                button = wx.Button(self.panel, label="", size=(80, 80))
                button.SetFont(wx.Font(24, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                button.Bind(wx.EVT_BUTTON, lambda event, row=r, col=c: self.on_button_click(event, row, col))
                self.buttons[r][c] = button

        # Restart Button
        self.restart_button = wx.Button(self.panel, label="Restart")
        self.restart_button.Bind(wx.EVT_BUTTON, self.on_restart)

    def _create_sizers(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.status_label, 0, wx.ALL | wx.CENTER, 10)

        board_sizer = wx.GridSizer(3, 3, 5, 5)
        for r in range(3):
            for c in range(3):
                board_sizer.Add(self.buttons[r][c], 0, wx.EXPAND)
        main_sizer.Add(board_sizer, 1, wx.EXPAND | wx.ALL, 10)

        main_sizer.Add(self.restart_button, 0, wx.ALIGN_CENTER | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
        self.panel.SetSizer(main_sizer)

    def load_ai_agents(self):
        self.agent_x = QLearningAgent("X")
        self.agent_o = QLearningAgent("O")
        self.agent_x.load_q_table("q_table_x.pkl")
        self.agent_o.load_q_table("q_table_o.pkl")
        if self.agent_x.q_table is None or self.agent_o.q_table is None:
            print("WARNING: Failed to load one or both AI Q-tables. AI playback might not work.")
            # Optionally disable the AI menu item
            # self.GetMenuBar().FindItemById(self.watch_ai_item.GetId()).Enable(False)

    def on_button_click(self, event, row, col):
        # Prevent clicks during AI playback
        if self.ai_playback_active:
            return

        button = self.buttons[row][col]
        if self.game_over or button.GetLabel() != "":
            return

        self._apply_move(row, col, self.current_player)
        winner = self.check_winner()

        if winner:
            self._handle_game_over(winner)
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            self.update_status(f"Player {self.current_player}'s turn")

    def _apply_move(self, row, col, player):
        """Helper to apply a move to the board (used by human and AI)"""
        button = self.buttons[row][col]
        button.SetLabel(player)
        button.Disable()
        button.SetForegroundColour(wx.BLACK if player == "X" else wx.RED)

    def _handle_game_over(self, winner):
        self.game_over = True
        if winner == "Draw":
            self.update_status("It's a Draw!")
        else:
            self.update_status(f"Player {winner} wins!")
        # Re-enable restart button if it was disabled during AI playback
        self.restart_button.Enable()
        self.ai_playback_active = False # Ensure flag is reset
        self.panel.Layout() # Refresh layout

    def check_winner(self):
        # Check rows
        for r in range(3):
            if self.buttons[r][0].GetLabel() == self.buttons[r][1].GetLabel() == self.buttons[r][2].GetLabel() != "":
                return self.buttons[r][0].GetLabel()
        # Check columns
        for c in range(3):
            if self.buttons[0][c].GetLabel() == self.buttons[1][c].GetLabel() == self.buttons[2][c].GetLabel() != "":
                return self.buttons[0][c].GetLabel()
        # Check diagonals
        if self.buttons[0][0].GetLabel() == self.buttons[1][1].GetLabel() == self.buttons[2][2].GetLabel() != "":
            return self.buttons[0][0].GetLabel()
        if self.buttons[0][2].GetLabel() == self.buttons[1][1].GetLabel() == self.buttons[2][0].GetLabel() != "":
            return self.buttons[0][2].GetLabel()
        # Check for draw
        for r in range(3):
            for c in range(3):
                if self.buttons[r][c].GetLabel() == "":
                    return False # Game not over if empty cell exists
        return "Draw" # It's a draw if no winner and no empty cells

    def update_status(self, message):
        self.status_label.SetLabel(message)

    def on_restart(self, event=None): # Allow calling without event
        # Stop existing AI thread if running
        if self.ai_thread and self.ai_thread.is_alive():
             # We should ideally have a proper way to signal the thread to stop.
             # For now, just set the flag and let it finish its current loop.
             self.ai_playback_active = False
             print("Stopping previous AI playback attempt...")
             # Consider joining the thread with a timeout, but careful not to freeze GUI

        self.current_player = "X"
        self.game_over = False
        self.ai_playback_active = False
        self.update_status(f"Player {self.current_player}'s turn")

        for r in range(3):
            for c in range(3):
                button = self.buttons[r][c]
                button.SetLabel("")
                button.Enable()
                button.SetForegroundColour(wx.NullColour)
        self.restart_button.Enable()
        self.panel.Layout() # Refresh layout after enabling buttons

    def on_watch_ai(self, event):
        if self.agent_x.q_table is None or self.agent_o.q_table is None:
             wx.MessageBox("AI agents not loaded correctly. Cannot start AI playback.", "Error", wx.OK | wx.ICON_ERROR)
             return

        print("Starting AI vs AI playback...")
        self.on_restart() # Reset board first
        self.ai_playback_active = True
        self.update_status("AI (X) thinking...")
        self.restart_button.Disable() # Disable restart during playback

        # Start AI game in a separate thread
        self.ai_thread = threading.Thread(target=self.run_ai_game, daemon=True)
        self.ai_thread.start()

    def run_ai_game(self):
        """Runs the AI game logic in a background thread."""
        current_ai = self.agent_x
        other_ai = self.agent_o
        delay = 0.7 # Seconds between moves

        while not self.game_over and self.ai_playback_active:
            # --- Get current state from GUI --- #
            board_state_list = []
            available_actions_indices = []
            for r in range(3):
                for c in range(3):
                    label = self.buttons[r][c].GetLabel()
                    board_state_list.append(label if label else " ")
                    if not label:
                        available_actions_indices.append(r * 3 + c)

            current_state_tuple = tuple(board_state_list)

            # --- AI chooses action --- #
            if not available_actions_indices:
                 break # Should be caught by check_winner earlier

            action_index = current_ai.choose_action(current_state_tuple, available_actions_indices)

            if action_index is None:
                 print(f"ERROR: AI {current_ai.player_mark} failed to choose an action!")
                 # Use wx.CallAfter for safety if updating GUI from here
                 wx.CallAfter(self.update_status, f"AI {current_ai.player_mark} Error!")
                 self.ai_playback_active = False # Stop playback
                 break

            row, col = divmod(action_index, 3)

            # --- Update GUI safely using wx.CallAfter --- #
            wx.CallAfter(self._update_gui_for_ai_move, row, col, current_ai.player_mark)

            # --- Check for winner (check_winner reads from GUI, so needs CallAfter) --- #
            # It's safer to check winner *after* the GUI update has been processed.
            # We can use wx.CallLater for this, or simplify by checking after the sleep.

            time.sleep(delay) # Pause for visualization
            if not self.ai_playback_active: break # Check if stopped during sleep

            # --- Check winner *after* likely GUI update and sleep --- #
            winner = self.check_winner() # This reads the GUI state directly
            if winner:
                 # Use CallAfter to update status and handle game over state
                 wx.CallAfter(self._handle_game_over, winner)
                 break # Exit AI loop
            else:
                 # --- Switch player and update status (via CallAfter) --- #
                 current_ai, other_ai = other_ai, current_ai
                 wx.CallAfter(self.update_status, f"AI ({current_ai.player_mark}) thinking...")

        # Final cleanup if loop terminated unexpectedly
        if not self.game_over:
            wx.CallAfter(self.update_status, "AI Playback Stopped")
            wx.CallAfter(self.restart_button.Enable)
            self.ai_playback_active = False
        print("AI game thread finished.")

    def _update_gui_for_ai_move(self, row, col, player):
        """GUI update logic to be called by wx.CallAfter."""
        if not self.ai_playback_active: return # Don't update if playback was stopped
        print(f"AI ({player}) playing at ({row}, {col})")
        self._apply_move(row, col, player)
        # Note: Winner check and player switch happen in the AI thread *after* this update

if __name__ == "__main__":
    app = wx.App(False)
    frame = TicTacToeFrame()
    frame.Show()
    app.MainLoop()