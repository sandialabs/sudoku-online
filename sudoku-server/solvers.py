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
import translate

import logging
logger = logging.getLogger(__name__)

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
        logger.debug("Found logical contradiction: invalid cells on board %s",
            str(sboard.getStateStr(True, False)))
        return 0
    nValues = sboard.countUncertainValues()
    logger.debug("Uncertainty state after %s\n%s\n%s uncertain values remaining",
        str(msg), str(sboard.getStateStr(True)), str(nValues))
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


BREAK = int(0xdead)
NORMAL = int(0xcafe)
def apply_one_operator(op, sboard):
    """ Apply one operator.
        Returns:
            boolean Changed if the operator changed the board,
            MAGIC BREAK if the operator loop should break/restart and NORMAL if it should continue.
    """
    prevValues = sboard.countUncertainValues()
    prevBoard = board.Board(sboard)
    sboard = get_operator(op)(sboard)
    newValues = calculate_status(sboard, op)
    changed = newValues < prevValues
    if changed and sboard.config.restart_op_search_on_match:
        return (sboard, BREAK)
    return (sboard, NORMAL)


def apply_logical_operator(op, sboard):
    """ Apply one logical operator.
    """
    prevValues = sboard.countUncertainValues()
    (sboard, control) = apply_one_operator(op, sboard)
    sboard = apply_free_operators(sboard)
    if sboard.config.retry_logical_op_after_free_ops and control != BREAK and sboard.countUncertainValues() < prevValues:
        ## Continue to iterate on the single logical operator, including free operators
        return apply_logical_operator(op, sboard)
    return (sboard, control)


def loop_operators(sboard, operations_list, function_to_apply):
    """  Loop over operations list, applying function_to_apply,
         given initial sboard, following configured control flow,
         until no values change.
    """
    initialUncertainValues = sboard.countUncertainValues()
    while(initialUncertainValues > 0):
        for op in operations_list:
            (sboard, control) = function_to_apply(op, sboard)
            if control == BREAK:
                break
        ## If none of the operators did anything, exit the loop
        if initialUncertainValues == sboard.countUncertainValues():
            break
        initialUncertainValues = sboard.countUncertainValues()
    return sboard


def apply_free_operators(sboard, force=False):
    """ Iterate over free operators until no values change. """
    # Simplify if we're being forced or our config allows it
    if (force == False and sboard.config.simplify == False):
        return sboard
    # Apply the free operators to a fixed point
    return loop_operators(sboard,
                          sboard.config.free_operations,
                          apply_one_operator)


# -----------------------------------------------------------------------------
# LOGICAL PUZZLE OPERATOR SELECTORS
# -----------------------------------------------------------------------------

def select_all_logical_operators_ordered(ordering=None):
    """ Returns an ordered list of parameterized logical operators. """
    if not ordering:
        def ordering(name):
            logger.debug("Asking to order operator %s", str(name))
            return board_update_descriptions.operators_description[name]['cost']
    costly_ops = sorted(
        [op['internal_name'] for op in translate.get_possible_operators()], key=ordering)
    logger.debug("Allowing for costly operations %s", str(costly_ops))
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
    # Iterate until we don't change the board or no uncertain values remain
    sboard = loop_operators(sboard,
                            logical_ops,
                            apply_logical_operator)

    req_ops = list(logical_ops)
    req_ops.extend(sboard.config.free_operations)
    sboard.config.log_operations_request(
        req_ops,
        f'Requested application of {len(logical_ops)} operators, {len(sboard.config.free_operations)} free operators',
        sboard)
    return sboard


