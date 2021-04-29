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
import { AnalysisQuestionPanel } from './AnalysisQuestionPanel';
import { ButtonWithAlertDialog } from './ButtonWithAlertDialog';
import { newSerialNumber } from './SudokuUtilities';
import { GameTreeView } from './GameTreeView';
import GameTree from './GameTree';
import { CellActionPanel } from './CellActionPanel';
import { LogicalOperatorPanel } from './LogicalOperatorPanel';
import PropTypes from 'prop-types';

import { DebugInfoPanel } from './DebugInfoPanel';


class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            abandonedGameTrees: [],
            activeBoardId: null,
            currentPuzzleIndex: null,
            gameTree: null,
            gameTreeExpandedNodes: new Set(),
            logicalOperatorsSelected: false,
            selectedBoardSquare: null,
            selectedLogicalOperators: [],
            selectedValue: null,
            selectLogicalOperatorsUpFront: false,
            analysisAnswer: "(no answer specified)"
        };
    }

    initializeGameTree(rootBoard) {
        console.log('SudokuGame: Initializing game tree.');
        const gameTree = GameTree.makeGameTreeNode(rootBoard);

        // Set the root node to be selected and give it a distinguished name
        gameTree.name = 'Starting Board';

        this.setState({
            gameTree: gameTree,
            activeBoardId: gameTree.data.board.serialNumber
        });
    } 

    boardAnnouncesChoice(board, cell, choice) {
        this.setState({
            selectedBoardSquare: cell,
            selectedValue: choice
        });
    }

    puzzleDisplayName() {
        if (this.state.currentPuzzleIndex === null) {
            return "(no current puzzle)";
        } else {
            return this.state.gameTree.data.board.displayName;
        }
    }

    handleNewBoards(parentSerial, newBoards, request) {
        
        console.log('handleNewBoards: parentSerial is ' + parentSerial);
        console.log('handleNewBoards: request: ');
        console.log(request);
        console.log('handleNewBoards: reply: ');
        console.log(newBoards);

        // Each new board needs to know about the action taken to produce it
        // so that it can come up with a meaningful name.
        for (const board of newBoards) {
            board.action = request.action
        }
        
        this.setState({
            gameTree: GameTree.addBoards(
                this.state.gameTree,
                parentSerial,
                newBoards
                ),
        });

        const newActiveSerial = findFirstNonBacktrackBoard(newBoards);
        console.assert(
            newActiveSerial !== null,
            "Couldn't find non-backtrack message in new boards"
            );
        this.changeActiveBoard(newActiveSerial);
    }

    activeBoard() {
        if (!this.state.hasOwnProperty('activeBoardId')) {
            throw new Error('ERROR: Game has no active board.  This shouldn\'t happen.');
        } else {
            const node = GameTree.findNodeById(this.state.gameTree, this.state.activeBoardId);
            return node.data.board;
        }
    }

    rootBoard() {
        if (!this.state.gameTree) {
            throw new Error('ERROR: rootBoard() called before we have a root board.');
        } else {
            return this.state.gameTree.data.board;
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

    announceBoardToggled(boardSerial) {
        const newExpandedNodes = new Set(this.state.gameTreeExpandedNodes);
        if (newExpandedNodes.has(boardSerial)) {
            newExpandedNodes.delete(boardSerial);
        } else {
            newExpandedNodes.add(boardSerial);
        }
        this.setState({
            gameTreeExpandedNodes: newExpandedNodes
        });
    }

    canCellActionsExecute() {
        if (this.state.selectLogicalOperatorsUpFront === true 
            && this.state.logicalOperatorsSelected === false) 
        {
            return false;
        }

        if (this.state.activeBoardId === null 
            || this.state.activeBoardId === -1)
        {
            return false;
        }

        if (this.state.selectedValue === null)
        {
            return false;
        }

        if (this.isTerminalNode(this.state.activeBoardId) === false) {
            return false;
        }

        return true;
    }

    // These reasons are listed in descending order of priority.
    cellActionsDisabledBecause() {
        if (this.state.selectLogicalOperatorsUpFront === true 
            && this.state.logicalOperatorsSelected === false) 
        {
            return 'Select Logical Operators First';
        }

        if (this.state.activeBoardId === null 
            || this.state.activeBoardId === -1)
        {
            return 'Error: No Active Board';
        }

        if (this.isTerminalNode(this.state.activeBoardId) === false) {
            return 'This board has already been acted upon';
        }

        if (this.state.selectedValue === null)
        {
            return 'You must select a square to operate upon';
        }
        
        return 'ERROR: No reason given for disabled actions';
    }

    render() {
        if (this.state.gameTree === null) {
            return (
                <div>
                   Loading Game Tree...
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
            console.assert(this.state.gameTree !== undefined,
                "SudokuGame: this.state.gameTree is undefined");
            console.log("Game tree:");
            console.log(this.state.gameTree);
            const board = this.activeBoard();
            
            let defaultAction = null;
            if (this.props.cellActions !== null && this.props.cellActions.length > 0) {
                // FIXME: make sure the default action is not disabled
                defaultAction = this.props.cellActions[0];
            }
            const rootBoard = this.rootBoard();
            const currentScore = this.computeScore();
            const actionsEnabled = this.canCellActionsExecute();
            const disabledReason = this.cellActionsDisabledBecause();
            const startingBoard = this.state.gameTree.data.board;
            const analysisQuestion = "How is a raven like a writing desk?";
            
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
                                disabledReason={disabledReason}

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
                        <Grid item xs={6}>
                            <Paper>
                                <Typography variant="h6">Current Puzzle: {startingBoard.displayName}</Typography>
                            </Paper>
                        </Grid>
                        <Grid item xs={6}>
                            <Paper>
                                <Typography variant="h6">Current Score: {currentScore}</Typography>
                            </Paper>
                        </Grid>
                    </Grid>
                    <Grid container item id="gameTree" xs={6}>
                        <GameTreeView
                            gameTree={this.state.gameTree}
                            activeBoardId={this.state.activeBoardId}
                            expandedNodes={this.state.gameTreeExpandedNodes}
                            changeActiveBoard={(serial) => {this.changeActiveBoard(serial);}}
                            announceBoardToggled={(serial) => {this.announceBoardToggled(serial);}}
                            />
                    </Grid>
                    <Grid container item id="activeBoard" xs={6}>
                         <ActiveBoardView
                            board={board}
                            announceChoice={(board, cell, choice) => {this.boardAnnouncesChoice(board, cell, choice);}}
                            selectedSquare={this.state.selectedBoardSquare}
                            selectedValue={this.state.selectedValue}
                            />
                    </Grid>
                    <Grid container id="questionPanel">
                        <AnalysisQuestionPanel
                            question={rootBoard.question}
                            handleAnswerChanged={(answer) => {this.handleAnalysisAnswerChanged(answer)}}
                        />
                    </Grid>
                    <Grid container id="finishOrResetButtonContainer">
                        <Grid item xs={3}>
                            <ButtonWithAlertDialog
                                buttonText={"Finish This Puzzle"}
                                dialogTitle={"Sudoku: Please Confirm"}
                                dialogText={"Are you sure you want to finish this puzzle and move on to the next one?"}
                                handleConfirmation={() => this.handleFinishButton()}
                                />
                        </Grid>
                        <Grid item xs={3}>
                            <ButtonWithAlertDialog
                                buttonColor="secondary"
                                buttonText={"Reset This Puzzle"}
                                dialogTitle={"Sudoku: Please Confirm"}
                                dialogText={"Are you sure you want to discard your work and start this puzzle over?"}
                                handleConfirmation={() => this.handleResetButton()}
                                />

                        </Grid>
                    </Grid>

                    <Grid container id="debugInfo">
                       <DebugInfoPanel 
                            gameConfiguration={this.props.gameConfiguration}
                            puzzleInfo={rootBoard}
                            puzzles={this.props.puzzles}
                            answer={this.state.analysisAnswer}
                            />
                    </Grid>
                </Grid>

                );
        }
    } // end of render()

    componentDidMount() {
        this.displayNextBoard()
    }

    handleAnalysisAnswerChanged(newAnswer) {
        console.log("User's answer to analysis question changed to '"
                    + newAnswer + "'.");
        this.setState({
            analysisAnswer: newAnswer
        });
    }

    handleFinishButton() {
        console.log('Finishing board and submitting result.');
        this.props.submitFinishedGameTree(
            this.state.gameTree,
            this.state.abandonedGameTrees,
            this.state.analysisAnswer
            );
        this.displayNextBoard();
    }

    handleResetButton() {
        this.resetState();
        this.initializeGameTree(
            this.props.puzzles[
                this.state.currentPuzzleIndex
                ]);
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
            .then(response => this.handleNewBoards(this.activeBoard().serialNumber, response, request));
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

    displayNextBoard() {
        if (this.props.puzzles === null 
            || this.props.puzzles.length === 0) {
            throw new Error("ERROR: No boards present.  Can't display next board.");
        }

        let nextBoardIndex = 0;
        if (this.state.currentPuzzleIndex !== null) {
            nextBoardIndex = this.state.currentPuzzleIndex + 1;
        } 

        if (nextBoardIndex === this.props.puzzles.length) {
            throw new Error("ERROR: Can't advance past the last board");
        }

        this.resetState();
        this.setState({
            currentPuzzleIndex: nextBoardIndex
        });

        const nextPuzzle = this.props.puzzles[nextBoardIndex];
        const selectUpFront = !nextPuzzle.rules.canChangeLogicalOperators;
        this.setState({
            selectLogicalOperatorsUpFront: selectUpFront,
        })

        this.initializeGameTree(nextPuzzle);

        // this.props.requestBoard({name: boardName})
        //     .then(
        //         (boardAsString) => {
        //             this.setState({
        //                 currentPuzzleIndex: nextBoardIndex
        //             });
        //             this.configureNewBoard(JSON.parse(boardAsString));
        //         }
        //         )
        //     .catch(
        //         (errorResponse) => {
        //             console.log('ERROR fetching board ' + nextBoardIndex + ' (' + boardName + '): '
        //                 + errorResponse);
        //         }
        //         );
    }


    resetState() {
        this.setState({
            selectLogicalOperatorsUpFront: false,
            logicalOperatorsSelected: false,
            selectedCellAction: null,
            selectedLogicalOperators: [],
            gameTree: null,
            gameTreeExpandedNodes: new Set(),
            selectedBoardSquare: null,
            selectedValue: null,
            analysisAnswer: "(no answer specified)"
        });
    }

    isTerminalNode(boardId) {
        const node = GameTree.findNodeById(this.state.gameTree, boardId);
        return (node.children === null 
                || node.children.length === 0);
    }
}

function findFirstNonBacktrackBoard(boardList) {
    for (const board of boardList) {
        if (board.backtrackingBoard === undefined
            || board.backtracingBoard === false) {
            return board.serialNumber;
        }
    }
    return null;
}

SudokuGame.propTypes = {
    cellActions: PropTypes.array.isRequired,
    logicalOperators: PropTypes.array.isRequired,    
    issueActionRequest: PropTypes.func.isRequired,
    submitFinishedGameTree: PropTypes.func.isRequired,
    puzzles: PropTypes.array,
    gameName: PropTypes.string
}
export default SudokuGame;

