from random import choice
from typing import List, Tuple
import copy

import numpy as np

from ...bot import Bot
from ...constants import Move, MOVE_VALUE_TO_DIRECTION
from ...snake import Snake


def is_on_grid(pos: np.array, grid_size: Tuple[int, int]) -> bool:
    """
    Check if a position is still on the grid
    """
    return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]


def collides(pos: np.array, snakes: List[Snake]) -> bool:
    """
    Check if a position is occupied by any of the snakes
    """
    for snake in snakes:
        if snake.collides(pos):
            return True
    return False


def distance(a: np.array, b: np.array) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class LewieBot(Bot):
    """
    Moves randomly, but makes sure it doesn't collide with other snakes
    """

    @property
    def name(self):
        return 'Serpent of the Light'

    @property
    def contributor(self):
        return 'Lewie'

    # TODO sometimes we go waaay to deep
    # - can limit max depth
    # - currently we do depth first. based on most promising path so far. probably better to do depth first.
    def _do_stuff2(self, snake, other_snake, candies, pos, history, path,
                   results):
        print(f"{len(history)} : {history}")
        options = {}
        for move in MOVE_VALUE_TO_DIRECTION:
            new_pos = pos + MOVE_VALUE_TO_DIRECTION[move]
            first_move = (history + [move])[0]
            score = len(history) + 1

            if not is_on_grid(new_pos, self.grid_size):
                print("ignore based on grid")
                continue

            if collides(new_pos, [snake, other_snake]):
                print("ignore based on collision")
                continue

            if any([(new_pos == p).all() for p in path]):
                print("ignore based on history")
                continue

            on_candy = False
            for candy in candies:
                if (new_pos == candy).all():
                    on_candy = True
                    if score < results[first_move][0]:
                        results[first_move] = [score, 1]
                    elif score == results[first_move][0]:
                        results[first_move][1] += 1
                    break
            if on_candy:
                continue

            min_score_to_closest_candy = sorted(
                [score + distance(new_pos, candy) for candy in candies])[0]

            if min_score_to_closest_candy >= results[first_move][0]:
                continue

            options[move] = min_score_to_closest_candy

        for move, _ in sorted(options.items(), key=lambda x: x[1]):
            new_snake = copy.deepcopy(snake)
            new_snake.move(MOVE_VALUE_TO_DIRECTION[move])
            new_pos = pos + MOVE_VALUE_TO_DIRECTION[move]
            self._do_stuff2(new_snake, other_snake, candies, new_pos,
                            history + [move], path + [new_pos], results)

    def _do_stuff(self, snake, other_snake, candies):
        print("------------------------")
        results = {
            m: [self.grid_size[0] * self.grid_size[1], 0]
            for m in MOVE_VALUE_TO_DIRECTION
        }

        self._do_stuff2(snake, other_snake, candies, snake[0], [], [], results)

        return results

    def determine_next_move(self, snake: Snake, other_snakes: List[Snake],
                            candies: List[np.array]) -> Move:
        # suicide if that would win the game
        if len(snake) > (len(other_snakes[0]) * 2):
            return [
                move for move in MOVE_VALUE_TO_DIRECTION
                if ((snake[0] +
                     MOVE_VALUE_TO_DIRECTION[move]) == snake[1]).all()
            ][0]

        result = self._do_stuff(snake, other_snakes[0], candies)

        return sorted(result.items(),
                      key=lambda x: x[1][0] * 10 - x[1][1])[0][0]

    def _determine_possible_moves(self, snake, other_snake) -> List[Move]:
        """
        Return a list with all moves that we want to do. Later we'll choose one from this list randomly. This method
        will be used during unit-testing
        """
        # highest priority, a move that is on the grid
        on_grid = [
            move for move in MOVE_VALUE_TO_DIRECTION
            if is_on_grid(snake[0] +
                          MOVE_VALUE_TO_DIRECTION[move], self.grid_size)
        ]
        if not on_grid:
            return list(Move)

        # then avoid collisions with other snakes
        collision_free = [
            move for move in on_grid if not collides(
                snake[0] + MOVE_VALUE_TO_DIRECTION[move], [snake, other_snake])
        ]

        # then avoid a dead end
        no_dead_ends = [
            move for move in collision_free if any([
                is_on_grid(
                    snake[0] + MOVE_VALUE_TO_DIRECTION[move] +
                    MOVE_VALUE_TO_DIRECTION[move2], self.grid_size)
                and not collides(
                    snake[0] + MOVE_VALUE_TO_DIRECTION[move] +
                    MOVE_VALUE_TO_DIRECTION[move2], [snake, other_snake])
                for move2 in MOVE_VALUE_TO_DIRECTION
            ])
        ]

        if no_dead_ends:
            return no_dead_ends
        if collision_free:
            return collision_free
        else:
            return on_grid

    def choose_move(self, moves: List[Move]) -> Move:
        """
        Randomly pick a move
        """
        return choice(moves)
