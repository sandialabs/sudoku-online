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
import React, { useState, useEffect } from 'react';
import SudokuGame from './SudokuGame';
import { request } from './SudokuUtilities';
import { ErrorBoundary } from './ErrorBoundary';
import { PropTypes } from 'prop-types';

import {
	useParams
} from 'react-router-dom';

 
function SudokuMain(props) {
	const [boards, setBoards] = useState(null);
	const [cellActions, setCellActions] = useState([]);
	const [logicalOperators, setLogicalOperators] = useState([]);

	const defaultGameName = "pilot_test_a_board";
	let gameName = defaultGameName;

	const params = useParams();

	if (props.gameNameInUrl) {
		gameName = params.gameName;
		console.log("SudokuMain: Using game name from URL: " + gameName);
		console.log("Params:");
		console.log(params);
	} else {
		console.log("SudokuMain: Using default game name.");
	}
    
	// Once the app has been added to the DOM, ask the server for the
	// state we need in order to run the game.  We will re-run this any
	// time the server address or game name change.

	useEffect(
		() => {
				requestLogicalOperatorList(props.serverAddress).then(
					(opList) => setLogicalOperators(JSON.parse(opList))
				).catch(
					(failure) => console.log('ERROR requesting logical operator list: ' + failure)
				);

				requestCellActionList(props.serverAddress).then(
						(actionList) => setCellActions(JSON.parse(actionList))
					).catch(
						(failure) => console.log('ERROR requesting cell action list: ' + failure)
					);
				
				requestGameConfiguration(gameName, props.serverAddress).then(
					(boardList) => setBoards(JSON.parse(boardList))
					).catch(
						(failure) => console.log('ERROR requesting game configuration: ' + failure)
					);
		},
		[props.serverAddress, gameName]
	);

	// Wrap up the server address in helper functions so that 
	// SudokuGame doesn't need to care
	const _requestBoard = (boardName) => requestBoard(boardName, props.serverAddress);
	const _sendActionRequest = (action) => sendActionRequestToServer(action, props.serverAddress);
	const _submitFinishedGameTree = (tree) => submitFinishedGameTree(tree, props.serverAddress);
	if (boards !== null) {
		return (
			<div key={6}>
				<ErrorBoundary>
					<SudokuGame 
						degree={props.degree}
						puzzles={boards}
						cellActions={cellActions}
						logicalOperators={logicalOperators}
						issueActionRequest={_sendActionRequest}
						submitFinishedGameTree={_submitFinishedGameTree}
						requestBoard={_requestBoard}
						/>
				</ErrorBoundary>
			</div>
		);
	} else {
		return (
			<div key={3}>Waiting for initial game state...</div>
		);
	}


}



function submitFinishedGameTree(completedTree, serverAddress) { 
	const myRequest = {
		method: 'POST',
		url: serverAddress + '/sudoku/request/submit_game_tree',
		headers: {
			'Content-Type': 'application/json; utf-8'
		},
		body: JSON.stringify(completedTree)
	};
	return request(myRequest);
}

function requestCellActionList(serverAddress) {
	const myRequest = {
		'method': 'GET',
		'url': serverAddress + '/sudoku/request/list_cell_actions'
	};
	return request(myRequest);
}

function requestGameConfiguration(gameName, serverAddress) {
	return request({
		'method': 'GET',
		'url': serverAddress + '/sudoku/request/boardsForGame/' + gameName
	});
}
	
function requestBoard(boardInfo, serverAddress) {
	return request({
		'method': 'POST',
		'url': serverAddress + '/sudoku/request/initialBoard',
		'headers': {
			'Content-Type': 'application/json; utf-8',
			'Accept': 'application/json'
		},
		'body': JSON.stringify(boardInfo)
	});
}

function requestLogicalOperatorList(serverAddress) {
	const myRequest = {
		'method': 'GET',
		'url': serverAddress + '/sudoku/request/list_logical_operators'
	}
	return request(myRequest);
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
function sendActionRequestToServer(action, serverAddress) {
	const myRequest = {
		'method': 'POST',
		'url': serverAddress + '/sudoku/request/evaluate_cell_action',
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

SudokuMain.propTypes = { 
	degree: PropTypes.number.isRequired,
	gameNameInUrl: PropTypes.bool.isRequired,
	serverAddress: PropTypes.string.isRequired
}
export default SudokuMain;