def logical_solve_action(sboard, logical_ops):
    child_board = logical_solve(sboard, logical_ops)
    child_board.addAction({'action': 'applyops', 'operators': list(logical_ops)})
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
    sboard.computeAccessibleCells()
    if sboard.accessible_cells:
        assert cell_id in sboard.accessible_cells, \
            f'Cannot pivot on cell {cell_id} that is not accessible in {sboard.accessible_cells}'
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
        b.addAction({'action': 'pivot', 'cell': list(type(b).getLocations(cell_id, b.getDegree())), 'value': v})

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
    sboard.computeAccessibleCells()
    if sboard.accessible_cells:
        assert cell_id in sboard.accessible_cells, \
            f'Cannot pivot on cell {cell_id} that is not accessible in {sboard.accessible_cells}'
    cell = sboard.getCell(cell_id)
    if(cell.isCertain()):
        return [sboard]

    expansion = []
    assigned = board.Board(sboard)
    removed = board.Board(sboard)

    action = None
    if make_exclusion_primary:
        assigned.setToBackground()
        action = 'exclude'
        expansion.append(removed)
        expansion.append(assigned)
    else:
        removed.setToBackground()
        action = 'assign'
        expansion.append(assigned)
        expansion.append(removed)

    cell_loc = list(type(assigned).getLocations(cell_id, assigned.getDegree()))

    bcell = assigned.getCell(cell_id)
    bcell.assign(value)
    progress = f'Assigning {str(bcell.getIdentifier())} = {board.Cell.displayValue(bcell.getCertainValue())}'
    assigned.config.complete_operation(action, progress, assigned, True)
    assigned.addAction({'action': 'assign', 'cell': cell_loc, 'value': value})

    bcell = removed.getCell(cell_id)
    bcell.exclude(value)
    progress = f'Removing {board.Cell.displayValue(value)} from {str(bcell.getIdentifier())}, resulting in {board.Cell.displayValues(bcell.getValueSet())}'
    removed.config.complete_operation(action, progress, removed, True)
    removed.addAction({'action': 'exclude', 'cell': cell_loc, 'value': value})

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


def collect_cells(sboard):
    """
    Given an sboard, collect the set of cells to select from.
    """
    # Get the list of board cells that are accessible
    access_cells = sboard.computeAccessibleCells()
    logger.debug("Accessible cells are %s", str(access_cells))
    cell_list = []
    #Need to get the actual cells not the identifier
    for ide in access_cells:
        cell_list.append(sboard.getCell(ide))
    return cell_list


def select(item_list, heuristic, criterion, selector):
    """
    Selects and returns a single selected item from item_list by the following:
    1. Apply heuristic to each item_list
    2. Filter the set of item_list according to criterion
    3. If multiple item_list satisfy criterion, select among those using selector
    Heuristic argument is a function that takes an item from item_list as
        input and returns a number (e.g., number of candidate values)
    Criterion argument is a function that takes a list of heuristic scores and
        returns whatever value(s) satisfy the criterion (e.g., max or min)
    Selector argument is a function that takes a list of items and
        returns whatever item is selected by selector
    Returns:
        One item from item_list
    """

    # Apply heuristic to get list of (item, score) tuples
    hscores = list(map(lambda item: (item, heuristic(item)), item_list))

    # Apply criterion to determine the best score
    selection = criterion([score for (item, score) in hscores])

    # Filter the list of heuristic scores to get the set of best cells
    best_list = [item for (item, score) in hscores if score == selection]

    # Pick one of the best cells at random
    if selector is None:
        selector = random.choice
    return selector(best_list)


# -----------------------------------------------------------------------------
# SEARCH PUZZLE CELL / BOARD / ACTION SELECTORS
# -----------------------------------------------------------------------------


def select_random_cell_with_fewest_uncertain_values(sboard):
    """ Return the Cell that has the fewest uncertain values. """
    return select(collect_cells(sboard), candidate_cell_values_heuristic, min, random.choice)


def select_random_cell_with_most_uncertain_values(sboard):
    """ Return the Cell that has the most uncertain values. """
    return select(collect_cells(sboard), candidate_cell_values_heuristic, max, random.choice)


