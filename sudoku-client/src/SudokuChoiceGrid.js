// SudokuChoiceGrid: grid showing available choices
// 
// Suppose we have a square that contains a list of possible
// choices.  This class renders a DxD grid containing 
// those choices and makes all of them buttons so that we
// can detect clicks.
// 
//

import React from 'react';
import PropTypes from 'prop-types';

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
  

class SudokuChoiceGrid extends React.Component {
	constructor(props) {
		super(props);
		this.handleClick = this.handleClick.bind(this);
	}

	render() {
		let gridRows = this.makeChoiceGridContents();
		return (
			<table className="sudoku-choice-grid">
				{gridRows}
			</table>
			)
	}

	makeChoiceGridContents() {
		const D = this.props.degree;
		const rows = [];
		let rowClass = 'sudoku-choice-grid';

		if (!this.props.accessible) {
			rowClass += ' inaccessible';
		}
		for (let row = 0; row < D; ++row) {
			const squaresInRow = [];
			for (let col = 0; col < D; ++col) {
				const value = row*D + col;
				if (this.props.moveList.includes(value)) {
					squaresInRow.push(
						this.makeChoiceButton(row, col, value)
						);
				} else {
					squaresInRow.push(this.makeBlankSquare(col));
				}
			}
			rows.push(
				<tr key={row} className={rowClass}>{squaresInRow}</tr>
				);
		}
		return (
			<tbody>{rows}</tbody>
			);
	}

	makeChoiceButton(row, col, value) {

		const onClick = (event) => {
			if (this.props.accessible) {
				this.handleClick(event);
			} 
		}

		let cellClasses = 'sudoku-choice-grid available';
		if (this.props.boardSquareIsSelected) {
			cellClasses += ' selected-square';
			if (value === this.props.selectedValue) {
				cellClasses += ' selected-value';
			}
		}

		let buttonClasses = 'sudoku-choice-grid';
		if (!this.props.accessible) {
			buttonClasses += ' inaccessible';
			cellClasses += ' inaccessible';
		} 
		return (
			<td className={cellClasses} key={col}>
				<button className={buttonClasses}
						onClick={onClick}
						value={value}
						id="button"
					>
					{value +1}
				</button>
			</td>
		);
	}

	makeBlankSquare(key) {
		const blankSpace = '\u00A0';
		let classes = 'sudoku-choice-grid unavailable';
		if (this.props.boardSquareIsSelected) {
			classes += ' selected-square';
		}
		if (!this.props.accessible) {
			classes += ' inaccessible';
		}
		return (
			<td className={classes} key={key}>
				<button className={classes}>{blankSpace}</button>
			</td>
			);
	}

	handleClick(event) {
		event.stopPropagation();
		this.props.announceChoiceSelection(this.props.boardRow, this.props.boardColumn, parseInt(event.target.value, 10));
	}
}

SudokuChoiceGrid.propTypes = {
	accessible: PropTypes.bool.isRequired,
	cellKey: PropTypes.array.isRequired,
	degree: PropTypes.number.isRequired,
	boardSquareIsSelected: PropTypes.bool.isRequired,
	selectedValue: PropTypes.number
};

export default SudokuChoiceGrid;
