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
import { requestInitialBoard, executeHeuristic } from './SudokuMockup';

class SudokuMain extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			initialBoard: null,
			initialBoardDegree: false,
			availableHeuristics: ['include/exclude'],
			selectedHeuristic: 'include/exclude'
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
						<p>Available Heuristics</p>
						<p>(fill this in)</p>
					</div>
					<div key={6}>
						<SudokuGame 
							degree={this.props.degree}
							initialBoard={this.state.initialBoard}
							issueBoardRequest={(board, move) => {this.handleBoardRequest(board, move);}}
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

	handleBoardRequest(board, action) {
		console.log("handleBoardRequest called, current heuristic is " + this.state.selectedHeuristic);
		const request = {
			board: board.asJson(),
			action: action,
			heuristic: this.state.selectedHeuristic
		};
		this.requestHeuristicResults(request,
									 (result) => {this.heuristicResultsArrived(board, action, result);});
	}

	heuristicResultsArrived(parentBoard, action, results) {
		console.log('UNIMPLEMENTED: heuristicResultsArrived called');
	}

	requestHeuristicResults(request, resultCallback) {
		console.log('UNIMPLEMENTED: requestHeuristicResults');
		console.log('request:');
		console.log(request);
		const result = executeHeuristic(JSON.stringify(request));
		console.log('Heuristic results:');
		console.log(result);

	}


	componentDidMount() {
		console.log('Main panel mounted.  Call out to get the initial game state.');
		// This will be replaced with a server call once we have a server to call


		const initialBoard = JSON.parse(requestInitialBoard(this.props.degree));
		console.log('initialBoard follows:');
		console.log(initialBoard);

		this.setState({
			initialBoard: initialBoard
		});

		
	}
}

export default SudokuMain;