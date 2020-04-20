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

class SudokuGame extends React.Component {
	// constructor(props) {
	// 	super(props);
	// }

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
					/>
				</div>
			</div>
			);
	}

}

export default SudokuGame;