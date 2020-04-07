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

	/// Make the array of squares, blocks, and whatnot.
	//
	// We can't have loops inside the return() clause in render(). 
	// Instead, what we do is set up a dummy element in return()
	// and inside that dummy element put the result of a function
	// call.  
	makeBoardComponents(moveLists) {
		const D = this.props.degree;
		var r, c;
		var thisRow;
	
		// This is the top-level container for everything.
		var table = [];
		var children = [];

		for (r = 0; r < D; ++r) {
			thisRow = [];
			for (c = 0; c < D; ++c) {
				thisRow.push(<span key={D*r + c}>({r},{c})</span>);
			}
			children.push(<div key={r}>{thisRow}</div>);
		}

		table.push(children);
		return table;
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
				<div key="3" id="board-{this.state.serialNumber}">
					{this.makeBoardComponents({})}
				</div>
			</div>
		);
	}


}


export default SudokuBoard;
