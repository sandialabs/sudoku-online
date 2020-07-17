#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David Stracuzzi, Michael Darling, Shelley Leger
Sandia National Laboratories
February 25, 2020

Sudoku Board operators.
"""

import board
# from board import Cell
import config_data
import copy

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
    Iterate until there are no new single-value cells.
    See comments below for additional algorithmic details.
    """

    # get the list of cells with singleton value set
    num_exclusions = 0
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

                if(c is cell):
                    continue
                # if c is not the cell we are currently propagating
                # then remove cell_value from c's candidate set

                excluded = c.exclude(cell_value)

                # if c is now certain,
                # then add it to list of of constraints to propagate
                if(excluded):
                    num_exclusions += 1
                    if c.isCertain():
                        plist.append(c)
                        # TODO MAL Does exclusion trigger when values are removed as possibilities,
                        # or only when an assignment is made?
                        # Here, we assume the latter.
                        terminate = config_data.match_set_operation(
                            'exclusion',
                            f'Assigned {c_name} = {board.Cell.displayValue(c.getCertainValue())}',
                            sboard)
                        if terminate:
                            # Don't update metadata like cell.setPropagated since the operation
                            # may not have been completely executed
                            # Don't need to complete the operation since it's assumed that
                            # we're counting every matched set
                            return sboard
                    # This is where we would terminate on successful application,
                    # but exclude is the cheapest and easiest of all logical ops,
                    # so we have a little optimization by not terminating here.

        cell.setPropagated()

    if num_exclusions > 0:
        config_data.complete_operation(
            'exclusion', f'Removed {num_exclusions} possible values', sboard)

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
    num_inclusions = 0
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
                num_inclusions += 1
                assign_cell = cell_list[0]
                assign_cell.assign(value)
                terminate = config_data.match_set_operation(
                    'inclusion',
                    f'Assigned {assign_cell.getIdentifier()} = {board.Cell.displayValue(assign_cell.getCertainValue())}',
                    sboard)
                if terminate:
                    return sboard

    if num_inclusions > 0:
        config_data.complete_operation(
            'inclusion', f'Assigned {num_inclusions} cells', sboard)

    return sboard


def __hidden_set_exclusion(sboard, hidden_set, intersection_unit_list):
    """
    After a possible hidden set has been identified, this method
    verifies whether the candidates are indeed a hidden set and
    excludes the appropriate values.
    Returns the number of cells that were affected by the hidden set.
    """
    len_hidden_set = len(hidden_set)

    num_operated_cells = 0
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

        if len(remaining_value_set) != len_hidden_set:
            continue
        # if the the number of remaining values is equal to the number of
        # cells in the set, then we've found a hidden set!

        for cell in unit_cells:
            associated_cell = sboard.getCell(cell)
            associated_value_set = associated_cell.getValueSet()

            if associated_cell in hidden_set:
                continue

            remaining_value_set -= associated_value_set

            if len(remaining_value_set) != len_hidden_set:
                continue
            # we've found a hidden set!

            for cell in hidden_set:
                cell_name = cell.getIdentifier()
                value_set = cell.getValueSet()
                value_set_before_exclusion = value_set.copy()
                exclusion_list = list(value_set - remaining_value_set)

                for value in exclusion_list:
                    cell.exclude(value)

                if len(exclusion_list) > 0:
                    num_operated_cells += 1
                    progress = f'HIDDEN SET {cell_name}: {board.Cell.displayValues(value_set_before_exclusion)} -> {board.Cell.displayValues(value_set)}'
                    config_data.debug_operation(
                        f'hiddenset', progress, sboard)

    return num_operated_cells


