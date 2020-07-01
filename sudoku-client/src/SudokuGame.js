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
        return this.allNodes[serialNumber];
    }

    addBoard(newBoard, parentId) {
        newBoard.serialNumber = newSerialNumber('board');
        console.log('addBoard: Assigned serial number ' + newBoard.serialNumber);
        if (this.root === null || parentId === undefined) {
            if (this.root === null) {
                console.log('First board received.  Setting game tree root to board ' 
                            + newBoard.serialNumber);
            } else {
                console.log('addBoard: parentId is ' + parentId + '.  Setting game tree root.');
            }
            this.root = new TreeNode(null);
            this.root.board = newBoard;
        } else {
            const parentNode = this.nodeBySerialNumber(parentId);
            if (parentNode === null || parentNode === undefined) {
                console.log('ERROR: Couldn\'t find tree node for board ' + parentId);
                return;
            }
            parentNode.addChildBoard(newBoard);
        }
        this.allNodes[newBoard.serialNumber] = newBoard;
        console.log('After adding board with serial number ' 
                    + newBoard.serialNumber 
                    + ', board array length is ' + this.allNodes.length);
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
    }
}


class SudokuGame extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            gameTree: null
        }
        if (this.props.initialBoard !== null) {
            console.log('SudokuGame: Non-null initial board supplied with props for constructor.');
            this.state.gameTree = new GameTree();
            this.state.gameTree.addBoard(this.props.initialBoard);
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
            gameTree: newGameTree
        });
    }

    boardAnnouncesChoice(board, cell, choice) {
        console.log("Board announcing choice: board serial number "
                    + board.state.serialNumber 
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
        console.log('UNIMPLEMENTED: handleNewBoards');
        console.log('type of response: ' + typeof(response));
        console.log(response);
        const updatedTree = this.state.gameTree;

        response.forEach(board => {updatedTree.addBoard(board, parentSerial);});
        this.setState({gameTree: updatedTree});
    }

    render() {
        console.log('SudokuGame.render(): this.props.initialBoard:');
        console.log(this.props.initialBoard);
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
            return (
                <div key={3}>
                    <div key={4}>
                        Hi.  This is the Sudoku game tree.  My responsibilities
                        are as follows:
                        <ul>
                            <li>On startup, go ask some server for an initial board.</li>
                            <li>Set up, maintain, and render the game tree.</li>
                            <li>When the user makes a move on a board, contact the
                                server to get the child nodes resulting from that move.</li>
                            <li>When the user has finished the game, transmit the entire
                                game tree to the server along with some metadata yet to
                                be established.</li>
                        </ul>
                    </div>
                    <div key={5}>
                        <SudokuBoard 
                            degree={this.props.degree}
                            board={this.state.gameTree.root.board} 
                            key={6}
                            announceChoice={ (board, cell, choice) => {this.boardAnnouncesChoice(board,cell,choice);} }
                        />
                    </div>
                </div>
                );
        }
    }
}

export default SudokuGame;