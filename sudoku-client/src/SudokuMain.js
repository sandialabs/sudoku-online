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
			availableHeuristics: null,
			selectedHeuristic: null
		};
	}

	render() {
		let heuristicPanelContents = [];

		if (this.state.availableHeuristics === null) {
			heuristicPanelContents.push(<p>Heuristic list is not yet available.</p>);
		} else {
			heuristicPanelContents = 
				this.state.availableHeuristics.map(
					heuristic => {
						return this.makeHeuristicRadioButton(heuristic.internal_name, heuristic.user_name);
					}
				);
		}

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
						{heuristicPanelContents}
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

	makeHeuristicRadioButton(internalName, userName) {
		console.log('makeHeuristicRadioButton: internalName ' + internalName + ', userName ' + userName + ', selectedHeuristic ' + this.state.selectedHeuristic);
		return (
			<div className='heuristic-form' key={internalName}>
			  <label>
			    <input
			      type='radio'
			      name='selectHeuristic'
			      value={internalName}
			      checked={this.state.selectedHeuristic === internalName}
			      onChange={event => {this.handleHeuristicSelection(event);}}
			      className='heuristic-radio-button'
			      />
			    {userName}
			  </label>
			</div>
			);
	}

	handleHeuristicSelection(changeEvent) {
		console.log('handleHeuristicSelection: Currently selected heuristic before change is ' + this.state.selectedHeuristic);
		console.log('handleHeuristicSelection: New heuristic is ' + changeEvent.target.value);
		this.setState({
			'selectedHeuristic': changeEvent.target.value
		});
	}

	/* Send off a request for asynchronous evaluation of a heuristic.
	 *
	 * This function will eventually make an HTTP call to an external
	 * server.  For now, it calls a mockup function that pretends
	 * to be asynchronous.
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
			board: board,
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
		const requestAsString = JSON.stringify(request);
		const resultAsString = executeHeuristic(requestAsString);

		return Promise.resolve(
			JSON.parse(
				executeHeuristic(
					JSON.stringify(request))));
	}


	requestHeuristicList() {
		const request = { 'heuristic': 'listHeuristics', 
	                      'board': null };

	    return Promise.resolve(
	    	JSON.parse(
	    		executeHeuristic(
	    			JSON.stringify(request))));
	}

	populateHeuristicList(resultFromServer) {
		console.log('Heuristic list from server:');
		console.log(resultFromServer);
		this.setState({'availableHeuristics': resultFromServer});
	}

	componentDidMount() {
		console.log('Main panel mounted.  Call out to get the initial game state.');
		// This will be replaced with a server call once we have a server to call

		const boardPromise = Promise.resolve(JSON.parse(requestInitialBoard(3)));

		boardPromise.then(
			(board) => (this.setState({initialBoard: board}))
			);

		this.requestHeuristicList().then(
			heuristicList => { this.populateHeuristicList(heuristicList); }
			);
		
	}
}

export default SudokuMain;