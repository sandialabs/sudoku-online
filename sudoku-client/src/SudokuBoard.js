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
	
	// Assemble the entire table for the board.
	// 
	// The table is just an array of rows.  
	makeBoardTable(moveLists) {
		const D = this.props.degree;
		var row;
		var blockRows = [];

		for (row = 0; row < D; ++row) {
			blockRows.push(this.makeBlockRow(row, moveLists));
		}

		return (
			<div className="boardTable">
				{blockRows}
			</div>
			);
	}

	// Assemble a single row containing D blocks.
	// 
	// 
	makeBlockRow(row, moveLists) {
		const D = this.props.degree;
		var blocks = [];
		var column;

		for (column = 0; column < D; ++column) {
			blocks.push(this.makeBlock(row, column, moveLists));
		}

		return (
			<span className="blockRow" key={row}>
				{blocks}
			</span>
			);

	}

	makeBlock(blockRow, blockColumn, moveLists) {
		return (
			<span className="block" key={blockRow}>
				{this.makeBlockContents(blockRow, blockColumn, moveLists)}
			</span>
			);
	}

	makeBlockContents(blockRow, blockColumn, moveLists) {
		const D = this.props.degree;
		var rows = [];
		var row;

		for (row = 0; row < D; ++row) {
			rows.push(this.makeSquareRow(blockRow, blockColumn, row, moveLists));
		}

		return (
			<span className="blockSquares">
				{rows}
			</span>
		);
	}

	makeSquareRow(blockRow, blockColumn, squareRow, moveLists) {
		const D = this.props.degree;
		var squaresInRow = [];
		var squareColumn;
		var boardRowId, boardColumnId;

		for (squareColumn = 0; squareColumn < D; ++squareColumn) {
			boardRowId = D*blockRow + squareRow;
			boardColumnId = D*blockColumn + squareColumn;
			squaresInRow.push(this.makeSquare(boardRowId, boardColumnId, moveLists));
		}

		return (
			<span className="squareRow" key={squareRow}>
				{squaresInRow}
			</span>
			);
	}

	makeSquare(row, column, moveLists) {
		return (
			<span className="square" key={column}>
				S({row},{column})
			</span>
			);
	}
	render() {
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
					{this.makeBoardTable({})}
				</div>
			</div>
		);
	}


}


export default SudokuBoard;
