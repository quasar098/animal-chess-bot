from board import *


class Bot:

    @staticmethod
    def find_best_move(game):
        def recurs(board: Board, depth=0):
            if depth > 6:
                return board
            moves = board.moves()
            index = 0
            thing = recurs(moves[index], depth+1)
            return [board] + (thing if isinstance(thing, list) else [thing])

        best_list = recurs(game.board.copy())[1]
        return best_list

    @staticmethod
    def make_best_move(game):
        if game.board.finished:
            return
        game.history.append(Bot.find_best_move(game))
        game.history_index += 1
        game.history = game.history[:game.history_index+1]
        if game.board.finished:
            play_sound(SoundId.GAME_OVER)
        else:
            play_sound(SoundId.MOVE)
