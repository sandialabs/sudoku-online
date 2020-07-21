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

    def __init__(self, puzzle=None, name=None):
        if name:
            name = name.strip()
        self.log = logger.SudokuLogger(puzzle, name)
        self.rules = {}

        self.actions = [
            k for k in board_update_descriptions.basic_actions_description.keys()]
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
        if not self.log:
            return
        if self.log.getName() and '?select_ops_upfront' in self.log.getName():
            # If we are selecting logical operators up front, they can't be changed later in the game
            self.rules['canChangeLogicalOperators'] = False
        else:
            # Otherwise they can be changed, and we have an additional action (applyops) to support that
            # Note that the apply_ops action is redundant with 'heuristics' in the request, but that's OK.
            # We could leave this as an assumption, but let's make it explicit
            self.rules['canChangeLogicalOperators'] = True
            if self.log.puzzle:
                # We have a puzzle with no name, so we still need to add 'applyops' to the list of actions
                self.actions.append('applyops')
        self.verify()

    def copy(self):
        """ Return a deepcopy of myself. """
        return copy.deepcopy(self)
        # MAL TODO See if the logger is being deepcopied properly too and not getting all wound up

    def add_config_mappings_to_dict(self, json_dict):
        """ Add the config mappings that ought to be shared with the client to the board dictionary
            that will be sent via json. """
        json_dict['puzzleName'] = self.log.getName()
        if self.actions:
            json_dict['availableActions'] = self.actions
        if self.rules:
            json_dict['rules'] = self.rules
        return json_dict

    def update_config_from_dict_mappings(self, json_dict):
        """ Add the configuration specified in the board json dictionary. """
        if 'availableActions' in json_dict:
            self.actions = json_dict['availableActions']
        if 'rules' in json_dict:
            self.rules = json_dict['rules']

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
