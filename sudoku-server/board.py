#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David Stracuzzi, Michael Darling, Michelle Leger
Sandia National Laboratories
December 12, 2019

Sudoku Board and Cell data structures.
"""

import logger
# import json
import uuid


class Cell():
    """
    A single cell on a Sudoku board.
    Each cell tracks and provides manipulation for the set of
    candidate values that the Cell may take.
    """

    value_set = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

    def __init__(self, identifier, value='.', degree=3):
        """ Initializes a Cell with an identifier and valueset or another cell.

        Args:
            identifier   : a string identifier within a board (value expected),
                            or a cell to copy
            value        : the set of potential values, or '.' for complete value set
            degree (int) : the number of blocks on a side (determines values)
        Returns:
            Cell   : a new cell.

        Identifier parameter must be either a string or a Cell.
        NOTE: the value set is copied via set.copy(), which is fine for
              ints and strs, but won't work if the values become some other
              complex object type.
        """
        if isinstance(identifier, Cell):
            #  If identifier is a Cell, make a copy
            self._id = identifier._id
            assert isinstance(self._id, str), "Cell's id should be a string"
            self._propagated = identifier._propagated
            # TODO: MAL: Michael, what is propagated for?
            assert isinstance(self._propagated, bool), "Cell's _propagated should be a boolean"
            self._values = identifier._values.copy()
            assert isinstance(self._values, set), "Cell's values should be a set"
            self._degree = identifier._degree
        else:
            # If identifier is a unique ID (str or int)
            self._id = identifier
            self._propagated = False
            self._degree = degree
            # TODO MAL come back to this as it will cause problems integrating with Andy
            if (value == '0' or value == '.'):
                # Collect those values up to degree^2
                # Slicing should automatically copy it
                self._values = Cell.getPossibleValueSet(degree)
            else:
                self._values = set(value)

    @classmethod
    def getNumPossibleValues(cls, degree=3):
        """ Returns the number of possible values: degee ^ 2
        """
        return degree ** 2

    @classmethod
    def getPossibleValues(cls, degree=3):
        """ Returns sorted list of all possible values for puzzle of degree.
        """
        try:
            return cls.value_set[:cls.getNumPossibleValues(degree)]
        except TypeError:
            assert False, "Cell's degree must be square-able (**2)"

    @classmethod
    def getPossibleValueSet(cls, degree=3):
        """ Returns set of all possible values for puzzle of degree.
        """
        return set(cls.getPossibleValues(degree))

    def __str__(self):
        return 'Cell(ID=' + str(self._id) + \
               ', Propagated=' + str(self._propagated) + \
               ', ValueSet={' + self.getStateStr(True) + '})'

    def assign(self, value):
        """
        Assigns value to self, removing all other candidates.

        Args:
            value   : the only value this cell can take on
        Returns:
            boolean : True if otherh values were eliminated by this assignment
                      False if no cell update occurred
        Raises:
            AssertionError  : if value was not a valid possibility
        """
        # TODO Is this assertion a problem?
        assert value in self._values, \
            "Cannot assign %s to Cell %s" % (str(value), str(self.getIdentifier))
        if len(self._values) > 1:
            self._values = {value}
            return True
        return False

    def exclude(self, value):
        """
        Remove value from self's set of candidate values.
        Return True if the value was present, False otherwise.
        """
        try:
            self._values.remove(value)
            return True
        except KeyError:
            return False

    def getCertainValue(self):
        """
        If cell has only one candidate value, return it
        Otherwise return None
        """

        if(len(self._values) == 1):
            return list(self._values)[0]
        return None

    def getIdentifier(self):
        """ Return identifier for self. """
        return self._id

    def getStateStr(self, uncertain=False):
        """
        If uncertain is False, then return value if Cell is certain
                               otherwise return '.'
        If uncertain is True, return the value set as a string
        """
        width = Cell.getNumPossibleValues(self._degree) + 1
        if(uncertain):
            s = sorted(self.getValueSet())
            if not s:
                # Underconstrained: highlight a conflict
                return str.center('!', width)
            return str.center(''.join(s), width)
        elif(len(self._values) == 1):
            return list(self._values)[0] + ' '
        else:
            return '. '

    def getValueSet(self):
        """ Return set of current possible values. """
        return self._values

    def hasValue(self, value):
        """ Return True iff value is possible in this Cell. """
        return value in self._values

    def isCertain(self):
        """ Return True iff this Cell has only one possible value. """
        return len(self._values) == 1

    def isOverConstrained(self):
        """ Return True iff this Cell has no possible values remaining. """
        return len(self._values) == 0

    def isPropagated(self):
        return self._propagated

    def setPropagated(self):
        self._propagated = True

# -----------------------------------------------------


class Board():
    """
    A single Sudoku board that maintains the current uncertainty state.
    A Board is an associative memory of cells indexed by location
    (e.g. A1, D3, etc.)
    Boards merely maintain state and answer questions about the state,
    see Unit and Solver for manipulation methods.
    """

    unit_defns = {}
    unit_map = {}

    @classmethod
    def getCellUnits(cls, cell_id, degree=3):
        """ Return units associated with cell_id in a puzzle of degree.

        cell_id may be a string or a Cell.
        """
        if not isinstance(cell_id, str):
            cell_id = cell_id.getIdentifier()
        return cls.unit_map[degree][cell_id]

    @classmethod
    def getUnitCells(cls, unit_id, degree=3):
        """ Return cells associated with unit_id in a puzzle of degree. """
        return cls.unit_defns[degree][unit_id]

    @classmethod
    def getAllCells(cls, degree=3):
        """ Get all cell names in a puzzle of degree. """
        return cls.unit_map[degree].keys()

    @classmethod
    def getAllUnits(cls, degree=3):
        """ Get all unit names in a puzzle of degree. """
        return cls.unit_defns[degree].keys()

    @classmethod
    def getSortedRows(cls, degree=3):
        """ Get all unit names in a puzzle of degree. """
        return sorted([name for name in filter(lambda x : cls.getUnitType(x) == 'row',
                                               cls.unit_defns[degree].keys())])

    @classmethod
    def getUnitType(cls, unit):
        """ Get the type of the unit.

        Note: previously we kept collections identifying the unit names,
            which was cleaner, but for now we're relying on the
            encoding in the unit name.
        """
        if unit[0] == 'c':
            return 'column'
        elif unit[0] == 'r':
            return 'row'
        elif unit[0] == 'b':
            return 'box'
        else:
            return 'Invalid Input'

    @classmethod
    def getAssociatedCells(cls, cell_id):
        """
        Get all cells in units associated with
        target cell, without repeats.
        """
        associated_units = cls.getCellUnits(cell_id)
        associated_cells = []
        for unit_id in associated_units:
            unit_cells = cls.getUnitCells(unit_id)
            for unit_cell in unit_cells:
                if unit_cell not in associated_cells and unit_cell != cell_id:
                    associated_cells.append(unit_cell)
        return associated_cells

    @classmethod
    def getCommonCells(cls, cell_id_list):
        """
        Get list of all cells jointly associated
        to all cells in the list
        """
        common_cell_set = set(cls.getAssociatedCells(cell_id_list[0]))

        for cell_id in cell_id_list:
            common_cell_set = common_cell_set & set(cls.getAssociatedCells(cell_id))

        return list(common_cell_set)

    @classmethod
    def getCommonUnits(cls, cell_id_list):
        """
        Get list of all units jointly associated
        to all cells in the list
        """
        common_unit_set = set(cls.getCellUnits(cell_id_list[0]))

        for cell_id in cell_id_list:
            common_unit_set = common_unit_set & set(cls.getCellUnits(cell_id))

        return list(common_unit_set)

    @classmethod
    def getUnionUnitSet(cls, cell_id_list):
        """
        Get union set of units for the given cells
        """
        union_unit_set = set(cls.getCellUnits(cell_id_list[0]))

        for cell_id in cell_id_list:
            union_unit_set = union_unit_set | set(cls.getCellUnits(cell_id))

        return union_unit_set

    @classmethod
    def getCellID(cls, row, col):
        """ Returns cell identifier given row and column identifier strings. """
        r = row[1]
        c = col[1:]
        return r + c

    @classmethod
    def getCellIDFromArrayIndex(cls, row, col):
        """ Returns cell identifier given row and column integer. """
        rnm = cls._rname(row)
        cnm = cls._cname(col)
        return cls.getCellID(rnm, cnm)

    @classmethod
    def getBoxID(cls, row, col, deg):
        """ Returns box identifier given row and column identifier and puzzle degree. """
        r = row[1]
        c = col[1:]
        # 1. Convert r back to int past 0 ('A' is 1)
        # 2. Bump up to next round for divide to work nicely (+ deg -1)
        box_off = int((int(c) + deg - 1) / deg)
        box_base = (int((ord(r) - 64 + deg - 1) / deg) - 1) * deg
        return 'b' + str(box_base + box_off)

    @classmethod
    def getLocations(cls, id, deg):
        """ Returns the row, column location of cell id as ints
        in a puzzle of degree deg.
        TODO: Currently assumes id is of the form "rc[c]"
        """
        r = ord(id[0])-64
        c = int(id[1:])
        return (r, c)

    @classmethod
    def _cname(cls, idx):
        # Start counting from 'c1'
        return 'c' + str(idx+1)

    @classmethod
    def _rname(cls, idx):
        # Start counting from 'rA'
        return 'r' + chr(65 + idx)

    @classmethod
    def _bname(cls, idx):
        # Start counting from 'b1'
        return 'b' + str(idx+1)

    @classmethod
    def initialize(cls, degree):
        """
        Initialize the unit definitions (mapping of unit names to cell names)
        and the unit map (mapping of cell names to unit names).

        Unit defns initially contains the NxN boxes.  This method adds the
        rows and columns and then creates the unit map by inverting the
        unit defns.
        """
        for degree in [degree]: #range(2, 4):
            width = degree ** 2

            # Map from each unit to cell names in that unit
            cls.unit_defns[degree] = {}
            for idx in range(width):
                # Unique names for each unit
                cls.unit_defns[degree][cls._cname(idx)] = []
                cls.unit_defns[degree][cls._rname(idx)] = []
                cls.unit_defns[degree][cls._bname(idx)] = []
            # Now populate each unit with cells
            for row in [cls._rname(idx) for idx in range(width)]:
                for col in [cls._cname(idx) for idx in range(width)]:
                    cell_id = cls.getCellID(row, col)
                    box_id = cls.getBoxID(row, col, degree)
                    cls.unit_defns[degree][row].append(cell_id)
                    cls.unit_defns[degree][col].append(cell_id)
                    cls.unit_defns[degree][box_id].append(cell_id)

            # Map from each cell to names of units it appears in
            cls.unit_map[degree] = {}
            for unit, cell_list in cls.unit_defns[degree].items():
                for cell in cell_list:
                    if(cell in cls.unit_map[degree]):
                        cls.unit_map[degree][cell].append(unit)
                    else:
                        cls.unit_map[degree][cell] = [unit]

    def __init__(self, state=['.' for i in range(0, 81)], degree=3):
        """
        Initialize a board for a puzzle of degree with the given state.
        State parameter can be a string, a json, or a Board to copy.
        """
        # MAL TODO Make sure the class was initialized before we started
        try:
            Board.unit_map[degree]
        except KeyError:
            Board.initialize(degree)

        self._state = dict()
        # Generate a UID integer from uuid1.  These bits are largely dependent on clock
        # (though it's been pointed out that they might leak a little information about MAC address)
        self._id = uuid.uuid1().int >> 64
        if isinstance(state, Board):
            # State is a Board; copy it, but keep the new identifier
            for cell in state.getCells():
                self._state[cell.getIdentifier()] = Cell(cell)
            self._degree = state.getDegree()
        elif isinstance(state, dict):
            # State was parsed from json; keep the same identifier and update fields appropriately
            # board_dict = json.loads(board_json)
            assignments = [item for row in state['assignments'] for item in row]
            options = [item for row in state['availableMoves'] for item in row]
            self._id = state['serialNumber']
            self._degree = state['degree']
            # Initialize cell state
            i = 0
            for identifier in sorted(Board.getAllCells(degree)):
                cell_state = assignments[i] if assignments[i] else options[i]
                self._state[identifier] = Cell(identifier, cell_state)
                i += 1
        else:
            # State is a str; initialize it
            i = 0
            for identifier in sorted(Board.getAllCells(degree)):
                self._state[identifier] = Cell(identifier, state[i])
                i += 1
            self._degree = degree

        Board.log = logger.SudokuLogger(state)

    def __str__(self):
        output = "Board State:\n"
        output += self.getStateStr(True)

        output += '\nCells:\n'
        for key in self._state:
            output += str(self._state[key]) + '\n'

        return output

    def getDegree(self):
        """ Returns the degree of this puzzle board. """
        return self._degree

    def getIdentifier(self):
        """ Returns the identifier of this puzzle board. """
        return self._id

    def countUncertainValues(self):
        n = 0

        for cell in self.getCells():
            if(not cell.isCertain()):
                n += len(cell.getValueSet())

        return n

    def getValueCountAndCells(self, unit_name, value):
        """
        counts number of times a value is present in a unit
        """
        value_count = 0
        cells_with_value = []
        if type(value) == int:
            value = str(value)
        for cell_name in self.getUnitCells(unit_name):
            cell = self.getCell(cell_name)
            if value in cell.getValueSet():
                value_count += 1
                cells_with_value.append(cell_name)
        return value_count, cells_with_value

    def getCell(self, cell_id):
        """
        Returns the identified cell
        """
        return self._state[cell_id]

    def getCells(self):
        """ Returns all of the cells in the board. """
        return self._state.values()

    def getCertainCells(self):
        """
        Return the list of cells that have only one candidate value
        """
        return [cell for cell in self.getCells() if cell.isCertain()]

    def getPuzzle(self):
        puzzle = ''
        for identifier in sorted(Board.getAllCells(self.getDegree())):
            puzzle += self.getCell(identifier).getStateStr(False).strip()
        return puzzle

    def getStateStr(self, uncertain=False, human_readable=True):
        """
        Returns the board as a string, with or without the
        uncertainty information
        """
        degree = self.getDegree()
        output = ''

        for identifier in sorted(Board.getAllCells(degree)):
            if human_readable:
                (row, col) = Board.getLocations(identifier, degree)
                output += self.getCell(identifier).getStateStr(uncertain)
                # Tricky formatting: first check if we should end a row
                if col == (degree ** 2):
                    output += '\n'
                # Then, if we didn't end a row, check if we should end a section.
                elif 0 == col % degree:
                    output += '| '

                # Finally, insert row separators if needed
                if(0 == row % degree and row != (degree ** 2) and col == (degree ** 2)):
                    if(uncertain):
                        # For each column, have one - for each possibility plus a space.
                        # Have degree columns per section, a + between each section,
                        #   and degree number of sections
                        output += '+-'.join([('-' * (degree ** 2) + '-') * degree] * degree) + '\n'
                    else:
                        # Have two -- for each column (degree), a + between each section,
                        #   and degree number of sections
                        output += '+-'.join(['--' * degree] * degree) + '\n'
            else:
                output += (self.getCell(identifier).getStateStr(uncertain).strip() + '|')

        return output

    def getSimpleJson(self):
        """ Return simple json listing possible values across the board. """
        def sorted_row_cells(row) :
            return sorted(Board.getUnitCells(row, self.getDegree()))
        brd = {
            'degree' : self.getDegree(),
            'serialNumber' : self.getIdentifier(),
            'assignments' : [[self.getCell(identifier).getCertainValue()
                              for identifier in sorted_row_cells(row)]
                             for row in Board.getSortedRows(self.getDegree())],
            'availableMoves' : [[sorted(filter(lambda x : x != self.getCell(identifier).getCertainValue(),
                                               self.getCell(identifier).getValueSet()))
                                 for identifier in sorted_row_cells(row)]
                                for row in Board.getSortedRows(self.getDegree())],
        }
        return brd
        # return json.dumps(brd)

    def getUncertainCells(self):
        """
        Return the list of cells that have multiple candidate values.
        """
        return [cell for cell in self.getCells() if not cell.isCertain()]

    def hasContradiction(self):
        """
        Returns True if any cell of the board has an empty value set.
        """

        for cell in self.getCells():
            if len(cell.getValueSet()) == 0:
                return True
        return False

    def invalidCells(self):
        """
        Returns the set of cells that make this board insoluble.

        Returns those cells that are over-constrained, i.e., that have no possible values left,
        and those cells that are assigned but that conflict with each other.
        """

        # Collect all cells that indicate that this board is in an invalid state
        problem_cell_ids = set()

        # For each unit of the Board, get the cells associated with the unit
        for unit in Board.getAllUnits(self.getDegree()):
            unit_cells = Board.getUnitCells(unit, self.getDegree())
            # Map values seen to the cells in that unit to find conflicts and identify the conflicting cells.
            values = dict()

            for cell_id in unit_cells:
                cell = self.getCell(cell_id)
                if cell.isOverConstrained():
                    # Some cell has no possible values left; note that and go on to the next cell
                    problem_cell_ids.add(cell_id)
                    # Note: The checks below will not trigger, but this may make the code flow clearer
                    continue

                cell_val = cell.getCertainValue()
                if cell_val is not None:
                    # This cell has been assigned a single value; check for overlap within the unit
                    if cell_val not in values:
                        # We haven't seen this value before; no problems yet
                        values[cell_val] = set()
                    else:
                        # We have seen this value before, so report all cells with that value so far
                        problem_cell_ids.add(cell_id)
                        problem_cell_ids.update(values[cell_val])
                    # Save the current value -> cell id for later overlap detection
                    values[cell_val].add(cell_id)

        return problem_cell_ids

    def isSolved(self):
        """
        Returns True if the board represents a valid solution.
        """

        # For each unit of the Board, get the associated Cells
        for unit in Board.getAllUnits(self.getDegree()):
            cells = Board.getUnitCells(unit, self.getDegree())
            values = set()

            # Get the set of values used in the unit
            for cell_id in cells:
                cell_val = self.getCell(cell_id).getCertainValue()
                if cell_val is None:
                    return False
                else:
                    values.add(cell_val)

            # If the set of values for the unit is not the full set of values
            if(values != Cell.getPossibleValueSet()):
                return False

        return True
