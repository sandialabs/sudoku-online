# JSON specification for Sudoku board

This is the definitive specification for the Sudoku board that we pass back and forth between client and server.  It will evolve, but only after discussion.

The driving principle behind what to include in this structure is that the client should be able to render the board, including all decorations, with only this struct.  It does not include any information about the game tree.

All coordinates will be represented as a 2-element list: `[row, column]`.  Indexing is 0-based.  The top left cell in the board has coordinates [0, 0].  The lower right cell for a degree-2 board has coordinates [3, 3].  The lower right cell for a degree-3 board has coordinates [8, 8].

Values within each cell are integers from 0 to (D^2 - 1), inclusive, where D is the degree of the board.  Values will probably be displayed *to the user* as integers from 1 to D^2 to agree with the bajillion Sudoku books out there,
but internally everything is integers with 0-based indexing.

All arrays will be laid out and accessed in row-major order: `array[r][c]` will get the element at coordinates [r, c].

## Board State

### Required Metadata

Required:
- *Board degree*: integer, 2 or 3 in almost all cases
- *Board serial number*: unique integer

### Other Metadata

We may want to highlight certain cells in the board, or pass around additional metadata about the board.

- *Board parent serial number*: optional unique integer of parent board
- *Goal cells*: cells whose values we want the user to affect indirectly
- *Accessible cells*: cells the user is permitted to act upon
- *Conflicting cells*: optional cells that have no possible solution (structured as a list just like accessibleCells)
- *solved*: optional boolean indicating whether this board represents an acceptable and complete solution
- *backtrackingBoard*: optional boolean indicating whether this board is only available to allow the user to backtrack and handle incorrect assignments or exclusions
- *puzzleName*: optional string name of the puzzle
- *rules*: a dictionary relating the rules under which a board shall be interpreted
- *cost*: a float showing the cost that should be attributed to this board (assumed for now to be a portion that applies across a board)

### Current Assignments

This is a 2D array.  Since Javascript doesn't have native 2D arrays, we represent it as a 1D array of 1D arrays.  The dimensions of this array will be D^2 rows by D^2 columns.

Each cell in this array will contain either an integer value, indicating that the value has already been assigned; or the Javascript value `null`, indicating that the cell has not been assigned.

### Available Moves

This is also a 2D array with dimensions D^2 by D^2.

Each cell in this array will contain a list.  If the corresponding cell in the Current Assignments array has an assignment, or if there are no possible moves left for the cell, the list will be empty.  Otherwise, the list will contain those values that have not been ruled out as moves.

Open question: do we propagate the exclusion constraint ("this value is not available because it's already taken") automatically or do we make the user ask for it?

### Rules

- *canChangeLogicalOperators*: If True, the logical operators may be selected by the user for this board.  Default (if not present) is True.

## Example

Whitespace in this example is for readability.  It is not significant.

The example move lists are probably incorrect.  They're intended as examples of syntax.

```json

{
    degree: 2,
    serialNumber: 12345,
    parentSerialNumber: 1234,
    puzzleName: "underconstrained1_4x4",
    assignments: [
                   [ 1,    2,    null, 4    ],
                   [ 3,    null, 1,    2    ],
                   [ 2,    3,    null, 1    ],
                   [ null, 1,    2,    null ]
                 ],

    availableMoves: [
                 [ [], [],     [3],    []     ],
                 [ [], [4, 1], [1, 2], []     ],
                 [ [], [],     [3, 4], []     ],
                 [ [4],[],     [],     [4, 3] ]
               ],

    goalCell: [0, 2],
    accessibleCells: [ [3, 0], [3, 3] ],
    solved: True,

    availableActions: ["applyops", "pivot", "assign", "exclude"],
    rules : {'canChangeLogicalOperators': True},
    cost : 87.5
}
```