def find_hidden_pairs(sboard):
    """
    A hidden pair is any group of two cells in the same unit
    that have 2 values between them that are not found in the
    rest of the cells in the unit.  Therefore we exclude all
    other values from the cells in the pair.
    """
    num_hidden_pairs = 0
    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        # these operators are useful only for cells with more than two values
        if len(current_cell.getValueSet()) <= 2:
            continue

        candidate_cells = __find_hidden_candidate_cells(sboard, current_cell)
        for candidate_cell in candidate_cells:
            candidate_cell_name = candidate_cell.getIdentifier()

            # get units that the pair have in common
            intersection_unit_list = sboard.getCommonUnits([current_cell_name,
                                                            candidate_cell_name])

            hidden_set = [current_cell, candidate_cell]
            num_cells_affected = __hidden_set_exclusion(
                sboard, hidden_set, intersection_unit_list)
            if num_cells_affected:
                num_hidden_pairs += 1
                progress = f'HIDDEN PAIR of {sorted([cell.getIdentifier() for cell in hidden_set])} excluded values from {num_cells_affected} cells'
                terminate = config_data.match_set_operation(
                    f'hiddenpairs', progress, sboard)
                if terminate:
                    return sboard

    if num_hidden_pairs > 0:
        config_data.complete_operation(
            'hiddenpairs', f'Found {num_hidden_pairs} hidden pairs that affected board.', sboard)
    return sboard


def find_hidden_triples(sboard):
    """
    A hidden triple is any group of three cells in the same unit
    that have 3 values between them that are not found in the
    rest of the cells in the unit.  Therefore we exclude all
    other values from the cells in the triple.
    """
    num_hidden_triples = 0
    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # these operators are useful only for cells with more than two values
        if len(current_value_set) <= 2:
            continue

        # the list of cells associated with the current cell
        current_units = sboard.getCellUnits(current_cell_name)

        candidate_cells = __find_hidden_candidate_cells(sboard, current_cell)
        for first_candidate_cell in candidate_cells:
            first_candidate_value_set = first_candidate_cell.getValueSet()

            if len(current_value_set & first_candidate_value_set) < 2:
                continue
            # cells have to have at least 2 values in common

            for second_candidate_cell in candidate_cells:
                if second_candidate_cell == first_candidate_cell:
                    continue

                first_candidate_name = first_candidate_cell.getIdentifier()
                first_candidate_units = sboard.getCellUnits(
                    first_candidate_name)

                second_candidate_name = second_candidate_cell.getIdentifier()
                second_candidate_value_set = second_candidate_cell.getValueSet()

                candidates_intersection_value_set = (second_candidate_value_set &
                                                     first_candidate_value_set)
                # if the first and second candidates are a pair, also,
                # we check if the value set across the three cells is greater than 4, # MAL TODO Why 4 vs 3?
                # otherwise we probably have a naked triple
                if (len(candidates_intersection_value_set) == 0
                    or len(current_value_set
                           | first_candidate_value_set
                           | second_candidate_value_set) <= 4):
                    continue

                second_candidate_units = sboard.getCellUnits(
                    second_candidate_name)

                # check to see if all three candidates have at least one common unit
                intersection_unit_list = list(set(current_units) &
                                              set(first_candidate_units) &
                                              set(second_candidate_units))

                if len(intersection_unit_list) > 0:
                    hidden_set = [
                        current_cell, first_candidate_cell, second_candidate_cell]
                    num_cells_affected = __hidden_set_exclusion(
                        sboard, hidden_set, intersection_unit_list)
                    if num_cells_affected:
                        num_hidden_triples += 1
                        progress = f'HIDDEN TRIPLE of {sorted([cell.getIdentifier() for cell in hidden_set])} excluded values from {num_cells_affected} cells'
                        terminate = config_data.match_set_operation(
                            f'hiddentriples', progress, sboard)
                        if terminate:
                            return sboard

    if num_hidden_triples > 0:
        config_data.complete_operation(
            'hiddentriples', f'Found {num_hidden_triples} hidden triples that affected board.', sboard)
    return sboard


