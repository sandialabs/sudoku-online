// GameTreeBoardRenderer: Render a Sudoku board in compact
// form to go into the game tree
// 
// This class is intended for use inside a Treebeard header
// decorator.
// 
// Required props:
// 	   board: SudokuBoard object with assignments, moveLists, and degree

import React from 'react';

class GameTreeBoard extends React.Component {
	
	render() {
		const assignmentArray = this.props.board.assignments;

		return (
			<div id="gameTreeBoard-{this.props.board.serialNumber}" className="board game-tree">
					{this.makeBoardTable(assignmentArray)}
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
	//     assignments: 2D array of assignments of values to cells
	//         
	// Returns:
	//     A new <div> containing the entire board.
	//     
	makeBoardTable(assignments) {
		const D = this.props.board.degree;
		const tableRows = [];

		const rowStyleName = 'sudoku-board-row degree-' + D;
		for (let row = 0; row < D*D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D*D; ++col) {
				squaresInRow.push(
					this.makeSquare(row, col, assignments)
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

	makeSquare(row, column, assignments) {
		let cellStyleName = 'sudoku-board-square inactive degree-' + this.props.degree;
		if (assignments[row][column] !== null) {
			return (
				<td className={cellStyleName} key={column}>
					{assignments[row][column]}
				</td>
				);
		} else {
			return (
				<td className={cellStyleName} key={column}></td>
				);
		}
	}
}


export {GameTreeBoard};
