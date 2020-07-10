#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David Stracuzzi, Michael Darling
Sandia National Laboratories
February 25, 2020

Sudoku Board operators.
"""

import board
# from board import Cell
import copy
# -----------------------------------------------------------------------------
# GLOBAL METHODS
# -----------------------------------------------------------------------------

verbosity = 1


def set_verbosity(v):
    """
    Set verbosity level for the logical operators.

    Verbosity levels:
    0 = Silent
    1 = Display initial and final board states only
    2 = Indicate cell assignments and associated rule as they are made
    3 = Show the board uncertainty state after each rule application
    """
    global verbosity
    verbosity = v

# -----------------------------------------------------------------------------
# LOGICAL METHODS
# -----------------------------------------------------------------------------


def logical_exclusion(sboard):
    """
   Applies logical exclusion operator.

    Args:
        sboard  : the board to which the exclusion operator will be applied
    Returns:
        board   : sboard, updated to remove values assigned elsewhere in a unit

    Propagates the exclusion constraints from the constraint list.
    For each cell whose value set has been reduced to one value v
        remove v from the value set of all other cells in the same unit.
    See comments below for additional algorithmic details.
    """

    # get the list of cells with singleton value set
    plist = sboard.getCertainCells()
    for cell in plist:

        # if this cell value has already been propagated, skip it
        if(cell.isPropagated()):
            continue

        cell_id = cell.getIdentifier()
        cell_value = cell.getCertainValue()
        unit_name_list = sboard.getCellUnits(cell_id)

        # for each of the units associated with cell
        for unit_name in unit_name_list:
            cell_name_list = sboard.getUnitCells(unit_name)

            # for each cell in the current unit
            for c_name in cell_name_list:
                c = sboard.getCell(c_name)

                # if c is not the cell we are currently propagating
                # then remove cell_value from c's candidate set
                if(c is not cell):
                    excluded = c.exclude(cell_value)

                    # if c is now certain,
                    # then add it to list of of constraints to propagate
                    if(excluded and c.isCertain()):
                        plist.append(c)
                        sboard.log.logOperator(
                            'exclusion', sboard.getStateStr(True, False))
                        if(verbosity > 1):
                            print("Assigned", c_name,
                                  "=", c.getCertainValue(),
                                  "by exclusion")
                            if(verbosity > 2):
                                print(str(sboard))

        cell.setPropagated()

    return sboard


def logical_inclusion(sboard):
    """
   Applies logical inclusion operator.

    Args:
        sboard  : the board to which the inclusion operator will be applied
    Returns:
        board   : sboard, updated to assign single possible values within a unit

    Search board units for values that have only one possible cell and
    make the associated cell value assignment.  Note that any cell
    assignments should have their exclusions propagated (not done by this
    function).
    """

    # for each unit of the board
    for unit in board.Board.getAllUnits(sboard.getDegree()):
        cell_name_list = board.Board.getUnitCells(unit, sboard.getDegree())

        # init dict to track cells for which each value is a candidate
        value_dict = {}
        for value in board.Cell.getPossibleValuesByDegree(sboard.getDegree()):
            value_dict[value] = []

        # for each cell in the unit
        for cell_name in cell_name_list:
            cell = sboard.getCell(cell_name)
            cell_values = cell.getValueSet()

            # fill out the value dict
            for value in cell_values:
                value_dict[value].append(cell)

        # search the value dict for values that have only one cell
        for value, cell_list in value_dict.items():

            # if only one cell can take value and that cell is uncertain
            # then assign value to the cell and append to constraint list
            if(len(cell_list) == 1 and not cell_list[0].isCertain()):
                cell_list[0].assign(value)
                sboard.log.logOperator(
                    'inclusion', sboard.getStateStr(True, False))
                if(verbosity > 1):
                    # TODO MAL make logging print the display value, not just the idx
                    print("Assigned", cell_list[0].getIdentifier(),
                          "=", value, "by inclusion")
                    if(verbosity > 2):
                        print(str(sboard))

    return sboard


def __hidden_set_exclusion(sboard, hidden_set, intersection_unit_list):
    """
    After a possible hidden set has been identified, this method
    verifies whether the candidates are indeed a hidden set and
    exlcudes the appropriate values.
    """
    num_excluded_values = 0
    len_hidden_set = len(hidden_set)
    hidden_type = ''
    if len_hidden_set == 2:
        hidden_type = 'PAIRS'
    if len_hidden_set == 3:
        hidden_type = 'TRIPLES'
    if len_hidden_set == 4:
        hidden_type = 'QUADS'

    hidden_set_names = []
    for cell in hidden_set:
        hidden_set_names.append(cell.getIdentifier())

    for unit in intersection_unit_list:
        unit_cells = sboard.getUnitCells(unit)

        # we search through cells associated to
        # see if some values are only present in the potential hidden cells
        remaining_value_set = set({})

        for cell in hidden_set:
            remaining_value_set = remaining_value_set | cell.getValueSet()
        for cell in unit_cells:
            # print (remaining_value_set)
            associated_cell = sboard.getCell(cell)

            if associated_cell not in hidden_set:
                associated_value_set = associated_cell.getValueSet()
                remaining_value_set = remaining_value_set - associated_value_set

        # if the the number of remaining values is equal to the number of
        # cells in the set, then we've found a hidden set!
        if len(remaining_value_set) == len_hidden_set:

            for cell in unit_cells:
                associated_cell = sboard.getCell(cell)
                associated_value_set = associated_cell.getValueSet()

                if associated_cell not in hidden_set:
                    remaining_value_set -= associated_value_set

                    if len(remaining_value_set) == len_hidden_set:
                        # we've found a hidden set!

                        num_excluded_values = 0
                        for cell in hidden_set:
                            cell_name = cell.getIdentifier()
                            value_set = cell.getValueSet()
                            value_set_before_exclusion = value_set.copy()
                            exclusion_list = list(
                                value_set - remaining_value_set)

                            for value in exclusion_list:
                                cell.exclude(value)

                            if len(exclusion_list) > 0:
                                sboard.log.logOperator('hidden'+hidden_type.lower(),
                                                       sboard.getStateStr(True, False))
                                if(verbosity > 1):
                                    print('HIDDEN ' + hidden_type, sorted(hidden_set_names),
                                          cell_name, '-', sorted(
                                              value_set_before_exclusion),
                                          '->', sorted(value_set))
    if num_excluded_values > 0:
        return True
    else:
        return False


def __find_hidden_pairs(sboard, current_cell):
    """
    A hidden pair is any group of two cells in the same unit
    that have 2 values between them that are not found in the
    rest of the cells in the unit.  Therefore we exclude all
    other values from the cells in the pair.
    """
    found_hidden_pair = False

    current_cell_name = current_cell.getIdentifier()
    candidate_cells = __find_hidden_candidate_cells(sboard, current_cell)
    for candidate_cell in candidate_cells:

        candidate_cell_name = candidate_cell.getIdentifier()

        # get units that the pair have in common
        intersection_unit_list = sboard.getCommonUnits([current_cell_name,
                                                        candidate_cell_name])

        found_hidden_pair = __hidden_set_exclusion(sboard, [current_cell, candidate_cell],
                                                   intersection_unit_list)
    return found_hidden_pair


def __find_hidden_triples(sboard, current_cell):
    """
    A hidden triple is any group of three cells in the same unit
    that have 3 values between them that are not found in the
    rest of the cells in the unit.  Therefore we exclude all
    other values from the cells in the triple.
    """
    found_hidden_triple = False
    current_cell_name = current_cell.getIdentifier()

    current_value_set = current_cell.getValueSet()
    current_units = sboard.getCellUnits(current_cell_name)

    candidate_cells = __find_hidden_candidate_cells(sboard, current_cell)
    for first_candidate_cell in candidate_cells:

        first_candidate_value_set = first_candidate_cell.getValueSet()

        # cells have to have at least 2 values in common
        if len(current_value_set & first_candidate_value_set) > 1:

            for second_candidate_cell in candidate_cells:
                if second_candidate_cell != first_candidate_cell:

                    first_candidate_name = first_candidate_cell.getIdentifier()
                    first_candidate_units = sboard.getCellUnits(
                        first_candidate_name)

                    second_candidate_name = second_candidate_cell.getIdentifier()
                    second_candidate_value_set = second_candidate_cell.getValueSet()

                    candidates_intersection_value_set = (second_candidate_value_set &
                                                         first_candidate_value_set)
                    # if the first and second candidates are a pair, also,
                    # we check if the value set across the three cells is greater than 4,
                    # otherwise we probably have a naked triple
                    if len(candidates_intersection_value_set) > 1 and len(current_value_set |
                                                                          first_candidate_value_set |
                                                                          second_candidate_value_set) > 4:

                        second_candidate_units = sboard.getCellUnits(
                            second_candidate_name)

                        # check to see if all three candidates have at least one common unit
                        intersection_unit_list = list(set(current_units) &
                                                      set(first_candidate_units) &
                                                      set(second_candidate_units))

                        if len(intersection_unit_list) > 0:
                            found_hidden_triple = __hidden_set_exclusion(sboard,
                                                                         [current_cell, first_candidate_cell,
                                                                             second_candidate_cell],
                                                                         intersection_unit_list)

    return found_hidden_triple


def __find_hidden_quads(sboard, current_cell):
    """
    A hidden quad is any group of four cells in the same unit
    that have 4 values between them that are not found in the
    rest of the cells in the unit.  Therefore we exclude all
    other values from the cells in the quad.
    """
    found_hidden_quad = False
    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()
    current_units = sboard.getCellUnits(current_cell_name)
    candidate_cells = __find_hidden_candidate_cells(sboard, current_cell)

    for first_candidate_cell in candidate_cells:

        first_candidate_value_set = first_candidate_cell.getValueSet()
        intersection_value_set = current_value_set & first_candidate_value_set

        # cells have to have at least 2 values in common
        if len(intersection_value_set) > 1:

            for second_candidate_cell in candidate_cells:
                if second_candidate_cell != first_candidate_cell:

                    first_candidate_name = first_candidate_cell.getIdentifier()
                    first_candidate_units = sboard.getCellUnits(
                        first_candidate_name)

                    second_candidate_name = second_candidate_cell.getIdentifier()
                    second_candidate_value_set = second_candidate_cell.getValueSet()

                    intersection_value_set = (first_candidate_value_set &
                                              second_candidate_value_set)
                    # if the first and second candidates are a pair, also,
                    # we check if the value set across the three cells is greater than 4,
                    # otherwise we probably have a naked quad
                    # print(intersection_value_set)
                    if len(intersection_value_set) > 0 and len(current_value_set |
                                                               first_candidate_value_set |
                                                               second_candidate_value_set) > 4:

                        second_candidate_units = sboard.getCellUnits(
                            second_candidate_name)

                        # check to see if all three candidates have at least one common unit
                        intersection_unit_set = (set(current_units) &
                                                 set(first_candidate_units) &
                                                 set(second_candidate_units))

                        if len(intersection_unit_set) > 0:
                            candidates = [current_cell, first_candidate_cell,
                                          second_candidate_cell]

                            for third_candidate_cell in candidate_cells:
                                if third_candidate_cell not in candidates:

                                    candidates.append(third_candidate_cell)
                                    third_candidate_value_set = \
                                        third_candidate_cell.getValueSet()
                                    third_candidate_name = \
                                        third_candidate_cell.getIdentifier()
                                    third_candidate_units = \
                                        sboard.getCellUnits(
                                            third_candidate_name)
                                    intersection_unit_set = (intersection_unit_set &
                                                             set(third_candidate_units))

                                    intersection_value_set = (second_candidate_value_set &
                                                              third_candidate_value_set)

                                    if (len(intersection_value_set) > 1 and
                                            len(intersection_unit_set) > 0):

                                        found_hidden_quad = __hidden_set_exclusion(sboard,
                                                                                   candidates, list(intersection_unit_set))
    return found_hidden_quad


def __find_hidden_candidate_cells(sboard, current_cell):
    """
    Compares all cells to the current one and makes a list of
    cells that meet the criterion for hidden candidacy.
    The criterion is that the length of the union of the candidate's
    and current cell's value sets must be at least 2.
    """

    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()
    current_associated_cells = sboard.getAssociatedCells(current_cell_name)
    candidate_cells = []
    # iterate through list of current cells too find possible hidden candidates
    for candidate_cell_name in current_associated_cells:

        candidate_cell = sboard.getCell(candidate_cell_name)
        candidate_value_set = candidate_cell.getValueSet()
        intersection_value_set = current_value_set & candidate_value_set
        if len(intersection_value_set) >= 2:
            candidate_cells.append(candidate_cell)

    return candidate_cells


def find_hidden_candidates(sboard, set_type):
    """
    Applies requested hidden candidates operator.

    Args:
        sboard  : the board to which the hidden candidates operator will be applied
        set_type   :  Specifies hidden candidates operator type, options are:
            "pairs", "triples", or "quads"
    Returns:
        board   : sboard, updated to remove values that are not hidden
            candidates from identified cells

    The cells in a hidden set contain values amongst them
    that have been exlcuded from the rest of the cells in
    the hidden set's common unit.  Therefore we can exclude
    all other values from the cells in the set."
    """

    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():

        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # these operators are useful only for cells with more than two values
        if len(current_value_set) > 2:
            # the list of cells associated with the current cell

            if set_type == 'pairs':
                __find_hidden_pairs(sboard, current_cell)

            if set_type == 'triples':
                __find_hidden_triples(sboard, current_cell)

            if set_type == 'quads':
                __find_hidden_quads(sboard, current_cell)

    return sboard


def __naked_set_exclusion(sboard, naked_set, exclusion_values):
    """
    After naked set is identified, this function elminates
    the set's values from all other cells in the set's
    common units.
    """

    num_operated_cells = 0
    len_naked_set = len(naked_set)
    set_type = ''
    if len_naked_set == 2:
        set_type = 'PAIRS'
    if len_naked_set == 3:
        set_type = 'TRIPLES'
    if len_naked_set == 4:
        set_type = 'QUADS'

    # get cells the pair have in common
    intersection_cell_list = sboard.getCommonCells(naked_set)

    # remove set's values from assciated cells
    for non_pair_cell_name in intersection_cell_list:
        non_pair_cell = sboard.getCell(non_pair_cell_name)

        exclusion_list = []
        for value in exclusion_values:
            if non_pair_cell.hasValue(value):
                non_pair_cell.exclude(value)
                exclusion_list.append(value)
                num_operated_cells += 1

        if verbosity > 1 and len(exclusion_list) > 0:
            print('NAKED '+set_type, sorted(exclusion_values), sorted(naked_set),
                  'removes', sorted(exclusion_list),
                  'from', non_pair_cell_name)

    if num_operated_cells > 0:
        sboard.log.logOperator('naked'+set_type.lower(),
                               sboard.getStateStr(True, False))
        return True
    else:
        return False


def __find_naked_pairs(sboard, current_cell, candidate_cells):
    """
    Search board for a pair of two cells situated in the
    same unit with the same value set with only two
    values remaining. Remove these two values from all
    cells associated with the pair.

    """
    found_pair = False
    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()
    # Now we iterate through the candidates
    for first_candidate_cell in candidate_cells:
        first_candidate_value_set = first_candidate_cell.getValueSet()

        # Look for naked pair
        if len(current_value_set) == 2 and current_value_set == first_candidate_value_set:
            # We found a naked pair!
            # print(current_cell, first_candidate_cell)
            found_pair = __naked_set_exclusion(sboard, [current_cell_name,
                                                        first_candidate_cell.getIdentifier()],
                                               current_value_set)
            return found_pair

    return found_pair


def __find_naked_triples(sboard, current_cell, candidate_cells):
    """
    A Naked Triple is any group of three cells in the same unit
    that contain IN TOTAL 3 values. We search for a set of such cells.
    The combinations of candidates for a Naked Triple will be
    one of the following:
        (123) (123) (123) - {3/3/3} in terms of candidates per cell
        (123) (123) (12) - {3/2/2} or some combination thereof
        (123) (12) (23) - {3/2/2}
        (12) (23) (13) - {2/2/2}
    """

    found_triple = False
    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()
    for first_candidate_cell in candidate_cells:
        first_candidate_name = first_candidate_cell.getIdentifier()
        first_candidate_value_set = first_candidate_cell.getValueSet()
        first_candidate_unit_set = set(
            sboard.getCellUnits(first_candidate_name))
        # We iterate again to find second candidate
        for second_candidate_cell in candidate_cells:
            second_candidate_name = second_candidate_cell.getIdentifier()
            second_candidate_unit_set = set(
                sboard.getCellUnits(second_candidate_name))

            # if the second candidate is not the same as the first and
            # they have a common unit
            if(second_candidate_cell != first_candidate_cell and
                    len(first_candidate_unit_set & second_candidate_unit_set) > 0):

                second_candidate_value_set = second_candidate_cell.getValueSet()

                # naked triple forms if the three cells have 3 values left amongst them
                union_values = (current_value_set | first_candidate_value_set |
                                second_candidate_value_set)
                if len(union_values) == 3:
                    # we've found a naked triple!
                    found_triple = __naked_set_exclusion(sboard, [current_cell_name,
                                                                  first_candidate_name,
                                                                  second_candidate_name],
                                                         union_values)
                    return found_triple

    return found_triple


def __find_naked_quads(sboard, current_cell, candidate_cells):
    """
    A Naked quad is any group of four cells in the same unit
    that contain IN TOTAL 4 values.  Therefore we can exclude
    these four values from all other cells in the unit.
    """
    found_quad = False
    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()

    for first_candidate_cell in candidate_cells:
        first_candidate_name = first_candidate_cell.getIdentifier()
        first_candidate_unit_set = set(
            sboard.getCellUnits(first_candidate_name))
        # We iterate again to find second candidate
        for second_candidate_cell in candidate_cells:
            second_candidate_name = second_candidate_cell.getIdentifier()
            second_candidate_unit_set = set(
                sboard.getCellUnits(second_candidate_name))

            # if the second candidate is not the same as the first and
            # they have a common unit
            if(second_candidate_cell != first_candidate_cell and
                    len(first_candidate_unit_set & second_candidate_unit_set) > 0):

                for third_candidate_cell in candidate_cells:
                    third_candidate_name = third_candidate_cell.getIdentifier()
                    third_candidate_unit_set = \
                        set(sboard.getCellUnits(third_candidate_name))

                    # if the third candidate is not the same as the first and second
                    # and all three have acommon unit
                    if(third_candidate_cell != first_candidate_cell and
                        third_candidate_cell != second_candidate_cell and
                        len(first_candidate_unit_set & second_candidate_unit_set &
                            third_candidate_unit_set) > 0):

                        first_candidate_value_set = first_candidate_cell.getValueSet()
                        second_candidate_value_set = second_candidate_cell.getValueSet()
                        third_candidate_value_set = third_candidate_cell.getValueSet()

                        # naked quad forms if the three cells have
                        # 4 values left amongst them
                        union_values = (current_value_set | first_candidate_value_set |
                                        second_candidate_value_set |
                                        third_candidate_value_set)
                        if len(union_values) == 4:
                            # we've found a naked quad!
                            found_quad = __naked_set_exclusion(sboard, [current_cell_name,
                                                                        first_candidate_name,
                                                                        second_candidate_name,
                                                                        third_candidate_name],
                                                               union_values)
                            return found_quad
    return found_quad


def __find_naked_candidate_cells(sboard, current_cell):
    """
    Compares all cells to the current one and makes a list of
    cells that meet the criteria for naked candidacy.
    The criteria are that the candidate needs to have between 2 and 4
    remaining values and the union of the candidate's and current cell's
    value set must be less than or equal to 4.
    """
    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()
    # the list of cells associated with the current cell
    current_associated_cells = sboard.getAssociatedCells(current_cell_name)

    # iterate through list of current's associated cells
    candidate_cells = []
    for candidate_cell_name in current_associated_cells:
        candidate_cell = sboard.getCell(candidate_cell_name)
        candidate_value_set = candidate_cell.getValueSet()

        # Candidate cell can only have 2 to 4 remaining values
        if len(candidate_value_set) > 1 and len(candidate_value_set) < 5:
            union = candidate_value_set | current_value_set

            # The candidate and current cell have to have a total of 4 values or less
            if len(union) <= 4:
                candidate_cells.append(candidate_cell)
    return candidate_cells


def find_naked_candidates(sboard, set_type):
    """
    Applies requested naked operator.

    Args:
        sboard  : the board to which the naked candidates operator will be applied
        set_type   :  Specifies naked candidates operator type, options are:
            "pairs", "triples", or "quads"
    Returns:
        board   : sboard, updated to remove values identified as naked
            candidates from related cells

    A Naked Pair is two cells in the same unit with the same two values remaining.

    A Naked Triple is any group of three cells in the same unit that contain
    IN TOTAL 3 values. The combinations of candidates for a Naked Triple will be
    one of the following:
        (123) (123) (123) - {3/3/3} in terms of candidates per cell
        (123) (123) (12) - {3/2/2} or some combination thereof
        (123) (12) (23) - {3/2/2}
        (12) (23) (13) - {2/2/2}

    A Naked Quad is any group of four cells in the same unit
    that contain IN TOTAL 4 values.  Therefore we can exclude
    these four values from all other cells in the unit.
    """

    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():

        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # looking only for cells with two to four remaining values
        if len(current_value_set) > 1 and len(current_value_set) < 5:

            candidate_cells = __find_naked_candidate_cells(
                sboard, current_cell)

            if set_type == 'pairs':
                __find_naked_pairs(sboard, current_cell, candidate_cells)

            if set_type == 'triples':
                __find_naked_triples(sboard, current_cell, candidate_cells)

            if set_type == 'quads':
                __find_naked_quads(sboard, current_cell, candidate_cells)

    return sboard


def __find_pointing_candidate_cells(sboard, current_cell):
    """
    Compares all cells to the current one and makes a list of
    cells that meet the criterion for hidden candidacy.
    The criterion is that the length of the union of the candidate's
    and current cell's value sets must be at least 2.
    """

    current_cell_name = current_cell.getIdentifier()
    current_value_set = current_cell.getValueSet()
    current_associated_cells = sboard.getAssociatedCells(current_cell_name)
    candidate_cells = []
    # iterate through list of current cells too find possible hidden candidates
    for candidate_cell_name in current_associated_cells:

        candidate_cell = sboard.getCell(candidate_cell_name)
        candidate_value_set = candidate_cell.getValueSet()
        intersection_value_set = current_value_set & candidate_value_set

        if len(intersection_value_set) > 0 and len(candidate_value_set) > 1:
            candidate_cells.append(candidate_cell)

    return candidate_cells


def __is_pointing_set(sboard, candidates):
    """
    Support method that verifies whether a set of cells
    is indeed a pointing set and excludes the appropriate
    values from the appropriate cells.
    """
    # variable initialization
    found_pointing_set = False
    current_units = sboard.getCellUnits(candidates[0].getIdentifier())
    current_value_set = candidates[0].getValueSet()
    intersection_unit_set = set(current_units)
    intersection_value_set = set(current_value_set)
    candidate_names = []

    # this loop stores the information for all candidates in single data structures
    for cell in candidates:

        intersection_unit_set = (intersection_unit_set &
                                 set(sboard.getCellUnits(cell.getIdentifier())))
        intersection_value_set = intersection_value_set & cell.getValueSet()
        candidate_names.append(cell.getIdentifier())

    # loop through units common to the candidates
    for unit in intersection_unit_set:

        unit_cells = sboard.getUnitCells(unit)

        # this variable is used to see if the candidates' common values are also
        # present in other cells in the unit
        remaining_value_set = intersection_value_set.copy()

        # For each cell in the unit, we substract their value set
        # from the candidate's intersection set, if any values
        # are left over, then these values are only common to
        # the candidates.
        for cell in unit_cells:
            associated_cell = sboard.getCell(cell)
            if associated_cell not in candidates:
                remaining_value_set -= associated_cell.getValueSet()

        # If there's only one value, it is only common
        # to the candidates. Therefore, we can remove this value
        # from the cells in the other unit common to the candidates.
        if len(remaining_value_set) == 1:

            remaining_value = remaining_value_set.pop()
            other_units = intersection_unit_set - set(unit)

            for other_unit in other_units:
                other_unit_cells = sboard.getUnitCells(other_unit)

                # If any of these cells have the pointing set's value,
                # we can exlcude it.
                for cell_name in other_unit_cells:
                    cell = sboard.getCell(cell_name)

                    if cell not in candidates:

                        if cell.hasValue(remaining_value):
                            found_pointing_set = True
                            values_before_exclusion = copy.copy(
                                cell.getValueSet())
                            cell.exclude(remaining_value)

                            pointing_type = ''
                            if len(candidates) == 3:
                                pointing_type = 'TRIPLE'
                            if len(candidates) == 2:
                                pointing_type = 'PAIR'
                            if(verbosity > 1):
                                print('POINTING '+pointing_type, sorted(candidate_names),
                                      '-', cell.getIdentifier()+':',
                                      sorted(values_before_exclusion), '->',
                                      sorted(cell.getValueSet()))
    if found_pointing_set:
        sboard.log.logOperator('pointing'+pointing_type.lower() + 's',
                               sboard.getStateStr(True, False))

    return found_pointing_set


def find_pointing_candidates(sboard, set_type):
    """
    Applies requested pointing pairs or triples operator.

    Args:
        sboard  : the board to which the pointing candidates operator will be applied
        set_type   :  Specifies pointing candidates operator type, options are:
            "pairs" or "triples"
    Returns:
        board   : sboard, updated to remove values identified as pointing sets
            from related cells

    If any one value is present only two or three times in just one unit,
    then we can remove that number from the intersection of a number unit.
    There are four types of intersections:
        1. A pair or triple in a box - if they are aligned on a row, the
            value can be removed from the rest of the row.
        2. A pair or triple in a box, if they are aligned on a column, the
            value can be removed from the rest of the column.
        3. A pair or triple on a row - if they are all in the same box, the
            value can be removed from the rest of the box.
        4. A pair or triple on a column - if they are all in the same box, the
            value can be removed from the rest of the box.
    """
    # found_pointing_pair = False
    # found_pointing_triple = False

    # iterate through all cells on the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # no point in operator if cell is already certain
        if len(current_value_set) > 1:
            current_units = sboard.getCellUnits(current_cell_name)

            # candidate are cells that have at least one
            # value in common with the current cell
            candidate_cells = __find_pointing_candidate_cells(
                sboard, current_cell)
            candidates = []
            for first_candidate_cell in candidate_cells:

                candidates = [current_cell, first_candidate_cell]

                # check to see if the two cells constitute a pointing pair
                if set_type == 'pairs':
                    # found_pointing_pair = __is_pointing_set(sboard, candidates)
                    return sboard

                # if requested, look for a pointing triple
                if set_type == 'triples':
                    for second_candidate_cell in candidate_cells:
                        second_candidate_cell_name = second_candidate_cell.getIdentifier()

                        if second_candidate_cell not in candidates:
                            first_candidate_cell_name = first_candidate_cell.getIdentifier()
                            first_candidate_units = \
                                sboard.getCellUnits(first_candidate_cell_name)
                            first_candidate_value_set = first_candidate_cell.getValueSet()
                            second_candidate_cell_name = second_candidate_cell.getIdentifier()
                            second_candidate_units = \
                                sboard.getCellUnits(second_candidate_cell_name)
                            second_candidate_value_set = second_candidate_cell.getValueSet()

                            # check if all three cells have at least one value in common
                            # also check if the all three cell have a common unit
                            if(len(current_value_set & first_candidate_value_set &
                                    second_candidate_value_set) > 0 and
                                len(set(current_units) & set(first_candidate_units) &
                                    set(second_candidate_units)) > 0):
                                candidates = [current_cell, first_candidate_cell,
                                              second_candidate_cell]

                                # check if the three cells consistitute a pointing triple
                                # found_pointing_triple = __is_pointing_set(sboard, candidates)
                                return sboard
    return sboard


def __find_xwings(sboard):
    """
    An X-Wing ocurrs when there are only 2 candidates for a value in each of
    2 different units of the same kind and these candidates also lie on 2 other units
    of the same kind.  Then we can exclude this value from the latter two units.
    """
    units_and_twice_occurring_values = []
    cells_containing_values = []

    # iterate through all units in the baord
    for unit in sboard.getAllUnits():
        # iterate through all possible values
        for value in board.Cell.getPossibleValuesByDegree(sboard.getDegree()):

            # this function count the number of times a value is present in a unit
            # and returns the count and the cells that contain this value
            value_count, cells_containing_value = sboard.getValueCountAndCells(
                unit, value)

            # For X-wing we need units that contain a value only twice
            if value_count == 2:
                units_and_twice_occurring_values.append([unit, value])
                cells_containing_values.append(cells_containing_value)

    # We iterate through all the units which have a value present only twice
    for i in range(len(units_and_twice_occurring_values)):
        current_unit = units_and_twice_occurring_values[i][0]
        current_value = units_and_twice_occurring_values[i][1]
        current_unit_type = sboard.getUnitType(current_unit)

        # We look for a second unit containing only two of a value
        for j in range(len(units_and_twice_occurring_values)):
            if i != j:

                second_unit = units_and_twice_occurring_values[j][0]
                second_value = units_and_twice_occurring_values[j][1]
                second_unit_type = sboard.getUnitType(second_unit)

                # if the two units contain the same value only twice each and
                # are of the same type, we may have an x-wing
                if second_value == current_value and second_unit_type == current_unit_type:
                    candidates = cells_containing_values[i] + \
                        cells_containing_values[j]
                    # print('candidates',candidates)
                    first_intersection_unit_list = \
                        list((set(sboard.getCellUnits(candidates[0])) &
                              set(sboard.getCellUnits(candidates[2]))))
                    second_intersection_unit_list = \
                        list((set(sboard.getCellUnits(candidates[1])) &
                              set(sboard.getCellUnits(candidates[3]))))

                    # If candidates have a second unit in common that's also  of the same type
                    # then we technically have found an x-wing.
                    # The only remaining question is whether any other cells
                    # in the second set of units have the value in question
                    if(len(first_intersection_unit_list) == 1 and
                        len(second_intersection_unit_list) == 1 and
                        (sboard.getUnitType(first_intersection_unit_list[0]) ==
                         sboard.getUnitType(second_intersection_unit_list[0]))):
                        # we've found an x-wing!

                        exclusion_value = current_value
                        excluded_cells = []

                        # we iterate through the units common to the candidates
                        for unit in (first_intersection_unit_list +
                                     second_intersection_unit_list):

                            unit_cells = sboard.getUnitCells(unit)

                            # iterating through all cells in these units
                            for cell_name in unit_cells:

                                if cell_name not in candidates:
                                    cell = sboard.getCell(cell_name)

                                    # if the value is presentin a cell, we exclude it
                                    if exclusion_value in cell.getValueSet():
                                        excluded_cells.append(cell_name)
                                        cell.exclude(exclusion_value)

                        if len(excluded_cells) > 0:
                            sboard.log.logOperator(
                                'xwings', sboard.getStateStr(True, False))

                            if(verbosity > 1):
                                print('X-WING', candidates, 'excludes', str(exclusion_value),
                                      'from', sorted(excluded_cells))
    return sboard


def __find_candidates(sboard, current_cell_name, num_values, num_intersection_values):
    """
    A support method to find candidate cells to be ywing or xyzwing pincers.
    """
    candidates = []
    current_cell = sboard.getCell(current_cell_name)
    current_value_set = current_cell.getValueSet()
    associated_cells = sboard.getAssociatedCells(current_cell_name)

    for associated_cell_name in associated_cells:
        associated_cell = sboard.getCell(associated_cell_name)
        associated_cell_value_set = associated_cell.getValueSet()
        intersection_value_set = current_value_set & associated_cell_value_set
        if (len(associated_cell_value_set) == num_values and
                len(intersection_value_set) > num_intersection_values):
            candidates.append(associated_cell)

    return candidates


def __find_ywings(sboard):
    """
    A y-wing forms when a "hinge" cell forms a conjugate pair with cells in
    two different units.  For example if cell 'A1' has the value 2 and 1, cell
    'B2' has the values 3 and 1, and cell 'A5' has the values 3 and 2, then we
    can elminate the value 3 from B5 or any other cell that is associated
    with B2 and A5.
    """
    found_ywing = False

    # iterate through all cells
    # the this cell will be the "hinge"
    for current_cell_name in sboard.getAllCells():

        pincer_candidates = []

        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # For ywing, all three cells can have only two values
        if len(current_value_set) == 2:
            # We look for cells associated with the
            # hinge that have only two values left
            pincer_candidates = __find_candidates(sboard, current_cell_name,
                                                  num_values=2,
                                                  num_intersection_values=0)

            # We iterate through all cells to find two candidates to be pincers
            for first_pincer_candidate in pincer_candidates:

                first_pincer_value_set = first_pincer_candidate.getValueSet()

                for second_pincer_candidate in pincer_candidates:

                    if first_pincer_candidate != second_pincer_candidate:
                        second_pincer_value_set = second_pincer_candidate.getValueSet()

                        first_pincer_associated_cells = \
                            sboard.getAssociatedCells(first_pincer_candidate)
                        second_pincer_associated_cells = \
                            sboard.getAssociatedCells(second_pincer_candidate)

                        # find the values that the two pincers have in common
                        candidate_intersection_value_set = (first_pincer_value_set &
                                                            second_pincer_value_set)

                        # find the cells associated with both pincers
                        associated_cells_intersection = (set(first_pincer_associated_cells) &
                                                         set(second_pincer_associated_cells))

                        # if the pincers have at least one associated cell in common
                        # and they have one value in common
                        if (len(associated_cells_intersection) > 0 and
                                len(candidate_intersection_value_set) == 1):

                            # And the hinge and the second pincer have at least one value in common
                            # the hinge also can't have the same value that the pincer's have in common
                            if(len(current_value_set & second_pincer_value_set) == 1
                                    and len(current_value_set & candidate_intersection_value_set) == 0):
                                # we've found a y-wing!
                                y_wing = [current_cell_name, first_pincer_candidate.getIdentifier(),
                                          second_pincer_candidate.getIdentifier()]

                                # The value common to the two pincer's is the one we can elminate
                                # From any cell that's common to both of them
                                exclusion_value = candidate_intersection_value_set.pop()
                                excluded_cells = []

                                # We iterate through the cells associated with both pincers
                                # we can exclude the value from these cells if they have it
                                for associated_cell_name in associated_cells_intersection:
                                    associated_cell = sboard.getCell(
                                        associated_cell_name)

                                    if (associated_cell.hasValue(exclusion_value) and
                                            associated_cell_name not in y_wing):
                                        found_ywing = True
                                        associated_cell.exclude(
                                            exclusion_value)
                                        excluded_cells.append(
                                            associated_cell_name)

                                if verbosity > 1 and len(excluded_cells) > 0:
                                    print('Y-WING', y_wing, 'excludes', str(exclusion_value), 'from',
                                          sorted(excluded_cells))

                                if found_ywing:
                                    sboard.log.logOperator(
                                        'ywings', sboard.getStateStr(True, False))
                                    return sboard

    return sboard


def __find_xyzwings(sboard):
    """
    This is an extension of Y-Wing. An xyz-wing forms when three cells that
    contain only 3 different numbers between them, but which fall outside the
    confines of one row/column/box, with t the hinge being able to see the other
    two; those other two having only one number in common; and the apex having
    all three numbers as candidates.  For example, if F9 has the values 1, 2,
    and 4, D9 has 1 and 2, and F1 has 1 and 4, we can eliminate 1 from F7.
    """
    found_xyz_wing = False

    # iterate through all cells. The current cell will be in the hinge.
    for current_cell_name in sboard.getAllCells():
        pincer_candidates = []

        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # the hinge can only have three values.
        if len(current_value_set) == 3:

            # the pincers can only have 2 values each.
            pincer_candidates = __find_candidates(sboard, current_cell_name,
                                                  num_values=2,
                                                  num_intersection_values=0)
        # iterate through the pincer candidates
        for first_pincer_candidate in pincer_candidates:
            first_pincer_value_set = first_pincer_candidate.getValueSet()

            for second_pincer_candidate in pincer_candidates:
                if second_pincer_candidate != first_pincer_candidate:
                    second_pincer_value_set = second_pincer_candidate.getValueSet()
                    candidate_intersection_set = (first_pincer_value_set &
                                                  second_pincer_value_set)

                    # the puncers have to have only 1 value in common
                    if len(candidate_intersection_set) == 1:

                        union_set = (current_value_set | first_pincer_value_set |
                                     second_pincer_value_set)

                        # the hinge and the two pincers can only have 3 values
                        # total
                        if len(union_set) == 3:
                            # we've found an xyz-wing!
                            xyz_wing = [current_cell_name,
                                        first_pincer_candidate.getIdentifier(),
                                        second_pincer_candidate.getIdentifier()]

                            # We can eliminate the value common to the xyz-wing
                            # from the cells that the cells forming the wing have
                            # in common
                            common_cells = sboard.getCommonCells(xyz_wing)
                            exclusion_set = current_value_set & candidate_intersection_set
                            exclusion_value = exclusion_set.pop()
                            excluded_cells = []

                            for cell_name in common_cells:
                                cell = sboard.getCell(cell_name)
                                if cell.hasValue(exclusion_value):
                                    found_xyz_wing = True
                                    excluded_cells.append(cell_name)
                                    cell.exclude(exclusion_value)
                            if verbosity > 1 and len(excluded_cells) > 0:
                                print('XYZ-WING', xyz_wing, 'excludes', str(exclusion_value),
                                      'from', sorted(excluded_cells))
                            if found_xyz_wing:
                                sboard.log.logOperator(
                                    'xyzwings', sboard.getStateStr(True, False))
                                return sboard
    return sboard


def find_wings(sboard, wing_type):
    """
    Applies requested *wing operator.

    Args:
        sboard  : the board to which the *wing operator will be applied
        wing_type   :  Specifies *wing operator type, options are:
            "x", "y", or "xyz"
    Returns:
        board   : sboard, updated to remove values identified with the *wing
            pattern from related cells

    An X-Wing ocurrs when there are only 2 candidates for a value in each of
    2 different units of the same kind and these candidates also lie on 2 other units
    of the same kind.  Then we can exclude this value from the latter two units.
    [TODO: include example]

    In a Y-wing, a "hinge" cell forms a conjugate pair with cells in
    two different units.  For example if cell 'A1' has the values 2 and 1, cell
    'B2' has the values 3 and 1, and cell 'A5' has the values 3 and 2, then we
    can elminate the value 3 from B5 or any other cell that is associated
    with B2 and A5.
    [TODO: define associated?]

    An XYZ-wing is an extension of Y-Wing in which three cells
    contain only 3 different numbers between them, but they fall outside the
    confines of one row/column/box, with t the hinge being able to see the other
    two; those other two having only one number in common; and the apex having
    all three numbers as candidates.  For example, if F9 has the values 1, 2,
    and 4, D9 has 1 and 2, and F1 has 1 and 4, we can eliminate 1 from F7.
    [TODO: clean explanation somewhat]
    """

    if wing_type == 'x':
        sboard = __find_xwings(sboard)
    if wing_type == 'y':
        sboard = __find_ywings(sboard)
    if wing_type == 'xyz':
        sboard = __find_xyzwings(sboard)

    return sboard


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
        if(verbosity > 1):
            print("Assigning %s=%s" % (str(bcell.getIdentifier()),
                                       str(bcell.getCertainValue())))
        expansion.append(b)

    return expansion


def expand_cell_with_assignment(sboard, cell_id, value):
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

    For each set of values that cell_id can take
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

    assigned = board.Board(sboard)
    bcell = assigned.getCell(cell_id)
    bcell.assign(value)
    if(verbosity > 1):
        print("Assigning %s=%s" % (str(bcell.getIdentifier()),
                                   str(bcell.getCertainValue())))
    expansion.append(assigned)

    removed = board.Board(sboard)
    bcell = removed.getCell(cell_id)
    bcell.exclude(value)
    if(verbosity > 1):
        print("Removing %s from %s, resulting in %s" % (str(bcell.getIdentifier()),
                                                        str(value),
                                                        str(bcell.getValueSet())))
    expansion.append(removed)

    return expansion
