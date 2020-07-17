/* Sudoku game tree and associated functions.
 * 
 * This is a Javascript class, not a React component.  It is used
 * throughout the Sudoku client to keep track of the game tree -- that
 * is, the record of decisions the user has made and their results.
 *
 * Classes: 
 *     GameTree
 *         Methods:
 *             constructor()
 *             nodeBySerialNumber(serial)
 *             addBoard(board, parentSerial)
 *             boardStructureForTreeView()
 *
 *     GameTreeNode
 *          Methods:
 *              constructor()
 *          Members:
 *              board: SudokuBoard structure
 *                 
 */

import FunctionalTree from './FunctionalTree';

function makeGameTreeNode(board) {
    return FunctionalTree.makeTreeNode(
        board.serialNumber,
        { board: board }
        );
}

function addChild(tree, parentId, childNode) {
    return FunctionalTree.addChild(tree, parentId, childNode);
}

function findNodeById(tree, desiredId) {
    return FunctionalTree.findNodeById(tree, desiredId);
}

function treeSize(tree) {
    return FunctionalTree.treeSize(tree);
}

function addBoard(tree, parentId, newBoard) {
    console.log('addBoard: newBoard is ' + newBoard);
    return addChild(
        tree,
        parentId,
        makeGameTreeNode(newBoard)
        );
}

// We can make this a lot more efficient by adding an 'addChildNodes'
// function in FunctionalTree.
// 
function addBoards(tree, parentId, newBoards) {
    let myTree = tree;
    console.log('addBoards: parentId is ' + parentId
        + ', newBoards are ' + newBoards);

    for (const board of newBoards) {
        console.log('inside addBoards: about to add board ' + board);
        myTree = addBoard(myTree, parentId, board);
    }
    return myTree;
}

const walkTree = FunctionalTree.walkTree;

const GameTreeNamespace = {
    makeGameTreeNode: makeGameTreeNode,
    addBoard: addBoard,
    addBoards: addBoards,
    findNodeById: findNodeById,
    treeSize: treeSize,
    walkTree: FunctionalTree.walkTree
};

export default GameTreeNamespace;
export { 
    makeGameTreeNode, 
    addChild, 
    findNodeById, 
    treeSize, 
    addBoard, 
    walkTree
};
