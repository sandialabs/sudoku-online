// SudokuGame: manage and render the entire game tree
// 
// Our implementation of Sudoku is intended to track the moves and
// decisions players make.  We represent these decisions explicitly
// by showing a tree of boards.  When the user makes a move in a 
// single square, the board is given one or more child nodes that
// illustrate the consequences of that move.
//
// This component manages the game tree, including initial setup.

import React from 'react';
import SudokuBoard from './SudokuBoard';
import { newSerialNumber } from './SudokuUtilities';

class GameTree {
    constructor() {
        this.root = null;
        this.allNodes = [];
    }

    nodeBySerialNumber(serialNumber) {
        console.log('nodeBySerialNumber: Requested node for board ' + serialNumber);
        const boardNode = this.allNodes[serialNumber];
        console.log('retrieved node: ');
        console.log(boardNode);
        return this.allNodes[serialNumber];
    }

    boardBySerialNumber(serialNumber) {
        return this.nodeBySerialNumber(serialNumber).board;
    }

    addBoard(newBoard, parentId) {
        newBoard.serialNumber = newSerialNumber('board');
        console.log('addBoard: Assigned serial number ' + newBoard.serialNumber);
        let newNode = null;
        if (this.root === null || parentId === undefined) {
            if (this.root === null) {
                console.log('First board received.  Setting game tree root to board ' 
                            + newBoard.serialNumber);
            } else {
                console.log('addBoard: parentId is ' + parentId + '.  Setting game tree root.');
            }
            newNode = new TreeNode(null);
            this.root = newNode;
            this.root.board = newBoard;
        } else {
            const parentNode = this.nodeBySerialNumber(parentId);
            if (parentNode === null || parentNode === undefined) {
                console.log('ERROR: Couldn\'t find tree node for board ' + parentId);
                return;
            }
            newNode = parentNode.addChildBoard(newBoard);
        }
        this.allNodes[newBoard.serialNumber] = newNode;
        console.log('After adding board with serial number ' 
                    + newBoard.serialNumber 
                    + ', board array length is ' + this.allNodes.length);
    }
        
    boardStructureForTreeView() {
        if (this.root === null) {
            return ({
                'name': 'empty tree',
                'toggled': false,
                'children': []
            }); 
        } else {
            return this.root.treeStructure();
        }
    }
}


class TreeNode {
    constructor(parent) {
        this.parent = parent;
        this.children = [];
        this.board = null;
    }

    addChildBoard(board) {
        const childNode = new TreeNode(this);
        childNode.board = board;
        this.children.push(childNode);
        return childNode;
    }

    treeStructure() {
        const childStructure = this.children.map(
            child => { return child.treeStructure(); }
            );

        return {
            'name': 'Board ' + this.board.serialNumber,
            'toggled': false,
            'children': childStructure
        }
    }
}


class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            gameTree: null,
        };
        if (this.props.initialBoard !== null) {
            console.log('SudokuGame: Non-null initial board supplied with props for constructor.');
            this.state.gameTree = new GameTree();
            this.state.gameTree.addBoard(this.props.initialBoard);
            this.state.activeBoardId = this.state.gameTree.root.board.serialNumber;
        }
    }

    // When we get our initial board, we need to update/initialize the game tree.
    componentDidUpdate(oldProps) {
        if (oldProps.initialBoard !== this.props.initialBoard) {
            this.initializeGameTree(this.props.initialBoard);
        }
    }

    initializeGameTree(rootBoard) {
        const newGameTree = new GameTree();
        newGameTree.addBoard(rootBoard);
        this.setState({
            gameTree: newGameTree,
            activeBoardId: newGameTree.root.board.serialNumber,
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
                         .catch(result => {console.log('ERROR handling heuristic request: ' + result);});
    }

    handleNewBoards(parentSerial, action, response) {
        console.log('handleNewBoards: parentSerial is ' + parentSerial);
        console.log('type of response: ' + typeof(response));
        console.log(response);
        const updatedTree = this.state.gameTree;

        response.forEach(board => {updatedTree.addBoard(board, parentSerial);});
        this.setState({gameTree: updatedTree});
    }

    activeBoard() {
        if (!this.state.hasOwnProperty('activeBoardId')) {
            console.log('ERROR: Game has no active board.  This shouldn\'t happen.');
        } else {
            console.log('active board ID: ' + this.state.activeBoardId);
            return this.state.gameTree.boardBySerialNumber(this.state.activeBoardId);
        }
    }

    render() {
        if (this.state.gameTree === null) {
            return (
                <div>
                   SudokuGame does not yet have a game tree.  This is OK; it means we don't
                   have our initial board yet.
                </div>
            );
        } else if (this.state.gameTree.root.board === null) {
            return (
                <div>
                    SudokuGame has a game tree but no root board.  This shouldn't happen.
                </div>
            );
        } else {
            const gameTree = JSON.stringify(this.state.gameTree.boardStructureForTreeView());
            const board = this.activeBoard();
            console.log('render(): active board serial number: ' + board.serialNumber);
            console.log('active board:');
            console.log(board);
            return (
                <table id="gameTable">
                    <tbody>
                        <tr>
                            <td id="entireTreeCell">
                               This cell will contain the entire game tree.  Structure: {gameTree}
                            </td>
                            <td id="activeBoardCell">
                               This cell will contain just the active board.
                               <SudokuBoard
                                    degree={this.props.degree}
                                    board={board}
                                    active={true}
                                    announceChoice={(board, cell, choice) => {this.boardAnnouncesChoice(board, cell, choice);}}
                                    />
                            </td>
                        </tr>
                    </tbody>
                </table>
                );
        }
    }
}

export default SudokuGame;