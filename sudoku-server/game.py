#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Wilson, Shelley Leger
Sandia National Laboratories
Spring, 2020

Test code for Sudoku games.
Requires python3.
"""

# Imports from our own code
import board
import board_update_descriptions
import config_data
import operators
import puzzles
import solvers
import translate

# Imports from Python standard library
import enum
import json
import random
import sys

import logging
logger = logging.getLogger(__name__)


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
        if len(self._active_nodes) > 1:
            print("Choose a board to explore. Please input the desired board number:")
            # MAL TODO gross
            for i in range(len(self._active_nodes)):
                node = self._active_nodes[i]
                print("Board Number {}:\n{}\n".format(i, node.board.getStateStr(True)))
            idx = int(input())
            active = self._active_nodes[idx]
            self._active_nodes.remove(active)
        else:
            active = self._active_nodes.pop()
        logger.info("Exploring board \n{}".format(
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

    NodeType = enum.Enum("NodeType",
                         "ROOT CHOICE SUCCESS FAILURE AUTO_MOVES SELECTED_MOVES CONDENSED",
                         module=__name__,
                         qualname="GameTreeNode.NodeType")

    SelectFrequency = enum.Enum("SelectFrequency",
                                "START_ONLY ON_EACH_DECISION",
                                module=__name__,
                                qualname="GameTreeNode.SelectFrequency")

    def __init__(self, board, logical_ops=None, cell_selector=None,
                 parent=None, moves=None, success=False,
                 node_type=None, game_state=None):
        self.board = board
        self.moves = moves
        self.parent = parent
        self.success = success
        self.children = []
        self._depth = 0
        self.node_type = node_type
        self._my_ops = logical_ops if logical_ops else parent._my_ops if parent else solvers.select_all_logical_operators_ordered()
        self._cellselector = cell_selector if cell_selector else parent._cellselector if parent else solvers.select_by_user

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
            logger.info("Puzzle solved!  Board:\n%s",
                      self.board.getStateStr())
            success_node = GameTreeNode(self.board,
                                        parent=self,
                                        success=True,
                                        node_type=GameTreeNode.NodeType.SUCCESS,
                                        game_state=self.game_state)
            self.children.append(success_node)
            self.game_state.addSuccessNode(success_node)
            return self.board

        # If the board is in an invalid state
        contradictions = self.board.invalidCells()
        if contradictions:
            logger.info("Move set led to contradictions %s.  Failure reached; must backtrack.  Board:\n%s",
                str(contradictions), self.board.getStateStr(True))
            failure_node = GameTreeNode(self.board,
                                        parent=self,
                                        moves=contradictions,
                                        success=False,
                                        node_type=GameTreeNode.NodeType.FAILURE,
                                        game_state=self.game_state)
            self.children.append(failure_node)
            return None

        # The board has potential: apply rules and see how far we get
        my_uncertainty = self.board.countUncertainValues()
        new_board = board.Board(self.board)
        resboard = solvers.logical_solve(new_board, self._my_ops)
        child_uncertainty = resboard.countUncertainValues()

        # We progressed. Make a new child and play it.
        if child_uncertainty < my_uncertainty:
            logger.info("Reduced uncertainty from %d to %d.", my_uncertainty, child_uncertainty)
            child_node = GameTreeNode(new_board,
                                      parent=self,
                                      node_type=GameTreeNode.NodeType.AUTO_MOVES,
                                      game_state=self.game_state)
            self.children.append(child_node)
            return child_node.play()

        # This board needs a decision made to progress it, so it's an active node.
        self.game_state.addActiveNodes([self])

        # Select an active state and keep exploring.
        while (self.game_state.hasActiveNode()):
            # MAL TODO bug in here trying to get back to an older state.
            explore = self.game_state.selectActiveNode()
            explore = self.selectNextApproach()
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
        print("Your goal is to answer the following question:")
        print(self.board._question)
        print("  HINT: you may not need to solve the whole board to answer this question.")
        print("The Goal cell, {}, will be *marked* on the board with asterisks '*'.".format(self.board.goal_cell))
        print("\n")

        # MAL TODO Allow for asking questions
        # print("\nWould you like to answer the question? y/n (", self.board._question ,")")
        # ans = input()
        # if ans == 'y'or ans == 'yes':
        #     print(question, "Please answer yes or no")
        #     inp = input()
        #     if inp == 'y': #self.board._answer:
        #         print("Congratulations! You got the question correct")
        #     else:
        #         print("I'm sorry. That answer is incorrect")

        while True:
            # TODO MAL this should use the board's idea of what cell actions it likes
            print("What action do you want to perform? {}".format(
                [self.board.config.actions]))
            action = input()
            if action in self.board.config.actions:
                break

        while True:
            # Select the arguments for the action somehow
            action_desc = board_update_descriptions.actions_description[action]
            cell = None
            args = None # CellID, (CellID, Value), or [ops]
            if "arguments" in action_desc:
                for arg_type in action_desc["arguments"]:
                    if "cell" == arg_type:
                        cell = self._cellselector(self.board)
                        args = cell.getIdentifier()
                    elif "value" == arg_type:
                        # We expect to have already seen the cell
                        if cell is None:
                            logger.warn("Can only have a value if a cellID has already been given.")
                        print(f"What value do you want to select? (of {str(cell.getValues())})")
                        value = int(input())
                        args = (args, value)
                    elif "operators" == arg_type:
                        # We currently assume that this command is mutually exclusive with the others and just replace the arguments
                        print("What operations would you like to use? (separate by a space) {}".format(self._my_ops))
                        args = str(input()).split(" ")
                        action = "applyops"

            logger.info("Requested action is %s with arguments %s.", str(action), str(args))
            try:
                collected = solvers.take_action(self.board, action, args)
                break
            except AssertionError as e:
                logger.warn(e)

        child_nodes = []
        for board in collected:
            logger.info("Simplifying child board %s.", board.getIdentifier())
            child = solvers.apply_free_operators(board)
            child_node = GameTreeNode(child,
                                      parent=self,
                                      node_type=GameTreeNode.NodeType.CHOICE,
                                      game_state=self.game_state)
            child_nodes.append(child_node)
        self.children.extend(child_nodes)
        self.game_state.addActiveNodes(child_nodes)

# -----------------------------------------------------


def test_sudoku():
    # root = translate.get_initial_board({"name": "underconstrained1"})
    root = translate.get_initial_board({"name": "hard4"})

    search_tree = GameTreeNode(root)
    print("Initial board:\n{}".format(root.getStateStr(True)))
    result = search_tree.play()
    print("Solved?",result.isSolved())
    print(f"Final board:\n{str(result.getStateStr(True))}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_sudoku()