def select_cell_by_user(sboard):
    """ Return the Cell selected by the user. """
    return select(collect_cells(sboard), uniform_heuristic, min, users_choice_cell)


def select_random_board_with_fewest_uncertain_values(node_list):
    """ Return the Board that has the fewest uncertain values, removing it from node_list. """
    board = select(node_list, candidate_board_uncertain_values_heuristic, min, random.choice)
    node_list.remove(board)
    return board


def select_random_board_with_most_uncertain_values(node_list):
    """ Return the Board that has the most uncertain values, removing it from node_list. """
    board = select(node_list, candidate_board_uncertain_values_heuristic, max, random.choice)
    node_list.remove(board)
    return board


def select_random_board_with_fewest_uncertain_cells(node_list):
    """ Return the Board that has the fewest uncertain cells, removing it from node_list. """
    board = select(node_list, candidate_board_uncertain_cells_heuristic, min, random.choice)
    node_list.remove(board)
    return board


def select_random_board_with_most_uncertain_cells(node_list):
    """ Return the Board that has the most uncertain cells, removing it from node_list. """
    board = select(node_list, candidate_board_uncertain_cells_heuristic, max, random.choice)
    node_list.remove(board)
    return board


def select_board_by_user(node_list):
    """ Return the Board selected by the user, removing it from node_list. """
    board = select(node_list, uniform_heuristic, min, users_choice_board)
    node_list.remove(board)
    return board


# -----------------------------------------------------------------------------
# SEARCH PUZZLE HEURISTICS
# Cell -> comparable value representing "goodness" of cell
# Board -> comparable value representing "goodness" of board
# -----------------------------------------------------------------------------


def candidate_cell_values_heuristic(cell):
    """ Taking in a Cell, return the number of candidate values. """
    return len(cell.getValues())


def uniform_heuristic(item):
    """ Taking in an item, return 1. """
    return 1


def candidate_board_uncertain_cells_heuristic(node):
    """ Taking in a GameTreeNode, return the number of uncertain cells. """
    return len(node.board.getUncertainCells())


def candidate_board_uncertain_values_heuristic(node):
    """ Taking in a GameTreeNode, return the number of uncertain values across cells. """
    return node.board.countUncertainValues()


# -----------------------------------------------------------------------------
# SEARCH PUZZLE SELECTORS
# [list of possible Cells] -> a single selected pivot Cell
# -----------------------------------------------------------------------------


def users_choice_cell(cell_list):
    """ Taking in a list of Cells, ask the user to select one and return it.
    """
    selected = None

    assert len(cell_list) > 0, "Can't select cell from empty list."
    if len(cell_list) == 1:
        logger.info("Selecting single cell %s", str(cell_list[0]))
        return cell_list[0]

    while True:
        names = sorted([cell.getIdentifier() for cell in cell_list])
        print("Which cell do you want to expand? {}".format(names))
        selected = input()
        if selected in names:
            logger.debug("User selected cell ID %s.", str(selected))
            match_cell = next(filter(lambda x: x.getIdentifier() == selected, cell_list))
            if match_cell:
                break
        logger.warn("Unable to find cell matching selected identifier %s.", str(selected))
    return match_cell


def users_choice_board(node_list):
    """
    Allow the user to select a board to continue exploring. Remove that board from the node_list
    """
    assert len(node_list) > 0, "Can't select board from empty list."
    if len(node_list) == 1:
        logger.info("Selecting single board %s", str(node_list[0]))
        return node_list[0]

    while True:
        print("Choose a board to explore.")
        # MAL TODO gross
        for i in range(len(node_list)):
            node = node_list[i]
            print("Board Number {}:\n{}\n".format(i, node.board.getStateStr(True)))
        print("Please input the desired board number:")
        idx = int(input())
        if idx >= 0 and idx < len(node_list):
            logger.debug("User selected board index %s.", str(idx))
            active = node_list[idx]
            break
        logger.warn("Selected index not valid (%s).", str(idx))
    return active
