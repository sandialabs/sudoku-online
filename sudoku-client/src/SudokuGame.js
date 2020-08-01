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
//  issueActionRequest: function
//  xxx revise this to just be the game object

import React from 'react';
import { Grid } from '@material-ui/core';

import { ActiveBoardView } from './ActiveBoardView';
import { newSerialNumber } from './SudokuUtilities';
import { GameTreeView } from './GameTreeView';
import GameTree from './GameTree';
import { clone } from 'ramda';
import { CellActionPanel } from './CellActionPanel';
import { LogicalOperatorPanel } from './LogicalOperatorPanel';
import PropTypes from 'prop-types';

class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            gameTree: null,
            activeBoardId: null,
            selectedLogicalOperators: [],
            selectedBoardSquare: null,
            selectedValue: null
        };

        if (this.props.initialBoard !== null) {
            console.log('SudokuGame: Non-null initial board supplied with props for constructor.');
            const ourBoard = clone(this.props.initialBoard);
            if ((!('serialNumber' in ourBoard)) 
                || ourBoard.serialNumber === undefined
                || ourBoard.serialNumber === null)
            {
                ourBoard.serialNumber = newSerialNumber('board');
                console.log('WARNING: SudokuGame: Assigning serial number ' + ourBoard.serialNumber + ' to initial board.');
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
        this.setState({
            selectedBoardSquare: cell,
            selectedValue: choice
        });
    }

    handleNewBoards(parentSerial, response) {
        console.log('handleNewBoards: parentSerial is ' + parentSerial);
        console.log('type of response: ' + typeof(response));
        console.log(response);
        console.log('response length: ' + response.length);

        this.setState({
            gameTree: GameTree.addBoards(
                this.state.gameTree,
                parentSerial,
                response
                ),
        });

        this.changeActiveBoard(response[0].serialNumber);

    }

    activeBoard() {
        if (!this.state.hasOwnProperty('activeBoardId')) {
            throw new Error('ERROR: Game has no active board.  This shouldn\'t happen.');
        } else {
            const node = GameTree.findNodeById(this.state.gameTree, this.state.activeBoardId);
            return node.data.board;
        }
    }

    changeActiveBoard(boardSerial) {
        if (boardSerial !== this.state.activeBoardId) {         
            console.log('SudokuGame: Request received to change active board to ' + boardSerial + '.');
            this.setState({
                activeBoardId: boardSerial,
                selectedBoardSquare: null,
                selectedValue: null
            });
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
            let defaultAction = null;
            if (this.props.cellActions !== null && this.props.cellActions.length > 0) {
                defaultAction = this.props.cellActions[0];
            }
            return (
                <div id="gameContainer">
                    <Grid container spacing={3} id="actionsAndOperators">
                        <Grid item xs={6}>
                            <CellActionPanel
                                allActions={this.props.cellActions}
                                permittedActions={[]}
                                defaultAction={defaultAction}
                                selectedActionChanged={(newAction) => {this.handleCellActionSelection(newAction)}}
                                executeAction={(action) => this.handleExecuteAction(action)}
                                />
                        </Grid>
                        <Grid item xs={6}>
                            <LogicalOperatorPanel
                                operators={this.props.logicalOperators}
                                selectionChanged={(operators) => {this.handleLogicalOperatorSelection(operators);}}
                                canChange={true}
                                />
                        </Grid>
                    </Grid>
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
                                        announceChoice={(board, cell, choice) => {this.boardAnnouncesChoice(board, cell, choice);}}
                                        />
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                );
        }
    } // end of render()


    handleLogicalOperatorSelection(operators) {
        console.log('Logical operator selection contains ' + operators.length + ' items');
        this.setState({
            selectedLogicalOperators: operators
        });
    }

    handleCellActionSelection(selectedAction) {
        this.setState({
            selectedCellAction: selectedAction
        })
    }

    handleExecuteAction(action) {
        const request = {
            action: {
                action: action.internal_name,
                cell: this.state.selectedBoardSquare, 
                value: this.state.selectedValue
            },
            board: this.activeBoard(),
            operators: this.state.selectedLogicalOperators.map(op => op.internal_name)
        };


        console.log('DEBUG: handleExecuteAction running.');
        console.log('request: ');
        console.log(request);
        this.props.issueActionRequest(request)
            .then(response => this.handleNewBoards(this.activeBoard().serialNumber, response));
    }

    /* The score for a game is the sum of the 'cost' attribute for all of its nodes. */
    computeScore() {
        const all_scores = [];

        GameTree.walkTree(
            this.state.gameTree,
            (node) => {
                if ('cost' in node && node.cost !== null) {
                    all_scores.push(node.cost);
                }
            }
            );

        return all_scores.reduce((a, b) => (a+b), 0);
    }

}

SudokuGame.propTypes = {
    cellActions: PropTypes.array,
    logicalOperators: PropTypes.array,    
    initialBoard: PropTypes.object,
    issueActionRequest: PropTypes.func.isRequired
}
export default SudokuGame;