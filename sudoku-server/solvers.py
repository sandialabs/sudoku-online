# -*- coding: utf-8 -*-
"""
David Stracuzzi, Michael Darling, Shelley Leger
Sandia National Laboratories
February 26, 2020

Sudoku Board solvers.
    - logical puzzle solvers, which simply apply logical operators
    - heuristic cell selectors
"""

import random
import operators
# import logger
import board

# -----------------------------------------------------------------------------
# LOGICAL PUZZLE SOLVER SUPPORT METHODS
# -----------------------------------------------------------------------------


def calculate_status(sboard, msg, threshold=2):
    """ Centralized diagnostics for after applying logical operators.

    Args:
        sboard  : the board to evaluate
        msg     : the message describing the operator just applied
        threshold : the value of verbosity above which these diagnostics
            should be printed
    Returns:
        int     : the number of uncertain values in sboard
    """
    nValues = sboard.countUncertainValues()
    if(operators.verbosity > threshold):
        print("Uncertainty state after " + msg)
        print(sboard.getStateStr(True))
        print("%d uncertain values remaining" % nValues)
    return nValues


def singles_operators(sboard):
    """ Iterate over exclusion and inclusion until no values change. """
    # print('in singles operators')
    nValues = sboard.countUncertainValues()
    prevValues = nValues + 1
    while(prevValues > nValues and nValues > 0):
        prevValues = nValues

        # Apply logical exclusion
        sboard = operators.logical_exclusion(sboard)
        nValues = calculate_status(sboard, "exclusion propagation", 2)

        # Apply logical inclusion
        sboard = operators.logical_inclusion(sboard)
        nValues = calculate_status(sboard, "inclusion assignment", 2)

    return sboard


def call_operator(sboard, operator_type, set_type):
    """ Call the given operator with the given type.

    Args:
        sboard  : The board to apply the specified operator to.
        operator_type   : the operator type ('pointing', 'naked',
            'hidden', or 'wing')
        set_type        : the parameter to pass to the operator functions
    Returns:
        Board, boolean   : the updated board passed in, and a boolean
            indicating whether the board was updated (i.e., the number
            of uncertain values in the board changed)
    """
    prevValues = sboard.countUncertainValues()

    if operator_type == 'pointing':
        sboard = operators.find_pointing_candidates(sboard, set_type)
    if operator_type == 'naked':
        sboard = operators.find_naked_candidates(sboard, set_type)
    if operator_type == 'hidden':
        sboard = operators.find_hidden_candidates(sboard, set_type)
    if operator_type == 'wing':
        sboard = operators.find_wings(sboard, set_type)

    nValues = calculate_status(sboard, operator_type + ' ' + set_type, 2)

    if nValues < prevValues:
        return sboard, True
    else:
        return sboard, False


# -----------------------------------------------------------------------------
# LOGICAL PUZZLE OPERATOR SELECTORS
# -----------------------------------------------------------------------------

def select_all_logical_operators_ordered():
    """ Returns an ordered list of parameterized logical operators. """
    return [['pointing', 'pairs'],
            ['naked', 'pairs'],
            ['hidden', 'pairs'],
            ['pointing', 'triples'],
            ['naked', 'triples'],
            ['hidden', 'triples'],
            ['wing', 'y'],
            ['wing', 'xyz'],
            ['wing', 'x'],
            ['naked', 'quads'],
            ['hidden', 'quads']
            ]


def parameterize_logical_operators(ops_list):
    """ Returns a logical operator selector ordered as the pairs given in ops_list. """
    my_ops = []
    if (operators.verbosity > 1):
        print(str(ops_list))
    it = iter(ops_list)
    for op in it:
        # TODO MAL BAD PRACTICE - ask cll for help
        param = next(it)
        my_ops.append([op, param])
    return my_ops

# -----------------------------------------------------------------------------
# LOGICAL PUZZLE SOLVERS
# -----------------------------------------------------------------------------


