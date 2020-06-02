// SudokuGame: manage and render the entire game tree
// 
// Our implementation of Sudoku is intended to track the moves and
// decisions players make.  We represent these decisions explicitly
// by showing a tree of boards.  When the user makes a move in a 
// single square, the board is given one or more child nodes that
// illustrate the consequences of that move.
//
// This component manages the game tree, including initial setup.

import React from 'react';
import SudokuBoard from './SudokuBoard';

class TreeNode {
	constructor(parent) {
		this.parent = parent;
		this.children = [];
		this.board = null;
	}

}


class SudokuGame extends React.Component {
	constructor(props) {
	 	super(props);
	 	const rootNode = new TreeNode(null);
		this.state = {
			treeRoot: rootNode
		}
	 	if (this.props.initialBoard !== null) {
	 		this.state.treeRoot.board = this.props.initialBoard;
	 	}
	}

	boardCellClicked(board, cell, choice) {
		console.log("Board cell clicked: board serial number "
					+ board.state.serialNumber 
					+ ", clicked cell " 
					+ cell);
	}

	render() {
		return (
			<div key={3}>
				<div key={4}>
				    Hi.  This is the Sudoku game tree.  My responsibilities
				    are as follows:
				    <ul>
				        <li>On startup, go ask some server for an initial board.</li>
				        <li>Set up, maintain, and render the game tree.</li>
				        <li>When the user makes a move on a board, contact the
				            server to get the child nodes resulting from that move.</li>
				        <li>When the user has finished the game, transmit the entire
				            game tree to the server along with some metadata yet to
				            be established.</li>
				    </ul>
				</div>
				<div key={5}>
					<SudokuBoard 
						degree={this.props.degree}
						board={this.props.initialBoard} 
						key={6}
						announceChoice={this.boardCellClicked}
					/>
				</div>
			</div>
			);
	}

}

export default SudokuGame;