#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Michael Darling, Shelley Leger
Sandia National Laboratories
July 12, 2020

Scoring and dispatch system configuration data for sudoku game actions.
"""

import sudoku_logger
import copy
import board_update_descriptions

import logging
logger = logging.getLogger(__name__)


def parse_name_config(name, initial_config=None):
    """ Given a board name with embedded config information, return a dictionary mapping config variables to values. """
    config_dict = initial_config if initial_config is not None else {}
    if 'cost' not in config_dict:
        config_dict['cost'] = 0
    if not name:
        return config_dict

    parameters = name.split('...')
    assert len(parameters) > 0, "Was unable to get any data from name."
    config_dict['puzzleName'] = name
    config_dict['displayName'] = parameters[0]
    for param in parameters[1:]:
        if '=' in param:
            assigned = param.split('=')
            assert(len(
                assigned) == 2), f"Assumed that the parameter would only have one '=': key=value, not {assigned}."
            if ',' in assigned[1]:
                value_list = assigned[1].split(',')
                config_dict[assigned[0]] = value_list
            else:
                config_dict[assigned[0]] = assigned[1]
            logger.debug("Found %s to set to %s (from %s).", str(assigned[0]),
                         str(config_dict[assigned[0]]), str(param))
        else:
            config_dict[param] = True
            logger.debug("Found %s to set to %s (from %s).", str(param),
                         str(config_dict[param]), str(param))
    logger.info("Final config dict is %s (from %s)",
                str(config_dict), str(name))
    return config_dict


class ConfigurationData():
    """ Collect all the configuration data for a board and its SudokuLogger and the solver.
    """

    def __init__(self, puzzle=None, name=None, initial_config: dict = None):
        if name:
            name = name.strip()
        self.log = sudoku_logger.SudokuLogger(puzzle, name)

        # Keep track of any special rules for the board (see apply_config_from_name below)
        self.rules = {}

        # Keep track of parameters associated with the board
        self.parameters = initial_config if initial_config is not None else {}

        # Keep track of available actions and operators and how to cost them
        self.actions = [
            k for k in board_update_descriptions.actions_description.keys()]
        self.free_operations = ['exclusion']
        self.costly_operations = ['inclusion',
                                  'pointingpairs', 'nakedpairs', 'ywings']
        # Limiting costly_operations for the test
        # self.costly_operations = [op for op in
        #                           filter(lambda op: op not in self.free_operations,
        #                                  board_update_descriptions.operators_description.keys())]

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

        self.apply_config_from_name()
        self.verify()

    def setParam(self, key, value):
        """ Add the mapping to our parameters storage. """
        if key in self.parameters and self.parameters[key] != value:
            logger.info("Overwriting config parameters %s (which was %s) with %s",
                        str(key), str(self.parameters[key]), str(value))
        self.parameters[key] = value

    def getParam(self, key):
        """ Add the mapping to our parameters storage. """
        if key not in self.parameters:
            logger.info("Returning None from non-existent config parameter %s",
                        str(key))
            return None
        return self.parameters[key]

    def apply_config_from_name(self):
        """ Parsing the puzzle name from the SudokuLogger, apply required configuration. """
        if not self.log:
            return
        name = self.log.name
        if name:
            self.parameters = parse_name_config(name, self.parameters)
            if 'costlyops' in self.parameters:
                # Get the part specifying the costly operations
                self.rules['specializedCostlyOperations'] = True
                # The ops themselves are verified later via self.verify
                self.costly_operations = self.parameters['costlyops']
        self.verify()

    def copy(self):
        """ Return a deepcopy of myself. """
        return copy.deepcopy(self)
        # MAL TODO See if the logger is being deepcopied properly too and not getting all wound up

    def add_config_mappings_to_dict(self, json_dict):
        """ Add the config mappings that ought to be shared with the client to the board dictionary
            that will be sent via json. """
        if self.actions:
            json_dict['availableActions'] = self.actions
        if self.rules:
            json_dict['rules'] = self.rules
            if 'specializedCostlyOperations' in self.rules:
                json_dict['costlyOperations'] = self.costly_operations
        for key in self.parameters.keys():
            json_dict[key] = self.parameters[key]
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
        board_string = board.getStateStr(True, False) if board else None
        logger.debug("Logging: %s %s on %s", str(
            op), str(msg2), str(board_string))
        return False

    def adjust_cost(self, op):
        """ Alter the cost associated with this board by the incoming cost.
        """
        logger.info("Calling adjust_cost given op %s", str(op))
        if op in self.free_operations:
            return

        # Cost it if it's not a free operation
        if not "cost" in self.parameters:
            self.parameters["cost"] = 0
        cost = board_update_descriptions.board_update_options[op]["cost"]
        self.parameters["cost"] = self.parameters["cost"] + cost

    def match_set_operation(self, op, msg2, board):
        """ Use the SudokuLogger that adds the cost if we need to increase our cost every matching set.
        This function is only called when a set has been matched (internally) and the logical operation triggered successfully.

        Args:
            op: the internal string name of the operator called
            msg2: a string message
            board: the Board resulting after the op
        Returns:
            True if the operator should terminate after this operation.
        """
        self.log.logOperator(
            op, "single_match", f"successful application per matching set. {msg2}", board,
            self.count_per_matching_set)
        if self.cost_per_matching_set:
            self.adjust_cost(op)

        return self.terminate_on_successful_operation

    def complete_operation(self, op, msg2, board, affected_board):
        """ Only add the cost at this point if we're not increasing our cost for every matching set.
        Return affected_board to indicated whether the operation did affect the board.
        This function is called when an operation is attempted, whether or not it modified the board.

        Args:
            op: the internal string name of the operator called
            msg2: a string message
            board: the Board resulting after the op
            affected_board: a boolean that describes whether the operation affected the Board
        Returns:
            affected_board (unneeded, but to indicate whether the operator should terminate).
        """
        if affected_board:
            # Cost on successful application
            self.log.logOperator(
                op, "applied", f"successful application. {msg2}", board,
                self.count_per_matching_use)
            if self.cost_per_matching_use:
                self.adjust_cost(op)
        else:
            # Cost on completion if costing any application of a logical operator
            self.log.logOperator(
                op, "application_attempt", f"attempted application. {msg2}", board,
                self.count_per_attempted_application)
            if self.cost_per_attempted_application:
                self.adjust_cost(op)

        return affected_board

    def start_operation(self, op, board):
        """ This operatio never costs, but it logs when an operation starts.
        This function is called when an operation is attempted, whether or not it modified the board.

        Args:
            op: the internal string name of the operator called
            board: the Board as passed in
        Returns:
            None
        """
        self.log.logOperator(
            op, "call", f"attempted application.", board, False)

        return None

    def log_operations_request(self, ops, msg2, board):
        """ Use the logger that adds the cost if we need to increase our cost every request.
        This function is called after a logical_solve.

        Args:
            op: the internal string name of the operator called
            msg2: a string message
            board: the Board resulting after the op
        Returns:
            True (unneeded, but to indicate that the operator should terminate).
        """
        for op in ops:
            cost_it = False if op in self.free_operations else True
            self.log.logOperator(
                op, "request", f"requested application. {msg2}", board,
                self.count_per_requested_application)
            if self.cost_per_requested_application:
                self.adjust_cost(op)
            # traceback.print_stack(file=sys.stdout)
        return self.terminate_on_successful_operation

    def debug_print(self, msg1, msg2, board):
        """ Over-use a convenient function to do logging.
        """
        board_string = board.getStateStr(True, False) if board else None
        logger.debug("Logging: %s %s on %s", str(
            msg1), str(msg2), str(board_string))


defaultConfig = ConfigurationData()
