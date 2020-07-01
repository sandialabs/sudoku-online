# Sudoku Server API

This file specifies the URLs that correspond to functions that the server will evaluate.  

THIS IS JUST A DRAFT.  Shelley and Andy will fill this out as they discuss what the interface will look like.


### Request Initial Board

*URL*: `/sudoku/request/initialBoard`

*Body*: `{ degree: N }` (N is an integer, probably 2 or 3)

*Response*: Single board represented as JSON

Do we need any other parameters for this request?

### Evaluate Heuristic

*URL*: `/sudoku/request/heuristic`

*Body*: 

```json
{
    'board': <JSON representation of board - see board.md>
    'action': {
        'action': 'selectValueForCell',
        'cell': [0,4],
        'value': 3
    },
    'heuristic': 'include/exclude'
}
```

*Response*: List of new boards to add to the tree

The caller is responsible for keeping track of where in the game tree the new boards should be added.


### Submit Game Record

To be determined.

