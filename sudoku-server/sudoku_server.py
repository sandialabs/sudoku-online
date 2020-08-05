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
from flask_cors import CORS
from markupsafe import escape

app = Flask(__name__)
CORS(app)

@app.route('/sudoku/request/initialBoard', methods=['GET', 'POST'])
def get_initial_board():
    """ Return an inital board.

    Defaults are set to select a random puzzle from puzzles.puzzles.
    """
    content = request.json
    if content is None:
        content = dict()

    return jsonify(game.get_initial_board(content))

    # TODO MAL add goalCell
    # TODO MAL add accessibleCells


@app.route('/sudoku/request/boardsForGame/<gamename>')
def get_boards_for_game(gamename):
    """ Return a list of boards associated with a game.

    Defaults are set to select a random puzzle from puzzles.puzzles and to simplify with inclusion/exclusion.
    """
    name = escape(gamename)
    # MAL TODO is there a way to let the app.route say if you ask for something without a gamename then we can make it None?
    if name is 'get_me_something_random':
        name = None
    board_names = game.get_boards_for_game(name)
    return jsonify(board_names)


# MAL TODO talk to Andy about changing this to a different name
@app.route('/sudoku/request/evaluate_cell_action', methods=['POST'])
def take_given_action():
    """ Returns the sets of boards created by taking a particular action.

    Possible actions can be obtained by calling list_heuristics.
    """
    content = request.json
    if content is None:
        print("Cannot apply action without context content (board, action, and parameters)")
        return jsonify(None)

    return jsonify(game.parse_and_apply_action(content))


@app.route('/sudoku/request/list_logical_operators', methods=['GET'])
def list_possible_operators():
    """ Returns the possible logical operators that could be applied.

    Possible actions include selectValueForCell (cell_id, value) and pivotOnCell (cell_id)
    """
    return jsonify(game.get_possible_operators())


@app.route('/sudoku/request/list_cell_actions', methods=['GET'])
def list_possible_actions():
    """ Returns the possible actions that could be applied.

    Possible actions include selectValueForCell (cell_id, value), pivotOnCell (cell_id),
    and applyLogicalOperators (list of logical operators to apply)
    """
    return jsonify(game.get_cell_actions())

@app.route('/sudoku/request/submit_game_tree', methods=['POST'])
def submit_game_tree():
    """Receive a completed game tree from the client.

    This is a placeholder method.  We may wind up doing this entirely
    on the client side, sending it from there to S3.
    """

    content = request.json
    if content is None:
        print("Cannot save game tree without a tree to save")
        return jsonify(None)

    return jsonify(game.submit_game_tree(content))


if __name__ == '__main__':
    app.run(host='http://localhost:5000', debug=True)
