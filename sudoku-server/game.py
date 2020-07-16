#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Wilson, Shelley Leger
Sandia National Laboratories
Spring, 2020

Test code for Sudoku games.
Requires python3.
"""

import enum
import board
import solvers
import puzzles
import random
import operators
import config_data


def get_initial_board(content, simplify=True):
    """
    Get an initial board of 'degreey' given a dict request, randomly if 'name' is None, else by name.

    If simplify is True, apply logical inclusion and exclusion operators to board
    until no more progress can be made.
    """
    puzzle = None
    assert isinstance(content, dict), \
        "Failed assumption that request for initial board is formatted as a dict"
    name = content['name'] if 'name' in content else None
    degree = content['degree'] if 'degree' in content else 3

    if name and name in puzzles.puzzles:
        print("Loading requested puzzle " + str(name))
        puzzle = puzzles.puzzles[name]
    else:
        (name, puzzle) = random.choice(list(puzzles.puzzles.items()))
        config_data.debug_print('select puzzle', name, None)
    full_board = board.Board(puzzle, degree, name)
    config_data.debug_print('load puzzle', name, full_board)
    if simplify:
        solvers.singles_operators(full_board)
    return full_board.getSimpleJson()


def parse_and_apply_action(content, simplify=True):
    """
    Given a requested action and board, parse and apply the given action to board.

    Possible actions include selectValueForCell (cell, value), pivotOnCell (cell), and
    applyLogicalOperators ([list of operators])
        board (Board)  : the Board on which the action should be performed.
        action  : the action to take, and appropriate operators as specified in server_api.md
            "selectValueForCell <cell_id> <value>" or
            "pivotOnCell <cell_id>" or
            "applyLogicalOperators [[op, param], ...]"
    Returns:
        [Boards] : a collection of boards resulting from the selection action.
    """
    assert isinstance(content, dict), \
        "Failed assumption that request for action on board is formatted as a dict"
    if 'board' not in content:
        return {'error': 'You must specify a board to act upon.'}
    board_dict = content['board']
    assert isinstance(
        board_dict, dict), "Failed assumption that the parsed board is a dict."
    board_object = board.Board(board_dict)

    if 'action' not in content:
        return {'error': 'You must specify an action to take on the given board.'}
    action_dict = content['action']
    assert isinstance(action_dict, dict), \
        "Failed assumption that the parsed action is a dict."
    assert 'action' in action_dict, "Failed assumption that action request specified the action to take."
    action_choice = action_dict['action']

    result = []
    cell_loc = None
    value = None
    if "Cell" in action_choice:
        assert 'cell' in action_dict, "Must specify cell in a *Cell action"
        cell_loc = action_dict['cell']
        assert isinstance(cell_loc, list) and 2 == len(cell_loc), \
            "Must specify cell using [x,y] location notation."
        cell_id = board.Board.getCellIDFromArrayIndex(cell_loc[0], cell_loc[1])
    if "Value" in action_choice:
        assert 'value' in action_dict, "Must specify cell value in *Value* actions"
        value = action_dict['value']
    if action_choice == "selectValueForCell":
        result = solvers.assign_cell_action(
            board_object, cell_id, value, simplify)
    elif action_choice == "excludeValueFromCell":
        result = solvers.exclude_cell_value_action(
            board_object, cell_id, value, simplify)
    elif action_choice == "pivotOnCell":
        # Expand the cell specified by the string parameter
        result = solvers.expand_cell_action(board_object, cell_id, simplify)
    elif action_choice == "applyLogicalOperators":
        # Apply the logical operators specified by the op/param list of pairs
        assert 'operators' in action_dict, \
            "Must specify list of operators in applyLogicalOperators action"
        operators = action_dict['operators']
        result = [solvers.logical_solve(board.Board(board_object), operators)]
    else:
        return {'error': ('unknown action ' + str(action_choice))}

    jsoned_result = []
    for full_board in result:
        jsoned_result.append(full_board.getSimpleJson())

    return jsoned_result


def _jsonify_action(name, description_dict):
    """ Remove all the extra cruft and dispatch fields,
        and create one dict describing the named action / operator. """
    short_description = {'internal_name': name}
    for data in ['requested_arguments', 'cost', 'user_name', 'description']:
        if data in description_dict:
            short_description[data] = description_dict[data]
    return short_description


def get_possible_actions():
    """ Return a list of all possible actions for this game.

    May eventually want to update to alter possible actions for all possible games. """
    # MAL TODO Do we want to take in multiple actions and apply them all?
    operators = list()
    for op in ['inclusion', 'xwings', 'ywings', 'nakedpairs', 'hiddenpairs', 'nakedtriples']:
        operators.append(_jsonify_action(
            op, config_data.operators_description[op]))

    actions = list()
    for (action, description) in config_data.actions_description.items():
        short_desc = _jsonify_action(action, description)
        if action == 'applyops':
            short_desc['operators'] = operators
        actions.append(short_desc)

    return actions


class ActiveGameTreeState():
    """
    A Sudoku game tree's active state.
    There should only be one instance per game.

    Members:
        _active_nodes (GameTreeNode list): a list of non-final nodes that a user can choose to expand upon
        _success_nodes (GameTreeNode list): a list of all successful boards
        _failure_nodes (GameTreeNode list): a list of all failed boards
    """

    def __init__(self):
        self._active_nodes = []
        self._success_nodes = []
        self._failure_nodes = []

    def addActiveNodes(self, nodes_list):
        """
        Add nodes_list to the list of possible active nodes.
        """
        self._active_nodes.extend(nodes_list)

    def hasActiveNode(self):
        """ Return True if active nodes remain for exploration. """
        return len(self._active_nodes) > 0

    def selectActiveNode(self):
        """
        Allow the user to select an active node to continue exploring.
        Remove that node from the _active_nodes list.
        """
        # MAL TODO make this actually give a choice
        if len(self._active_nodes) > 1:
            print("Choose a board to explore:\n")
            # MAL TODO gross
            for i in range(len(self._active_nodes)):
                node = self._active_nodes[i]
                print("{}\n{}".format(i, node.board.getStateStr(True)))
            idx = int(input())
            active = self._active_nodes[idx]
            self._active_nodes.remove(active)
        else:
            active = self._active_nodes.pop()
        print("DEBUG: Exploring board \n{}".format(
            active.board.getStateStr(True)))
        return active

    def addSuccessNode(self, node):
        """
        Add node to the list of success nodes to track.
        """
        self._success_nodes.append(node)

    def printSuccessNodes(self):
        """
        Print all successful game boards discovered.
        """
        print("Successful boards: \n{}".format(
            "\n".join([node.board.getStateStr() for node in self._success_nodes])))


class GameTreeNode():
    """
    Node in Sudoku game tree

    Members:
       board (Board): Fully described board for this node in the tree (including uncertainty information)
       moves (list of moves): Moves that distinguish new board from parent, or conflicts (sim.)
       parent (GameTreeNode): Parent node
       success (Boolean): redundant with node_type, provides a quick way to check on the type of the node
       children (list of GameTreeNode): Child nodes
       node_type (enum of ROOT, CHOICE, SUCCESS, FAILURE, MOVES, CONDENSED):
                        indicates mechanism used for expansion of node / children

       game_state: MAL TODO doing this incorrectly: a global game state that keeps the list of incomplete boards to explore from
    """

    NodeType = enum.Enum('NodeType',
                         'ROOT CHOICE SUCCESS FAILURE AUTO_MOVES SELECTED_MOVES CONDENSED',
                         module=__name__,
                         qualname='GameTreeNode.NodeType')

    SelectFrequency = enum.Enum('SelectFrequency',
                                'START_ONLY ON_EACH_DECISION',
                                module=__name__,
                                qualname='GameTreeNode.SelectFrequency')

    def __init__(self, board, parent=None, moves=None, success=False, node_type=None, game_state=None):
        self.board = board
        self.moves = moves
        self.parent = parent
        self.success = success
        self.children = []
        self._depth = 0
        self.node_type = node_type

        self.game_state = ActiveGameTreeState() if game_state is None else game_state
        # TODO MAL: add a self.explanation to keep track of what each node was doing (e.g., pivot cell?)

        if parent is not None:
            self._depth = parent._depth + 1

    def play(self):
        """
        Steps this game board, setting up children GameTreeNodes as appropriate.

        Checks for a satisfied or unsatisifiable board assignment, terminating if found.
        Attempts to apply rules specified, recursing if progress is made.
        If no progress is made, selects a new approach, potentially splitting into several children.
        """

        # If the board is fully constrained and a valid solution
        if self.board.isSolved():
            self._debug("Puzzle solved!  Board:\n{}".format(
                self.board.getStateStr()))
            success_node = GameTreeNode(self.board,
                                        parent=self,
                                        success=True,
                                        node_type=GameTreeNode.NodeType.SUCCESS,
                                        game_state=self.game_state)
            self.children.append(success_node)
            self.game_state.addSuccessNode(success_node)
            return

        # If the board is in an invalid state
        contradictions = self.board.invalidCells()
        if contradictions:
            self._debug("Move set led to contradictions {}.  Failure reached; must backtrack.  Board:\n{}".format(
                str(contradictions), self.board.getStateStr(True)))
            failure_node = GameTreeNode(self.board,
                                        parent=self,
                                        moves=contradictions,
                                        success=False,
                                        node_type=GameTreeNode.NodeType.FAILURE,
                                        game_state=self.game_state)
            self.children.append(failure_node)
            return

        # The board has potential: apply rules and see how far we get
        # MAL QUESTION: Do we unit propagate before they make the first decision or not? See example board 10.
        new_board = board.Board(self.board)
        my_ops = solvers.select_all_logical_operators_ordered()
        resboard = solvers.logical_solve(new_board, my_ops)
        determined_moves = [item
                            for item in resboard.getCertainCells() if item not in self.board.getCertainCells()]

        # We applied rules and made progress.  Recurse.
        if len(determined_moves) > 0:
            self._debug("{} determined move(s)".format(
                len(determined_moves)))
            child_node = GameTreeNode(resboard,
                                      parent=self,
                                      moves=determined_moves,
                                      node_type=GameTreeNode.NodeType.AUTO_MOVES,
                                      game_state=self.game_state)
            self.children.append(child_node)
            child_node.play()
            return

        # We had no given progress.  A decision must be made: pivot node? new rule? backtrack?
        explore = self.selectNextApproach()
        explore.play()

        # We explored for a while.  If there are more active states, keep exploring.
        while (self.game_state.hasActiveNode()):
            explore = self.game_state.selectActiveNode()
            explore.play()

        self.game_state.printSuccessNodes()
        return

    def selectNextApproach(self):
        """
        Generator of new GameTreeNodes.
        This is the policy location for how to handle an "unable to progress".

        For now, we manually select a pivot cell and then generate all the children, registering them with the game state.
        We then have the user select an active state to explore and return that state.
        In the future, we could select new rules, new solvers, backtrack, etc.
        """
        # TODO: This is where we will select the "unable to progress" policy. For now, manually select pivot cell.
        child_nodes = self.pivotOnCell()
        self.game_state.addActiveNodes(child_nodes)

        # TODO MAL: I think we want to unit propagate after we make an assignment from a pivot but before we select?
        return self.game_state.selectActiveNode()

    def pivotOnCell(self):
        """
        Taking in a set of uncertain cells in options, ask the user to select one to expand on.
        Return a list of all new GameTreeNodes with the pivot node expanded.
        """
        # Get only the cells that have multiple possibilities at this point
        options = self.board.getUncertainCells()
        # TODO: filter the options based on the constraints imposed by the test
        options = options

        # Select a cell to pivot
        names = [cell.getIdentifier() for cell in options]
        print(
            "Which cell do you want to expand into all possible options? {}".format(names))
        selected = input()
        pivot = self.board.getCell(selected)
        new_boards = solvers.expand_cell_action(
            self.board, pivot.getIdentifier())

        # Make a new board for each possible value for that cell
        children = []
        for child in new_boards:
            move = set()
            # WARNING: PROBABLY BREAKS ABSTRACTION BARRIER
            move.add(pivot.getIdentifier())
            child_node = GameTreeNode(child,
                                      parent=self,
                                      moves=move,
                                      node_type=GameTreeNode.NodeType.CHOICE,
                                      game_state=self.game_state)
            children.append(child_node)

        # return all new GameTreeNodes
        return children

    def _debug(self, message):
        print("DEBUG: {}{}".format(
            ''.join([' '] * self._depth),
            message))

# -----------------------------------------------------


def test_sudoku():
    # board.Board.initialize()
    root = board.Board(puzzles.puzzles['underconstrained1'])

    # solver = Solver(board)
    # solver.setVerbosity(3)
    # solver.solve()

    search_tree = GameTreeNode(root)
    print("Initial board:\n{}".format(root.getStateStr(True)))
    search_tree.play()
    # print("Solved?",root.isSolved())


if __name__ == '__main__':
    test_sudoku()
