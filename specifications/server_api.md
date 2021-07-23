# Sudoku Server API

This file specifies the URLs that correspond to functions that the server will evaluate.

To run the server, set FLASK_APP=sudoku-server/sudoku_server.py,
then `flask run`.

### Request Initial Board

*URL*: `/sudoku/request/initialBoard`

*Body*: `{ 'degree': N, 'name': <string_name> }` (N is an integer, probably 2 or 3),
and the optional parameter name specifies which puzzle to pull and may specify cofiguration information
by separating configuration options with `...`
(e.g., `test7-i26e36hp10...goal=C6...name=Pilot Test Board2...select_ops_upfront...question=Can C6 be odd?`).
In SudokuOnline, this will be used to identify how far into the series of puzzles a player is.

*Response*: Single board represented as JSON

### Request Game Boards

*URL*: *'/sudoku/request/boardsForGame/<gamename>'

Example request:
/sudoku/request/boardsForGame/test_game1_6

*Response* : Ordered list of inital boards (rerpesented as JSON) that make up the game <gamename>

Example Response:
```json
[ <JSON representation of board - see board.md>, <JSON representation of board - see board.md>, ... ]
```

Defaults are set to select a random puzzle from puzzles.puzzles and to simplify with exclusion.

### Evaluate Cell Action

*URL*: `/sudoku/request/evaluate_cell_action`

*Body*: No body required.

```json
{
    'board': <JSON representation of board - see board.md>,
    'action': {
        'action': 'assign',
        'cell': [0,4],
        'value': 3
    },
    'operators': ['inclusion', 'pointingpairs', 'ywings']
}
```

*Response*: List of new boards to add to the tree

The caller is responsible for keeping track of where in the game tree the new boards should be added.

For now, the caller is also responsible for keeping track of the heuristics selected up front and listing them in 'heuristics'.  This may need to change.

### List Logical Operators

*URL*: `/sudoku/request/list_logical_operators`

*Body*: No body required.

*Response*: List of logical operators with both internal name and user-visible name and cost.

Example response:
```json
[
    {   'internal_name': 'inclusion',
        'cost': 100,
        'user_name': 'Inclusion',
        'short_description': 'Assign values that have only one possible cell.',
        'description': 'Search board units for values that have only one possible cell and make that assignment.'},
    {   'internal_name': 'pointingpairs',
        'cost': 250,
        'user_name': 'Pointing pairs',
        'short_description': 'Remove aligned value pairs from other units.',
        'description': 'If any one value is present only two or three times in just one unit, then we can remove that number from the intersection of a number unit. There are four types of intersections: 1. A pair or triple in a box - if they are aligned on a row, the value can be removed from the rest of the row. 2. A pair or triple in a box, if they are aligned on a column, the value can be removed from the rest of the column. 3. A pair or triple on a row - if they are all in the same box, the value can be removed from the rest of the box. 4. A pair or triple on a column - if they are all in the same box, the value can be removed from the rest of the box.'}
]
```

### List Cell Actions

*URL*: `/sudoku/request/list_cell_actions`

*Body*: No body required.

*Response*: List of actions that the user can take on a cell with both internal name and user-visible name and cost.

Example response:

```json
[
    {   'internal_name': 'pivot',
        'arguments': ['cell'],
        'cost': 500,
        'user_name': 'Pivot',
        'short_description': 'Expand all choices for cell.',
        'description': 'Return a separate board for each possible value in cell.'},
    {   'internal_name': 'assign',
        'arguments': ['cell', 'value'],
        'cost': 100,
        'user_name': 'Assign',
        'short_description': 'Assign given value to cell.',
        'description': 'Return one board with the assignment and another (backup) with the exclusion.'},
]
```

### Submit Game Record

The client will pass the server a big json object with keys like game_id, session_id, and the full game tree.
There may also be a key for aborted attempts.
Given this big json blob, the server will save it somewhere.
The server can assume that json blobs are unique. (This will be ensured by adding timestamp to identifier).
We are expecting multiple clients per server, but the server is stateless, and client ids will ensure that there is no problem with overlap.
The server will just add the json blob to a file that we can pull back down from AWS.
