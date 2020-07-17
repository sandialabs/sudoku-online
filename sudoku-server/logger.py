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
import config_data

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

    @ classmethod
    def logOperatorProgress(cls, operator, verbosity1_str=None, board=None):
        """ Log that an operator made progress without logging a new application of the operator
            or causing the cost of the operator to be incurred.
            Each argument is printed at increasing verbosity levels."""
        if(verbosity > 0 and operator):
            print('operator', operator)
        if(verbosity > 1 and verbosity1_str):
            print(verbosity1_str)
        if(verbosity > 2 and board):
            print(board.getStateStr(True, False))

    def __init__(self, puzzle=None, name=None):
        self.puzzle = puzzle
        self.name = name
        self.solution = ''
        self.board_state_list = []
        self.num_operators = 0
        # a list of each operator applictaion so we can keep track of the
        # order that they were applied.
        self.operators_use_list = []
        self.difficulty_score = 0

        # operators_use_count provides a dict of each operator that was used and
        # the number of times they were applied.
        self.operators_use_count = dict()
        for action in config_data.board_update_options.keys():
            self.operators_use_count[action] = 0

    def logOperator(self, operator, verbosity1_str=None, board=None):
        """ Log that an application of an operator as respects a board state. """
        self.logOperatorProgress(operator, verbosity1_str, board)

        if board:
            self.board_state_list.append(board.getStateStr(True, False))
        self.num_operators += 1
        self.operators_use_list.append(operator)

        self.operators_use_count[operator] += 1
        self.difficulty_score += config_data.board_update_options[operator]['cost']

    def setPuzzle(self, puzzle):
        self.puzzle = puzzle

    def getPuzzle(self):
        return self.puzzle

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setSolution(self, solution):
        self.solution = solution

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
            if (self.getSolution() != log_dict['solution']
                or self.difficulty_score != log_dict['difficulty_score']
                # this is redundant with score
                or self.getDifficultyLevel() != log_dict['difficulty_level']
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

        game = {
            'puzzle': self.getPuzzle(),
            'name': self.getName(),
            'solution': self.getSolution(),
            'difficulty_score': self.difficulty_score,
            'difficulty_level': self.getDifficultyLevel(),
            'order_of_operators': self.operators_use_list,
            'board_states': self.board_state_list
        }

        for key in self.operators_use_count.keys():
            game[f'num_{key}'] = self.operators_use_count[key]

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
