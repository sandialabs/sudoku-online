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
							issueBoardRequest={(board, move) => {return this.handleBoardRequest(board, move);}}
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

	/* Send off a request for someone else to evaluate a heuristic on a board.
	 *
	 * Arguments:
	 *     board: Sudoku board to send (should it already be JSON?)
	 *     action: struct containing the request being made
	 *
	 * Returns:
	 *     Promise that will resolve with the results of whatever heuristic runs.
	 */

	handleBoardRequest(board, action) {
		console.log("handleBoardRequest called, current heuristic is " + this.state.selectedHeuristic);
		const request = {
			board: board.asJson(),
			action: action,
			heuristic: this.state.selectedHeuristic
		};

		// When we switch over to an actual server, this line will be replaced
		// with something that makes an actual HTTP request.
		return this.mockupHeuristicRequest(request);
	}

	/* Pretend that we're calling out to a server to evaluate a heuristic
	 *
	 * At present, our heuristics are all in Heuristics.js and SudokuMockup.js
	 * and are called as (synchronous) functions.  In order to move this prototype
	 * closer to the regime where we're actually calling out to a distant server,
	 * we wrap that function call in a Javascript Promise object to force the
	 * recipient to work as if it's asynchronous.
	 */

	mockupHeuristicRequest(request) {
		return Promise.resolve(
			JSON.parse(
				executeHeuristic(
					JSON.stringify(request))));
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