def logical_solve(sboard, logical_ops, restart=True):
    """ Solves sboard using only logical operators.

    Args:
        sboard (Board)  : the board to apply operators to
        logical_ops ([[operator, parameter], ...])  :
            a list of [operator, parameter] pairs describing the set of
            parameterized operators to apply and the order in which
            to apply them (applying inclusion and exclusion to a fixed
            point in between each specified logical operator)
        restart (boolean)   : whether to restart at the first
            operator in the logical_ops list once one operator actually
            affects the board (True) or to continue from the next
            operator in the list (False)
    Returns:
        sboard (Board) modified by the logical operators until no
            operator in logical_ops can make any more changes,
        OR None if sboard reaches a contradiction.

    Currently iterates between propagating exclusions and assigning
    inclusions until no new constraints are identified.
    """

    nValues = sboard.countUncertainValues()
    prevValues = nValues + 1  # Force the first iteration of the loop
    # Iterate until we don't change the board or no uncertain values remain
    while(prevValues > nValues and nValues > 0):
        prevValues = nValues
        sboard = singles_operators(sboard)

        for op, param in logical_ops:
            sboard, operator_applied = call_operator(sboard, op, param)
            nValues = sboard.countUncertainValues()
            if operator_applied:
                if restart:
                    # If the operator made a change to board and restart is True,
                    # we will go back to the beginning of logical_ops
                    break
                else:
                    # Otherwise, we will continue with the next operator,
                    # so we need to force inclusion / exclusion
                    sboard = singles_operators(sboard)

    # If we found a contradiction (bad guess earlier in search), return None
    if(sboard.invalidCells()):
        if(operators.verbosity > 1):
            print("Found logical contradiction.")
        return None
    return sboard

# -----------------------------------------------------------------------------
# BEYOND-LOGICAL PUZZLE SOLVER SUPPORT METHODS
# -----------------------------------------------------------------------------


def simplify_expansions(sboard_collection, simplify, include_invalid_boards=True):
    """ If simplify is true, apply singles_operators to all boards in sboard_collection. """
    ret = []
    for brd in sboard_collection:
        if simplify:
            # Apply inclusion and exclusion for free
            brd = operators.logical_exclusion(brd)
        if include_invalid_boards or not brd.invalidCells():
            # Include the board if we're including everything
            # OR if it's not got a proven contradiction yet
            ret.append(brd)
    return ret


def expand_cell_action(sboard, cell_id, simplify=True):
    """ Expand all possible values of cell and simplify resulting boards.

    Args:
        sboard (Board)   : the Board containing the Cell to be expanded.
        cell_id (String) : the name of the Cell to pivot on
    Returns:
        [Boards] : the set of boards that result from assigning the selected
            cell to each possible value.

    Inclusion and exclusion have been applied to each possible board.
    """
    # TODO MAL we can change this to partition if we want! :)
    expansion = operators.expand_cell(sboard, cell_id)
    return simplify_expansions(expansion, simplify)


def assign_cell_action(sboard, cell_id, value, simplify=True):
    """ Assign value to cell_id, returning the assigned board and the one with all other options.

    Args:
        sboard (Board)   : the Board containing the Cell to be expanded.
        cell_id (String) : the name of the Cell to assign value to
    Returns:
        [Boards] : the board that result from assigning the selected
            cell to the value, and the board from removing that value from the options.

    Inclusion and exclusion have been applied to each possible board.
    The board with all the other options is set to a background board.
    """
    expansion = operators.expand_cell_with_assignment(
        sboard, cell_id, value, make_exclusion_primary=False)
    return simplify_expansions(expansion, simplify)


def exclude_cell_value_action(sboard, cell_id, value, simplify=True):
    """ Assign value to cell_id, returning the board with value removed and the one with that value assigned.

    Args:
        sboard (Board)   : the Board containing the Cell to be expanded.
        cell_id (String) : the name of the Cell to remove value from
    Returns:
        [Boards] : the board that result from assigning the selected
            cell to the value, and the board from removing that value from the options.

    Inclusion and exclusion have been applied to each possible board.
    The board with the assignment is set to a background board.
    """
    expansion = operators.expand_cell_with_assignment(
        sboard, cell_id, value, make_exclusion_primary=True)
    return simplify_expansions(expansion, simplify)


def take_action(sboard, action, parameter):
    """ Given a board and a selected action, perform that action.

    Args:
        sboard (Board)  : the Board on which the action should be performed.
        action  : the action to take. May be
            "expand_cell <cell_id>" or
            "select_logical_ops [[op, param], ...]"
        parameter
    Returns:
        [Boards] : a collection of boards resulting from the selection action.
    """
    if action == "selectValueForCell":
        # Assign the value to the given cell
        (cell_id, value) = parameter
        return assign_cell_action(sboard, cell_id, value)
    elif action == "pivotOnCell":
        # Expand the cell specified by the string parameter
        cell_id = parameter
        return expand_cell_action(sboard, cell_id)
    elif action == "applyLogicalOperators":
        # Apply the logical operators specified by the op/param list of pairs
        return [logical_solve(board.Board(sboard), parameter)]


