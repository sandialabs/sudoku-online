#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Michael Darling
Sandia National Laboratories
April 5, 2020

Logging and scoring system for Sudoku solver
"""
import os.path
import csv
import json
import pprint
import board_update_descriptions

verbosity = 0


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


# difficulty score constants
SCORE_BEGINNER = 4500
SCORE_EASY = 5500
SCORE_MEDIUM = 6900
SCORE_TRICKY = 9300
SCORE_FIENDISH = 14000
SCORE_DIABOLICAL = 25000


class SudokuLogger():

    def __init__(self, puzzle=None, name=None):
        self.puzzle = puzzle
        self.name = name
        self.solution = ''
        self.board_state_list = []
        # a list of each operator applictaion so we can keep track of the
        # order that they were applied.
        self.operators_use_list = []
        self.difficulty_score = 0

        # operators_use_count provides a dict of each operator that was used and
        # the number of times they were applied.
        self.operators_use_count = dict()
        for action in board_update_descriptions.board_update_options.keys():
            self.operators_use_count[action] = 0

    def logOperator(self, operator, verbosity1_str=None, board=None, count_operator=True, cost_operator=True):
        """ Log an application of an operator to a board state, increasing the cost of the operator ot be incurred.
            Each argument is printed at increasing verbosity levels.

            Args:
                op: the internal string name of the operator called, to be printed at verbosity level 1
                msg2: a string message to be printed at verbosity 2
                board: a Board to use to print the state string at verbosity level 3
                affected_board: a boolean that describes whether the operation affected the Board
        """
        if count_operator:
            # Only count the operator if we're told to (essentially, at the set level)
            self.operators_use_count[operator] += 1
            verbosity1_str = f'Logging {verbosity1_str}'
            if board:
                self.board_state_list.append(board.getStateStr(True, False))
            self.operators_use_list.append(operator)
        if cost_operator:
            # Update the cost if we're told to (essentially, if the operator is not free)
            self.difficulty_score += board_update_descriptions.board_update_options[operator]['cost']
            verbosity1_str = f'Costing {verbosity1_str}'

        if(verbosity > 0 and operator):
            print('operator', operator)
        if(verbosity > 1 and verbosity1_str):
            print(verbosity1_str)
        if(verbosity > 2 and board):
            print(board.getStateStr(True, False))

    def setPuzzle(self, puzzle):
        self.puzzle = puzzle

    def getPuzzle(self):
        return self.puzzle

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setSolution(self, sboard):
        self.solution = {
            'assignments': sboard.getStateStr(False, False, ''),
            'invalid_cells': sboard.invalidCells()
        }
        if sboard.isSolved():
            self.solution['solution_state'] = 'solved'
        elif self.solution['invalid_cells']:
            self.solution['solution_state'] = 'insoluble'
        else:
            self.solution['solution_state'] = 'partial'

    def getSolution(self):
        return self.solution

    def getDifficultyScore(self):
        return self.difficulty_score

    def getDifficultyLevel(self):
        score = self.difficulty_score

        if score <= SCORE_BEGINNER:
            return 'beginner'
        if score <= SCORE_EASY:
            return 'easy'
        if score <= SCORE_MEDIUM:
            return 'medium'
        if score <= SCORE_TRICKY:
            return 'tricky'
        if score <= SCORE_FIENDISH:
            return 'fiendish'
        if score <= SCORE_DIABOLICAL:
            return 'diabolical'

    def compare_json_to_self(self, log_dict):
        """ Given a log_dict, see if we came up with the same information as last time.
            Return True if log_dict represents the same information, and False if it differs.
        """
        try:
            assert self.getPuzzle() == log_dict['puzzle'], \
                'Should only call compare_json_to_self on data from the same puzzle'
            if (self.getSolution()['assignments'] != log_dict['solution']['assignments']
                or self.difficulty_score != log_dict['difficulty_score']
                or self.operators_use_list != log_dict['order_of_operators']
                or self.board_state_list != log_dict['board_states']
                    or self.name != log_dict['name']):
                return False

            if len(self.operators_use_count.keys()) != len([k for k in filter(lambda key: 'num_' in key, log_dict.keys())]):
                return False
            for key in self.operators_use_count.keys():
                if self.operators_use_count[key] != log_dict[f'num_{key}']:
                    return False
        except KeyError:
            return False

        return True

    def get_simple_json_repr(self):
        """ Return a log dictionary representing the state of this logger object (the minimal information we want saved).
        """
        game = {
            'puzzle': self.getPuzzle(),
            'puzzleName': self.getName(),
            'cost': self.getDifficultyScore(),
        }
        return game

    def get_full_json_repr(self):
        """ Return a log dictionary representing the state of this logger object (all the information we want saved).
        """
        game = self.get_simple_json_repr()

        # Repetition for script API compatibility for now.
        game['difficulty_score'] = self.getDifficultyScore(),
        game['name'] = self.getName(),

        game['solution'] = self.getSolution()
        game['difficulty_level'] = self.getDifficultyLevel()
        game['order_of_operators'] = self.operators_use_list
        game['board_states'] = self.board_state_list

        for key in self.operators_use_count.keys():
            game[f'num_{key}'] = self.operators_use_count[key]
        return game

    def printLogJSON(self):
        """ Print the json log."""
        append_to_file = False
        file_name = 'game_logs.json'
        logs = []

        if os.path.isfile(file_name):
            append_to_file = True
            with open(file_name) as file:
                logs = json.load(file)

            log_to_replace = None
            for log in logs:
                if log['puzzle'] == self.getPuzzle():
                    if self.compare_json_to_self(log):
                        # No need to try to log again.
                        if (verbosity > 1):
                            print(
                                f'puzzle {self.getPuzzle()} already logged. Returning.')
                        return True
                    else:
                        print(
                            f'puzzle {self.getPuzzle()} has differing statistics from the log file. Replacing in log file.')
                        # We want to rewrite the entire log file
                        append_to_file = False
                        log_to_replace = log
                        break
            if log_to_replace:
                logs.remove(log_to_replace)

        game = self.get_full_json_repr()
        logs.append(game)

        if append_to_file:
            with open(file_name, "r+") as file:
                logs = json.load(file)

                logs.append(game)
                file.seek(0)
                json_logs = json.dumps(logs, indent=4)

                file.write(json_logs)
        else:
            with open(file_name, "w") as file:
                json_logs = json.dumps(logs, indent=4)
                file.write(json_logs)

        return False


log = SudokuLogger()
