// GameTreeBoardRenderer: Render a Sudoku board in compact
// form to go into the game tree
// 
// This class is intended for use inside a Treebeard header
// decorator.
// 
// Required props:
// 	   board: SudokuBoard object with assignments, moveLists, and degree

import React from 'react';
import PropTypes from 'prop-types';

class GameTreeBoard extends React.Component {
	
	render() {
		const assignmentArray = this.props.board.assignments;
		const tableData = this.makeBoardTable(assignmentArray);
		return (
			<table>
			   <tbody>
			     <tr>
			        <td>{this.props.name}</td>
			        <td>{tableData}</td>
			     </tr>
			   </tbody>
			</table>
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
		const tableStyle = 'miniature-board degree-' + D;
		const boardId = 'game-tree-board-' + this.props.board.serialNumber;

		const tableRows = [];

		for (let row = 0; row < D*D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D*D; ++col) {
				squaresInRow.push(
					this.makeSquare(row, col, assignments)
					);
			}
			tableRows.push(
				<tr className={tableStyle} key={row}>{squaresInRow}</tr>
				);
		}

		return (
			<table className={tableStyle} id={boardId}>
				<tbody>{tableRows}</tbody>
			</table>
			);
	}

	makeSquare(row, column, assignments) {
		let classes = [ 
		   'miniature-board', 
		   'degree-' + this.props.board.degree
		   ];

		if (assignments[row][column] !== null) {
			// return (
			// 	<td className={cellStyleName} key={column}>
			// 		{assignments[row][column]}
			// 	</td>
			// 	);
			classes.push('assigned');
			const cellStyleName = classes.join(' ');
			const bg_blue = { backgroundColor: 'blue' };

			return (
				<td className={cellStyleName} style={bg_blue} key={column}>
					<span className='occupied'></span>
				</td>
				);
		} else {
			const cellStyleName = classes.join(' ');
			return (
				<td className={cellStyleName} key={column}></td>
				);
		}
	}
}


GameTreeBoard.propTypes = {
	name: PropTypes.string,
	board: PropTypes.object
};

export {GameTreeBoard};
