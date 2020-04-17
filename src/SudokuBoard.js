import newSerialNumber, range from './SudokuUtilities.js';

export { SudokuBoard };

// function makeSquaresForBoard(degree) {
// 	const squaresPerRow = degree*degree;

// 	var boardRows = Array(squaresPerRow).fill(null);
	
// 	var row, column;	
// 	for (row = 0; row < squaresPerRow; row++) {
// 		boardRows[row] = Arrays(squaresPerRow).fill(null);
// 		for (column = 0; column < squaresPerRow; ++column) {
// 			boardRows[row][column] = makeSudokuSquare(degree);
// 		}
// 	}
// 	return boardRows;
// }

// // The moves are stored as a 2-dimensional array.
// // 
// function initialMovesForBoard(degree) {
// 	const numRows = degree * degree;
// 	var board = Array(numRows).fill(null);
// 	var row, column;

// 	for (row = 0; row < numRows; ++row) {
// 		board[row] = Array(numRows).fill(null);
// 		for (column = 0; column < numRows; ++column) {
// 			board[row][column] = initialMovesForSquare(degree);
// 		}
// 	}
// 	return board;
// }

// // TODO: have this create blocks of D x D squares instead of a single D^2 x D^2 array

// function moveListsToSquares(degree, moveLists) {
// 	const numRows = degree * degree;
// 	var children = [];
// 	var table = [];
// 	var row, column;
// 	var squaresThisRow;

// 	for (row = 0; row < numRows; ++row) {
// 		squaresThisRow = makeSquaresForRow(moveLists[row]);
// 		children.push(
// 			<div class="board-row">
// 				{squaresThisRow}
// 			</div>
// 			);
// 	}

// 	table.push(children);
// 	return table;
// }


class SudokuBoard extends React.Component {
	constructor(props) {
		super(props);
		const degree = this.props.degree;

		this.state = {
			serial: newSerialNumber("SudokuBoard"),
			moves: initialMovesForBoard(this.props.degree),
		};
	}

	render() {
		return (
			<div class="board">
				<p>
					Serial number: {this.state.serial}
				</p>
				<p>
					Degree: {this.props.degree}
				</p>
				
			</div>
			);
	}
}