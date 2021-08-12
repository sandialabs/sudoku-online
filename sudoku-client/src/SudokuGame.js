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

import { Grid } from '@material-ui/core';
import { Paper } from '@material-ui/core';
import { Typography } from '@material-ui/core';

import { ActionSelectionPanel } from './ActionSelectionPanel';
import { ActiveBoardView } from './ActiveBoardView';
import { AnalysisAnswerPanel } from './AnalysisAnswerPanel';
import { ButtonWithAlertDialog } from './ButtonWithAlertDialog';
import { GameInfoDialog } from './GameInfoDialog';
import { MechanicalTurkIdForm } from './MechanicalTurkIdForm';
import { GameTreeView } from './GameTreeView';
import GameTree from './GameTree';
import PropTypes from 'prop-types';


class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            abandonedGameTrees: [],
            activeBoardId: null,
            currentPuzzleIndex: null,
            currentPuzzleInitialScore: props.initialScore,
            gameTree: null,
            gameTreeExpandedNodes: new Set(),
            logicalOperatorsSelected: false,
            mechanicalTurkId: 'unspecified',
            selectedBoardSquare: null,
            selectedLogicalOperators: [],
            selectedValue: null,
            selectLogicalOperatorsUpFront: false,
            analysisAnswer: "(no answer specified)",
            resetCount: 0
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
            && this.state.logicalOperatorsSelected === false) {
            return false;
        }

        if (this.state.activeBoardId === null
            || this.state.activeBoardId === -1) {
            return false;
        }

        // XXX REFACTOR -- need 'readyToExecute' flag from ActionSelectionPanel
        if (this.state.selectedBoardSquare === null
            && (this.state.selectedLogicalOperators === null
                || this.state.selectedLogicalOperators.length === 0)) {
            return false;
        }

        if (this.isTerminalNode(this.state.activeBoardId) === false) {
            return false;
        }

        return true;
    }

    // These reasons are listed in descending order of priority.
    cellActionsDisabledBecause() {
        // XXX REFACTOR -- need 'logicalOpsFrozen' flag
        if (this.state.selectLogicalOperatorsUpFront === true
            && this.state.logicalOperatorsSelected === false) {
            return 'Select Logical Operators First';
        }

        if (this.state.activeBoardId === null
            || this.state.activeBoardId === -1) {
            return 'Error: No Active Board';
        }

        if (this.isTerminalNode(this.state.activeBoardId) === false) {
            return 'This board has already been acted upon';
        }

        if (this.state.selectedBoardSquare === null) {
            return 'You must select a square or some logical operators';
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

      
            const rootBoard = this.rootBoard();
            const currentScore = this.state.currentPuzzleInitialScore - this.computeScore();
            const actionsCanExecute = this.canCellActionsExecute();
            const disabledReason = this.cellActionsDisabledBecause();
            const userCanFinishPuzzle = (this.state.analysisAnswer !== "(no answer specified"
                                         && this.state.mechanicalTurkId !== "unspecified");
            let finishButtonDialogText = "Are you sure you want to submit your answer to this puzzle and move on?";
            let finishButtonDialogTitle = "Sudoku: Please Confirm";
            if (!userCanFinishPuzzle) {
                finishButtonDialogText = "You must first answer the analysis question and provide your Mechanical Turk ID."
                finishButtonDialogTitle = "Sudoku: Some Information Missing";
            }
            const logicalOperatorsFrozen = (
                this.state.selectLogicalOperatorsUpFront
                && this.state.logicalOperatorsSelected
            );

            console.log('SudokuGame: props.cellActions:');
            console.log(this.props.cellActions);
            const enabledActions = actionsEnabledGivenSelection(
                this.state.selectedBoardSquare,
                this.state.selectedValue,
                this.state.selectedLogicalOperators,
                this.state.selectLogicalOperatorsUpFront
            );

            // Single Source Of Truth principle suggests that the decision 
            // of whether or not cell actions can execute should be made
            // entirely at this level.

            return (
                <Grid container id="gameContainer">
                    <Grid item id="questionPanel">
                        <Paper>
                            <Typography variant="h2">The Question: {rootBoard.question}</Typography>
                        </Paper>
                    </Grid>

                    <Grid container wrap="nowrap"
                        justify="flex-start"
                        id="boardAndOperators"
                        spacing={2}
                    >
                        <Grid item xs={5} xl={4} id="gameBoard">
                            <ActiveBoardView
                                board={board}
                                announceChoice={(board, cell, choice) => { this.boardAnnouncesChoice(board, cell, choice); }}
                                selectedSquare={this.state.selectedBoardSquare}
                                selectedValue={this.state.selectedValue}
                            />
                            <Typography variant="h5">Current Score: {currentScore}</Typography>
                        </Grid>

                        <Grid container item xs={3} xl={2} id="actionsAndOperators" direction="column">
                            <ActionSelectionPanel
                                cellActions={this.props.cellActions}
                                // this stays here
                                permittedActions={enabledActions}
                                // refactor
                                actionsCanExecute={actionsCanExecute}
                                // refactor
                                executeActionCallback={(action, operators) => this.handleExecuteAction(action, operators)}
                                // refactor
                                disabledReason={disabledReason}
                                logicalOperators={this.props.logicalOperators}
                                selectLogicalOperatorsUpFront={this.state.selectLogicalOperatorsUpFront}
                                logicalOperatorsFrozenCallback={() => this.setState({logicalOperatorsSelected: true})}
                                logicalOperatorSelectionChangedCallback={(opList) => this.handleLogicalOperatorSelection(opList)}
                                key={this.state.resetCount}
                                />
                        </Grid>

                        <Grid item container
                            id="gameTree"
                            xs={4} med={5} xl={6}
                            justify="flex-start"
                            direction="column">
                            <Typography variant="h5">Decision Tree</Typography>
                            <GameTreeView
                                gameTree={this.state.gameTree}
                                activeBoardId={this.state.activeBoardId}
                                expandedNodes={this.state.gameTreeExpandedNodes}
                                changeActiveBoard={(serial) => { this.changeActiveBoard(serial); }}
                                announceBoardToggled={(serial) => { this.announceBoardToggled(serial); }}
                            />
                        </Grid>

                    </Grid>

                    <Grid container id="answerInput">
                        <Grid item>
                            <AnalysisAnswerPanel
                                handleAnswerChanged={(answer) => { this.handleAnalysisAnswerChanged(answer) }}
                                key={this.state.currentPuzzleIndex}
                            />
                        </Grid>
                        <Grid item>
                            <MechanicalTurkIdForm
                                handleChange={(value) => { this.setState({ mechanicalTurkId: value }); }}
                            />
                        </Grid>
                    </Grid>

                    <Grid container id="finishOrResetButtonContainer">
                        <Grid item>
                            <ButtonWithAlertDialog
                                buttonText={"Finish This Puzzle"}
                                dialogTitle={finishButtonDialogTitle}
                                dialogText={finishButtonDialogText}
                                handleConfirmation={() => this.handleFinishButton(userCanFinishPuzzle)}
                            />
                        </Grid>
                        <Grid item>
                            <ButtonWithAlertDialog
                                buttonColor="secondary"
                                buttonText={"Reset This Puzzle"}
                                dialogTitle={"Sudoku: Please Confirm"}
                                dialogText={
                                    "Are you sure you want to discard "
                                    + "your work and start this puzzle "
                                    + "over?  You will not get back "
                                    + "the points you have already spent."
                                }
                                handleConfirmation={() => this.handleResetButton()}
                            />

                        </Grid>
                    </Grid>
                    <GameInfoDialog
                        dialogTitle={"Welcome!"}
                        dialogText={"Hello! This web site is meant to be used from Amazon's Mechanical Turk."}
                        defaultState={true}
                    />
                    <GameInfoDialog
                        dialogTitle={"Game finished!"}
                        dialogText={
                            "Thank you for playing these Sudoku boards. " +
                            "You have finished the last puzzle in this game; " +
                            "please close this window. You may choose to play " +
                            "additional games, if available, " +
                            "by returning to whence you came."
                        }
                        handleConfirmation={() => this.handleCloseWindow()}
                        registerOpen={(callback) => this.registerEndGameOpen(callback)}
                    />
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

    handleExecuteLogicalOperators() {
        const shortNames = this.state.selectedLogicalOperators.map(
            (op) => op.internal_name
        );
        console.log('handleExecuteLogicalOperators: Selected operators: ' + JSON.stringify(shortNames));
    }

    handleFinishButton(canFinish) {
        if (canFinish) {
            this.props.submitFinishedGameTree({
                finishedTree: this.state.gameTree,
                abandonedTrees: this.state.abandonedGameTrees,
                answer: this.state.analysisAnswer,
                mechanicalTurkId: this.state.mechanicalTurkId
            });
            this.displayNextBoard();
        }   
    }

    handleResetButton() {
        const abandonedTree = clone(this.state.gameTree);
        const currentScore = this.state.currentPuzzleInitialScore - this.computeScore();
        this.setState({
            abandonedGameTrees: this.state.abandonedGameTrees.concat(abandonedTree),
            currentPuzzleInitialScore: currentScore
        });
        this.resetState();
        this.configureNewBoard(
            this.props.puzzles[
            this.state.currentPuzzleIndex
            ]);
        this.setState({
            resetCount: this.state.resetCount + 1
        });
    }

    registerEndGameOpen(callback) {
        this.openEndGame = callback;
    }

    handleCloseWindow() {
        window.open("about:blank", "_self");
        window.close();
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

    handleExecuteAction(cellAction, selectedLogicalOperators) {
        let operatorString = '(empty)';
        if (selectedLogicalOperators.length > 0) {
            operatorString = selectedLogicalOperators.map(
                (operator) => operator.internal_name
                ).join(', ');;
        }

        console.log('SudokuGame.executeAction: cellAction: '
            + cellAction.internal_name
            + ', operators: '
            + operatorString
            );

            const request = {
            action: {
                action: cellAction.internal_name,
                cell: this.state.selectedBoardSquare,
                value: this.state.selectedValue,
                operators: selectedLogicalOperators.map(op => op.internal_name)
            },
            board: this.activeBoard(),
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

        return all_scores.reduce((a, b) => (a + b), 0);
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
            this.openEndGame()
            return
        }

        this.resetState();
        this.setState({
            currentPuzzleIndex: nextBoardIndex
        });

        const nextPuzzle = this.props.puzzles[nextBoardIndex];
        // const selectUpFront = !nextPuzzle.rules.canChangeLogicalOperators;
        // this.setState({
        //     selectLogicalOperatorsUpFront: selectUpFront,
        // })

        this.configureNewBoard(nextPuzzle);

    }


    resetState() {
        // TODO reset analysis question state
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

// Cell actions are available, or not, depending on whether their
// prerequisites are selected on the game board.
//
// Assign and Exclude require the user to select an available value.
//
// Pivot just requires that the user select an available (unassigned)
// cell -- whether or not they select a value in the cell is immaterial.

function actionsEnabledGivenSelection(selectedCell, selectedValue, selectedLogicalOperators, selectLogicalOperatorsUpFront) {
    return {
        assign: (selectedValue !== null
            && selectedValue !== -1
            && selectedCell !== null),
        exclude: (selectedValue !== null
            && selectedValue !== -1
            && selectedCell !== null),
        pivot: (selectedCell !== null),
        applyops: (selectedLogicalOperators !== null
            && selectedLogicalOperators.length > 0
            && selectLogicalOperatorsUpFront === false)
    };
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
    initialScore: PropTypes.number
}

SudokuGame.defaultProps = {
    initialScore: 100000
}
export default SudokuGame;
