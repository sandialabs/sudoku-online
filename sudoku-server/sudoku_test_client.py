#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Shelley Leger
Sandia National Laboratories
July 2, 2020

Lightweight sudoku client for sudoku online testing.
"""
import requests
import json
from flask import jsonify
import board_update_descriptions


def do_single_test(dbg_message, success_func, req_func):
    """ Ensure that results are as expected per success_func, which takes in the json results expected. """
    print(f"Testing {dbg_message}.")
    res = req_func()
    if not res.ok:
        print(f"Failed to get result {dbg_message} but got {res}.")
        return
    result = res.json()
    if success_func(result):
        print(f"PASSED TEST {dbg_message}.")
    else:
        print(f"Failed succes check for {dbg_message}.")
        print(f"Results are {result}.")
    print(json.dumps(result))
    return result


def do_tests():
    boardname = "underconstrained1"
    msg = f"getting specific {boardname}"
    do_single_test(msg,
                   lambda d_board: "puzzleName" in d_board and d_board["puzzleName"] == boardname,
                   lambda: requests.post("http://localhost:5000/sudoku/request/initialBoard",
                                         json={"name": boardname,
                                               "degree": 3}))

    do_single_test(f"getting a random board",
                   lambda d_board: ("puzzleName" in d_board),
                   lambda: requests.get("http://localhost:5000/sudoku/request/initialBoard"))

    # MAL TODO use appropriate paths for these tests
    with open("../tests/json/fiendish2-5788010997871579626.pivot-1-4.json") as f:
        action = json.load(f)
    do_single_test(f"pivot action",
                   lambda d_array: (len(d_array) == 3),
                   lambda: requests.post(
                       "http://localhost:5000/sudoku/request/evaluate_cell_action", json=action))

    with open("../tests/json/fiendish2-5788010997871579626.assign-1-4-to6.json") as f:
        action = json.load(f)
    do_single_test(f"assign action",
                   lambda d_array: (len(d_array) == 2),
                   lambda: requests.post(
                       "http://localhost:5000/sudoku/request/evaluate_cell_action", json=action))

    with open("../tests/json/fiendish2-5788010997871579626.exclude-1-4-rm6.json") as f:
        action = json.load(f)
    do_single_test(f"exclude action",
                   lambda d_array: (len(d_array) == 2),
                   lambda: requests.post(
                       "http://localhost:5000/sudoku/request/evaluate_cell_action", json=action))

    do_single_test(f"list logical operators",
                   lambda d_list: (len(d_list) == len(
                       board_update_descriptions.operators_description.keys()) - 1),
                   lambda: requests.get("http://localhost:5000/sudoku/request/list_logical_operators"))

    do_single_test(f"list cell actions",
                   lambda d_list: (len(d_list) == len(
                       board_update_descriptions.basic_actions_description.keys())),
                   lambda: requests.get("http://localhost:5000/sudoku/request/list_cell_actions"))

    hard4_board = do_single_test(f"getting hard4 board for future tests",
                                 lambda d_board: (("puzzleName" in d_board)
                                                  and (d_board["puzzleName"] == "hard4")),
                                 lambda: requests.post("http://localhost:5000/sudoku/request/initialBoard",
                                                       json={"name": "hard4", "degree": 3}))

    # MAL TODO consider better success functions from here on out.
    new_req = {"board": hard4_board, "action": {
        "action": "applyops", "operators": ["inclusion"]}}
    just_inclusion = do_single_test(f"applying inclusion to hard4",
                                    lambda d_list: ((len(d_list) == 1)
                                                    and ("assignments" in d_list[0])
                                                    and (d_list[0]["assignments"][0] == [2, None, None, 5, None, 8, None, 0, 1])),
                                    lambda: requests.post(
                                        "http://localhost:5000/sudoku/request/evaluate_cell_action",
                                        json=new_req))

    inclusion_squared = None
    if just_inclusion:
        new_req2 = {"board": just_inclusion[0], "action": {
            "action": "applyops", "operators": ["inclusion"]}}
        inclusion_squared = do_single_test(f"applying inclusion to hard4 a second time",
                                        lambda d_list: ((len(d_list) == 1)
                                                        and ("assignments" in d_list[0])
                                                        and (d_list[0]["assignments"] == just_inclusion[0]["assignments"])),
                                        lambda: requests.post(
                                            "http://localhost:5000/sudoku/request/evaluate_cell_action",
                                            json=new_req2))

    logical_ops = None
    if inclusion_squared:
        new_req3 = {"board": inclusion_squared[0], "action": {
            "action": "applyops", "operators": ["inclusion", "pointingpairs"]}}
        logical_ops = do_single_test(f"applying inclusion and pointing pairs to hard4 (after inclusion 2x)",
                                    lambda d_list: ((len(d_list) == 1)
                                                    and ("assignments" in d_list[0])
                                                    and (d_list[0]["assignments"] == [[2, 3, 4, 5, 7, 8, 6, 0, 1], [8, 0, 6, 1, 2, 4, 3, 7, 5], [7, 1, 5, 3, 6, 0, 8, 2, 4], [5, 4, 8, 6, 3, 7, 0, 1, 2], [3, 2, 1, 8, 0, 5, 4, 6, 7], [0, 6, 7, 4, 1, 2, 5, 3, 8], [6, 5, 2, 7, 4, 3, 1, 8, 0], [4, 7, 3, 0, 8, 1, 2, 5, 6], [1, 8, 0, 2, 5, 6, 7, 4, 3]])),
                                    lambda: requests.post(
                                        "http://localhost:5000/sudoku/request/evaluate_cell_action",
                                        json=new_req3))

    boards = []
    gamename = "test_game1_4"
    boards = do_single_test(f"getting game {gamename}",
                   lambda d_list: ((len(d_list) == 4)
                                    and ("displayName" in d_list[2])
                                    and (d_list[2]["displayName"] == "hard4")),
                   lambda: requests.get(
                       f"http://localhost:5000/sudoku/request/boardsForGame/{gamename}"))

    for b in boards:
        msg = f"applying inclusion from selected {gamename} one at a time on board {b}"
        do_single_test(msg,
                       lambda d_boards: ((len(d_boards) > 0)
                                        and ("puzzleName" in d_boards[0])
                                        and ("puzzleName" in b)
                                        and (d_boards[0]["puzzleName"] == b["puzzleName"])),
                       lambda: requests.post("http://localhost:5000/sudoku/request/evaluate_cell_action",
                                             json={"board": b, "action": {
                                                   "action": "applyops", "operators": ["inclusion"]}}))

    boards = do_single_test(f"getting random game",
                            lambda d_list: (len(d_list) > 0),
                            lambda: requests.get(
                                "http://localhost:5000/sudoku/request/boardsForGame/get_me_something_random"))

    for b in boards:
        msg = f"applying inclusion from random game one at a time on board {b} "
        do_single_test(msg,
                       lambda d_boards: ((len(d_boards) > 0)
                                        and ("puzzleName" in d_boards[0])
                                        and ("puzzleName" in b)
                                        and (d_boards[0]["puzzleName"] == b["puzzleName"])),
                       lambda: requests.post("http://localhost:5000/sudoku/request/evaluate_cell_action",
                                             json={"board": b, "action": {
                                                   "action": "applyops", "operators": ["inclusion"]}}))

    boardname = "pointing_pair_test...select_ops_upfront"
    result_logical_ops_upfront = do_single_test(
        f"get board for logical ops upfront selection",
        lambda d_board: (("puzzleName" in d_board)
                         and (d_board["puzzleName"] == boardname)
                         and ("availableActions" in d_board and d_board["availableActions"] == ["selectops"])
                         and ("rules" in d_board and "canChangeLogicalOperators" in d_board["rules"])
                         and (d_board["rules"]["canChangeLogicalOperators"] == True)
                         ),
        lambda: requests.post("http://localhost:5000/sudoku/request/initialBoard",
                              json={"name": "pointing_pair_test...select_ops_upfront",
                                    "degree": 3}))

    log_req = {"board": result_logical_ops_upfront, "action": {
        "action": "selectops", "operators": ["inclusion", "pointingpairs"]}}
    result_applying_ops_upfront_noywings = do_single_test(
        f"apply inclusion, pointing pairs to board for logical ops upfront test, and ensure logicalops no longer selectable",
        lambda d_boards: ((len(d_boards) == 1)
                          and ("puzzleName" in d_boards[0])
                          and (d_boards[0]["puzzleName"] == boardname)
                          and ("rules" in d_boards[0])
                          and ("canChangeLogicalOperators" in d_boards[0]["rules"])
                          and (d_boards[0]["rules"]["canChangeLogicalOperators"] == False)
                          and ("availableActions" in d_boards[0])
                          and (set(d_boards[0]["availableActions"]) == set(board_update_descriptions.basic_actions_description.keys()))
                          and ("assignments" in d_boards[0])
                          and (d_boards[0]["assignments"] != [3, 0, 6, 8, 4, 2, 5, 7, 1], [1, 4, 5, 0, 7, 6, 8, 3, 2], [8, 7, 2, 1, 3, 5, 4, 0, 6], [7, 6, 1, 4, 0, 8, 3, 2, 5], [4, 2, 8, 3, 5, 1, 7, 6, 0], [0, 5, 3, 2, 6, 7, 1, 4, 8], [6, 8, 0, 7, 1, 3, 2, 5, 4], [5, 1, 7, 6, 2, 4, 0, 8, 3], [2, 3, 4, 5, 8, 0, 6, 1, 7])),
        lambda: requests.post(
            "http://localhost:5000/sudoku/request/evaluate_cell_action",
            json=log_req))

    log_req = {"board": result_logical_ops_upfront, "action": {
        "action": "selectops", "operators": ["inclusion", "pointingpairs", "ywings"]}}
    result_applying_ops_upfront_with_ywings = do_single_test(
        f"apply inclusion, pointing pairs, ywings to board for logical ops upfront test",
        lambda d_boards: ((len(d_boards) == 1)
                          and ("puzzleName" in d_boards[0])
                          and (d_boards[0]["puzzleName"] == boardname)
                          and ("availableActions" in d_boards[0])
                          and (set(d_boards[0]["availableActions"]) == set(board_update_descriptions.basic_actions_description.keys()))
                          and ("assignments" in d_boards[0])
                          and (d_boards[0]["assignments"] == [3, 0, 6, 8, 4, 2, 5, 7, 1], [1, 4, 5, 0, 7, 6, 8, 3, 2], [8, 7, 2, 1, 3, 5, 4, 0, 6], [7, 6, 1, 4, 0, 8, 3, 2, 5], [4, 2, 8, 3, 5, 1, 7, 6, 0], [0, 5, 3, 2, 6, 7, 1, 4, 8], [6, 8, 0, 7, 1, 3, 2, 5, 4], [5, 1, 7, 6, 2, 4, 0, 8, 3], [2, 3, 4, 5, 8, 0, 6, 1, 7])),
        lambda: requests.post(
            "http://localhost:5000/sudoku/request/evaluate_cell_action",
            json=log_req))

    if result_applying_ops_upfront_noywings:
        log_req = {"board": result_applying_ops_upfront_noywings[0], "action": {
            "action": "pivot", "cell": [0, 0]},
            "evaluate_cell_actions": ["inclusion", "pointingpairs"]}
    result = do_single_test(
        f"pivot on cell, applying selected ops inclusion, pointing pairs to board for logical ops upfront test after first inclusion, pointing_pairs test",
        lambda d_boards: ((len(d_boards) == 4)
                          and ("puzzleName" in d_boards[1])
                          and (d_boards[1]["puzzleName"] == boardname)
                          and ("availableActions" in d_boards[0])
                          and (set(d_boards[1]["availableActions"]) == set(board_update_descriptions.basic_actions_description.keys()))
                          and ("assignments" in d_boards[1])
                          and (d_boards[1]["assignments"] == [3, 0, 6, 8, 4, 2, 5, 7, 1], [1, 4, 5, 0, 7, 6, 8, 3, 2], [8, 7, 2, 1, 3, 5, 4, 0, 6], [7, 6, 1, 4, 0, 8, 3, 2, 5], [4, 2, 8, 3, 5, 1, 7, 6, 0], [0, 5, 3, 2, 6, 7, 1, 4, 8], [6, 8, 0, 7, 1, 3, 2, 5, 4], [5, 1, 7, 6, 2, 4, 0, 8, 3], [2, 3, 4, 5, 8, 0, 6, 1, 7])),
        lambda: requests.post(
            "http://localhost:5000/sudoku/request/evaluate_cell_action",
            json=log_req))

    gamename = "test_game_ptgprs"
    boards = do_single_test(f"getting game {gamename}",
                            lambda d_list: ((len(d_list) == 3)
                                            and ("puzzleName" in d_list[2])
                                            and (d_list[2]["puzzleName"] == "pointing_pair_test...goal=B1")),
                            lambda: requests.get(
                                f"http://localhost:5000/sudoku/request/boardsForGame/{gamename}"))

    for b in boards:
        msg = f"applying inclusion from {gamename} one at a time to board {b}"
        do_single_test(msg,
                       lambda d_boards: ((len(d_boards) > 0)
                                        and ("puzzleName" in d_boards[0])
                                        and ("puzzleName" in b)
                                        and (d_boards[0]["puzzleName"] == b["puzzleName"])),
                       lambda: requests.post("http://localhost:5000/sudoku/request/evaluate_cell_action",
                                             json={"board": b, "action": {
                                                   "action": "applyops", "operators": ["inclusion"]}}))

    boardname = "pointing_pair_test...goal=B1"
    accessible_cells = do_single_test(
        f"get board for goal cell test",
        lambda d_board: (("puzzleName" in d_board)
                         and (d_board["puzzleName"] == boardname)
                         and ("goalCell" in d_board)
                         and ([1, 0] == d_board["goalCell"])),
        lambda: requests.post("http://localhost:5000/sudoku/request/initialBoard",
                              json={"name": boardname,
                                    "degree": 3}))

    boardname = "pointing_pair_test...goal=B1"
    accessible_cells = do_single_test(
        f"get board for accessible_cells test",
        lambda d_board: (("puzzleName" in d_board)
                         and (d_board["puzzleName"] == boardname)
                         and ("accessibleCells" in d_board)
                         and ([1, 0] not in d_board["accessibleCells"])
                         and ([1, 7] not in d_board["accessibleCells"])
                         and ([5, 0] not in d_board["accessibleCells"])
                         and ([0, 1] not in d_board["accessibleCells"])
                         ),
        lambda: requests.post("http://localhost:5000/sudoku/request/initialBoard",
                              json={"name": boardname,
                                    "degree": 3}))

    log_req = {"board": accessible_cells, "action": {
        "action": "pivot", "cell": [4, 1]},
        "evaluate_cell_actions": ["inclusion", "pointingpairs"]}
    do_single_test(
        f"tried to pivot on valid cell",
        lambda d_boards: ((len(d_boards) == 4)
                          and ("puzzleName" in d_boards[0])
                          and (d_boards[0]["puzzleName"] == boardname)
                          and ("accessibleCells" in d_boards[0])
                          and ([1, 0] not in d_boards[0]["accessibleCells"])),
        lambda: requests.post("http://localhost:5000/sudoku/request/evaluate_cell_action",
                              json=log_req))

    gamename = "pilot_test_a_board"
    boards = do_single_test(f"getting game {gamename}",
                            lambda d_list: ((len(d_list) == 2)
                                            and ("puzzleName" in d_list[0])
                                            and (d_list[0]["puzzleName"] == "test7-i26e36hp10...goal=C6...name=Pilot Test Board...question=Can C6 be a 7?")),
                            lambda: requests.get(
                                f"http://localhost:5000/sudoku/request/boardsForGame/{gamename}"))

    for b in boards:
        msg = f"getting from {gamename} one at a time; board {b}"
        do_single_test(msg,
                       lambda d_boards: ((len(d_boards) > 0)
                                        and ("puzzleName" in d_boards[0])
                                        and ("puzzleName" in b)
                                        and (d_boards[0]["puzzleName"] == b["puzzleName"])),
                       lambda: requests.post("http://localhost:5000/sudoku/request/evaluate_cell_action",
                                             json={"board": b, "action": {
                                                   "action": "applyops", "operators": ["inclusion"]}}))

do_tests()