def find_hidden_quads(sboard):
    """
    A hidden quad is any group of four cells in the same unit
    that have 4 values between them that are not found in the
    rest of the cells in the unit.  Therefore we exclude all
    other values from the cells in the quad.
    """
    num_hidden_quads = 0
    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # these operators are useful only for cells with more than two values
        if len(current_value_set) <= 2:
            continue

        # the list of cells associated with the current cell
        current_units = sboard.getCellUnits(current_cell_name)

        candidate_cells = __find_hidden_candidate_cells(sboard, current_cell)
        for first_candidate_cell in candidate_cells:
            first_candidate_value_set = first_candidate_cell.getValueSet()
            intersection_value_set = current_value_set & first_candidate_value_set

            # cells have to have at least 2 values in common
            if len(intersection_value_set) < 2:
                continue

            for second_candidate_cell in candidate_cells:
                if second_candidate_cell == first_candidate_cell:
                    continue

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
                if (len(intersection_value_set) == 0
                    or len(current_value_set
                           | first_candidate_value_set
                           | second_candidate_value_set) <= 4):
                    continue

                second_candidate_units = sboard.getCellUnits(
                    second_candidate_name)

                # check to see if all three candidates have at least one common unit
                intersection_unit_set = (set(current_units) &
                                         set(first_candidate_units) &
                                         set(second_candidate_units))

                if len(intersection_unit_set) == 0:
                    continue

                candidates = [current_cell, first_candidate_cell,
                              second_candidate_cell]

                for third_candidate_cell in candidate_cells:
                    if third_candidate_cell in candidates:
                        continue

                    candidates.append(third_candidate_cell)
                    third_candidate_value_set = third_candidate_cell.getValueSet()
                    third_candidate_name = third_candidate_cell.getIdentifier()
                    third_candidate_units = sboard.getCellUnits(
                        third_candidate_name)
                    intersection_unit_set = (intersection_unit_set &
                                             set(third_candidate_units))

                    intersection_value_set = (second_candidate_value_set &
                                              third_candidate_value_set)

                    if (len(intersection_value_set) > 1 and
                            len(intersection_unit_set) > 0):
                        num_cells_affected = __hidden_set_exclusion(
                            sboard, candidates, list(intersection_unit_set))
                        if num_cells_affected:
                            num_hidden_quads += 1
                            progress = f'HIDDEN QUAD of {sorted([cell.getIdentifier() for cell in candidates])} excluded values from {num_cells_affected} cells'
                            terminate = config_data.match_set_operation(
                                f'hiddenquads', progress, sboard)
                            if terminate:
                                return sboard

    if num_hidden_quads > 0:
        config_data.complete_operation(
            'hiddenquads', f'Found {num_hidden_quads} hidden quads that affected board.', sboard)
    return sboard


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


def __naked_set_exclusion(sboard, naked_set, exclusion_values):
    """
    After naked set is identified, this function elminates
    the set's values from all other cells in the set's
    common units.
    """
    num_operated_cells = 0

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

        if len(exclusion_list) > 0:
            num_operated_cells += 1
            progress = f'NAKED SET removes {board.Cell.displayValues(exclusion_list)} from {non_pair_cell_name}'
            config_data.debug_operation(f'nakedset', progress, sboard)

    return num_operated_cells


def find_naked_pairs(sboard):
    """
    A Naked Pair is two cells in the same unit with the same two values remaining.

    Search board for a pair of two cells situated in the
    same unit with the same value set with only two
    values remaining. Remove these two values from all
    cells associated with the pair.
    """
    num_naked_pairs = 0
    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # looking only for cells with two remaining values
        if len(current_value_set) != 2:
            continue

        candidate_cells = __find_naked_candidate_cells(sboard, current_cell)

        # Now we iterate through the candidates
        for first_candidate_cell in candidate_cells:
            first_candidate_value_set = first_candidate_cell.getValueSet()

            # Look for naked pair
            if current_value_set != first_candidate_value_set:
                continue

            # We found a naked pair!
            # print(current_cell, first_candidate_cell)
            naked_set = [current_cell_name,
                         first_candidate_cell.getIdentifier()]
            num_cells_affected = __naked_set_exclusion(
                sboard, naked_set, current_value_set)
            if num_cells_affected:
                num_naked_pairs += 1
                progress = f'NAKED PAIR of {naked_set} excluded values from {num_cells_affected} cells'
                terminate = config_data.match_set_operation(
                    f'nakedpairs', progress, sboard)
                if terminate:
                    return sboard

    if num_naked_pairs > 0:
        config_data.complete_operation(
            'nakedpairs', f'Found {num_naked_pairs} naked pairs that affected board.', sboard)
    return sboard


