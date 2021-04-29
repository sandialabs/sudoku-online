#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Michael Darling, Shelley Leger, Melissa Ginaldi
Sandia National Laboratories
April 5, 2020

Logging and scoring system for Sudoku solver
"""
import board_update_descriptions
import board

import os.path
import csv
import json

import logging
logger = logging.getLogger(__name__)

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
        self.solution = str(None)
        self.solution_state = str(None)
        self.difficulty_score = 0

        self.board_updates = []
        # operators_use_count provides a dict of each operator that was used and
        # the number of times they were applied.
        self.operators_use_count = dict()
        self.operators_called_count = dict()
        for action in board_update_descriptions.board_update_options.keys():
            self.operators_use_count[action] = 0
            self.operators_called_count[action] = 0

    def logOperator(self, operator, phase, msg_str=None, board=None, count_operator=True, cost_operator=True):
        """ Log an application of an operator to a board state, increasing the cost of the operator ot be incurred.

            Args:
                operator: the internal string name of the operator called, to be logged
                msg_str: a string message to be logged
                board: a Board to use to print the state string for the log
                count_operator: a boolean that describes whether the operation should be counted
                cost_operator: a boolean that describes whether the operation should be costed
        """
        state = {}
        state["operator"] = str(operator)
        state["phase"] = str(phase)
        state["board"] = board.getStateStr(True, False)
        state["increment_operator_count"] = count_operator
        state["increase_cost"] = cost_operator
        state["total_uncertainty"] = board.countUncertainValues()
        state["cellbased_associated_uncertainty"] = {}
        state["max_uncertain_cell"] = None
        for cell in board.getUncertainCells():
            uncertain_count = board.countAssociatedUncertainValuesGivenUncertainCell(cell)
            state["cellbased_associated_uncertainty"][cell.getIdentifier()] = uncertain_count
            if ((not state["max_uncertain_cell"])
                or uncertain_count > state["max_uncertain_cell"]["count"]):
                state["max_uncertain_cell"] = {"id": cell.getIdentifier(), "values": cell.getValues(), "count": uncertain_count}
        self.board_updates.append(state)

        if phase == "call":
            # Count every called operator
            self.operators_called_count[operator] +=1
        if count_operator:
            # Only count the operator if we're told to (essentially, at the set level)
            self.operators_use_count[operator] += 1
        if cost_operator:
            # Update the cost if we're told to (essentially, if the operator is not free)
            self.difficulty_score += board_update_descriptions.board_update_options[operator]["cost"]

        logger.debug("operator %s (phase %s) Message %s Board %s", str(operator), str(phase), str(msg_str), str(board.getStateStr(True, False)))

    def setSolution(self, sboard):
        self.solution = sboard.getStateStr(False, False, "")
        self.invalid_cells = sboard.invalidCells() # This returns a list of str identifiers

        if sboard.isSolved():
            self.solution_state = "solved"
        elif self.invalid_cells:
            self.solution_state = "insoluble"
        else:
            self.solution_state = "partial"

    def getDifficultyLevel(self):
        score = self.difficulty_score

        if score <= SCORE_BEGINNER:
            return "beginner"
        if score <= SCORE_EASY:
            return "easy"
        if score <= SCORE_MEDIUM:
            return "medium"
        if score <= SCORE_TRICKY:
            return "tricky"
        if score <= SCORE_FIENDISH:
            return "fiendish"
        if score <= SCORE_DIABOLICAL:
            return "diabolical"

    def get_simple_json_repr(self):
        """ Return a log dictionary representing the state of this SudokuLogger object (the minimal information we want saved).
        """
        game = {
            "name": self.name,
            "solution_state": self.solution_state,
            "puzzle": self.puzzle,
            "cost": self.difficulty_score,
            "level": self.getDifficultyLevel(),
            "solution": self.solution,
        }
        return game

    def get_full_json_repr(self):
        """ Return a log dictionary representing the state of this SudokuLogger object (all the information we want saved).
        """
        game = self.get_simple_json_repr()
        for key in self.operators_use_count.keys():
            game[f"num_successful_{key}"] = self.operators_use_count[key]
        for key in self.operators_use_count.keys():
            game[f"num_called_{key}"] = self.operators_called_count[key]
        game["updates"] = self.board_updates

        return game

    def printLogJSON(self):
        """ Print the json log."""
        append_to_file = False
        file_name = "game_logs.json"
        logs = []

        if os.path.isfile(file_name):
            append_to_file = True
            with open(file_name) as logfile:
                logs = json.load(logfile)

            log_to_replace = None
            for log in logs:
                if "puzzleName" in log and log["puzzleName"] == self.name:
                    logger.info("Puzzle %s already logged. Overwriting.", self.puzzle)
                    # We want to rewrite the entire log file because this puzzle was already there
                    append_to_file = False
                    log_to_replace = log
                    break
            if log_to_replace:
                logs.remove(log_to_replace)

        game = self.get_full_json_repr()
        logs.append(game)

        with open(file_name, "w") as logfile:
           json.dump(logs, logfile, indent=4)

        return False

    def printCSV(self):
        file_name = "logs.csv"
        headers = []
        operators_use_count = self.operators_use_count
        num_headers = 0
        puzzle_already_logged = False

        if not os.path.isfile(file_name):
            headers = ["Puzzle Name",
                        "Solution Type",
                        "Starting State",
                        "Score",
                        "Difficulty",
                        "Ending State"]
            for key in self.operators_called_count.keys():
                headers.append("Number of called "+ key)
            for key in operators_use_count.keys():
                 headers.append("Number of successful " + key + " uses")
            headers.append("All The Details")
            num_headers = len(headers)

            f = open(file_name, "w+")
            for i in range(num_headers+1):
                if i == num_headers:
                     f.write("\n")
                elif i == num_headers - 1:
                    f.write(headers[i])
                else:
                    f.write(headers[i]+",")
            f.close()
        else:
            f = open(file_name)
            csv_f = csv.reader(f)
            for row in csv_f:
                if self.puzzle == row[1].replace("'",""):
                    puzzle_already_logged = True
            f.close()

        if puzzle_already_logged:
            logger.info("Already logged this puzzle. Adding another.")
        f = open(file_name, "a+")

        f.write(self.name + ", ")
        f.write(self.solution_state + ", ")
        f.write(self.puzzle + ", ")
        f.write(str(self.difficulty_score) + ", ")
        f.write(self.getDifficultyLevel() + ", ")
        f.write(self.solution + ", ")

        for key in self.operators_called_count.keys():
            f.write(str(self.operators_called_count[key])+ ", ")

        for key in self.operators_use_count.keys():
            f.write(str(operators_use_count[key]) + ", ")

        # Could write board_updates also
        f.write("\n")

        f.close()
