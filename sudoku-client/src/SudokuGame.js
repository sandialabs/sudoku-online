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


class GameTree {
	constructor() {
		this.root = null;
		this.allNodes = [];
	}

	nodeBySerialNumber(serialNumber) {
		return this.allNodes[serialNumber];
	}

	addBoard(newBoard, parent=null) {
		console.log('addBoard: New board is ' + newBoard + ', type is ' + typeof(newBoard));
		console.log(newBoard);
		if (this.root === null || parent === null) {
			this.root = new TreeNode(null);
			this.root.board = newBoard;
		} else {
			const parentNode = this.nodeBySerialNumber(parent);
			parentNode.addChildBoard(newBoard);
		}
		this.allNodes[newBoard.serial] = newBoard;
	}
		
}


class TreeNode {
	constructor(parent) {
		this.parent = parent;
		this.children = [];
		this.board = null;
	}

	addChildBoard(board) {
		const childNode = new TreeNode(this);
		childNode.board = board;
		this.children.push(childNode);
	}
}


class SudokuGame extends React.Component {
	constructor(props) {
	 	super(props);

		this.state = {
			gameTree: null
		}
		if (this.props.initialBoard !== null) {
			console.log('SudokuGame: Non-null initial board supplied with props for constructor.');
			this.state.gameTree = new GameTree();
			this.state.gameTree.addBoard(this.props.initialBoard);
		}
	}

	// When we get our initial board, we need to update/initialize the game tree.
	componentDidUpdate(oldProps) {
		console.log('SudokuGame componentDidUpdate called.')
		if (oldProps.initialBoard !== this.props.initialBoard) {
			this.initializeGameTree(this.props.initialBoard);
		}
	}

	initializeGameTree(rootBoard) {
		const newGameTree = new GameTree();
		newGameTree.addBoard(rootBoard);
		this.setState({
			gameTree: newGameTree
		});
	}

	boardAnnouncesChoice(board, cell, choice) {
		console.log("Board announcing choice: board serial number "
					+ board.state.serialNumber 
					+ ", clicked cell " 
					+ cell);
		console.log('this.props:');
		console.log(this.props);
		const action = {
			'action': 'selectValueForCell',
			'cell': cell,
			'value': choice
		};
		this.props.issueBoardRequest(board, action);
	}

	render() {
		console.log('SudokuGame.render(): this.props.initialBoard:');
		console.log(this.props.initialBoard);
		if (this.state.gameTree === null) {
			return (
				<div>
				   SudokuGame does not yet have a game tree.  This is OK; it means we don't
				   have our initial board yet.
				</div>
			);
		} else if (this.state.gameTree.root.board === null) {
			return (
				<div>
				    SudokuGame has a game tree but no root board.  This shouldn't happen.
				</div>
			);
		} else {
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
							board={this.state.gameTree.root.board} 
							key={6}
							announceChoice={ (board, cell, choice) => {this.boardAnnouncesChoice(board,cell,choice);} }
						/>
					</div>
				</div>
				);
		}
	}
}

export default SudokuGame;