def find_naked_triples(sboard):
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

    num_naked_triples = 0
    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # looking only for cells with two to three remaining values
        if len(current_value_set) < 2 or len(current_value_set) > 3:
            continue

        candidate_cells = __find_naked_candidate_cells(
            sboard, current_cell)

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

                if(second_candidate_cell == first_candidate_cell
                    or len(first_candidate_unit_set
                           & second_candidate_unit_set) == 0):
                    continue
                # if the second candidate is not the same as the first and
                # they have a common unit

                second_candidate_value_set = second_candidate_cell.getValueSet()

                # naked triple forms if the three cells have 3 values left amongst them
                union_values = (current_value_set | first_candidate_value_set |
                                second_candidate_value_set)
                if len(union_values) != 3:
                    continue

                # we've found a naked triple!
                naked_set = [current_cell_name,
                             first_candidate_name, second_candidate_name]
                num_cells_affected = __naked_set_exclusion(
                    sboard, naked_set, union_values)
                if num_cells_affected:
                    num_naked_triples += 1
                    progress = f'NAKED TRIPLE of {naked_set} excluded values from {num_cells_affected} cells'
                    terminate = config_data.match_set_operation(
                        f'nakedtriples', progress, sboard)
                    if terminate:
                        return sboard

    if num_naked_triples > 0:
        config_data.complete_operation(
            'nakedtriples', f'Found {num_naked_triples} naked triples that affected board.', sboard)
    return sboard


def find_naked_quads(sboard):
    """
    A Naked quad is any group of four cells in the same unit
    that contain IN TOTAL 4 values.  Therefore we can exclude
    these four values from all other cells in the unit.
    """
    num_naked_quads = 0
    # iterate through every cell in the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        current_value_set = current_cell.getValueSet()

        # looking only for cells with two to four remaining values
        if len(current_value_set) < 2 or len(current_value_set) > 4:
            continue

        candidate_cells = __find_naked_candidate_cells(sboard, current_cell)

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
                if(second_candidate_cell == first_candidate_cell
                   or len(first_candidate_unit_set & second_candidate_unit_set) == 0):
                    continue

                for third_candidate_cell in candidate_cells:
                    third_candidate_name = third_candidate_cell.getIdentifier()
                    third_candidate_unit_set = set(
                        sboard.getCellUnits(third_candidate_name))

                    # if the third candidate is not the same as the first and second
                    # and all three have acommon unit
                    if(third_candidate_cell == first_candidate_cell
                            or third_candidate_cell == second_candidate_cell
                            or len(first_candidate_unit_set
                                   & second_candidate_unit_set
                                   & third_candidate_unit_set) == 0):
                        continue

                    first_candidate_value_set = first_candidate_cell.getValueSet()
                    second_candidate_value_set = second_candidate_cell.getValueSet()
                    third_candidate_value_set = third_candidate_cell.getValueSet()

                    # naked quad forms if the three cells have
                    # 4 values left amongst them
                    union_values = (current_value_set | first_candidate_value_set |
                                    second_candidate_value_set |
                                    third_candidate_value_set)
                    if len(union_values) != 4:
                        continue

                    # we've found a naked quad!
                    naked_set = [current_cell_name, first_candidate_name,
                                 second_candidate_name, third_candidate_name]
                    num_cells_affected = __naked_set_exclusion(
                        sboard, naked_set, union_values)
                    if num_cells_affected:
                        num_naked_quads += 1
                        progress = f'NAKED QUAD of {naked_set} excluded values from {num_cells_affected} cells'
                        terminate = config_data.match_set_operation(
                            f'nakedquads', progress, sboard)
                        if terminate:
                            return sboard

    if num_naked_quads > 0:
        config_data.complete_operation(
            'nakedquads', f'Found {num_naked_quads} naked quads that affected board.', sboard)
    return sboard


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
    num_operated_cells = 0
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
    if len(intersection_unit_set) < 2:
        # A pointing set has to share two units
        return 0
    # progress = f'POINTING SET {candidate_names}: {sorted(intersection_unit_set)} shares {board.Cell.displayValues(intersection_value_set)}'
    # config_data.debug_operation(f'pointingset', progress, sboard)

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

        # If there're any values left, they are only common
        # to the candidates. Therefore, we can remove these values
        # from the cells in the other unit common to the candidates.
        if len(remaining_value_set) == 0:
            continue

        other_units = intersection_unit_set - set(unit)
        for other_unit in other_units:
            other_unit_cells = sboard.getUnitCells(other_unit)

            # If any of these cells have the pointing set's value,
            # we can exlcude it.
            for cell_name in other_unit_cells:
                cell = sboard.getCell(cell_name)
                if cell in candidates:
                    continue

                excluded_something = False
                for value in remaining_value_set:
                    excluded_something |= cell.exclude(value)
                if excluded_something:
                    num_operated_cells += 1
                    progress = f'POINTING SET {candidate_names}: removed values in {board.Cell.displayValues(remaining_value_set)} from {cell.getIdentifier()}'
                    config_data.debug_operation(
                        f'pointingset', progress, sboard)

    return num_operated_cells


