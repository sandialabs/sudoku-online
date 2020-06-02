// SudokuChoiceGrid: grid showing available choices
// 
// Suppose we have a square that contains a list of possible
// choices.  This class renders a DxD grid containing 
// those choices and makes all of them buttons so that we
// can detect clicks.
// 
//

import React from 'react';
// import { range } from './SudokuUtilities';

/// SudokuBoard: Renderable, interactive Sudoku board
//
// Props: 
//     degree (int): Degree of board (will usually be 2 or 3)
//
// NOTE: We will probably start keeping the move lists and the
// assignments in the object's state so that it knows when
// to re-render.  Until then, we pass moveLists down to each
// function in its entirety instead of trying to subset it for
// each specific block, row, and column.
//
// NOTE: We nest <span> elements pretty deeply in order to take
// advantage of the CSS display attributes table, table-row,
// and table-data.  The containment hierarchy looks like this:
// 
// <div class='boardTable'> (entire board)
//   <span class='blockRow'> (one row of blocks; there are D of these)
//     <span class='block'> (one DxD block of cells; there are D of
//                           these in each row of blocks)
//       <span class='blockSquares'> (table containing the cells for
//                                    one block)
//         <span class='squareRow'> (table row containing D cells;
//                                   there are D of these in block)
//           <span class='square'> (one cell in the Sudoku board)
//           
// The hierarchy will go farther down when we render the move list
// in each cell.
  
class SudokuChoiceGrid extends React.Component {
	constructor(props) {
		super(props);
	}

	render() {
		console.log('Rendering choiceGrid for square ' + this.props.boardRow + ', ' + this.props.boardColumn);
		console.log('Move list: ' + this.props.moveList);
		let gridRows = this.makeChoiceGridContents();
		return (
			<table>
				{gridRows}
			</table>
			)
	}

	makeChoiceGridContents() {
		const D = this.props.degree;
		const rows = [];

		for (let row = 0; row < D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D; ++col) {
				const value = row*D + col;
				if (this.props.moveList.includes(value)) {
					console.log('\tValue ' + value + ' is valid for this square');
					squaresInRow.push(this.makeChoiceButton(value));
				} else {
					squaresInRow.push(this.makeBlankSquare());
				}
			}
			rows.push(
				<tr>{squaresInRow}</tr>
				);
			console.log('DEBUG: After rows.push, squaresInRow.length is ' + squaresInRow.length + ', rows.length is ' + rows.length);
		}

		console.log('DEBUG: Rows: ' + rows);
		return (
			<tbody>{rows}</tbody>
			);
	}

	makeChoiceButton(value) {
		return (
			<td className="choiceAvailable">
				<button className="choiceButton"
						onClick={() => {this.handleClick(value);}}
					>
					{value}
				</button>
			</td>
		);
	}

	makeBlankSquare() {
		const blankSpace = '\u00A0';
		return (
			<td className="choiceUnavailable">{blankSpace}</td>
			);
	}

	handleClick(value) {
		this.props.announceChoiceSelection(this.props.boardRow, this.props.boardColumn, value);
	}
}


export default SudokuChoiceGrid;
