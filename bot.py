from random import choice
from typing import List, Tuple

import numpy as np

from ...bot import Bot
from ...constants import Move, MOVE_VALUE_TO_DIRECTION
from ...snake import Snake


def is_on_grid(pos: np.array, grid_size: Tuple[int, int]) -> bool:
    return 0 <= pos[0] < grid_size[0] and 0 <= pos[1] < grid_size[1]


def collides(pos: np.array, snakes: List[Snake]) -> bool:
    for snake in snakes:
        if snake.collides(pos):
            return True
    return False


def get_distance(source: np.array, target: np.array) -> int:
    return abs(source[0] - target[0]) + abs(source[1] - target[1])


def get_minimum_distance(source, targets):
    return min([get_distance(source, target) for target in targets])


class Node:

    def __init__(self, position, *, parent=None):
        self.position = position
        self.parent = parent
        self.cost_so_far = 0
        self.estimated_total = 0

    def __eq__(self, other):
        return (self.position == other.position).all()


class LewieBot(Bot):

    @property
    def name(self):
        return 'Serpent of the Light'

    @property
    def contributor(self):
        return 'Lewie'

    def _is_valid_position(self, position, snake, other_snake):
        return is_on_grid(position, self.grid_size) and not collides(
            position, [snake, other_snake])

    def _get_valid_moves(self, position, snake, other_snake):
        return [
            move for move in MOVE_VALUE_TO_DIRECTION
            if self._is_valid_position(
                position + MOVE_VALUE_TO_DIRECTION[move], snake, other_snake)
        ]

    def _get_neighbors(self, current_node, snake, other_snake):
        return [
            Node(current_node.position + MOVE_VALUE_TO_DIRECTION[move],
                 parent=current_node) for move in self._get_valid_moves(
                     current_node.position, snake, other_snake)
        ]

    def _get_move_to_candy(self, snake, other_snake, candies):
        # IDEAS to improve
        # - remove candies that are inside snake
        # - use heuristic to determine if candy is inside snake based on
        #   position of candy in snake and number of turns taken
        # - select better structures for work and done

        work = self._get_neighbors(Node(snake[0]), snake, other_snake)
        done = []

        while work:

            current_index = 0
            current_node = work[current_index]
            for index, item in enumerate(work):
                if item.estimated_total < current_node.estimated_total:
                    current_index = index
                    current_node = item

            work.pop(current_index)
            done.append(current_node)

            if any([(current_node.position == candy).all()
                    for candy in candies]):
                first_pos = None
                while current_node:
                    if current_node.parent:
                        first_pos = current_node.position
                    current_node = current_node.parent
                for move in MOVE_VALUE_TO_DIRECTION:
                    if ((first_pos -
                         snake[0]) == MOVE_VALUE_TO_DIRECTION[move]).all():
                        return move
                # TODO handle this
                raise Exception("TODO should not happen")

            for neighbor in self._get_neighbors(current_node, snake,
                                                other_snake):
                if neighbor in done:
                    continue

                neighbor.cost_so_far = current_node.cost_so_far + 1
                neighbor.estimated_total = neighbor.cost_so_far + get_minimum_distance(
                    neighbor.position, candies)

                try:
                    index = work.index(neighbor)
                    node = work[index]
                    if neighbor.cost_so_far < node.cost_so_far:
                        node = neighbor  # TODO does this work?
                except ValueError:
                    work.append(neighbor)

    def _will_suicide_win(self, snake, other_snake):
        return len(snake) > (len(other_snake) * 2)

    def _get_suicide_move(self, snake):
        return [
            move for move in MOVE_VALUE_TO_DIRECTION
            if ((snake[0] + MOVE_VALUE_TO_DIRECTION[move]) == snake[1]).all()
        ][0]

    def _get_backup_move(self, snake, other_snake):
        return next(iter(self._get_valid_moves(snake[0], snake, other_snake)),
                    Move.UP)

    def determine_next_move(self, snake: Snake, other_snakes: List[Snake],
                            candies: List[np.array]) -> Move:
        other_snake = other_snakes[0]

        if self._will_suicide_win(snake, other_snake):
            return self._get_suicide_move(snake)

        return self._get_move_to_candy(snake, other_snake,
                                       candies) or self._get_backup_move(
                                           snake, other_snake)
