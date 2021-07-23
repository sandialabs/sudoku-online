#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shelley Leger
Sandia National Laboratories
July 2, 2020

Lightweight sudoku server for sudoku online.
"""

import translate
import board

from flask import Flask, request, jsonify
from flask_cors import CORS
from markupsafe import escape

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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

    result = translate.get_initial_board(content).getSimpleJson()
    logger.info("Returning from get_initial_board: %s", str(result))
    return jsonify(result)


@app.route('/sudoku/request/boardsForGame/<gamename>')
def get_boards_for_game(gamename):
    """ Return a list of boards associated with a game.

    Defaults are set to select a random puzzle from puzzles.puzzles and to simplify with inclusion/exclusion.
    """
    name = escape(gamename)
    # MAL TODO is there a way to let the app.route say if you ask for something without a gamename then we can make it None?
    if name == 'get_me_something_random':
        name = None
    boards = translate.get_boards_for_game(name)
    json_boards = [b.getSimpleJson() for b in boards]
    logger.info("Returning boards for game %s: %s", str(gamename), str(json_boards))
    return jsonify(json_boards)


@app.route('/sudoku/request/evaluate_cell_action', methods=['POST'])
def take_given_action():
    """ Returns the sets of boards created by taking a particular action.

    Possible actions can be obtained by calling list_cell_actions
    (and list_logical_operators to get logical operators to apply).
    """
    content = request.json
    if content is None:
        logger.warn("Cannot apply action without context content (board, action, and parameters)")
        return jsonify(None)

    result = translate.parse_and_apply_action(content)
    logger.info("Returning result for evaluate_cell_action: %s", str(result))
    return jsonify(result)


@app.route('/sudoku/request/list_logical_operators', methods=['GET'])
def list_possible_operators():
    """ Returns the possible logical operators that could be applied.

    Possible operators are described in board_update_descriptions.py.
    """
    result = translate.get_possible_operators()
    logger.info("Listing possible operators: %s", str(result))
    return jsonify(result)


@app.route('/sudoku/request/list_cell_actions', methods=['GET'])
def list_possible_actions():
    """ Returns the possible actions that could be applied.

    Possible actions are described in board_update_descriptions.py.
    """
    result = translate.get_cell_actions()
    logger.info("Listing possible actions: %s", str(result))
    return jsonify(result)


@app.route('/sudoku/request/submit_game_tree', methods=['POST'])
def submit_game_tree():
    """Receive a completed game tree from the client.

    This is a placeholder method.  We may wind up doing this entirely
    on the client side, sending it from there to S3.
    """
    content = request.json
    if content is None:
        logger.warn("Cannot save game tree without a tree to save.")
        return jsonify(None)

    result = translate.submit_game_tree(content)
    logger.info("Returning from submit_game_tree: %s", str(result))
    return jsonify(result)


if __name__ == '__main__':
    app.run(host='http://localhost:5000', debug=True)
