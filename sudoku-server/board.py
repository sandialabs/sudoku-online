#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
David Stracuzzi, Michael Darling, Michelle Leger
Sandia National Laboratories
December 12, 2019

Sudoku Board and Cell data structures.
"""

# import json
import uuid
import config_data
import copy

import logging
logger = logging.getLogger(__name__)

class Cell():
    """
    A single cell on a Sudoku board.
    Each cell tracks and provides manipulation for the set of
    candidate values that the Cell may take.
    """

    # An ordered list of
    display_list = ['1', '2', '3', '4', '5', '6', '7',
                    '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

    def __init__(self, identifier, value='.', degree=3):
        """ Initializes a Cell with an identifier and valueset or another cell.

        Args:
            identifier   : a string identifier within a board (value expected),
                            or a cell to copy
            value        : the collection of potential values, or '.' for complete value set
            degree (int) : the number of blocks on a side (determines values)
        Returns:
            Cell   : a new cell.

        Fields:
            propagated (boolean) : True if the cell assignment has been propagated to
                sister cells (i.e., removing values from that cell)

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
            assert isinstance(self._propagated, bool), \
                "Cell's _propagated should be a boolean"
            self._values = sorted(list(identifier._values))
            self._degree = identifier._degree
        else:
            # If identifier is a unique ID (str or int)
            self._id = identifier
            self._propagated = False
            self._degree = degree
            if (value == '0' or value == '.'):
                # Get all possible values
                self._values = sorted(Cell.getPossibleValuesByDegree(degree))
            elif isinstance(value, str):
                self._values = [self.getValueDisplays(
                    self._degree).index(value)]
            elif isinstance(value, list):
                self._values = sorted((value))
            elif isinstance(value, int):
                self._values = [value]

        assert isinstance(self._values, list), "Cell's values should be a list"

    @ classmethod
    def getPossibleValuesByDegree(cls, degree=3):
        """ Returns sorted list of all possible values for puzzle of degree.
        Raises:
            TypeError if degree is not squareable
        """
        try:
            return [x for x in range(degree ** 2)]
        except TypeError:
            assert False, "Cell's degree must be square-able (**2)"

    @ classmethod
    def getValueDisplays(cls, degree=3):
        """ Returns sorted list of all display values for puzzle of degree.

        Note: this could be canonicalized to save memory, but it isn't.
        """
        return [cls.display_list[idx] for idx in cls.getPossibleValuesByDegree(degree)]

    @ classmethod
    def displayValues(cls, values):
        """ Returns list of displays of the sorted list of values.
        """
        return sorted([cls.display_list[idx] for idx in values])

    @ classmethod
    def displayValue(cls, val):
        """ Returns displays of the value val.
        """
        return cls.display_list[val]

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
            boolean : True if other values were eliminated by this assignment
                      False if no cell update occurred
        Raises:
            AssertionError  : if value was not a valid possibility
        """
        assert value in self._values, \
            "Cannot assign %s to Cell %s" % (
                str(value), str(self.getIdentifier()))
        if len(self._values) > 1:
            self._values = [value]
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
        except ValueError:
            return False

    def getCertainValue(self):
        """
        If cell has only one candidate value, return it
        Otherwise return None
        """
        if(len(self._values) == 1):
            return self._values[0]
        return None

    def getIdentifier(self):
        """ Return identifier for self. """
        return self._id

    def getStateStr(self, uncertain=False, goal_cell = None):
        """
        If uncertain is False, then return value if Cell is certain
                               otherwise return '.'
        If uncertain is True, return the value set as a string
        """
        displays = Cell.getValueDisplays(self._degree)
        width = sum([len(x) for x in displays]) + 1
        if(uncertain):
            s = [displays[val] for val in self.getValues()]
            if not s:
                # Underconstrained: highlight a conflict
                return str.center('X', width)
            s = str(''.join(s))
            if goal_cell == self.getIdentifier():
                # Highlight the goal cell
                s = '*' + s + '*'
            elif goal_cell and goal_cell[1] == self.getIdentifier()[1]:
                # Save space to match with the goal cell
                s = ' ' + s + ' '
            return str.center(''.join(s), width)
        elif self.isCertain():
            return displays[self.getCertainValue()] + ' '
        else:
            return '. '

    def getValues(self):
        """ Return ordered list of current possible values. """
        return sorted(self._values)

    def getValueSet(self):
        """ Return set of current possible values. """
        return set(self._values)

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

    @ classmethod
    def getCellUnits(cls, cell_id, degree=3):
        """ Return units associated with cell_id in a puzzle of degree.

        cell_id may be a string or a Cell.
        """
        if not isinstance(cell_id, str):
            cell_id = cell_id.getIdentifier()
        return cls.unit_map[degree][cell_id]

    @ classmethod
    def getUnitCells(cls, unit_id, degree=3):
        """ Return cells associated with unit_id in a puzzle of degree. """
        return cls.unit_defns[degree][unit_id]

    @ classmethod
    def getAllCells(cls, degree=3):
        """ Get all cell names in a puzzle of degree. """
        return cls.unit_map[degree].keys()

    @ classmethod
    def getAllUnits(cls, degree=3):
        """ Get all unit names in a puzzle of degree. """
        return cls.unit_defns[degree].keys()

    @ classmethod
    def getSortedRows(cls, degree=3):
        """ Get all unit names in a puzzle of degree. """
        return sorted([name for name in filter(lambda x: cls.getUnitType(x) == 'row',
                                               cls.unit_defns[degree].keys())])

    @ classmethod
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

    @ classmethod
    def getAssociatedCellIds(cls, cell_id):
        """
        Get all cell IDs in units associated with
        target cell, without repeats.
        Return empty list if no cell_id is given
        """
        associated_cells = []
        if cell_id:
            associated_units = cls.getCellUnits(cell_id)
            for unit_id in associated_units:
                unit_cells = cls.getUnitCells(unit_id)
                for unit_cell in unit_cells:
                    if unit_cell not in associated_cells and unit_cell != cell_id:
                        associated_cells.append(unit_cell)
        return associated_cells

    @ classmethod
    def getCommonCells(cls, cell_id_list):
        """
        Get list of all cells jointly associated
        to all cells in the list
        """
        common_cell_set = set(cls.getAssociatedCellIds(cell_id_list[0]))

        for cell_id in cell_id_list:
            common_cell_set = common_cell_set & set(
                cls.getAssociatedCellIds(cell_id))

        return list(common_cell_set)

    @ classmethod
    def getCommonUnits(cls, cell_id_list):
        """
        Get list of all units jointly associated
        to all cells in the list
        """
        common_unit_set = set(cls.getCellUnits(cell_id_list[0]))

        for cell_id in cell_id_list:
            common_unit_set = common_unit_set & set(cls.getCellUnits(cell_id))

        return list(common_unit_set)

    @ classmethod
    def getUnionUnitSet(cls, cell_id_list):
        """
        Get union set of units for the given cells
        """
        union_unit_set = set(cls.getCellUnits(cell_id_list[0]))

        for cell_id in cell_id_list:
            union_unit_set = union_unit_set | set(cls.getCellUnits(cell_id))

        return union_unit_set

    @ classmethod
    def getCellID(cls, row, col):
        """ Returns cell identifier given row and column identifier strings. """
        r = row[1]
        c = col[1:]
        return r + c

    @ classmethod
    def getCellIDFromArrayIndex(cls, row, col):
        """ Returns cell identifier given row and column integer. """
        rnm = cls._rname(row)
        cnm = cls._cname(col)
        return cls.getCellID(rnm, cnm)

    @ classmethod
    def getBoxID(cls, row, col, deg):
        """ Returns box identifier given row ('rX') and column ('cY[Y]') identifier and puzzle degree. """
        r = row[1]
        c = col[1:]
        # 1. Convert r back to int past 0 ('A' is 1)
        # 2. Bump up to next round for divide to work nicely (+ deg -1)
        box_off = int((int(c) + deg - 1) / deg)
        box_base = (int((ord(r) - 64 + deg - 1) / deg) - 1) * deg
        return 'b' + str(box_base + box_off)

    @ classmethod
    def getLocations(cls, id, deg):
        """ Returns the row, column location of cell id as int indices into a 2D array
        in a puzzle of degree deg.
        TODO: Currently assumes id is of the form "rc[c]"
        """
        r = ord(id[0])-64
        c = int(id[1:])
        return (r-1, c-1)

    @ classmethod
    def _cname(cls, idx):
        # Start counting from 'c1'
        return 'c' + str(idx+1)

    @ classmethod
    def _rname(cls, idx):
        # Start counting from 'rA'
        return 'r' + chr(65 + idx)

    @ classmethod
    def _bname(cls, idx):
        # Start counting from 'b1'
        return 'b' + str(idx+1)

    @ classmethod
    def initialize(cls, degree):
        """
        Initialize the unit definitions (mapping of unit names to cell names)
        and the unit map (mapping of cell names to unit names).

        Unit defns initially contains the NxN boxes.  This method adds the
        rows and columns and then creates the unit map by inverting the
        unit defns.
        """
        for degree in [degree]:  # range(2, 4):
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

    def __init__(self, state=['.' for i in range(0, 81)], degree=3, name=None):
        """
        Initialize a board for a puzzle of degree with the given state.
        State parameter can be a string, a json, or a Board to copy.

        Locals:
            _state (dict {str -> Cell}): a mapping from every cell identifier to the Cell encapsulating that Cell's state
            _id (int): a unique identifier
            _parent_id (int): identifier of this board's parent
            goal_cell (str): the name/id of the goal cell to answer the question about
            accessible_cells (list[str]): the list of cell ids about which a user can take an action (eg, pivot, assign, exclude)
        """
        try:
            Board.unit_map[degree]
        except KeyError:
            Board.initialize(degree)

        # Generate a UID integer from uuid1.  These bits are largely dependent on clock
        # (though it's been pointed out that they might leak a little information about MAC address)
        self._id = uuid.uuid1().int >> 64
        self._is_background = False
        self._action = {}
        self._state = dict()
        assert isinstance(degree, int), "Degree must be an int."
        assert 2 <= degree <= 4, "Degree must be between 2 and 4 for now."
        self._degree = degree
        self._parent_id = None
        assert name is None or isinstance(name, str), f"Name must be a str, not {name} of type {type(name)}."
        self.accessible_cells = None
        self.config = None
        if isinstance(state, Board):
            # State is a Board; copy it, but keep the new identifier
            logger.info("Initializing Board for Board %s (from %s).", str(state.getIdentifier()), str(state.getPuzzleName()))
            logger.debug("Incoming Board is %s.", str(state))
            for cell in state.getCells():
                self._state[cell.getIdentifier()] = Cell(cell)
            self._degree = state.getDegree()
            self._parent_id = state._id
            self.accessible_cells = state.accessible_cells
            self.config = state.config.copy()
        elif isinstance(state, dict):
            # State was parsed from json; keep the same identifier and update fields appropriately
            # board_dict = json.loads(board_json)
            logger.info("Initializing Board for dict %s.", str(state))
            params = copy.deepcopy(state)
            assert 'serialNumber' in state, "Expecting serialNumber in state provided."
            self._id = state['serialNumber']
            del params['serialNumber']

            assert 'assignments' in state, "Expecting assignments in state provided."
            assert 'availableMoves' in state, "Expecting availableMoves in state provided."
            assignments = [item
                           for row in state['assignments'] for item in row]
            options = [item for row in state['availableMoves'] for item in row]
            # Initialize cell state
            i = 0
            for identifier in sorted(Board.getAllCells(degree)):
                cell_state = assignments[i] if assignments[i] is not None else options[i]
                self._state[identifier] = Cell(identifier, cell_state)
                i += 1
            del params['assignments']
            del params['availableMoves']

            if 'degree' in state:
                self._degree = state['degree']
            else:
                logger.warn("'degree' not specified in state: board initialization or use may fail unexpectedly.")
            if 'parentSerialNumber' in state:
                self._parent_id = state['parentSerialNumber']
                del params['parentSerialNumber']
            if 'goalCell' in state:
                goal = state['goalCell']
                assert len(goal) == 2, "Expected exactly a row and column index for goal."
                cell_id = self.getCellIDFromArrayIndex(goal[0], goal[1])
                if 'goal' in params:
                    assert params['goal'] == cell_id, "goalCell details do not match stored goal."
                params['goal'] = cell_id
                del params['goalCell']
            if 'accessibleCells' in state:
                self.accessible_cells = []
                for accs in state['accessibleCells']:
                    assert len(accs) == 2, "Expected exactly a row and column index for accessibleCell."
                    self.accessible_cells.append(self.getCellIDFromArrayIndex(accs[0], accs[1]))
                del params['accessibleCells']
            else:
                self.computeAccessibleCells()
            if 'action' in state:
                self.action = state['action']
                del params['action']
            if 'backtrackingBoard' in state:
                self._is_background = state['backtrackingBoard']
                del params['backtrackingBoard']
            self.config = config_data.ConfigurationData(self.getStateStr(
                False, False, ''), name, params)
        elif isinstance(state, str):
            logger.info("Initializing Board for string %s, name %s.", str(state), str(name))
            i = 0
            for identifier in sorted(Board.getAllCells(degree)):
                self._state[identifier] = Cell(identifier, state[i])
                i += 1
            self._degree = degree

            self.config = config_data.ConfigurationData(self.getStateStr(
                False, False, ''), name)
            logger.debug("Crafted config to be %s.", str(self.config))
            self.computeAccessibleCells()
            logger.debug("Calculated accessible cells as %s.", str(self.accessible_cells))
        else:
            raise TypeError('Can\'t initialize Board from input type ' + type(state)
                            + '. (Must be Board, dict, or str.)')

    def __str__(self):
        output = "Board " + str(self._id) \
            + " (child of " + str(self._parent_id) + ") State:\n"
        output += self.getStateStr(True)

        output += '\nCells:\n'
        for key in self._state:
            output += str(self._state[key]) + '\n'

        return output

    def getGoalCell(self):
        """ If we have a goal cell, return it; otherwise, return None. """
        if self.config and self.config.parameters and "goal" in self.config.parameters:
            return self.config.parameters["goal"]
        return None

    def computeAccessibleCells(self):
        """ If we have a goal cell, compute accessible cells and store them in self.accessible_cells.
            If we don't have a goal cell, return all remaining uncertain cells. """
        goal_cell = self.getGoalCell()
        offlimits = self.getAssociatedCellIds(goal_cell)
        if goal_cell:
            offlimits.append(goal_cell)

        def inlimits(cell):
            if cell == goal_cell:
                return False
            if self.getCell(cell).isCertain():
                return False
            if cell in offlimits:
                return False
            return True

        self.accessible_cells = \
            [cell for cell in filter(inlimits,
                                     self.getAllCells())]
        if len(self.accessible_cells) == 0:
            # Devolve to any uncertain cells except the goal cell
            def inlimits2(cell):
                if cell == goal_cell:
                    return False
                if self.getCell(cell).isCertain():
                    return False
                return True
            self.accessible_cells = \
                [cell for cell in filter(inlimits2,
                                         self.getAllCells())]
        return self.accessible_cells

    def setToBackground(self):
        """ Sets this board to indicate whether it should be considered a background board.

        Background boards represent places to which a user can back up over his own decision
        if he accidentally placed himself in a corner.  They are lower priority.
        """
        self._is_background = True

    def addAction(self, action: dict):
        """ Adds the action describing the item that changed this board to this state to the board description. """
        if not self._action:
            self._action = action
        for (key, value) in action.items():
            if key == 'action' and key in self._action and value == 'applyops':
                # Don't overwrite an existing action with applyops
                continue
            self._action[key] = value

    def getDegree(self):
        """ Returns the degree of this puzzle board. """
        return self._degree

    def getIdentifier(self):
        """ Returns the identifier of this puzzle board. """
        return self._id

    def getDisplayName(self):
        """ Returns the simple display name of this puzzle board. """
        if not self.config:
            return None
        return self.config.getParam("displayName")

    def getPuzzleName(self):
        """ Returns the fully qualified puzzle name of this puzzle board. """
        if not self.config:
            return None
        return self.config.getParam("puzzleName")

    def getQuestion(self):
        """ Returns the question associated with this puzzle board. """
        if not self.config:
            return None
        return self.config.getParam("question")

    def countUncertainValues(self):
        """ Counts the number of uncertain values summed across all uncertain cells.
        """
        uncertain_cells = filter(lambda c: not c.isCertain(), self.getCells())
        n = sum([len(cell.getValues()) for cell in uncertain_cells])
        return n

    def countAssociatedUncertainValuesGivenUncertainCell(self, cell):
        """ Counts the number of uncertain values summed across all uncertain cells associated with cell,
            if cell is uncertain.
            I.e.,  counts the number of uncertain values across cells in the row, column, and box of cell.
        """
        if cell.isCertain():
            return 0
        associations = [self.getCell(c) for c in self.getAssociatedCellIds(cell)]
        uncertain_cells = [c for c in filter(lambda c: not c.isCertain(), associations)]
        n = sum([len(cell.getValues()) for cell in uncertain_cells])
        return n

    def getValueCountAndCells(self, unit_name, value):
        """ Counts number of times a value is present in a unit.
        """
        value_count = 0
        cells_with_value = []
        for cell_name in self.getUnitCells(unit_name):
            cell = self.getCell(cell_name)
            if value in cell.getValues():
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

    def getStateStr(self, uncertain=False, human_readable=True, sep='|'):
        """
        Returns the board state as a string, with or without uncertainty information
        sep separates the cells in a non human-readable printing
        """
        degree = self.getDegree()
        output = ''

        for identifier in sorted(Board.getAllCells(degree)):
            if human_readable:
                (row, col) = Board.getLocations(identifier, degree)
                # Tricky formatting: first check if we should end a row
                if 0 == col:
                    # Have to have this as a separate check so our elif down below triggers properly
                    # and we don't end up with an extra | right before the first line
                    if 0 != row:
                        output += '\n'
                # Then, if we didn't end a row, check if we should end a section.
                elif 0 == col % degree:
                    output += '| '

                # Finally, insert row separators if needed
                if(0 == row % degree and row != 0 and col == 0):
                    if(uncertain):
                        # For each column, have one - for each possibility plus a space.
                        # Have degree columns per section, a + between each section,
                        #   and degree number of sections
                        output += '+-'.join([('-' * (degree ** 2) + '-')
                                             * degree] * degree) + '\n'
                    else:
                        # Have two -- for each column (degree), a + between each section,
                        #   and degree number of sections
                        output += '+-'.join(['--' * degree] * degree) + '\n'

                # Finally print the state string
                output += self.getCell(identifier).getStateStr(uncertain, self.getGoalCell())
            else:
                output += (self.getCell(identifier).getStateStr(uncertain, None).strip() + sep)

        return output

    def getSimpleJson(self):
        """ Return simple json-compatible dictionary listing possible values across the board. """
        def sorted_row_cells(row):
            return sorted(Board.getUnitCells(row, self.getDegree()))
        brd = {
            'degree': self.getDegree(),
            'serialNumber': self.getIdentifier(),
            'assignments': [[self.getCell(identifier).getCertainValue()
                             for identifier in sorted_row_cells(row)]
                            for row in Board.getSortedRows(self.getDegree())],
            'availableMoves': [[sorted(filter(lambda x: x != self.getCell(identifier).getCertainValue(),
                                              self.getCell(identifier).getValues()))
                                for identifier in sorted_row_cells(row)]  # for each cell id in the row,
                               # print all the values for that cell that aren't the certain value
                               # (this gives us an empty list when the cell is certain)
                               for row in Board.getSortedRows(self.getDegree())],
        }
        if self._parent_id:
            brd['parentSerialNumber'] = self._parent_id
        if self.isSolved():
            brd['solved'] = True
        invalid_cells = self.invalidCells()
        if invalid_cells:
            # Get the locations in row, column form of the given cell id
            invalid_locs = [list(type(self).getLocations(
                ident, self.getDegree())) for ident in invalid_cells]
            brd['conflictingCells'] = invalid_locs
        if self._is_background:
            brd['backtrackingBoard'] = True
        brd = self.config.add_config_mappings_to_dict(brd)

        logger.debug(f"Goal cell, accessible_cells: {self.getGoalCell()} and {self.accessible_cells}.")
        if self.getGoalCell():
            brd['goalCell'] = list(type(self).getLocations(self.getGoalCell(), self.getDegree()))
        self.computeAccessibleCells()
        if self.accessible_cells:
            accessible_locs = [list(type(self).getLocations(
                ident, self.getDegree())) for ident in self.accessible_cells]
            brd['accessibleCells'] = accessible_locs
        else:
            brd['accessibleCells'] = []
        brd['action'] = self._action
        return brd

    def getUncertainCells(self):
        """
        Return the list of cells that have multiple candidate values.
        """
        return [cell for cell in self.getCells() if not cell.isCertain()]

    def invalidCells(self):
        """
        Returns the set of cell IDs for cells that make this board insoluble.

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

        return list(problem_cell_ids)

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
                    # Cell hasn't been assigned yet, or is over-constrained
                    return False
                else:
                    values.add(cell_val)

            # If the set of values for the unit is not the full set of values
            if(values != set(Cell.getPossibleValuesByDegree(self.getDegree()))):
                # Assignment doesn't represent all possible values
                # At least one cell has a conflicting assignment, or is over-constrained
                #   (at least, you'll find that after applying exclusion if you haven't already)
                return False

        return True
