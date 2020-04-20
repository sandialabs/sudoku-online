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
                               
import { reshape1Dto2D } from './ArrayUtilities';

class SudokuBoard extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			serialNumber: -1,
		};
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
		var row;
		var blockRows = [];

		for (row = 0; row < D; ++row) {
			blockRows.push(this.makeBlockRow(row, assignments, moveLists));
		}

		return (
			<table className="boardTable">
				<tbody>{blockRows}</tbody>
			</table>
			);
	}

	// Assemble a single row containing D blocks.
	// 
	// This function creates D blocks and attaches them to a 
	// container.  No real work is done, just delegation.
	// 
	// Arguments:
	//     row: Integer index of the row to generate
	//     moveLists: 2D array of move lists for the entire board
	//     
	// Returns:
	//     <span> element for a row of blocks in the table
	makeBlockRow(row, assignments, moveLists) {
		const D = this.props.degree;
		var blocks = [];
		var column;

		for (column = 0; column < D; ++column) {
			blocks.push(this.makeBlock(row, column, assignments, moveLists));
		}

		return (
			<tr className="blockRow" key={row}>{blocks}</tr>
			);

	}

	makeBlock(blockRow, blockColumn, assignments, moveLists) {
		const blockContents = this.makeBlockContents(
			blockRow,
			blockColumn,
			assignments,
			moveLists);

		return (
			<td className="block" key={blockColumn}>{blockContents}</td>
		);
	}

	makeBlockContents(blockRow, blockColumn, assignments, moveLists) {
		const D = this.props.degree;
		var rows = [];

		for (let row = 0; row < D; ++row) {
			rows.push(this.makeSquareRow(blockRow, blockColumn, row, assignments, moveLists));
		}

		return (
			<table className="blockSquares">
				<tbody>{rows}</tbody>
			</table>
		);
	}

	makeSquareRow(blockRow, blockColumn, squareRow, assignments, moveLists) {
		const D = this.props.degree;
		var squaresInRow = [];
		var squareColumn;
		var boardRowId, boardColumnId;

		for (squareColumn = 0; squareColumn < D; ++squareColumn) {
			boardRowId = D*blockRow + squareRow;
			boardColumnId = D*blockColumn + squareColumn;
			squaresInRow.push(this.makeSquare(boardRowId, boardColumnId, assignments, moveLists));
		}

		return (
			<tr className="squareRow" key={squareRow}>{squaresInRow}</tr>
			);
	}

	makeSquare(row, column, assignments, moveLists) {
		if (assignments[row][column] !== null) {
			return (
				<td className="square assigned">
					{assignments[row][column]}
				</td>
				);
		} else {
			const choiceGrid = this.makeChoiceGrid(moveLists[row][column]);
			return (
				<td>
					<table className="square choiceGrid" key={column}>
						<tbody>{choiceGrid}</tbody>
					</table>
				</td>
			);
		}
	}

	makeChoiceGrid(moveList) {
		const D = this.props.degree;
		const choices = new Set(moveList);
		var rows = [];
		for (let row = 0; row < D; ++row) {
			rows.push(this.makeChoiceRow(choices, row));
		}
		return rows;
	}

	makeChoiceRow(choices, row) {
		const D = this.props.degree;
		const choiceSquares = []
		for (let column = 0; column < D; ++column) {
			const value = D*row + column;
			let squareValue = '\u00A0';
			let squareClass = 'choiceSquare ';
			if (choices.has(value)) {
				squareValue = value;
				squareClass += 'choiceAvailable';
			} else {
				squareClass += 'choiceUnavailable';
			}
			choiceSquares.push(
				<td className={squareClass}>{squareValue}</td>
				);
		}
		return (
			<tr className="choiceRow">{choiceSquares}</tr>
		);
	}

	render() {
		const D = this.props.degree;
		const moveListArray = reshape1Dto2D(this.props.board.availableMoves,
											D*D, D*D);
		const assignmentArray = reshape1Dto2D(this.props.board.assignments,
											  D*D, D*D);
		return (
			<div key="10" className="entireBoardPlusDecorations">
				<div key="1">
					This is a Sudoku board.  Its degree is {this.props.degree}.
					This object's responsibilities are as follows:
					<ul>
						<li>Receive the board state from the game tree</li>
						<li>Set up a D^2 x D^2 array of SudokuSquare objects</li>
						<li>Pass the relevant "permitted moves" list to each square</li>
						<li>Identify which square has been clicked</li>
					</ul>
				</div>
				<p key="2">The next element down is the number board.</p>
				<div key="3" id="board-{this.state.serialNumber}" className="board">
					{this.makeBoardTable(assignmentArray, moveListArray)}
				</div>
			</div>
		);
	}


}


export default SudokuBoard;
