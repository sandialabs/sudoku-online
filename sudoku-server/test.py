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
import logger
import config_data
import solvers
import argparse
import puzzles
import operators
import math


def test_sudoku(args):
    # TODO MAL move set_verbosity to config_data
    logger.set_verbosity(args.verbosity)

    my_ops = []
    if args.opselector == "all_logical_operators_ordered":
        my_ops = solvers.select_all_logical_operators_ordered()
    if args.parameterizeoperators:
        my_ops = args.parameterizeoperators

    if not args.puzzles:
        args.puzzles = puzzles.puzzles.keys()

    for name in args.puzzles:
        layout = puzzles.puzzles[name]
        sboard = board.Board(layout, int(
            math.sqrt(math.sqrt(len(layout)))), name)
        msg = f'Initial state of {name}:\n{sboard.getStateStr()}\n{sboard.getSimpleJson()}'
        sboard.config.debug_print('initial state', msg, None)

        cellselector = getattr(solvers, "select_" + args.cellselector)
        # sboard = solver(sboard, opselector, cellselector)
        if args.solver == 'logical':
            sboard = solvers.logical_solve(sboard, my_ops)
        elif args.solver == 'combined':
            sboard = solvers.combined_solve(sboard, my_ops, cellselector)

        msg = None
        if sboard:
            for key in sboard.config.log.operators_use_count.keys():
                # Print this at verbosity level 1
                msg = f'{key} uses: {sboard.config.log.operators_use_count[key]}'
                sboard.config.debug_print(msg, None, None)
            msg = f'puzzle,log,score, sboard {sboard._puzzle_name}({sboard.config.log.getPuzzle()}): {str(sboard.config.log.getDifficultyScore())}, {sboard.config.log.getDifficultyLevel()}\n{sboard.getStateStr()}'
            sboard.config.debug_print(msg, None, None)

            if sboard.config.log_all_boards or sboard.isSolved():
                sboard.config.log.setSolution(sboard)
                sboard.config.log.printLogJSON()
            msg = f'Final state of {name}:\n{sboard.getStateStr()}\n{sboard.getSimpleJson()}'
            sboard.config.debug_print('final state', msg, None)
        else:
            msg = f'Final state of {name}: INSOLUBLE'
            config_data.defaultConfig.debug_print('final state', msg, None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Call sudoku solver, parameterized as desired')
    parser.add_argument('--puzzles', metavar='NAME', type=str, nargs='*',
                        help='puzzles to run through the solver; do not use argument to run all puzzles.')
    parser.add_argument('--verbosity', '-v', action='count', default=0)
    # parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('--solver', nargs='?', choices=['logical', 'combined'],
                        default='logical', help='solver to use')
    parser.add_argument('--cellselector', nargs='?',
                        choices=['random_cell_with_fewest_uncertain_values',
                                 'by_user'],
                        default='random_cell_with_fewest_uncertain_values',
                        help='function to select pivot cell')
    parser.add_argument('--opselector', nargs='?',
                        choices=['all_logical_operators_ordered'],
                        default='all_logical_operators_ordered',
                        help='function to select which logical operators to use')
    parser.add_argument('--parameterizeoperators', metavar='LOGICALOPERATOR',
                        nargs='*',
                        choices=solvers.select_all_logical_operators_ordered(),
                        help='manually specify logical operators; overrides opselector')

    args = parser.parse_args()
    test_sudoku(args)
