from logic import (
    ComputerPlayer,
    Game,
    GameHandler,
    HumanPlayer,
    SelectionSet,
)


s = SelectionSet(selections=["rock", "paper", "scissors"], relations=[[0, -1, 1], [1, 0, -1], [-1, 1, 0]])
g = Game(name="Rock Paper Scissors", selection_set=s)
human = HumanPlayer("afozk95")
computer = ComputerPlayer("random")
handler = GameHandler(game=g, player1=human, player2=computer)
handler.play()
