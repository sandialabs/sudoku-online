#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shelley Leger
Sandia National Laboratories
July 2, 2020

Lightweight sudoku server for sudoku online.
"""

import game
import board

from flask import Flask, request, jsonify
app = Flask(__name__)


#@app.route('/sudoku/request/initialize', methods=['GET'])
#def do_initialize_board_class():
#    board.Board.initialize()
#    print(board.Board.unit_map)
#    return jsonify("Welcome")


@app.route('/sudoku/request/initialBoard', methods=['GET', 'POST'])
def get_initial_board():
    """ Return an inital board.

    Defaults are set to select a random puzzle from puzzles.puzzles and to simplify with inclusion/exclusion.
    """
    content = request.json
    if content is None:
        content = dict()

    return jsonify(game.get_initial_board(content))

    # TODO MAL add goalCell
    # TODO MAL add accessibleCells
    # TODO MAL add parent

# MAL TODO talk to Andy about changing this to a different name
@app.route('/sudoku/request/heuristic', methods=['POST'])
def take_given_action():
    """ Returns the sets of boards created by taking a particular action.

    Possible actions include selectValueForCell (cell_id, value), pivotOnCell (cell_id),
    and applyLogicalOperators (list of logical operators to apply)
    """
    content = request.json
    if content is None:
        print("Cannot apply action without context content (board, action, and parameters)")
        return jsonify(None)

    return jsonify(game.parse_and_apply_action(content))


if __name__ == '__main__':
    app.run(host='http://localhost:5000', debug=True)
