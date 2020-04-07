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

class SudokuBoard extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			serialNumber: -1,
		};
	}

	render() {
		return (
			<div>
				This is a Sudoku board.  Its degree is {this.props.degree}.
			</div>
		);
	}
}


export default SudokuBoard;