def find_pointing_pairs(sboard):
    """
    Applies pointing pairs operator.

    Args:
        sboard  : the board to which the pointing candidates operator will be applied
    Returns:
        board   : sboard, updated to remove values identified as pointing sets
            from related cells

    If any one value is present only two times in just one unit,
    and that pair is aligned within another unit,
    then we can remove that number from the intersection of another unit.
    There are four types of intersections:
        1. A value in a pair in a box aligned on a row
            can be removed from the rest of the row.
        2. A value in a pair in a box aligned on a column
            can be removed from the rest of the column.
        3. A value in a pair in a row in the same box as each other
            can be removed from the rest of the box.
        4. A value in a pair in a column in the same box as each other
            can be removed from the rest of the box.
    """
    return __find_pointing_candidates(sboard, "pairs")


def find_pointing_triples(sboard):
    """
    Applies pointing triples operator.

    Args:
        sboard  : the board to which the pointing candidates operator will be applied
    Returns:
        board   : sboard, updated to remove values identified as pointing sets
            from related cells

    If any one value is present only three times in just one unit,
    and that triple is aligned within another unit,
    then we can remove that number from the intersection of another unit.
    There are four types of intersections:
        1. A value in a triple in a box aligned on a row
            can be removed from the rest of the row.
        2. A value in a triple in a box aligned on a column
            can be removed from the rest of the column.
        3. A value in a triple in a row in the same box as each other
            can be removed from the rest of the box.
        4. A value in a triple in a column in the same box as each other
            can be removed from the rest of the box.
    """
    return __find_pointing_candidates(sboard, "triples")


