// SudokuMain: run the whole thing
// 
// This component is the top-level container for all the machinery 
// involved in the Sudoku game:
// 
// - the game tree itself
// - the heuristic selector panel
// - the score display (?)
// 
// 
import React from 'react';
import SudokuGame from './SudokuGame';
import { requestInitialBoard } from './SudokuMockup';

class SudokuMain extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			initialBoardReceived: false,
			initialBoardDegree: false,
		};
	}

	render() {
		if (this.state.initialBoardReceived) {
			return (
				<div key={3}>
					<div key={4}>
				    	Hi.  This is the Sudoku app.  My responsibilities
				    	are as follows:
				    	<ul>
				        	<li>Maintain connections between all the different components.</li>
				        	<li>Handle communication with the server.</li>
					    </ul>
					</div>
					<div key={5}>
						<SudokuGame />
					</div>
				</div>
			);
		} else {
			return (
				<div key={3}>Waiting for initial game state...</div>
			);
		}
	}

	componentDidMount() {
		console.log('Main panel mounted.  Call out to get the initial game state.');
		// This will be replaced with a server call once we have a server to call
		this.setState({
			initialBoardReceived: true
		});

		const initialBoard = requestInitialBoard(this.props.degree);
		console.log('initialBoard follows:');
		console.log(initialBoard);
		
	}
}

export default SudokuMain;