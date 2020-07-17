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
import config_data
import board

# -----------------------------------------------------------------------------
# LOGICAL PUZZLE SOLVER SUPPORT METHODS
# -----------------------------------------------------------------------------


def calculate_status(sboard, msg):
    """ Centralized diagnostics for after applying logical operators.

    Args:
        sboard  : the board to evaluate
        msg     : the message describing the operator just applied
    Returns:
        int     : the number of uncertain values in sboard
    """
    nValues = sboard.countUncertainValues()
    progress = f'Uncertainty state after {msg}\n{sboard.getStateStr(True)}\n{str(nValues)} uncertain values remaining'
    config_data.debug_print('status', progress, sboard)
    return nValues


def apply_free_operators(sboard, force=False):
    """ Iterate over free operators until no values change. """
    # Simplify if we're being forced or our config allows it
    if (force == False and config_data.config.simplify == False):
        return sboard
    nValues = sboard.countUncertainValues()
    prevValues = nValues + 1
    while(prevValues > nValues and nValues > 0):
        prevValues = nValues
        for op in config_data.config.free_actions:
            sboard = call_operator(sboard, op)
            nValues = calculate_status(sboard, op)
            if nValues < prevValues:
                # Use the computationally cheapest free operator
                break
    return sboard


def call_operator(sboard, op_name):
    """ Call the given operator.

    Args:
        sboard  : The board to apply the specified operator to.
        op_name : the operator function name to apply
    Returns:
        Board, boolean   : the updated board passed in, and a boolean
            indicating whether the board was updated (i.e., the number
            of uncertain values in the board changed)
    """
    try:
        op_func = config_data.operators_description[op_name]['function']
        function = getattr(operators, op_func)
    except KeyError:
        print(f'Can\'t call operator {op_name}')
        return None

    return function(sboard)


# -----------------------------------------------------------------------------
# LOGICAL PUZZLE OPERATOR SELECTORS
# -----------------------------------------------------------------------------

def select_all_logical_operators_ordered(ordering=None):
    """ Returns an ordered list of parameterized logical operators. """
    if not ordering:
        def ordering(name):
            return config_data.operators_description[name]['cost']
    costly_ops = sorted(config_data.config.costly_actions, key=ordering)
    config_data.debug_print(str(costly_ops), None, None)
    return costly_ops


# -----------------------------------------------------------------------------
# LOGICAL PUZZLE SOLVERS
# -----------------------------------------------------------------------------


# TODO MAL come back to the inclusion / exclusion issue
def logical_solve(sboard, logical_ops, restart=True):
    """ Solves sboard using only logical operators.

    Args:
        sboard (Board)  : the board to apply operators to
        logical_ops ([operator, ...])  :
            a list of logical operator function names describing the set of
            logical operators to apply and the order in which
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

    sboard = apply_free_operators(sboard)
    nValues = sboard.countUncertainValues()
    prevValues = nValues + 1  # Force the first iteration of the loop
    # Iterate until we don't change the board or no uncertain values remain
    while(prevValues > nValues and nValues > 0):
        prevValues = nValues

        for op in logical_ops:
            sboard = call_operator(sboard, op)
            nValues = calculate_status(sboard, op)
            if nValues < prevValues:
                # We progressed the board
                sboard = apply_free_operators(sboard)
                if restart:  # TODO MAL move restart to config
                    # If the operator made a change to board and restart is True,
                    # we will go back to the beginning of logical_ops
                    break

    # If we found a contradiction (bad guess earlier in search), return None
    if(sboard.invalidCells()):
        progress = f'Found logical contradiction.'
        config_data.debug_print('invalidcells', progress, sboard)
        return None
    return sboard

# -----------------------------------------------------------------------------
# BEYOND-LOGICAL PUZZLE SOLVER SUPPORT METHODS
# -----------------------------------------------------------------------------


def simplify_expansions(sboard_collection, include_invalid_boards=True):
    """ Apply apply_free_operators to all boards in sboard_collection. """
    ret = []
    for brd in sboard_collection:
        brd = apply_free_operators(brd)
        # TODO MAL move include_invalid_boards to config
        if include_invalid_boards or not brd.invalidCells():
            # Include the board if we're including everything
            # OR if it's not got a proven contradiction yet
            ret.append(brd)
    return ret


def expand_cell_action(sboard, cell_id):
    """ Expand all possible values of cell.

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
    return simplify_expansions(expansion)


def assign_cell_action(sboard, cell_id, value):
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
    expansion = operators.expand_cell_with_assignment(sboard, cell_id, value)
    return simplify_expansions(expansion)


def exclude_cell_value_action(sboard, cell_id, value):
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
    expansion = operators.expand_cell_with_exclusion(sboard, cell_id, value)
    return simplify_expansions(expansion)


# TODO MAL remove this function
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
        config_data.debug_print('solved', f'Puzzle solved.', result)
        return result

    # If we found a contradiction (bad guess earlier in search), return None
    elif(not result or result.invalidCells()):
        config_data.debug_print('incorrect', f'Found contradiction.', result)
        return None

    # Some action needs to be taken
    msg = f'Taking action, selecting cell using {str(cellselector)} and expanding cell using {str(expand_cell_action)}'
    config_data.debug_print('take action', msg, result)
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
