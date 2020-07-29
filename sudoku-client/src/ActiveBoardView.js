// ActiveBoardView: expanded board with choice grids
// 
// This component displays a single Sudoku board. A board's size
// is defined by a parameter D (its *degree*). The board 
// comprises a square D*D x D*D grid of cells, or equivalently,
// a D x D grid of blocks where each block is a grid of D x D 
// cells.  
// 
// Cells in a Sudoku board can either be *assigned* (a value
// has been assigned to that cell) or *unassigned* (there are
// zero or more possibilities still open).  This component
// renders assigned cells by showing the value for that cell
// and unassigned cells as a grid of the choices still available.
// 
// ActiveBoardView does not do any validation of the board's
// contents.
// 
// Interface:
// 
// Required props:
//     board - SudokuBoard structure.  Must contain the following
//         members:
//         
//         - degree: non-negative integer
//         - assignments: 2D array with (degree*degree) rows and
//           columns.  Each element of the array must either be
//           a value or 'null', indicating unassigned.
//         - availableMoves: 2D array with (degree*degree) rows
//           and columns.  Each element must be a list of values
//           that the caller wants to display as possible assignments
//           for the corresponding cell.
//           
// Style:
//    (to be filled in)

import React from 'react';
                               
import SudokuChoiceGrid from './SudokuChoiceGrid';

class ActiveBoardView extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			selectedSquare: null,
			selectedChoiceSquare: null
		}
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
		const D = this.props.board.degree;
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
			<table className="sudoku-board active">
				<tbody>{tableRows}</tbody>
			</table>
			);
	}

	makeSquare(row, column, assignments, moveLists) {
		let cellStyleName = 'sudoku-board-square active degree-' + this.props.board.degree;
		if (this.state.selectedSquare !== null
			&& this.state.selectedSquare[0] == row
			&& this.state.selectedSquare[1] == column) {
			cellStyleName += ' selected';
		}

		const allCellStyleNames = cellStyleName;
		if (assignments[row][column] !== null) {
			return (
				<td className={allCellStyleNames} key={column}>
					{assignments[row][column]}
				</td>
				);
		} else {
			const choiceGrid = this.makeChoiceGrid(moveLists[row][column], row, column);
			return (
				<td className={allCellStyleNames} key={column}>
					{choiceGrid}
				</td>
			);
		}
	}

	makeChoiceGrid(moveList, boardRow, boardColumn) {
		const squareIsSelected = (
			this.state.selectedSquare !== null
			&& this.state.selectedSquare[0] === boardRow
			&& this.state.selectedSquare[1] === boardColumn
			);

		return (
			<SudokuChoiceGrid
				degree={this.props.board.degree}
				moveList={moveList}
				boardRow={boardRow}
				boardColumn={boardColumn}
				boardSquareIsSelected={squareIsSelected}
				selectedValue={this.state.selectedValue}
				announceChoiceSelection={ (row, column, value) => {this.choiceSelected(row, column, value);} }
				/>
			);
	}

	choiceSelected(row, column, value) {
		console.log('Board: User chose value ' + value + ' in cell (' + row + ', ' + column + ')');
		this.setState({
			selectedSquare: [row, column],
			selectedValue: value
		});

		if ('announceChoice' in this.props) {
			this.props.announceChoice(this.props.board, [row, column], value);
		} else {
			console.log('ActiveBoardView: No announceChoice callback in props.');
		}
	}

	asJson() {
		return this.props.board;
	}

	serial() {
		return this.props.board.serialNumber;
	}
}


export { ActiveBoardView };
