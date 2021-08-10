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
	
	render() {
		return this.makeLabeledGameTable();
	}

	

	makeLabeledGameTable(assignments, moveLists) {
		const D = this.props.board.degree;
		const labelRowTable = _makeLabelRowTable(D);
		const labelColumnTable = _makeLabelColumnTable(D);

		const gameBoard = this.makeBoardTable(
			this.props.board.assignments,
			this.props.board.availableMoves
			);

		return (
			<div id='activeBoardContainer' className='no-borders'>
				<div id='topLabels' className='no-borders'>
					{labelRowTable}
				</div>
				<div id='sideLabelsAndBoard' className='no-borders'>
					<span id='sideLabels' className='no-borders'>
						{labelColumnTable}
					</span>
					<span id='gameBoard' className='no-borders'>
						{gameBoard}
					</span>
				</div>
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

		const accessibleCellKeys = this.props.board.accessibleCells.map(
			(coords) => (coords[0].toString() + coords[1].toString())
			);

		const tableStyle = 'active-board degree-' + D;

		for (let row = 0; row < D*D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D*D; ++col) {
				squaresInRow.push(
					this.makeSquare(row, col, assignments, moveLists, accessibleCellKeys)
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

	makeSquare(row, column, assignments, moveLists, accessibleCellKeys) {
		let cellStyleName = 'active-board square degree-' + this.props.board.degree;
		if (this.props.selectedSquare !== null
			&& this.props.selectedSquare[0] === row
			&& this.props.selectedSquare[1] === column) {
			cellStyleName += ' selected-square';
		}

		let allCellStyleNames = cellStyleName;
		const cellKey = row.toString() + column.toString();
		const cellIsAccessible = (accessibleCellKeys.indexOf(cellKey) !== -1);
		if (cellIsAccessible) {
			allCellStyleNames += ' accessible';
		} else {
			allCellStyleNames += ' inaccessible';
		}
		
		const selectIfAccessible = () => {
			if (cellIsAccessible) {
				return this.selectCell(row, column);
			} else {
				console.log('Cell ' + cellKey + ' is inaccessible in '
					        + 'this puzzle.  Ignoring selection.');
			}
		}

		const cellIsGoal = (
			this.props.board.goalCell !== undefined 
			&& this.props.board.goalCell !== null 
			&& row === this.props.board.goalCell[0]
			&& column === this.props.board.goalCell[1]
			);

		if (cellIsGoal) {
			allCellStyleNames += ' goal-cell';
		}

		if (assignments[row][column] !== null) {
			return (
				<td className={allCellStyleNames} key={column}>
					{assignments[row][column] +1}
				</td>
				);
		} else {
			const choiceGrid = this.makeChoiceGrid(
				moveLists[row][column], 
				row, 
				column,
				accessibleCellKeys
				);

			return (
				<td className={allCellStyleNames} 
				    key={column} 
				    onClick={selectIfAccessible}
					>
					{choiceGrid}
				</td>
			);
		}
	}

	makeChoiceGrid(moveList, boardRow, boardColumn, accessibleCellKeys) {
		const squareIsSelected = (
			this.props.selectedSquare !== null
			&& this.props.selectedSquare[0] === boardRow
			&& this.props.selectedSquare[1] === boardColumn
			);

		const cellKey = boardRow.toString() + boardColumn.toString();
		const isCellAccessible = (accessibleCellKeys.indexOf(cellKey) !== -1);
		return (
			<SudokuChoiceGrid
				cellKey={[boardRow, boardColumn]}
				degree={this.props.board.degree}
				moveList={moveList}
				boardRow={boardRow}
				boardColumn={boardColumn}
				boardSquareIsSelected={squareIsSelected}
				selectedValue={this.props.selectedValue}
				announceChoiceSelection={ (row, column, value) => {this.choiceSelected(row, column, value);}}
				accessible={isCellAccessible}
				/>
			);
	}

	choiceSelected(row, column, value) {
		console.log('Board: User chose value ' + value + ' in cell (' + row + ', ' + column + ')');
		this.props.announceChoice(this.props.board, [row, column], value);
	}

	selectCell(row, column) {
		console.log('Board: User selected cell (' + row + ', ' + column + ')');
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
	board: PropTypes.object.isRequired,
	selectedSquare: PropTypes.array,
	selectedValue: PropTypes.number,
}

// Make a single-row table that starts with a blank square and includes
// one cell for each column in the table

function _makeLabelRowTable(degree) {
	const cells = [];
	let label = ' ';

	// The first cell is an empty label
	cells.push(
		<td className='label blank-square' key={-1}>
			{label}
		</td>
	);
	
	for (let i = 0; i < degree*degree; ++i) {
		label = _columnLabel(i);	
		cells.push(
			<td className='label column-label' key={i}>
				{label}
			</td>
			);
	}

	return (
		<table className='label columns'>
			<tbody>
				<tr>{cells}</tr>
			</tbody>
		</table>
		);
}

// Make a single-column table where every row contains a single cell
// with the label for a single row in the game table.
function _makeLabelColumnTable(degree) {
	const rows = [];

	// The blank cell in the upper left has already been taken care of
	// in makeLabelRowTable.  All we need here is the label for each
	// row.
	for (let i = 0; i < degree*degree; ++i) {
		const label = _rowLabel(i);
		rows.push(
			<tr key={i}>
				<td className='label row-label'>
					{label}
				</td>
			</tr>
			);
	}
	return (
		<table className='label rows'>
			<tbody>
				{rows}
			</tbody>
		</table>
		);
}

// Convert a number from 0-8 to a string digit
// Note: the labels after column 9 are :, ;, <, =, and >.  Beware.

function _columnLabel(index) {
	return String.fromCharCode(48 + index + 1);
}

// Convert a number from 0-9 into a letter from A to Z
function _rowLabel(index) {
	return String.fromCharCode(65 + index);
}

export { ActiveBoardView };
