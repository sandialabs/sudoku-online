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
import board_update_descriptions
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
    # If we found a contradiction (bad guess earlier in search), return 0
    #    as no more cells can be assigned
    if(sboard.invalidCells()):
        progress = f'Found logical contradiction.'
        sboard.config.debug_print('invalidcells', progress, sboard)
        return 0
    nValues = sboard.countUncertainValues()
    progress = f'Uncertainty state after {msg}\n{sboard.getStateStr(True)}\n{str(nValues)} uncertain values remaining'
    sboard.config.debug_print('status', progress, sboard)
    return nValues


def get_operator(op_name):
    """ Call the given operator.

    Args:
        op_name : the operator function name to apply
    Returns:
        Board(s): the updated board passed in, or a collection
            of boards if that's what the operator returns
    """
    try:
        op_func = board_update_descriptions.operators_description[op_name]['function']
        function = getattr(operators, op_func)
    except KeyError:
        raise Exception(f'Can\'t find operator {op_name}')
    except AttributeError:
        raise Exception(f'Can\'t find function {op_func}')

    return function


def get_action(action_name):
    """ Call the given action.

    Args:
        action_name : the operator function name to apply
    Returns:
        Board(s): the updated board passed in, or a collection
            of boards if that's what the operator returns
    """
    try:
        # Yes, it's insecure, but at least we're getting the thing we eval from ourselves
        action_func = board_update_descriptions.actions_description[action_name]['function']
        function = eval(action_func)
    except KeyError:
        raise(f'Can\'t find action {action_name}')
    except AttributeError:
        raise(f'Can\'t find function {action_func}')

    return function


def apply_free_operators(sboard, force=False):
    """ Iterate over free operators until no values change. """
    # Simplify if we're being forced or our config allows it
    if (force == False and sboard.config.simplify == False):
        return sboard
    nValues = sboard.countUncertainValues()
    prevValues = nValues + 1
    # Apply the free operators to a fixed point
    # All of these fancy shenanigans with control flow
    #   are just to ensure that these operators are applied
    #   in the same order whether they are free or paid
    while(prevValues > nValues and nValues > 0):
        prevValues = nValues
        for op in sboard.config.free_operations:
            sboard = get_operator(op)(sboard)
            nValues = calculate_status(sboard, op)
            if (nValues < prevValues):
                # If this is the first operator, and it ran
                #   to completion, then we can pretend the it
                #   was the base of the fixed point
                if (op == sboard.config.free_operations[0]
                    and sboard.config.explore_to_fixed_point
                        and not sboard.config.terminate_on_successful_operation):  # This last should be redundant
                    prevValues = nValues
                # Otherwise we need to restart
                elif sboard.config.restart_op_search_on_match:
                    break
    return sboard


# -----------------------------------------------------------------------------
# LOGICAL PUZZLE OPERATOR SELECTORS
# -----------------------------------------------------------------------------

def select_all_logical_operators_ordered(ordering=None):
    """ Returns an ordered list of parameterized logical operators. """
    if not ordering:
        def ordering(name):
            return board_update_descriptions.operators_description[name]['cost']
    costly_ops = sorted(
        config_data.defaultConfig.costly_operations, key=ordering)
    config_data.defaultConfig.debug_print(str(costly_ops), None, None)
    return costly_ops


# -----------------------------------------------------------------------------
# LOGICAL PUZZLE SOLVERS
# -----------------------------------------------------------------------------


def logical_solve(sboard, logical_ops):
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
        list of one item,
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
            sboard = get_operator(op)(sboard)
            opValues = calculate_status(sboard, op)
            if (opValues < prevValues):
                # Apply free operators if we made any progress
                sboard = apply_free_operators(sboard)
                freeValues = sboard.countUncertainValues()
                nValues = freeValues
                # If this is the first operator, and it ran
                #   to completion, then we can pretend the it
                #   was the base of the fixed point
                if (op == logical_ops[0]
                    and sboard.config.explore_to_fixed_point
                        and not sboard.config.terminate_on_successful_operation):  # This last should be redundant
                    prevValues = opValues
                # Otherwise we need to restart, unless the free operators didn't change anything
                if (nValues < prevValues
                        and sboard.config.restart_op_search_on_match):
                    break

    req_ops = list(logical_ops)
    req_ops.extend(sboard.config.free_operations)
    sboard.config.log_operation_request(
        req_ops,
        f'Requested application of {len(logical_ops)} operators, {len(sboard.config.free_operations)} free operators',
        sboard)
    return sboard


def logical_solve_action(sboard, logical_ops):
    child_board = logical_solve(sboard, logical_ops)
    return [child_board]

# -----------------------------------------------------------------------------
# SEARCH METHODS
# -----------------------------------------------------------------------------


