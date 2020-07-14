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
import solvers
import argparse
import puzzles
import operators


def test_sudoku(args):
    logger.set_verbosity(args.verbosity)

    my_ops = []
    if args.opselector == "all_logical_operators_ordered":
        my_ops = solvers.select_all_logical_operators_ordered()
    if args.parameterizeoperators:
        my_ops = solvers.parameterize_logical_operators(
            args.parameterizeoperators)

    if not args.puzzles:
        args.puzzles = puzzles.puzzles.keys()

    for name in args.puzzles:
        layout = puzzles.puzzles[name]
        sboard = board.Board(layout)
        if(operators.verbosity > 0):
            print("Initial State of %s:" % name)
            print(sboard.getStateStr())
            print(sboard.getSimpleJson())

        cellselector = getattr(solvers, "select_" + args.cellselector)
        #sboard = solver(sboard, opselector, cellselector)
        if args.solver == 'logical':
            sboard = solvers.logical_solve(sboard, my_ops)
        elif args.solver == 'combined':
            sboard = solvers.combined_solve(sboard, my_ops, cellselector)

        if(operators.verbosity > 0):

            if sboard and sboard.isSolved():
                for key in sboard.log.operators_use_count.keys():
                    print(key, 'uses:', sboard.log.operators_use_count[key])
                print('sboard,log,score', str(sboard.log.getDifficultyScore())+':',
                      sboard.log.getDifficultyLevel())

                sboard.log.setSolution(sboard.getStateStr(False, False, ''))
                sboard.log.printLogJSON()

            print("Final State of %s:" % name)
            if sboard is not None:
                print(sboard.getStateStr())
                print(sboard.getSimpleJson())
            else:
                print("INSOLUBLE")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Call sudoku solver, parameterized as desired')
    parser.add_argument('--puzzles', metavar='NAME', type=str, nargs='*',
                        help='puzzles to run through the solver; do not use argument to run all puzzles.')
    parser.add_argument('--verbosity', '-v', action='count', default=1)
    #parser.add_argument('--outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
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
    parser.add_argument('--parameterizeoperators', metavar="OPTYPE SETTYPE",
                        nargs='*',
                        help='manually specify <optype settype> logical operator pairs; overrides opselector')  # TODO add help describing options

    args = parser.parse_args()
    test_sudoku(args)
