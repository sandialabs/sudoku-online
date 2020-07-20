# Sudoku Server API

This file specifies the URLs that correspond to functions that the server will evaluate.

THIS IS JUST A DRAFT.  Shelley and Andy will fill this out as they discuss what the interface will look like.


### Request Initial Board

*URL*: `/sudoku/request/initialBoard`

*Body*: `{ 'degree': N, 'name': <string_name> }` (N is an integer, probably 2 or 3),
and the optional parameter name specifies which puzzle to pull.
In SudokuOnline, this will be used to identify how far into the series of puzzles a player is.

*Response*: Single board represented as JSON

Do we need any other parameters for this request?

### Evaluate Heuristic

*URL*: `/sudoku/request/heuristic`

*Body*:

```json
{
    'board': <JSON representation of board - see board.md>
    'action': {
        'action': 'assign',
        'cell': [0,4],
        'value': 3
    },
    'heuristics': ['inclusion', 'pointingpairs', 'ywings']
}
```

*Response*: List of new boards to add to the tree

The caller is responsible for keeping track of where in the game tree the new boards should be added.

For now, the caller is also responsible for keeping track of the heuristics selected up front and listing them in 'heuristics'.  This may need to change, in which case the solver will track the heuristics in the puzzle name.  *TODO* discuss between Shelley and Andy.

### List Heuristics

*URL*: `/sudoku/request/list_heuristics`

*Body*: No body required.

*Response*: List of heuristics with both internal name and user-visible name.  Note: This may be modified to include the cost of applying each heuristic.

Example response:

```json
[
    { 'internal_name': 'inclusion', 'user_name': 'Include/Exclude', 'cost': 100},
    { 'internal_name': 'pivot', 'user_name': 'Expand All Choices', 'cost': 200 }
]
```

### Submit Game Record

To be determined.