# -----------------------------------------------------------------------------
# SEARCH PUZZLE CELL SELECTORS
# -----------------------------------------------------------------------------

def select(sboard, heuristic, criterion, selector):
    """
    Selects and returns a single cell from sboard by the following:
    1. Apply heuristic to each uncertain cell
    2. Filter the set of cells according to criterion
    3. If multiple cells satisfy criterion, select among those using selector
    Heuristic argument is a function that takes an uncertain cell as
        input and returns a number (e.g., number of candidate values)
    Criterion argument is a function that takes a list of heuristic scores and
        returns whatever value(s) satisfy the criterion (e.g., max or min)
    Selector argument is a function that takes a list of cells and
        returns whatever cell is selected by selector
    """

    # Get the list of board cells that are uncertain
    cell_list = sboard.getUncertainCells()

    # Apply heuristic to get list of (cell, score) tuples
    hscores = list(map(lambda cell: (cell, heuristic(cell)), cell_list))

    # Apply criterion to determine the best score
    selection = criterion([score for (cell, score) in hscores])

    # Filter the list of heuristic scores to get the set of best cells
    best_list = [cell for (cell, score) in hscores if score == selection]

    # Pick one of the best cells at random
    if selector is None:
        selector = random.choice
    return selector(best_list)


def select_random_cell_with_fewest_uncertain_values(sboard):
    """ Return the Cell that has the fewest uncertain values. """
    return select(sboard, candidate_values_heuristic, min, random.choice)


def select_random_cell_with_most_uncertain_values(sboard):
    """ Return the Cell that has the fewest uncertain values. """
    return select(sboard, candidate_values_heuristic, max, random.choice)


def select_by_user(sboard):
    """ Return the Cell selected by the user. """
    return select(sboard, uniform_heuristic, min, users_choice)

# -----------------------------------------------------------------------------
# SEARCH PUZZLE HEURISTICS
# Cell -> comparable value representing "goodness" of cell
# -----------------------------------------------------------------------------


def candidate_values_heuristic(cell):
    """ Taking in a Cell, return the number of candidate values. """
    return len(cell.getValues())


def uniform_heuristic(cell):
    """ Taking in a Cell, return 1. """
    return 1

# -----------------------------------------------------------------------------
# SEARCH PUZZLE SELECTORS
# [list of possible Cells] -> a single selected pivot Cell
# -----------------------------------------------------------------------------


def users_choice(cell_list):
    """ Taking in a list of Cells, ask the user to select one and return it.

    Takes in the Board containing the Cells to help extracting the correct one.
    """
    names = sorted([cell.getIdentifier() for cell in cell_list])
    print("Which cell do you want to expand? {}".format(names))
    selected = input()
    print(selected)
    return next(filter(lambda x: x.getIdentifier() == selected, cell_list))

# -----------------------------------------------------------------------------
# LOGIC/SEARCH COMBINED PUZZLE SOLVERS
# -----------------------------------------------------------------------------


def combined_solve(sboard, logical_ops=[], cellselector=None):
    """
    Solves sboard to a single completion by using a combination of logical and
    search-based operators.  Applies logical_solve to completion on
    initial board, then selects a cell to expand, then returns to
    logical_solve again.  Process continues recursively until a solution
    or contradiction is found.  If solution, final board state is returned.
    If contradiction, returns None and tests another of the expansion
    candidates.
    """

    # Apply logical solver first
    result = logical_solve(sboard, logical_ops)

    # If the puzzle is solved, just return the solution
    if(result and result.isSolved()):
        if(operators.verbosity > 1):
            print("Puzzle solved.")
        return result

    # If we found a contradiction (bad guess earlier in search), return None
    elif(not result or result.invalidCells()):
        if(operators.verbosity > 1):
            print("Found contradiction.")
        return None

    # Some action needs to be taken
    if (operators.verbosity > 2):
        print("Taking selecting cell using " + str(cellselector)
              + " and expanding cell using " + str(expand_cell_action))
    cell = cellselector(result)
    expansion = expand_cell_action(result, cell.getIdentifier())
    for brd in expansion:
        brd2 = combined_solve(brd, logical_ops, cellselector)
        if(brd2 is None):  # if we get None back, try another value
            continue
        else:  # found solution
            return brd2

    # Tried all candidate values and failed
    # May happen if we tried a bad candidate earlier in the recursive search
    return None
