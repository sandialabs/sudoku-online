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
import PropTypes from 'prop-types';

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

		return this.makeBoardTable(assignmentArray, moveListArray);

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

		const tableStyle = 'active-board degree-' + D;
		for (let row = 0; row < D*D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D*D; ++col) {
				squaresInRow.push(
					this.makeSquare(row, col, assignments, moveLists)
					);
			}
			tableRows.push(
				<tr key={row} className={tableStyle}>{squaresInRow}</tr>
				);
		}

		return (
			<table className={tableStyle}>
				<tbody>{tableRows}</tbody>
			</table>
			);
	}

	makeSquare(row, column, assignments, moveLists) {
		let cellStyleName = 'active-board square degree-' + this.props.board.degree;
		if (this.state.selectedSquare !== null
			&& this.state.selectedSquare[0] === row
			&& this.state.selectedSquare[1] === column) {
			cellStyleName += ' selected-square';
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
				<td className={allCellStyleNames} key={column} onClick={() => this.selectCell(row, column)}>
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

		this.props.announceChoice(this.props.board, [row, column], value);
	}

	selectCell(row, column) {
		console.log('Board: User selected cell (' + row + ', ' + column + ')');
		this.setState({
			selectedSquare: [row, column]
		});

		this.props.announceChoice(this.props.board, [row, column], -1);
	}

	asJson() {
		return this.props.board;
	}

	serial() {
		return this.props.board.serialNumber;
	}
}

ActiveBoardView.propTypes = {
	announceChoice: PropTypes.func.isRequired,
	board: PropTypes.object.isRequired
}

export { ActiveBoardView };
