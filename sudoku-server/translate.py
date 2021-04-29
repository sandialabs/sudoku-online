#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Wilson, Shelley Leger
Sandia National Laboratories
Spring, 2020

Test code for Sudoku games.
Requires python3.
"""

# Imports from our own code
import board
import board_update_descriptions
import config_data
import operators
import puzzles
import solvers

# Imports from Python standard library
import enum
import json
import random
import sys

import logging
logger = logging.getLogger(__name__)


def get_initial_board(content):
    """
    Get an initial board of 'degree' given a dict request, randomly if 'name' is None, else by name.
    """
    logger.debug("Calling get_initial_board with content %s.", str(content))
    puzzle = None
    assert isinstance(content, dict), \
        "Failed assumption that request for initial board is formatted as a dict"
    name = content["name"] if "name" in content else None
    logger.debug(f"Name is {name}")
    degree = content["degree"] if "degree" in content else 3

    basename = None
    if name:
        parameters = config_data.parse_name_config(name)
        assert "displayName" in parameters, f"Cannot find puzzle displayName in parameters ({str(parameters)})."
        basename = parameters["displayName"]
        if basename and basename in puzzles.puzzles:
            logger.info("Loading requested puzzle " + str(basename))
            puzzle = puzzles.puzzles[basename]
        else:
            # Just warn, and return an empty result
            logger.warn("Puzzle %s does not seem to exist.", str(basename))
            return {"error": f"You must specify an existing puzzle (one of {puzzles.puzzles.keys()})."}
    else:
        (basename, puzzle) = random.choice(list(puzzles.puzzles.items()))
        name = basename
        logger.info("select puzzle %s", name)
    full_board = board.Board(puzzle, degree, name)
    logger.info("load puzzle %s %s", name, full_board.getStateStr(True, False))
    logger.info("Configured requested puzzle " + str(name))
    logger.debug(full_board.getSimpleJson())
    parameters = config_data.parse_name_config(name)
    if "select_ops_upfront" in parameters:
        # For the initial board only, the only possible action is selectOps
        #   and the canChangeLogicalOperators is True
        #   so let's just overwrite them here.
        full_board.config.actions = ["selectops"]
        full_board.config.rules["canChangeLogicalOperators"] = True
    if full_board.config.simplify_initial_board:
        solvers.apply_free_operators(full_board)
    logger.info("Simplified requested puzzle " + str(basename))
    return full_board


def __configure_games(name_list, alternatives_list):
    """
    Given a list of games, do whatever configuration needs to be done to configure them.
    """

    if not alternatives_list:
        return name_list

    alt = alternatives_list.pop()
    # MAL TODO randomly reorder the name_list

    for i in range(int(len(name_list)/2)):
        name_list[i] += f"...{alt}"

    return __configure_games(name_list, alternatives_list)


def get_boards_for_game(name):
    """
    Return a list of initial Boards associated with a game, randomly if 'name' is None, else by name.

    Associates appropriate configuration with each puzzle as indicated by the request.
    """
    game = {}
    if name and name in puzzles.games:
        logger.info("Loading requested game " + str(name))
        game = puzzles.games[name]
    else:
        (name, game) = random.choice(list(puzzles.games.items()))
        logger.info("select game %s", name)

    game_names = game["puzzles"]
    if "config_alterations" not in game:
        logger.warn("Should at least provide empty list for 'config_alterations' in game description.")
        game["config_alterations"] = []
    if "randomly_apply" in game["config_alterations"]:
        game_names = __configure_games(
            list.copy(game["puzzles"]), list.copy(game["config_alterations"]["randomly_apply"]))
    if "default_config" in game["config_alterations"]:
        default_config = game["config_alterations"]["default_config"]
        if "costly_ops" in default_config:
            config_data.defaultConfig.costly_operations = default_config["costly_ops"]
    logger.info("load game name: %s", str(game_names))

    game_boards = []
    for name in game_names:
        game_boards.append(get_initial_board({"name" : name}))
    return game_boards


def __parse_cell_arg(cell_loc):
    """ Parse a cell location into a cell_id. """
    assert isinstance(cell_loc, list) and 2 == len(cell_loc), \
        "Must specify cell using [x,y] location notation."
    cell_id = board.Board.getCellIDFromArrayIndex(cell_loc[0], cell_loc[1])
    logger.debug(f"Found cell argument {cell_id}")
    return cell_id


def __parse_value_arg(value):
    """ Parse a value. """
    assert isinstance(value, int) and value >= 0, \
        "Assuming that all values are represented as non-negative ints. (offending value: {})".format(value)
    logger.debug(f"Found value argument {value}")
    return value


def __parse_operators_arg(ops_list):
    """ Parse a list of operators. """
    assert isinstance(ops_list, list), \
        "Must specify list of operators in applyLogicalOperators action"
    logger.debug(f"Found operators argument {ops_list}")
    return ops_list


def __collect_argument(arg_nm, action_dict):
    """ Collect the argument specified. """
    try:
        # Yes, it's insecure, but at least we're getting the thing we eval from ourselves
        parser_function = eval(f"__parse_{arg_nm}_arg")
        raw_val = action_dict[arg_nm]
        return parser_function(raw_val)
    except AttributeError:
        raise Exception(
            f"Can't extract argument {arg_nm} needed")
    except KeyError:
        raise Exception(
            f"Can't find value for argument {arg_nm} needed")


def __collect_args(action, action_dict):
    """
    Given a request action and a dictionary of the content request,
    return a list of the parsed arguments needed for that action.
    """
    assert action in board_update_descriptions.actions_description, \
        f"Cannot exercise action {action}"
    try:
        arg_names = board_update_descriptions.actions_description[action]["arguments"]
    except KeyError:
        raise Exception(f"Cannot find description for action {action}")

    if len(arg_names) == 1:
        return __collect_argument(arg_names[0], action_dict)
    elif len(arg_names) == 2:
        return (__collect_argument(arg_names[0], action_dict),
                __collect_argument(arg_names[1], action_dict))
    else:
        raise Exception(
            f"Haven't implemented parsing for arguments {arg_names}")


def parse_and_apply_action(content):
    """
    Given a requested action and board, parse and apply the given action to board.

    Possible actions include selectValueForCell (cell, value), pivotOnCell (cell), and
    applyLogicalOperators ([list of operators])
        board (Board)  : the Board on which the action should be performed.
        action  : the action to take, and appropriate operators as specified in server_api.md
    Returns:
        [Boards] : a collection of boards resulting from the selection action.
    """
    assert isinstance(content, dict), \
        "Failed assumption that request for action on board is formatted as a dict"
    if "board" not in content:
        return {"error": "You must specify a board to act upon."}
    board_dict = content["board"]
    assert isinstance(
        board_dict, dict), "Failed assumption that the parsed board is a dict."
    board_object = board.Board(board_dict)

    if "action" not in content:
        return {"error": "You must specify an action to take on the given board."}
    action_dict = content["action"]
    assert isinstance(action_dict, dict), \
        "Failed assumption that the parsed action is a dict."
    assert "action" in action_dict, "Failed assumption that action request specified the action to take."
    action_choice = action_dict["action"]

    logger.info("Action choice: {}".format(action_choice))

    try:
        args = __collect_args(action_choice, action_dict)
        collected = solvers.take_action(
            board.Board(board_object), action_choice, args)
        result = []
        if "heuristics" in content:
            logicalops = content["heuristics"]
            assert isinstance(logicalops, list), \
                "Failed assumption that the parsed action argument heuristics is a list."
            for brd in collected:
                result.extend(solvers.take_action(brd, "applyops", logicalops))
        else:
            result = collected

    except Exception as e:
        return {"error": f"{e}"}

    jsoned_result = []
    game_score = True
    average_score = 0
    for full_board in result:
        jsoned_result.append(full_board.getSimpleJson())
        if game_score and full_board.config.cost_per_game_not_per_board:
            if average_score == 0:
                average_score = full_board.config.log.difficulty_score
            else:
                assert average_score == full_board.config.log.difficulty_score, \
                    "Can't average score when assuming that the scores are the same across child boards"
        else:
            game_score = False
    if game_score and (len(jsoned_result) > 0):
        # Amortize the game score across all the boards,
        #   as each currently has the same score as a single board would
        #   and we want to amortize that cost across all children boards
        average_score /= len(jsoned_result)
        for full_board in jsoned_result:
            full_board["cost"] = average_score

    return jsoned_result


def _jsonify_action(name, description_dict):
    """ Remove all the extra cruft and dispatch fields,
        and create one dict describing the named action / operator. """
    short_description = {"internal_name": name}
    for data in ["arguments", "cost", "user_name", "description", "short_description"]:
        if data in description_dict:
            short_description[data] = description_dict[data]
    return short_description


def get_possible_operators():
    """ Return a list of all possible operators for this game. """
    operators = list()
    for op in config_data.defaultConfig.costly_operations:
        operators.append(_jsonify_action(
            op, board_update_descriptions.operators_description[op]))
    return operators


def get_cell_actions():
    """ Return a list of all possible actions for this game.

    May eventually want to update to alter possible actions for all possible games. """
    operators = get_possible_operators()

    actions = list()
    for act in config_data.defaultConfig.actions:
        short_desc = _jsonify_action(
            act, board_update_descriptions.actions_description[act])
        if act == "applyops":
            short_desc["operators"] = operators
        actions.append(short_desc)

    return actions

def submit_game_tree(tree):
    logger.info("Saving game tree.", file=sys.stderr)
    with open("latest-game.json", "w") as outfile:
        outfile.write(json.dumps(tree))
    return {
        "message": "Game tree successfully saved."
    }
