#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Michael Darling, Shelley Leger
Sandia National Laboratories
July 12, 2020

Scoring and dispatch system configuration data for sudoku game actions.
"""

import logger
import copy
import board_update_descriptions


class ConfigurationData():
    """ Collect all the configuration data for a board and its logger and the solver.
    """

    def __init__(self, puzzle=None, name=None, is_first_board=False):
        if name:
            name = name.strip()
        self.log = logger.SudokuLogger(puzzle, name)
        # This is a placeholder to carry information through from the board so that we can know when to apply certain configurations (below)
        self.is_first_board = is_first_board

        self.actions = [
            k for k in board_update_descriptions.actions_description.keys()]
        self.free_operations = ['exclusion']
        self.costly_operations = [op for op in
                                  filter(lambda op: op not in self.free_operations,
                                         board_update_descriptions.operators_description.keys())]

        # If True, we should terminate on a logical_operator's first successful application,
        # devolving to cheaper strategies.
        # If False, we continue to try to find all matching possibilities for an operator.
        self.terminate_on_successful_operation = False
        # If True, have a logical operator explore to a fixed point
        # (i.e., re-explore the entire board for the operator after changes have been made)
        self.explore_to_fixed_point = True
        # If True, we increase the cost of the board every time the operator matches a set.
        # If False (and terminate_on_successful_operation is False), users get multiple matches for free.
        self.cost_per_matching_set = True
        # If True, we restart trying logical operators from the beginning when we find one that works.
        self.restart_op_search_on_match = True

        # TODO MAL move configuration in here
        # self.verbosity = 0

        # Simplify boards using the free operators given any opportunity
        self.simplify = True
        # Simplify the initial board before sending back to the client
        self.simplify_initial_board = True
        # Prune invalid boards for the user, or send them back showing how they're invalid?
        self.prune_invalid_boards = False

        # If True, log all boards, otherwise, log only solved boards
        self.log_all_boards = True

        self.apply_config_from_name()
        self.verify()

    def apply_config_from_name(self):
        """ Parsing the puzzle name from the logger, apply required configuration. """
        if not self.log or not self.log.getName():
            return
        name = self.log.getName()
        config_strs = name.split('?')
        del config_strs[0]
        for conf in config_strs:
            if 'select_ops_upfront' in conf:
                if self.is_first_board:
                    # This is the first board and can only offer logical ops
                    self.actions = ['applyops']
                elif 'applyops' in self.actions:
                    # TODO MAL may want to refactor to allow for checking whether a board should have an op
                    # This is subsequent boards, so user can't select logical ops
                    self.actions.remove('applyops')
            if 'freeops' in conf:
                ops_str = conf.split('=')[1]
                ops = ops_str.split('&')
                self.free_operations = []
                for op in ops:
                    if op:  # Hack because I'm sometimes getting '' from split
                        self.free_operations.append(op)
                        if op in self.costly_operations:
                            self.costly_operations.remove(op)
            if 'costlyops' in conf:
                ops_str = conf.split('=')[1]
                ops = ops_str.split('&')
                self.costly_operations = []
                for op in ops:
                    if op:  # Hack because I'm sometimes getting '' from split
                        self.costly_operations.append(op)
        self.verify()

    def check_free_ops(self, logical_ops):
        """ Check to see if the chosen logical ops should be applied as free operations hence-forward. """
        if not self.log or not self.log.getName():
            return
        name = self.log.getName()
        if '?select_ops_upfront' in name:
            for op in logical_ops:
                # Not using .extend so that we can ensure that we're not adding an operation that's already there
                if op not in self.free_operations:
                    self.free_operations.append(op)
            self.costly_operations = []
            if 'applyops' in self.actions:
                self.actions.remove('applyops')
            self.log.setName(
                f'{name}?freeops={"&".join(self.free_operations)}?costlyops=')
        self.verify()

    def copy(self):
        """ Return a deepcopy of myself. """
        return copy.deepcopy(self)
        # MAL TODO See if the logger is being deepcopied properly too and not getting all wound up

    def verify(self):
        """ Perform a series of assertions to ensure that the configurations are self-consistent.
        """
        # This assumption is because if you terminate on successful operation, the logical operators
        #    don't call complete_operation (which would update the board cost when cost_per_matching_set is False)
        if self.terminate_on_successful_operation:
            assert self.cost_per_matching_set, \
                'Cannot terminate on successful operation unless applying cost on every matching set'
        # This assumption is because the operators.apply_free_operators, which is used to simplify
        #   the initial board, checks self.simplify before actually executing anything
        if self.simplify_initial_board:
            assert self.simplify, 'Must simplify throughout if you simplify initial boards.'
        if self.explore_to_fixed_point:
            assert not self.terminate_on_successful_operation, \
                'Cannot explore an operator to a fixed point if we stop it after one successful match.'
        shared_actions = set(self.free_operations).intersection(
            self.costly_operations)
        assert 0 == len(
            shared_actions), f'Cannot have {shared_actions} as both free and costed'
        for act in self.free_operations:
            assert act in board_update_descriptions.operators_description.keys(), \
                f'Cannot have non-existant free operation {act}'
        for act in self.costly_operations:
            assert act in board_update_descriptions.operators_description.keys(), \
                f'Cannot have non-existant costly operation {act}'
        for act in self.actions:
            assert act in board_update_descriptions.actions_description.keys(), \
                f'Cannot have non-existant action {act}'

    def debug_operation(self, op, msg2, board):
        """ Don't increase our operator cost for this partial operation.
            Return False (unneeded, but to indicate that the operator should not terminate).
        """
        self.log.logOperatorProgress(op, msg2, board)
        return False

    def match_set_operation(self, op, msg2, board):
        """ Use the logger that adds the cost if we need to increase our cost every matching set.
            Return True if the operator should terminate after this operation.
        """
        if self.cost_per_matching_set:
            self.log.logOperator(op, msg2, board)
        else:
            self.log.logOperatorProgress(op, msg2, board)
        return self.terminate_on_successful_operation

    def complete_operation(self, op, msg2, board):
        """ Only add the cost at this point if we're not increasing our cost for every matching set.
        Return True (unneeded, but to indicate that the operator should not terminate).
        """
        if self.cost_per_matching_set:
            self.log.logOperatorProgress(op, msg2, board)
        else:
            self.log.logOperator(op, msg2, board)
        return True

    def debug_print(self, msg1, msg2, board):
        """ Over-use a convenient function to do level 1, 2, 3 verbosity printing.
        """
        self.log.logOperatorProgress(msg1, msg2, board)


defaultConfig = ConfigurationData()
