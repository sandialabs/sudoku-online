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


# operator cost constants
COST_INCLUSION = 100
COST_EXCLUSION = 100
COST_POINTING_PAIRS = 250
COST_NAKED_PAIRS = 500
COST_HIDDEN_PAIRS = 1200
COST_POINTING_TRIPLES = 1300
COST_NAKED_TRIPLES = 1400
COST_HIDDEN_TRIPLES = 1600
COST_XWINGS = 1600
COST_YWINGS = 1600
COST_XYZWINGS = 1600
COST_NAKED_QUADS = 4000
COST_HIDDEN_QUADS = 5000

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
        self.operators_use_count = {
            'inclusion': 0,
            'exclusion': 0,
            'pointingpairs': 0,
            'nakedpairs': 0,
            'hiddenpairs': 0,
            'pointingtriples': 0,
            'nakedtriples': 0,
            'xwings': 0,
            'hiddentriples': 0,
            'ywings': 0,
            'xyzwings': 0,
            'nakedquads': 0,
            'hiddenquads': 0
        }

    def logOperator(self, operator, board_state):

        self.board_state_list.append(board_state)
        self.num_operators += 1
        print('operator', operator)
        self.operators_use_list.append(operator)

        operator_count = self.operators_use_count[operator]
        self.operators_use_count[operator] = operator_count + 1

        if operator == 'inclusion':
            self.difficulty_score += COST_INCLUSION

        if operator == 'exclusion':
            self.difficulty_score += COST_EXCLUSION

        if operator == 'pointingpairs':
            self.difficulty_score += COST_POINTING_PAIRS

        if operator == 'nakedpairs':
            self.difficulty_score += COST_NAKED_PAIRS

        if operator == 'hiddenpairs':
            self.difficulty_score += COST_HIDDEN_PAIRS

        if operator == 'pointingtriples':
            self.difficulty_score += COST_POINTING_TRIPLES

        if operator == 'nakedtriples':
            self.difficulty_score += COST_NAKED_TRIPLES

        if operator == 'hiddentriples':
            self.difficulty_score += COST_HIDDEN_TRIPLES

        if operator == 'xwings':
            self.difficulty_score += COST_XWINGS

        if operator == 'ywings':
            self.difficulty_score += COST_YWINGS

        if operator == 'xyzwings':
            self.difficulty_score += COST_XYZWINGS

        if operator == 'nakedquads':
            self.difficulty_score += COST_NAKED_QUADS

        if operator == 'hiddenquads':
            self.difficulty_score += COST_HIDDEN_QUADS

    def setPuzzle(self, puzzle):
        self.puzzle = puzzle

    def getPuzzle(self):
        return self.puzzle.getPuzzle()

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


#    def printCSV(self):
#        file_name = 'logs.csv'
#        headers = []
#        operators_use_count = self.operators_use_count
#        num_headers = 0
#        puzzle_already_logged = False
#
#        if not os.path.isfile(file_name):
#            headers = ['puzzle',
#                       'solution',
#                       'score',
#                       'difficulty',
#                       'order of operators']
#            for key in operators_use_count.keys():
#                headers.append('num ' + key)
#
#            headers.append('board states')
#
#            num_headers = len(headers)
#
#            f = open(file_name, "w+")
#            for i in range(num_headers+1):
#                if i == num_headers:
#                    f.write('\n')
#                elif i == num_headers - 1:
#                    f.write(headers[i])
#                else:
#                    f.write(headers[i]+',')
#            f.close()
#        else:
#            f = open(file_name)
#            csv_f = csv.reader(f)
#            for row in csv_f:
#                if self.getPuzzle() == row[0].replace('\'',''):
#                    puzzle_already_logged = True
#            f.close()
#
#        if puzzle_already_logged:
#            print('already logged this puzzle')
#        else:
#            f = open(file_name, "a+")
#
#            f.write('\'' + self.getPuzzle() + '\',')
#            f.write('\'' + self.getSolution() + '\',')
#            f.write(str(self.difficulty_score) + ',')
#            f.write(self.getDifficultyLevel() + ',')
#
#            for operator in self.operators_use_list:
#                f.write(operator + ';')
#
#            f.write(',')
#            for key in self.operators_use_count.keys():
#                f.write(str(operators_use_count[key]) + ',')
#
#            state_string = '\''
#            for state in self.board_state_list:
#                state_string += state + '\''+':'
#            #print('state_string')
#            #print(state_string)
#            os.write(f.fileno(),state_string)
#            f.flush()
#            os.fsync(f.fileno())
#
#            #f.flush()
#            #os.fsync(f.fileno())
#            #f.write('!!!!!!\n')
#
#            f.close()
