from typing import Any, Dict, List, Optional, Tuple
from abc import ABC
from enum import Enum
import random


class Result(Enum):
    WIN = 1
    TIE = 0
    LOSE = -1

    def __str__(self) -> str:
        return self.name.lower()


class SelectionSet:
    def __init__(self, selections: List[str], relations: List[List[int]]) -> None:
        self.selections: List[str] = selections
        self.relations: List[List[int]] = relations
    
    def get_result(self, selection1: str, selection2: str) -> Tuple[Result, Result]:
        assert selection1 in self.selections, f"{selection1} is not a valid selection"
        assert selection2 in self.selections, f"{selection2} is not a valid selection"

        index1 = self.selections.index(selection1)
        index2 = self.selections.index(selection2)
        return Result(self.relations[index1][index2]), Result(self.relations[index2][index1])


class Game:
    def __init__(self, name: str, selection_set: SelectionSet) -> None:
        self.name = name
        self.selection_set: SelectionSet = selection_set


class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.history: List[Dict[str, Any]] = []

    def play(self, game: Game) -> str:
        pass

    def observe(self, player_move: str, opponent_move: str, player_result: Result, opponent_result: Result) -> None:
        self.history.append(
            {
                "player_move": player_move,
                "opponent_move": opponent_move,
                "player_result": player_result,
                "opponent_result": opponent_result,
            }
        )
    
    def __str__(self) -> str:
        return self.name


class HumanPlayer(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    def ask_move(self, game: Game) -> str:
        selections = game.selection_set.selections
        selections_str = ", ".join(selections)
        question_str = f"Your move? [{selections_str}]:\n"
        while True:
            answer = input(question_str)
            parsed_move = self.parse_move(answer, selections)
            if parsed_move is not None:
                return parsed_move

    def parse_move(self, answer: str, selections: List[str]) -> Optional[str]:
        return answer if answer in selections else None

    def play(self, game: Game) -> str:
        return self.ask_move(game)
    
    def __str__(self) -> str:
        return f"(human){super().__str__()}"


class ComputerPlayer(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
    
    def play(self, game: Game) -> str:
        return self.play_uniformly_random(game)
    
    def play_uniformly_random(self, game: Game) -> str:
        selections = game.selection_set.selections
        return random.choice(selections)
    
    def play_weighted_random(self, game: Game) -> str:
        selections = game.selection_set.selections
        relations = game.selection_set.relations

        selections_weights = []
        for s_relation in relations:
            lose_count = s_relation.count(-1)
            win_count = s_relation.count(1)
            total_count = win_count + lose_count
            weight = 0 if total_count == 0 else win_count / total_count
            selections_weights.append(weight)

        return random.choices(selections, selections_weights, k=1)[0]
    
    def __str__(self) -> str:
        return f"(computer){super().__str__()}"


class GameHandler:
    def __init__(self, game: Game, player1: Player, player2: Player) -> None:
        self.game: Game = game
        self.player1: Player = player1
        self.player2: Player = player2
        self.history: List[Dict[str, Any]] = []

    def add_turn_to_history(self, player1_move: str, player2_move: str, player1_result: Result, player2_result: Result) -> None:
        self.history.append(
            {
                "player1_move": player1_move,
                "player2_move": player2_move,
                "player1_result": player1_result,
                "player2_result": player2_result,
            }
        )

    def get_current_result(self) -> Dict[str, Dict[Result, int]]:
        tmp_dct = {result: 0 for result in Result}
        result_counts_by_player = {
            "player1": tmp_dct.copy(),
            "player2": tmp_dct.copy(),
        }
        for turn_result in self.history:
            result_counts_by_player["player1"][turn_result["player1_result"]] += 1
            result_counts_by_player["player2"][turn_result["player2_result"]] += 1
        
        return result_counts_by_player

    def get_current_result_str(self) -> str:
        result_counts_by_player = self.get_current_result()
        p1_w, p1_t, p1_l = (result_counts_by_player["player1"][result] for result in [Result.WIN, Result.TIE, Result.LOSE])
        p2_w, p2_t, p2_l = (result_counts_by_player["player2"][result] for result in [Result.WIN, Result.TIE, Result.LOSE])
        result_str = f"{self.player1} ({p1_w}W, {p1_t}T, {p1_l}L) vs {self.player2} ({p2_w}W, {p2_t}T, {p2_l}L)"
        return result_str

    def play_turn(self) -> None:
        player1_move = self.player1.play(self.game)
        player2_move = self.player2.play(self.game)
        player1_result, player2_result = self.game.selection_set.get_result(player1_move, player2_move)
        self.player1.observe(player1_move, player2_move, player1_result, player2_result)
        self.player2.observe(player2_move, player1_move, player2_result, player1_result)
        print(self.get_result_str(player1_move, player2_move, player1_result, player2_result))
        self.add_turn_to_history(player1_move, player2_move, player1_result, player2_result)
        print(self.get_current_result_str())

    def play(self, max_num_of_turns: Optional[int] = None) -> None:
        i_turn = 0
        while True:
            self.play_turn()
            i_turn += 1
            if i_turn == max_num_of_turns:
                break

    def get_result_str(self, player1_move: str, player2_move: str, player1_result: Result, player2_result: Result) -> str:
        result_str = f"{self.player1} chooses {player1_move} and {self.player2} chooses {player2_move}\n"
        result_str += f"{self.player1} {player1_result}s and {self.player2} {player2_result}s\n"
        return result_str
