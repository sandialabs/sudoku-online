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
//  submitFinishedGameTree: function
//  

import React from 'react';
import { clone } from 'ramda';

import { Button } from '@material-ui/core';
import { Grid } from '@material-ui/core';
import { Paper } from '@material-ui/core';
import { Typography } from '@material-ui/core';


import { ActiveBoardView } from './ActiveBoardView';
import { newSerialNumber } from './SudokuUtilities';
import { GameTreeView } from './GameTreeView';
import GameTree from './GameTree';
import { CellActionPanel } from './CellActionPanel';
import { LogicalOperatorPanel } from './LogicalOperatorPanel';
import PropTypes from 'prop-types';


const SELECT_OPS_ACTION = {
    cost: 0,
    description: 'Select cell operations that will be applied after every move',
    internal_name: 'selectops',
    user_name: 'Select Logical Operations',
};

class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            currentPuzzleIndex: null,
            gameTree: null,
            activeBoardId: null,
            selectedLogicalOperators: [],
            selectedBoardSquare: null,
            selectedValue: null,
            selectLogicalOperatorsUpFront: false,
            logicalOperatorsSelected: false
        };

        if (this.props.initialBoard !== null && this.props.initialBoard !== undefined) {
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
                // FIXME: make sure the default action is not disabled
                defaultAction = this.props.cellActions[0];
            }
            const currentScore = this.computeScore();
            const actionsEnabled = (
                this.state.selectLogicalOperatorsUpFront === false
                || this.state.logicalOperatorsSelected
                );
            const logicalOperatorsFrozen = (
                this.state.selectLogicalOperatorsUpFront 
                && this.state.logicalOperatorsSelected
                );

            return (
                <Grid container id="gameContainer">
                    <Grid container item xs={12} id="actionsAndOperators">
                        <Grid item xs={6}>
                            <CellActionPanel
                                allActions={this.props.cellActions}
                                permittedActions={board.availableActions}
                                defaultAction={defaultAction}
                                selectedActionChanged={(newAction) => {this.handleCellActionSelection(newAction)}}
                                executeAction={(action) => this.handleExecuteAction(action)}
                                actionsEnabled={actionsEnabled}
                                />
                        </Grid>
                        <Grid item xs={6}>
                            <LogicalOperatorPanel
                                operators={this.props.logicalOperators}
                                selectionChanged={(operators) => {this.handleLogicalOperatorSelection(operators);}}
                                selectLogicalOperatorsUpFront={this.state.selectLogicalOperatorsUpFront}
                                logicalOperatorsFrozen={logicalOperatorsFrozen}
                                confirmOperatorSelection={() => {
                                    console.log("SudokuGame: Confirming logical operator selection.");
                                    this.setState({logicalOperatorsSelected: true});
                                }}
                                />
                        </Grid>
                        <Grid item xs={12}>
                            <Paper>
                                <Typography variant="h4">Current Score: {currentScore}</Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                    <Grid container item id="gameTree" xs={6}>
                        <GameTreeView
                            tree={this.state.gameTree}
                            changeActiveBoard={(serial) => {this.changeActiveBoard(serial);}}
                            />
                    </Grid>
                    <Grid container item id="activeBoard" xs={6}>
                         <ActiveBoardView
                            board={board}
                            announceChoice={(board, cell, choice) => {this.boardAnnouncesChoice(board, cell, choice);}}
                            />
                    </Grid>
                    <Grid item xs={12} id="doneButtonContainer">
                        <Button variant="contained" color="primary" onClick={() => this.handleFinish()}>Finish This Board</Button>
                    </Grid>
                </Grid>
                );
        }
    } // end of render()

    componentDidMount() {
        this.requestNextBoard()
    }

    handleFinish() {
        console.log('Finishing board and submitting result.');
        this.props.submitFinishedGameTree(this.state.gameTree);
    }

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
                if ('cost' in node.data.board) {
                    all_scores.push(node.data.board.cost);
                }
            }
            );

        return all_scores.reduce((a, b) => (a+b), 0);
    }

    configureNewBoard(board) {
        // XXX YOU ARE HERE
        // Check to see if 'selectOps' is in this board's permitted actions.
        // If so, set flags that will tell render() to display the info dialog,
        // the logical ops panel to display its "Confirm Selection" button,
        // and disable the cell actions until that's done.
        if (board.puzzleName.indexOf("select_ops_upfront") !== -1) {
            this.setState({
                selectLogicalOperatorsUpFront: true,
                logicalOperatorsSelected: false
            });
        } else {
            this.setState({
                selectLogicalOperatorsUpFront: false,
                logicalOperatorsSelected: false
            });
        }
        this.initializeGameTree(board);
    }

    requestNextBoard() {
        if (this.props.boards === null || this.props.boards.length === 0) {
            console.log('ERROR: Can\'t request next board when there are no boards!');
            return;
        }

        let nextBoardIndex = 0;

        if (this.state.currentPuzzleIndex !== null) {
            nextBoardIndex = this.state.currentPuzzleIndex + 1;
            if (nextBoardIndex === this.props.puzzles.length) {
                console.log('ERROR: Can\'t advance past the last board.');
                return;
            }
        }

        const boardName = this.props.boards[nextBoardIndex];
        this.props.requestBoard({name: boardName})
            .then(
                (boardAsString) => {
                    this.setState({
                        currentPuzzleIndex: nextBoardIndex
                    });
                    this.configureNewBoard(JSON.parse(boardAsString));
                }
                )
            .catch(
                (errorResponse) => {
                    console.log('ERROR fetching board ' + nextBoardIndex + ' (' + boardName + '): '
                        + errorResponse);
                }
                );
    }
}


SudokuGame.propTypes = {
    cellActions: PropTypes.array.isRequired,
    logicalOperators: PropTypes.array.isRequired,    
    initialBoard: PropTypes.object,
    issueActionRequest: PropTypes.func.isRequired,
    submitFinishedGameTree: PropTypes.func.isRequired,
    requestBoard: PropTypes.func.isRequired,
    boards: PropTypes.array
}
export default SudokuGame;

// YOU ARE HERE: 
// After that, set a flag in this.state that talks about whether or not we need to set the operators up front.
// 
// If we do, add a "Confirm Operator Selection" button to the logical operator panel.  Have it pop up a yes/no
// modal dialog box: "The N logical operators you have chosen will cost X points per move.  Select Confirm to
// make your selection or Cancel to go back and change your choices.  Once you confirm your choices, you will
// not be able to modify them until you start another board."
// 
// After confirmation, enable all the cell actions and proceed as normal.
// 
// Alternately, pop up that dialog as soon as the board is displayed and explain that for this game you have
// to select operators up front.  That's probably the better idea because it doesn't require the user to 
// guess at anything.