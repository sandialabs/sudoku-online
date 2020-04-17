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
			initialBoard: null,
			initialBoardDegree: false,
		};
	}

	render() {
		if (this.state.initialBoard !== null) {
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
						<SudokuGame 
							degree={this.props.degree}
							initialBoard={this.state.initialBoard}
						/>
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


		const initialBoard = requestInitialBoard(this.props.degree);
		console.log('initialBoard follows:');
		console.log(initialBoard);

		this.setState({
			initialBoard: initialBoard
		});

		
	}
}

export default SudokuMain;