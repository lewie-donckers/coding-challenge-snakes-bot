from random import choice
from typing import List, Tuple

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

    def determine_next_move(self, snake: Snake, other_snakes: List[Snake],
                            candies: List[np.array]) -> Move:
        # suicide if that would win the game
        if len(snake) > (len(other_snakes[0]) * 2):
            return [
                move for move in MOVE_VALUE_TO_DIRECTION
                if ((snake[0] +
                     MOVE_VALUE_TO_DIRECTION[move]) == snake[1]).all()
            ][0]

        moves = self._determine_possible_moves(snake, other_snakes[0])

        # find closest candy
        candy = next(
            iter(
                sorted({
                    index: distance(snake[0], candies[index])
                    for index in range(len(candies))
                }.items(),
                       key=lambda x: x[1])))[0]

        # try to find move in direction of candy
        for move in moves:
            before = distance(snake[0], candies[candy])
            after = distance(snake[0] + MOVE_VALUE_TO_DIRECTION[move],
                             candies[candy])
            if before > after:
                return move

        return self.choose_move(moves)

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