def __find_pointing_candidates(sboard, set_type):
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
    num_pointing_pairs = 0
    num_pointing_triples = 0

    # iterate through all cells on the board
    for current_cell_name in sboard.getAllCells():
        current_cell = sboard.getCell(current_cell_name)
        # no point in operator if cell is already certain
        if current_cell.isCertain():
            continue

        # candidate are cells that have at least one
        # value in common with the current cell
        candidate_cells = __find_pointing_candidate_cells(
            sboard, current_cell)
        candidates = []
        for first_candidate_cell in candidate_cells:
            candidates = [current_cell, first_candidate_cell]
            # check to see if the two cells constitute a pointing pair
            if set_type == 'pairs':
                num_cells_affected = __is_pointing_set(sboard, candidates)
                if num_cells_affected:
                    num_pointing_pairs += 1
                    progress = f'POINTING PAIR of {sorted([cell.getIdentifier() for cell in candidates])} excluded values from {num_cells_affected} cells'
                    terminate = config_data.match_set_operation(
                        f'pointingpairs', progress, sboard)
                    if terminate:
                        return sboard
                # We're doing pairs, so there's no need to continue onwards to triples
                continue

            assert set_type == 'triples', f'Only support pointing pairs and pointing triples, not {set_type}'
            for second_candidate_cell in candidate_cells:
                if second_candidate_cell in candidates:
                    continue

                current_units = sboard.getCellUnits(current_cell_name)
                current_value_set = current_cell.getValueSet()
                first_candidate_units = sboard.getCellUnits(
                    first_candidate_cell.getIdentifier())
                first_candidate_value_set = first_candidate_cell.getValueSet()
                second_candidate_units = sboard.getCellUnits(
                    second_candidate_cell.getIdentifier())
                second_candidate_value_set = second_candidate_cell.getValueSet()

                # check if all three cells have at least one value in common
                # also check if the all three cell have a common unit
                if(len(current_value_set & first_candidate_value_set &
                        second_candidate_value_set) == 0 or
                    len(set(current_units) & set(first_candidate_units) &
                        set(second_candidate_units)) == 0):
                    continue

                candidates = [current_cell,
                              first_candidate_cell, second_candidate_cell]

                # check if the three cells consistitute a pointing triple
                num_cells_affected = __is_pointing_set(sboard, candidates)
                if num_cells_affected:
                    num_pointing_triples += 1
                    progress = f'POINTING TRIPLE of {sorted([cell.getIdentifier() for cell in candidates])} excluded values from {num_cells_affected} cells'
                    terminate = config_data.match_set_operation(
                        f'pointingtriples', progress, sboard)
                    if terminate:
                        return sboard

    if num_pointing_pairs:
        config_data.complete_operation(
            'pointingpairs', f'Found {num_pointing_pairs} pointing pairs that affected board.', sboard)
    elif num_pointing_triples:
        config_data.complete_operation(
            'pointingtriples', f'Found {num_pointing_triples} pointing triples that affected board.', sboard)
    return sboard


