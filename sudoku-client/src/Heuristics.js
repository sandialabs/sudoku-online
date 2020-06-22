// Heuristics.js -- dummy implementation of Sudoku heuristics

import { reshape1Dto2D } from './ArrayUtilities';
import { computeMoveLists } from './SudokuUtilities';
import { clone, filter } from 'ramda';

function dispatch(request) {

    console.log('dispatch: Board is ');
    console.log(request.board);

    if (request.heuristic === 'include/exclude') {
        return evaluateIncludeExclude(request);
    } else {
        console.log('ERROR: Unknown heuristic ' + request.heuristic);
        return null;
    }
}

function evaluateIncludeExclude(request) {
    const D = request.board.degree;
    const assignments = request.board.assignments;
    const moveLists = request.board.availableMoves;
    
    // Assumption check: the cell the user wants to assign cannot 
    // already be assigned.
    const chosenCell = request.action.cell;
    console.assert(
        assignments[chosenCell[0]][chosenCell[1]] === null,
        {
            chosenCell: chosenCell, 
            error: 'Cell is not empty', 
            assignments: assignments
        });

    // Assumption check: the chosen value must be between 0 and D*D-1, inclusive.
    console.assert(request.action.value >= 0 && request.action.value < D*D,
        {value: request.action.value,
         error: 'Chosen value must be between 0 and ' + D*D-1}
         );

    const tempAssignments = clone(assignments);
    tempAssignments[chosenCell[0]][chosenCell[1]] = request.action.value;
    const [newAssignments, newMoveLists] = propagateConstraints(D, tempAssignments, moveLists);
    return {
        'assignments': newAssignments,
        'movesAvailable': newMoveLists
    };

}


function propagateConstraints(degree, assignments, moveLists) {
    // assumption: assignments and moveLists are both 2D D*D arrays
    
    // assumption: elements in the assignments array are either 'null'
    // (unassigned) or an integer between 0 and D*D-1, inclusive
    
    // note -- we're not making fully-constrained moves; that's up 
    // to the user or to a different heuristic
    const newMoveLists = constrainMoves(degree, assignments, moveLists);
    return [clone(assignments), newMoveLists];
}


function constrainMoves(degree, assignments, moveLists) {
    let newMoveLists = computeMoveLists(clone(assignments));
    return newMoveLists;
}

export { dispatch };
