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
import traceback
import sys

def parse_name_config(name):
    """ Given a board name with embedded config information, return a dictionary mapping config variables to values. """
    parameters = name.split('?')
    config_dict = {}
    assert len(parameters) > 0, "Was unable to get any data from name."
    config_dict['puzzleName'] = parameters[0]
    for param in parameters[1:]:
        if '=' in param:
            assigned = param.split('?')
            assert(len(assigned) == 2), f"Assumed that the parameter would only have one '=': key=value, not {assigned}."
            if ',' in assigned[1]:
                value_list = assigned[1].split(',')
                config_dict[assigned[0]] = value_list
            else:
                config_dict[assigned[0]] = assigned[1]
        else:
            config_dict[param] = True
    return config_dict

class ConfigurationData():
    """ Collect all the configuration data for a board and its logger and the solver.
    """

    def __init__(self, puzzle=None, name=None):
        if name:
            name = name.strip()
        self.log = logger.SudokuLogger(puzzle, name)

        # Keep track of any special rules for the board (see apply_config_from_name below)
        self.rules = {}

        # Keep track of available actions and operators and how to cost them
        self.actions = [
            k for k in board_update_descriptions.basic_actions_description.keys()]
        self.free_operations = ['exclusion']
        self.costly_operations = [op for op in
                                  filter(lambda op: op not in self.free_operations,
                                         board_update_descriptions.operators_description.keys())]

        # Keep track of configuration for control flow

        # If True, we should terminate on a logical_operator's first successful application.
        # If False, we continue to try to find all matching possibilities for an operator.
        self.terminate_on_successful_operation = False
        # If True, apply a single logical operator to a fixed point, interleaving free operators as appropriate
        self.retry_logical_op_after_free_ops = True
        # If True, have a logical operator explore to a fixed point
        # (i.e., re-explore the entire board for the operator after changes have been made)
        self.explore_to_fixed_point = True
        # If True, we restart trying logical operators from the beginning when we find one that works.
        self.restart_op_search_on_match = True

        # Keep track of scoring information

        # If True, have score tracked per game instead of per board
        #   Should only be true if cost per requested application is also True
        self.cost_per_game_not_per_board = False

        # If True, we increase the cost of the board every time the operator matches a set.
        self.cost_per_matching_set = False
        # If True, users get charged on a successful application
        #   no matter how many matches they get (>1) on that application
        self.cost_per_matching_use = True
        # If True, increase the cost of the puzzle every time a logical operator is attempted,
        # whether or not it was successful
        self.cost_per_attempted_application = False
        # If True, increase the cost of the puzzle every time a logical operator is requested,
        # whether or not it was successful, and no matter how many times it was attempted during that request
        self.cost_per_requested_application = False

        # If True, increase the count ofthe operator every time it matches a set.
        self.count_per_matching_set = True
        # If True, increase the count ofthe operator every time it has a successful appliction (no matter how many sets).
        self.count_per_matching_use = False
        # If True, increase the cost of the puzzle every time a logical operator is attempted, successful or not
        self.count_per_attempted_application = False
        # If True, increase the cost of the puzzle every time a logical operator is requested, used or not
        self.count_per_requested_application = False

        # Keep track of how to simplify boards and board sets

        # Simplify boards using the free operators given any opportunity
        self.simplify = True
        # Simplify the initial board before sending back to the client
        self.simplify_initial_board = True
        # Prune invalid boards for the user, or send them back showing how they're invalid?
        self.prune_invalid_boards = False

        # Keep track of what information to print

        # If True, log all boards, otherwise, log only solved boards
        self.log_all_boards = True
        # TODO MAL move configuration in here
        # self.verbosity = 0

        self.goal_cell_name = None

        self.apply_config_from_name()
        self.verify()

    def apply_config_from_name(self):
        """ Parsing the puzzle name from the logger, apply required configuration. """
        if not self.log:
            return
        name = self.log.getName()
        if name:
            parameters = parse_name_config(name)
            if 'select_ops_upfront' in parameters:
                # If we are selecting logical operators up front, they can't be changed later in the game
                self.rules['canChangeLogicalOperators'] = False
            elif 'costlyops' in parameters:
                # Get the part specifying the costly operations
                self.rules['specializedCostlyOperations'] = True
                # The ops themselves are verified later via self.verify
                self.costly_operations = parameters['costlyops']

        if 'canChangeLogicalOperators' not in self.rules:
            # They can be changed, and we have an additional action (applyops) to support that
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
        logger_dict = self.log.get_simple_json_repr()
        for k in logger_dict.keys():
            json_dict[k] = logger_dict[k]
        if self.actions:
            json_dict['availableActions'] = self.actions
        if self.rules:
            json_dict['rules'] = self.rules
            if 'specializedCostlyOperations' in self.rules:
                json_dict['costlyOperations'] = self.costly_operations
        return json_dict

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
            Returns:
                False (unneeded, but to indicate that the operator should not terminate).
        """
        self.log.logOperator(op, msg2, board, False, False)
        # traceback.print_stack(file=sys.stdout)
        return False

    def match_set_operation(self, op, msg2, board):
        """ Use the logger that adds the cost if we need to increase our cost every matching set.
        This function is only called when a set has been matched (internally) and the logical operation triggered successfully.

        Args:
            op: the internal string name of the operator called, to be printed at verbosity level 1
            msg2: a string message to be printed at verbosity 2
            board: a Board to use to print the state string at verbosity level 3
        Returns:
            True if the operator should terminate after this operation.
        """
        # Cost it if we are costing per matching set AND it's not a free operation
        cost_it = False if op in self.free_operations else True
        self.log.logOperator(
            op, f'successful application per matching set. {msg2}', board,
            self.count_per_matching_set,
            cost_it & self.cost_per_matching_set)

        return self.terminate_on_successful_operation

    def complete_operation(self, op, msg2, board, affected_board):
        """ Only add the cost at this point if we're not increasing our cost for every matching set.
        Return affected_board to indicated whether the operation did affect the board.
        This function is called when an operation is attempted, whether or not it modified the board.

        Args:
            op: the internal string name of the operator called, to be printed at verbosity level 1
            msg2: a string message to be printed at verbosity 2
            board: a Board to use to print the state string at verbosity level 3
            affected_board: a boolean that describes whether the operation affected the Board
        Returns:
            affected_board (unneeded, but to indicate whether the operator should terminate).
        """
        # Cost it if it's not a free operation
        cost_it = False if op in self.free_operations else True
        # Cost on completion if costing any application of a logical operator
        self.log.logOperator(
            op, f'attempted application. {msg2}', board,
            self.count_per_attempted_application,
            cost_it & self.cost_per_attempted_application)
        if affected_board:
            # Cost on successful application
            self.log.logOperator(
                op, f'successful application. {msg2}', board,
                self.count_per_matching_use,
                cost_it & self.cost_per_matching_use)

        return affected_board

    def log_operation_request(self, ops, msg2, board):
        """ Use the logger that adds the cost if we need to increase our cost every request.
        This function is called after a logical_solve.

        Args:
            ops: the list of internal string names of the operators called, to be printed at verbosity level 1
            msg2: a string message to be printed at verbosity 2
            board: a Board to use to print the state string at verbosity level 3
                We replace this argument with
        Returns:
            True (unneeded, but to indicate that the operator should terminate).
        """
        for op in ops:
            cost_it = False if op in self.free_operations else True
            self.log.logOperator(
                op, f'requested application. {msg2}', board,
                self.count_per_requested_application,
                cost_it & self.cost_per_requested_application)
            # traceback.print_stack(file=sys.stdout)
        return self.terminate_on_successful_operation

    def debug_print(self, msg1, msg2, board):
        """ Over-use a convenient function to do level 1, 2, 3 verbosity printing.
        """
        self.log.logOperator(msg1, msg2, board, False, False)


defaultConfig = ConfigurationData()
