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

res = requests.post('http://localhost:5000/sudoku/request/initialBoard')
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