def find_xwings(sboard):
    """
    An X-Wing ocurrs when there are only 2 candidates for a value in each of
    2 different units of the same kind and these candidates also lie on 2 other units
    of the same kind.  Then we can exclude this value from the latter two units.
    """
    units_and_twice_occurring_values = []
    num_xwings = 0

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
                units_and_twice_occurring_values.append(
                    (unit, value, cells_containing_value))

    # We iterate through all the units which have a value present only twice
    for (current_unit, current_value, current_cells_containing_value) \
            in units_and_twice_occurring_values:

        # We look for a second unit containing only two of a value
        for (second_unit, second_value, second_cells_containing_value) \
                in units_and_twice_occurring_values:
            if current_unit == second_unit and current_value == second_value:
                continue
            current_unit_type = sboard.getUnitType(current_unit)
            second_unit_type = sboard.getUnitType(second_unit)

            # if the two units contain the same value only twice each and
            # are of the same type, we may have an x-wing
            if second_value == current_value and second_unit_type == current_unit_type:
                candidates = current_cells_containing_value + \
                    second_cells_containing_value
                first_intersection_unit_list = list((set(sboard.getCellUnits(candidates[0])) &
                                                     set(sboard.getCellUnits(candidates[2]))))
                second_intersection_unit_list = list((set(sboard.getCellUnits(candidates[1])) &
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
                        num_xwings += 1
                        progress = f'X-WING {candidates} excludes {board.Cell.displayValue(exclusion_value)} from {sorted(excluded_cells)}'
                        terminate = config_data.match_set_operation(
                            'xwings', progress, sboard)
                        if terminate:
                            return sboard

    if num_xwings > 0:
        config_data.complete_operation(
            'xwings', f'Discovered {num_xwings} that affected the board', sboard)
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


def find_ywings(sboard):
    """
    A y-wing forms when a "hinge" cell forms a conjugate pair with cells in
    two different units.  For example if cell 'A1' has the value 2 and 1, cell
    'B2' has the values 3 and 1, and cell 'A5' has the values 3 and 2, then we
    can elminate the value 3 from B5 or any other cell that is associated
    with B2 and A5.
    """
    num_ywings = 0
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
                    if first_pincer_candidate == second_pincer_candidate:
                        continue

                    second_pincer_value_set = second_pincer_candidate.getValueSet()

                    first_pincer_associated_cells = sboard.getAssociatedCells(
                        first_pincer_candidate)
                    second_pincer_associated_cells = sboard.getAssociatedCells(
                        second_pincer_candidate)

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
                                    excluded_something = associated_cell.exclude(
                                        exclusion_value)
                                    assert excluded_something, 'Surprisingly, we didn\'t find a value in ywings that worked.'
                                    excluded_cells.append(associated_cell_name)

                            if len(excluded_cells) > 0:
                                num_ywings += 1
                                progress = f'Y-WING {y_wing} excludes {board.Cell.displayValue(exclusion_value)} from {sorted(excluded_cells)}'
                                terminate = config_data.match_set_operation(
                                    'ywings', progress, sboard)
                                if terminate:
                                    return sboard

    if num_ywings > 0:
        config_data.complete_operation(
            'ywings', f'Discovered {num_ywings} that affected the board', sboard)
    return sboard


def find_xyzwings(sboard):
    """
    This is an extension of Y-Wing. An xyz-wing forms when three cells that
    contain only 3 different numbers between them, but which fall outside the
    confines of one row/column/box, with t the hinge being able to see the other
    two; those other two having only one number in common; and the apex having
    all three numbers as candidates.  For example, if F9 has the values 1, 2,
    and 4, D9 has 1 and 2, and F1 has 1 and 4, we can eliminate 1 from F7.
    """
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
                                    excluded_cells.append(cell_name)
                                    cell.exclude(exclusion_value)

                            if len(excluded_cells) > 0:
                                progress = f'XYZ-WING {xyz_wing} excludes {board.Cell.displayValue(exclusion_value)} from {sorted(excluded_cells)}'
                                config_data.match_set_operation(
                                    'xyzwings', progress, sboard)
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
        expansion.append(b)

        progress = f'Assigning {str(bcell.getIdentifier())} = {board.Cell.displayValue(bcell.getCertainValue())}'
        config_data.match_set_operation('pivot', progress, sboard)

    progress = f'Pivoted on {str(bcell.getIdentifier())} for {len(expansion)} new (unvalidated) boards'
    config_data.complete_operation('pivot', progress, sboard)

    return expansion


def expand_cell_with_assignment(sboard, cell_id, value):
    """
    Expands the board cell identified by cell_id into a board with that value assigned,
    and a board with that value excluded (and marked as backup).

    Args:
        sboard  : the starting board to "expand"
        cell_id : the identifier of the cell to expand
        value : a value to assign to cell_id,
            intersecting those values with valid values
    Returns:
        collection of board  : new boards.  Each board is a copy of sboard
            except that in the first board cell_id is set to value
            and in the second (backup) board cell_id contains the remaining values.
    NOTE: propagation of the assigned value is not performed automatically.
    """
    return __expand_cell_with_assignment(sboard, cell_id, value, False)


def expand_cell_with_exclusion(sboard, cell_id, value):
    """
    Expands the board cell identified by cell_id into a board with that value excluded,
    and a board with that value excluded (and marked as backup).

    Args:
        sboard  : the starting board to "expand"
        cell_id : the identifier of the cell to expand
        value : a value to assign to cell_id,
            intersecting those values with valid values
    Returns:
        collection of board  : new boards.  Each board is a copy of sboard
            except that in the first board cell_id contains the remaining values
            and in the second (backup) board cell_id is set to value.
    NOTE: propagation of the assigned value is not performed automatically.
    """
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
    config_data.match_set_operation(action, progress, sboard)

    bcell = removed.getCell(cell_id)
    bcell.exclude(value)
    progress = f'Removing {board.Cell.displayValue(value)} from {str(bcell.getIdentifier())}, resulting in {board.Cell.displayValues(bcell.getValueSet())}'
    config_data.match_set_operation(action, progress, sboard)

    progress = f'Performed {action} on {str(bcell.getIdentifier())} with {board.Cell.displayValue(value)} for {len(expansion)} new (unvalidated) boards'
    config_data.complete_operation(action, progress, sboard)

    return expansion
