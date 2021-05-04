#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shelley Leger
Sandia National Laboratories
February 25, 2020

Test code for sudoku package.
    - define a set of test sudoku problems to use to test the sudoku infrastructure
    - run the sudoku infrastructure
    - define heuristics and evaluation functions to pass to the sudoku infrastructure
"""

import board
import config_data
import game
import operators
import puzzles
import solvers
import translate

import argparse
import math

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def test_sudoku(args):
    logger.info("Beginning test_sudoku.")
    # TODO MAL move set_verbosity to config_data
    if args.verbosity:
        logging.basicConfig(level=logging.DEBUG)

    my_ops = []
    if args.opselector == "all_logical_operators_ordered":
        my_ops = solvers.select_all_logical_operators_ordered()
    if args.parameterizeoperators:
        my_ops = args.parameterizeoperators
    logger.info("Using logical operators %s", str(my_ops))

    board_collection = []
    if not args.puzzles:
        args.puzzles = []
        if not args.games:
            args.puzzles = puzzles.puzzles.keys()
    logger.debug("Requesting puzzles %s", str(args.puzzles))
    for name in args.puzzles:
        sboard = translate.get_initial_board({"name": name})
        board_collection.append(sboard)
    if args.games:
        logger.debug("Requesting games %s", str(args.games))
        for name in args.games:
            gameboards = translate.get_boards_for_game(name)
            board_collection.extend(gameboards)

    for sboard in board_collection:
        logger.info("Initial state of %s:\n%s\n%s", sboard.getPuzzleName(), sboard.getStateStr(), sboard.getSimpleJson())

        cellselector = getattr(solvers, "select_" + args.cellselector)
        boardselector = getattr(solvers, "select_" + args.boardselector)
        search_tree = game.GameTreeNode(sboard, my_ops, cellselector)
        result = search_tree.play()

        if result:
            result.config.log.setSolution(result)
            logger.info("Final state of %s:\n%s\n%s", result.getPuzzleName(), result.getStateStr(), result.getSimpleJson())
            # TODO MAL This needs to be logging the search_tree, not the result
            result.config.log.printLogJSON()
            result.config.log.printCSV()
        else:
            logger.info("Final state of %s: INSOLUBLE", str(name))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Call sudoku solver, parameterized as desired")
    parser.add_argument("--puzzles", metavar="NAME", type=str, nargs="*",
                        help="puzzles to run through the solver; do not use argument to run all puzzles.")
    parser.add_argument("--games", metavar="NAME", type=str, nargs="*",
                        help="games to run through the solver; include configuration in game name as desired.")
    parser.add_argument("--verbosity", "-v", action="count", default=0)
    # parser.add_argument("--outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout)
    parser.add_argument("--cellselector", nargs="?",
                        choices=["random_cell_with_fewest_uncertain_values",
                                 "random_cell_with_most_uncertain_values",
                                 "cell_by_user"],
                        default="cell_by_user",
                        help="function to select pivot cell")
    parser.add_argument("--boardselector", nargs="?",
                        choices=["random_board_with_fewest_uncertain_values",
                                 "random_board_with_most_uncertain_values",
                                 "random_board_with_fewest_uncertain_cells",
                                 "random_board_with_most_uncertain_cells",
                                 "board_by_user"],
                        default="board_by_user",
                        help="function to select pivot board")
    parser.add_argument("--opselector", nargs="?",
                        choices=["all_logical_operators_ordered"],
                        default="all_logical_operators_ordered",
                        help="function to select which logical operators to use")
    parser.add_argument("--parameterizeoperators", metavar="LOGICALOPERATOR",
                        nargs="*",
                        choices=solvers.select_all_logical_operators_ordered(),
                        help="manually specify logical operators; overrides opselector")

    args = parser.parse_args()
    test_sudoku(args)