def expand_cell(sboard, cell_id):
    """
    Expands the board cell identified by cell_id.

    Args:
        sboard  : the starting board to "expand"
        cell_id : the identifier of the cell to expand
    Returns:
        collection of board  : new boards.  Each board is a copy of sboard
            except that cell_id is set to a unique possible value.
            The collection of boards together cover the possible values of
            cell_id in sboard.

    For each value that cell_id can take
        create a new (duplicate) board and assign one of the candidate partition sets
            to the identified cell
    Returns a list of Boards with the cell value assigned
    If identified cell has only one possible value, simply returns [sboard]
    NOTE: propagation of the assigned value is not performed automatically.
    """

    cell = sboard.getCell(cell_id)
    if(cell.isCertain()):
        return [sboard]

    expansion = []
    for v in cell.getValueSet():
        b = board.Board(sboard)
        bcell = b.getCell(cell_id)
        bcell.assign(v)
        expansion.append(b)

        progress = f'Assigning {str(bcell.getIdentifier())} = {board.Cell.displayValue(bcell.getCertainValue())}'
        b.config.complete_operation('pivot', progress, b, True)

    progress = f'Pivoted on {str(bcell.getIdentifier())} for {len(expansion)} new (unvalidated) boards'
    sboard.config.complete_operation('pivot', progress, sboard, True)

    return expansion


def expand_cell_with_assignment(sboard, cell_and_val):
    """
    Expands the board cell identified by cell_id into a board with that value assigned,
    and a board with that value excluded (and marked as backup).

    Args:
        sboard  : the starting board to "expand"
        cell_and_val : a tuple:
            cell_id : the identifier of the cell to expand
            value : a value to assign to cell_id,
                intersecting those values with valid values
    Returns:
        collection of board  : new boards.  Each board is a copy of sboard
            except that in the first board cell_id is set to value
            and in the second (backup) board cell_id contains the remaining values.
    NOTE: propagation of the assigned value is not performed automatically.
    """
    (cell_id, value) = cell_and_val
    return __expand_cell_with_assignment(sboard, cell_id, value, False)


def expand_cell_with_exclusion(sboard, cell_and_val):
    """
    Expands the board cell identified by cell_id into a board with that value excluded,
    and a board with that value excluded (and marked as backup).

    Args:
        sboard  : the starting board to "expand"
        cell_and_val : a tuple:
            cell_id : the identifier of the cell to expand
            value : a value to assign to cell_id,
                intersecting those values with valid values
    Returns:
        collection of board  : new boards.  Each board is a copy of sboard
            except that in the first board cell_id contains the remaining values
            and in the second (backup) board cell_id is set to value.
    NOTE: propagation of the assigned value is not performed automatically.
    """
    (cell_id, value) = cell_and_val
    return __expand_cell_with_assignment(sboard, cell_id, value, True)


def __expand_cell_with_assignment(sboard, cell_id, value, make_exclusion_primary=False):
    """
    Expands the board cell identified by cell_id into partitions specified.

    Args:
        sboard  : the starting board to "expand"
        cell_id : the identifier of the cell to expand
        value : a value to assign to cell_id,
            intersecting those values with valid values
    Returns:
        collection of board  : new boards.  Each board is a copy of sboard
            except that in the first board cell_id is set to value
            and in the second board cell_id contains the remaining values.
            The collection of boards together cover the possible values of
            cell_id in sboard.
    NOTE: propagation of the assigned value is not performed automatically.
    """

    cell = sboard.getCell(cell_id)
    if(cell.isCertain()):
        return [sboard]

    expansion = []
    assigned = board.Board(sboard)
    expansion.append(assigned)
    removed = board.Board(sboard)
    expansion.append(removed)

    action = None
    if make_exclusion_primary:
        assigned.setToBackground()
        action = 'exclude'
    else:
        removed.setToBackground()
        action = 'assign'

    bcell = assigned.getCell(cell_id)
    bcell.assign(value)
    progress = f'Assigning {str(bcell.getIdentifier())} = {board.Cell.displayValue(bcell.getCertainValue())}'
    assigned.config.complete_operation(action, progress, assigned, True)

    bcell = removed.getCell(cell_id)
    bcell.exclude(value)
    progress = f'Removing {board.Cell.displayValue(value)} from {str(bcell.getIdentifier())}, resulting in {board.Cell.displayValues(bcell.getValueSet())}'
    removed.config.complete_operation(action, progress, removed, True)

    progress = f'Performed {action} on {str(bcell.getIdentifier())} with {board.Cell.displayValue(value)} for {len(expansion)} new (unvalidated) boards'
    sboard.config.complete_operation(action, progress, sboard, True)

    return expansion


# -----------------------------------------------------------------------------
# BEYOND-LOGICAL PUZZLE SOLVER SUPPORT METHODS
# -----------------------------------------------------------------------------


def take_action(sboard, expansion_op, args):
    """ Apply apply_free_operators to all boards in sboard_collection. """
    sboard_expansion = get_action(expansion_op)(sboard, args)

    ret = []
    for brd in sboard_expansion:
        brd = apply_free_operators(brd)
        if (sboard.config.prune_invalid_boards
                and brd.invalidCells()):
            continue
        # Include the board if we're including everything
        # OR if it's not got a proven contradiction yet
        ret.append(brd)
    return ret


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
        result.config.debug_print('solved', f'Puzzle solved.', result)
        return result

    # If we found a contradiction (bad guess earlier in search), return None
    elif(not result or result.invalidCells()):
        sboard.config.debug_print('incorrect', f'Found contradiction.', result)
        return None

    # Some action needs to be taken
    msg = f'Taking action, selecting cell using {str(cellselector)} and expanding cell using {str(expand_cell_action)}'
    result.config.debug_print('take action', msg, result)
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
