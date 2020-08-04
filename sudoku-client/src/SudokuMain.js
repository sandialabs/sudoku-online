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
import { request } from './SudokuUtilities';

class SudokuMain extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			initialBoard: null,
			cellActions: [],
			logicalOperators: [],
			serverAddress: 'http://localhost:5000'
		};

		this.sendActionRequestToServer = this.sendActionRequestToServer.bind(this);
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
					<div key={6}>
						<SudokuGame 
							degree={this.props.degree}
							initialBoard={this.state.initialBoard}
							issueBoardRequest={(board, move) => {return this.handleBoardRequest(board, move);}}
							cellActions={this.state.cellActions}
							logicalOperators={this.state.logicalOperators}
							issueActionRequest={this.sendActionRequestToServer}
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

	/* Send a request to the server to perform the requested action.
	 *
	 * It is the caller's responsibility to populate the action object
	 * with the following items:
	 *
	 * - board
	 * - requested action (internal name)
	 * - list of requested logical operators (internal names)
	 */
	sendActionRequestToServer(action) {
		const myRequest = {
			'method': 'POST',
			'url': this.state.serverAddress + '/sudoku/request/evaluate_cell_action',
			'headers': {
				'Content-Type': 'application/json; utf-8',
				'Accept': 'application/json'
			},
			'body': JSON.stringify(action)
		}
		return request(myRequest)
				.then((reply) => JSON.parse(reply))
				.catch((error) => console.log('ERROR sending action request to server: ' + error));
	}

	requestCellActionList() {
		const myRequest = {
			'method': 'GET',
			'url': this.state.serverAddress + '/sudoku/request/list_cell_actions'
		};
		return request(myRequest);
	}

	requestLogicalOperatorList() {
		const myRequest = {
			'method': 'GET',
			'url': this.state.serverAddress + '/sudoku/request/list_logical_operators'
		}
		return request(myRequest);
	}

	populateLogicalOperatorList(resultFromServer) {
		const parsedResponse = JSON.parse(resultFromServer);
		console.log('Received ' + parsedResponse.length + ' logical operators from server.');
		console.log(parsedResponse)
		this.setState({'logicalOperators': parsedResponse});
	}

	populateCellActionList(resultFromServer) {
		const parsedResponse = JSON.parse(resultFromServer);
		console.log('Received ' + parsedResponse.length + ' cell actions from server.');
		console.log(parsedResponse)
		this.setState({'cellActions': parsedResponse});
	}

	componentDidMount() {
		console.log('Main panel mounted.  Call out to get the initial game state.');
		// This will be replaced with a server call once we have a server to call

		this.requestInitialBoard().then(
				(successResponse) => {this.receiveInitialBoard(successResponse);}
			).catch(
				(failure) => {console.log('ERROR requesting initial board: ' + failure);}
			);

		this.requestLogicalOperatorList().then(
				(opList) => { this.populateLogicalOperatorList(opList); }
			).catch(
				(failure) => {console.log('ERROR requesting logical operator list: ' + failure);}
			);

		this.requestCellActionList().then(
				(actionList) => {this.populateCellActionList(actionList);}
			).catch(
				(failure) => {console.log('ERROR requesting cell action list: ' + failure);}
			);
		
	}

	requestInitialBoard(serverAddress) {
		return request({
			'method': 'GET',
			'url': this.state.serverAddress + '/sudoku/request/initialBoard'
		});
	}

	receiveInitialBoard(response) {
		const board = JSON.parse(response);
		console.log('Initial board: name ' + board.name + ', serial number ' + board.serialNumber + ', board object:');
		console.log(board);
		this.setState({initialBoard: board});
	}
}

export default SudokuMain;