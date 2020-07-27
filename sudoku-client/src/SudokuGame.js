// SudokuGame: manage and render the entire game tree
// 
// Our implementation of Sudoku is intended to track the moves and
// decisions players make.  We represent these decisions explicitly
// by showing a tree of boards.  When the user makes a move in a 
// single square, the board is given one or more child nodes that
// illustrate the consequences of that move.
//
// This component manages the game tree, including initial setup.

// Required props:
//  cellActions: list of cell actions (from server)
//  logicalOperators: list of logical operators (from server)
//  initialBoard: top of game
//  xxx revise this to just be the game object

import React from 'react';
import { ActiveBoardView } from './ActiveBoardView';
import { newSerialNumber } from './SudokuUtilities';
import { GameTreeView } from './GameTreeView';
import GameTree from './GameTree';
import { clone } from 'ramda';
import { CellActionPanel } from './CellActionPanel';

class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            gameTree: null,
            activeBoardId: null,
        };

        if (this.props.initialBoard !== null) {
            console.log('SudokuGame: Non-null initial board supplied with props for constructor.');
            const ourBoard = clone(this.props.initialBoard);
            if ((!('serialNumber' in ourBoard)) 
                || ourBoard.serialNumber === undefined
                || ourBoard.serialNumber === null)
            {
                ourBoard.serialNumber = newSerialNumber('board');
                console.log('SudokuGame: Assigning serial number ' + ourBoard.serialNumber + ' to initial board.');
            }
            this.state.gameTree = GameTree.makeGameTreeNode(ourBoard);
            this.state.activeBoardId = this.state.gameTree.data.board.serialNumber;
        }
    }

    initializeGameTree(rootBoard) {
        console.log('SudokuGame: Initializing game tree.');
        const tree = GameTree.makeGameTreeNode(rootBoard);
        this.setState({
            gameTree: tree,
            activeBoardId: tree.id
        });
    } 

    boardAnnouncesChoice(board, cell, choice) {
        console.log("Board announcing choice: board serial number "
                    + board.serialNumber 
                    + ", clicked cell " 
                    + cell);
        const action = {
            'action': 'selectValueForCell',
            'cell': cell,
            'value': choice
        };

        return this.props.issueBoardRequest(board, action)
                         .then(result => {this.handleNewBoards(board.serialNumber, action, result);})
 //                        .catch(result => {console.log('ERROR handling heuristic request: ' + result);});
    }

    handleNewBoards(parentSerial, action, response) {
        console.log('handleNewBoards: parentSerial is ' + parentSerial);
        console.log('type of response: ' + typeof(response));
        console.log(response);
        console.log('response length: ' + response.length);

        this.setState({
            gameTree: GameTree.addBoards(
                this.state.gameTree,
                parentSerial,
                response
                )
        });
    }

    activeBoard() {
        if (!this.state.hasOwnProperty('activeBoardId')) {
            console.log('ERROR: Game has no active board.  This shouldn\'t happen.');
        } else {
            const node = GameTree.findNodeById(this.state.gameTree, this.state.activeBoardId);
            return node.data.board;
        }
    }

    changeActiveBoard(boardSerial) {
        if (boardSerial !== this.state.activeBoardId) {         
            console.log('SudokuGame: Request received to change active board to ' + boardSerial + '.');
            this.setState({activeBoardId: boardSerial});
        }    
    }

    render() {
        if (this.state.gameTree === null) {
            return (
                <div>
                   SudokuGame does not yet have a game tree.  This is OK; it means we don't
                   have our initial board yet.  If this message doesn't go away immediately,
                   make sure the server is running on localhost port 5000.
                </div>
            );
        } else if (this.state.gameTree.data.board === null
                   || this.state.gameTree.data.board === undefined) {
            return (
                <div>
                    SudokuGame has a game tree but no root board.  This shouldn't happen.
                </div>
            );
        } else {
            const board = this.activeBoard();
            console.log('render(): active board serial number: ' + board.serialNumber);
            return (
                <div id="gameContainer">
                    <div id="actionsAndOperators">
                        <span id="cellActions">
                            <CellActionPanel
                                actions={this.props.cellActions}
                                selectedActionChanged={(newAction) => {console.log('selectedActionChanged: ' + newAction);}}
                                executeAction={() => {console.log('executeAction clicked');}}
                                />
                        </span>
                    </div>
                    <table id="gameTable">
                        <tbody>
                            <tr>
                                <td id="entireTreeCell">
                                    <div>
                                        <p>This cell will contain the entire game tree.</p>
                                        <GameTreeView
                                            tree={this.state.gameTree}
                                            changeActiveBoard={(serial) => {this.changeActiveBoard(serial);}}
                                            />
                                    </div>
                                </td>
                                <td id="activeBoardCell">
                                   <p>Currently active: Board {board.serialNumber}</p>
                                   <ActiveBoardView
                                        board={board}
                                        active={true}
                                        announceChoice={(board, cell, choice) => {this.boardAnnouncesChoice(board, cell, choice);}}
                                        />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                );
        }
    }
}

export default SudokuGame;