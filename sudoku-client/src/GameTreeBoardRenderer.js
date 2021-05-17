// SudokuBoard: single state in a Sudoku game
//
// This class contains a standard Sudoku board.  It is specified
// by one parameter: its *degree*.  A degree-D Sudoku board
// is a square (D^2) cells on a side for a total of D^4 cells.
// The standard 9x9 board found in books and newspapers is a 
// degree-3 board.
// 
// We use the standard Sudoku rules.  Each cell must contain an 
// integer between 1 and D^2.  No two cells in the same row or
// column can contain the same value.  In addition, the board 
// is divided into D x D *blocks*, each a D x D array of cells,
// and no two cells within the same block can contain the same
// value.  

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
                               
import SudokuChoiceGrid from './SudokuChoiceGrid';

class SudokuBoard extends React.Component {
	constructor(props) {
		super(props);
	}
	
	render() {
		const moveListArray = this.props.board.availableMoves;
		const assignmentArray = this.props.board.assignments;

		return (
			<div key="3" id="board-{this.props.board.serialNumber}" className="board">
					{this.makeBoardTable(assignmentArray, moveListArray)}
			</div>
		);	
	}


	/// Make the board as an array of blocks.
	//
	// In order to draw thick borders around the D x D blocks of
	// squares, and in order to keep the code simple, we build up
	// the board as a grid of D x D blocks instead of a (D*D) x (D*D)
	// array of squares.
	// 
	// This function assembles the grid of blocks.
	// 
	// Arguments:
	//     moveLists: 2D array of move lists, one for each cell in 
	//         the board.
	//         
	// Returns:
	//     A new <div> containing the entire board.
	//     
	makeBoardTable(assignments, moveLists) {
		const D = this.props.degree;
		const tableRows = [];

		const rowStyleName = 'sudoku-board-row degree-' + D;
		for (let row = 0; row < D*D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D*D; ++col) {
				squaresInRow.push(
					this.makeSquare(row, col, assignments, moveLists)
					);
			}
			tableRows.push(
				<tr className={rowStyleName} key={row}>{squaresInRow}</tr>
				);
		}

		return (
			<table className="sudoku-board-table">
				<tbody>{tableRows}</tbody>
			</table>
			);
	}

	makeSquare(row, column, assignments, moveLists) {
		let cellStyleName = 'sudoku-board-square degree-' + this.props.degree;
		if (this.props.active) {
			cellStyleName += ' active'; 
		} else {
			cellStyleName += ' inactive';
		}
		const allCellStyleNames = cellStyleName;
		if (assignments[row][column] !== null) {
			return (
				<td className={allCellStyleNames} key={column}>
					{assignments[row][column] +1}
				</td>
				);
		} else {
			if (this.props.active) {
				const choiceGrid = this.makeChoiceGrid(moveLists[row][column], row, column);
				return (
					<td className={allCellStyleNames} key={column}>
						{choiceGrid}
					</td>
				);
			} else {
				return (
					<td className={allCellStyleNames} key={column}></td>
					);
			}
		}
	}

	makeChoiceGrid(moveList, boardRow, boardColumn) {
		return (
			<SudokuChoiceGrid
				degree={this.props.degree}
				moveList={moveList}
				boardRow={boardRow}
				boardColumn={boardColumn}
				announceChoiceSelection={ (row, column, value) => {this.choiceSelected(row, column, value);} }
				/>
			);
	}

	choiceSelected(row, column, value) {
		console.log('Board: User chose value ' + value + ' in cell (' + row + ', ' + column + ')');
		this.props.announceChoice(this.props.board, [row, column], value);
	}

	asJson() {
		return this.props.board;
		
		// const result = {
		// 	degree: this.props.degree,
		// 	serial: this.props.board.serialNumber,
		// 	availableMoves: this.props.board.availableMoves,
		// 	assignments: this.props.board.assignments
		// };
		// return result;
	}

	serial() {
		return this.props.board.serialNumber;
	}
}


export default SudokuBoard;
