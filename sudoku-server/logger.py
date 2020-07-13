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

# difficulty score constants
SCORE_BEGINNER = 4500
SCORE_EASY = 5500
SCORE_MEDIUM = 6900
SCORE_TRICKY = 9300
SCORE_FIENDISH = 14000
SCORE_DIABOLICAL = 25000


class SudokuLogger():

    def __init__(self, puzzle):
        self.puzzle = puzzle
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
        for action in config_data.operators_description.keys():
            self.operators_use_count[action] = 0

    def logOperator(self, operator, board_state):

        self.board_state_list.append(board_state)
        self.num_operators += 1
        print('operator', operator)
        self.operators_use_list.append(operator)

        operator_count = self.operators_use_count[operator]
        self.operators_use_count[operator] = operator_count + 1
        self.difficulty_score += config_data.operators_description[operator]['cost']

    def setPuzzle(self, puzzle):
        self.puzzle = puzzle

    def getPuzzle(self):
        return self.puzzle

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

    def printLogJSON(self):
        puzzle_already_logged = False
        file_exists = False
        file_name = 'game_logs.json'

        if os.path.isfile(file_name):
            print('is file')
            file_exists = True
            file = open(file_name)
            logs = json.load(file)

            for log in logs:
                if log['puzzle'] == self.getPuzzle():
                    print(log['puzzle'])
                    puzzle_already_logged = True

        if puzzle_already_logged:
            print('puzzle already logged')
            return True

        operators_use_count = self.operators_use_count
        operators_string = ''
        for operator in self.operators_use_list:
            operators_string += operator + ';'
        state_string = ''
        for state in self.board_state_list:
            state_string += state + ':'

        game = {
            'puzzle': self.getPuzzle(),
            'solution': self.getSolution(),
            'difficulty_score': self.difficulty_score,
            'difficulty_level': self.getDifficultyLevel(),
        }

        for key in operators_use_count.keys():
            game['num_' + key] = operators_use_count[key]

        game['order_of_operators'] = self.operators_use_list
        game['board_states'] = self.board_state_list

        if file_exists:
            with open(file_name, "r+") as file:
                logs = json.load(file)

                logs.append(game)
                file.seek(0)
                json_logs = json.dumps(logs, indent=4)

                file.write(json_logs)
        else:
            with open(file_name, "w") as file:
                json_logs = json.dumps([game], indent=4)
                file.write(json_logs)

        return False
