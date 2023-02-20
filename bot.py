from board import *


class Bot:

    @staticmethod
    def find_best_move(game: "Game"):
        original = game.board.copy()

        my_possible_moves = original.moves()

        best_move = None
        best_move_score = 0

        # for each possible move available
        for board in my_possible_moves:
            opponent_moves = board.moves()
            # find the best move that the opponent can make from that position (2nd level)
            if len(opponent_moves) == 0:
                return my_possible_moves[0]
            best_move_for_opponent = opponent_moves[0]
            best_move_for_opponent_score = best_move_for_opponent.get_who_is_winning()

            if original.whose_turn != Team.RED:
                best_move_for_opponent_score = 100-best_move_for_opponent_score

            # if the best move for the opponent (2nd level) was worse off for them, then declare a new best
            if best_move is None:
                best_move = board
                best_move_score = best_move_for_opponent_score
            if best_move_score < best_move_for_opponent_score:
                best_move = board
                best_move_score = best_move_for_opponent_score

        return best_move

    @staticmethod
    def make_best_move(game: "Game"):
        if game.board.finished:
            return
        game.history.append(Bot.find_best_move(game))
        game.history_index += 1
        game.history = game.history[:game.history_index+1]
        if game.board.finished:
            play_sound(SoundId.GAME_OVER)
        else:
            play_sound(SoundId.MOVE)
