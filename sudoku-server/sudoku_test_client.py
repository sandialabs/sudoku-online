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

res = requests.post('http://localhost:5000/sudoku/request/initialBoard', json={"name": "underconstrained1",
                                                                               'degree': 3})
if res.ok:
    result = res.json()
    print(json.dumps(result))

res = requests.get('http://localhost:5000/sudoku/request/initialBoard')
if res.ok:
    result = res.json()
    print(json.dumps(result))

# MAL TODO use appropriate paths for these tests
with open('../tests/json/fiendish2-5788010997871579626.pivot-1-4.json') as f:
    action = json.load(f)
res = requests.post(
    'http://localhost:5000/sudoku/request/heuristic', json=action)
if res.ok:
    print(json.dumps(res.json()))

with open('../tests/json/fiendish2-5788010997871579626.assign-1-4-to6.json') as f:
    action = json.load(f)
res = requests.post(
    'http://localhost:5000/sudoku/request/heuristic', json=action)
if res.ok:
    print(json.dumps(res.json()))

with open('../tests/json/fiendish2-5788010997871579626.exclude-1-4-rm6.json') as f:
    action = json.load(f)
res = requests.post(
    'http://localhost:5000/sudoku/request/heuristic', json=action)
if res.ok:
    print(json.dumps(res.json()))

print("Trying to list heuristics")
res = requests.get('http://localhost:5000/sudoku/request/list_heuristics')
if res.ok:
    print(json.dumps(res.json()))

res = requests.post('http://localhost:5000/sudoku/request/initialBoard', json={"name": "test2-i24e40",
                                                                               'degree': 3})
if res.ok:
    result = res.json()
    print(json.dumps(result))

res = requests.post('http://localhost:5000/sudoku/request/initialBoard', json={"name": "test36-i30e33np2hp2yw1",
                                                                               'degree': 3})
if res.ok:
    result = res.json()
    print(json.dumps(result))

print("Interacting, testing logical ops")

res = requests.post('http://localhost:5000/sudoku/request/initialBoard', json={"name": "hard4",
                                                                               'degree': 3})
if res.ok:
    result = res.json()
    print(json.dumps(result))

new_req = {'board': result, 'action': {
    'action': 'applyops', 'operators': ['inclusion']}}
res = requests.post(
    'http://localhost:5000/sudoku/request/heuristic', json=new_req)
if res.ok:
    result2 = res.json()
    print(json.dumps(result2))

new_req2 = {'board': result2[0], 'action': {
    'action': 'applyops', 'operators': ['inclusion']}}
res = requests.post(
    'http://localhost:5000/sudoku/request/heuristic', json=new_req2)
if res.ok:
    result3 = res.json()
    print(json.dumps(result3))

new_req2 = {'board': result3[0], 'action': {
    'action': 'applyops', 'operators': ['inclusion', 'pointingpairs']}}
res = requests.post(
    'http://localhost:5000/sudoku/request/heuristic', json=new_req2)
if res.ok:
    result3 = res.json()
    print(json.dumps(result3))

# TODO MAL Consider trying to check whether result2 equals result3
