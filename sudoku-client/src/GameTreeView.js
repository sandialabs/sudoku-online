/* Render the Sudoku game tree in a tree view.
 *
 * This component renders the game tree, including miniatures of all 
 * available boards.  It is responsible for highlighting the active
 * board and signaling when a different active board has been
 * selected.
 *
 * Expected props:
 *     tree: JSON object containing the tree structure
 */

import React, {Component} from 'react';
import { Treebeard, theme as defaultTheme, decorators as defaultDecorators } from 'react-treebeard';
import { clone } from 'ramda';
import { GameTreeBoard } from './GameTreeBoard';
import PropTypes from 'prop-types';
import GameTree from './GameTree';

/*
 * Okay, here's the deal.
 *
 * Treebeard keeps state about what parts of the tree are expanded
 * or collapsed in the tree itself.  That means that if we replace
 * the tree with whatever comes in from props, the tree will get 
 * re-collapsed every time it updates unless we take other measures.
 *
 * One thing we could do would be to use the React 
 * componentDidUpdate(prevProps, prevState) function.  
 * That gets called after updating but not on the first render.  We
 * can add any new nodes to the tree in there.
 *
 * Expected Props:
 *     tree: JSON object containing tree to display
 *     changeActiveBoard: Function to call when a different board is
 *         selected in the game tree.  Takes one argument -- the serial
 *         number of the board to make active. 
 */


class GameTreeView extends Component {
    constructor(props){
        super(props);
        this.onToggle = this.onToggle.bind(this);
//        this.onSelect = this.onSelect.bind(this);

        this.state = {
            renderableTree: prepareTreeForTreebeard(clone(this.props.tree)),
            selectedNode: null
        };

        this.decorators = clone(defaultDecorators);
        this.decorators.Header = GameTreeBoardHeader;

        this.theme = clone(defaultTheme);
        this.theme.tree.base.backgroundColor = 'white';
        this.theme.tree.base.color = 'black';
        this.theme.tree.node.subtree = '50px';
        this.theme.tree.node.activeLink.background = '#A0A0A0';
    }
    
    // The game tree will always be fully expanded.  Clicking on a node only
    // changes the active view.
    onToggle(node, toggled) {
        const selectedNode = this.state.selectedNode;
        if (selectedNode) {
            selectedNode.active = false;
        }
        node.active = true;
        // if (node.children) {
        //     node.toggled = toggled;
        // }
        this.setState({selectedNode: node});
        if (this.props.changeActiveBoard) {
            console.log('onToggle: selected node is...');
            console.log(node);
            this.props.changeActiveBoard(node.data.board.serialNumber);
        }
    }

    render() {
        if (this.state.renderableTree) {
            return (
                <Treebeard
                    data={this.state.renderableTree}
                    onToggle={this.onToggle}
                    decorators={this.decorators}
                    style={this.theme}
                />
            );
        } else {
            return (
                <div>Game tree not yet available.</div>
                );
        }
    }

    // The nontrivial thing about this component is that it stores
    // state related to the Treebeard tree view in the data structure
    // for the tree itself.  That's why we cloned the tree out of
    // our props to put into our state.  It's unfortunate, but that's
    // the way Treebeard works.
    // 
    // The effect of this is that we have to detect when the tree
    // has been updated and then propagate the new state ourselves.
    // We can detect the update by observing that tree.maxSerialNumber()
    // is different between the tree currently in our props and the 
    // tree currently in our state.
    // 
    // When we detect that, we will replace the tree in the state
    // with the one in the props, but we will also copy over all of
    // the Treebeard state related to which nodes are open/closed
    // and which node is selected so the tree view doesn't reset
    // itself. 
     
    componentDidUpdate(oldProps, oldState) {
        console.log('GameTreeView: componentDidUpdate called');
        let shouldUpdate = false;

        if (!(this.state.renderableTree && this.props.tree)) {
            // At least one of these is out of sync.
            console.log('GameTreeView: Setting up new tree.  this.props.tree is ' + this.props.tree + ', this.state.renderableTree is ' + this.state.renderableTree);
            shouldUpdate = true;
        } else {
            shouldUpdate = hasTreeSizeChanged(this.state.renderableTree, this.props.tree);
        }

        if (shouldUpdate === false) {
            return;
        } else {
            if (this.state.renderableTree && this.props.tree) {
                console.log('GameTreeView: Updating tree after node count changed from ' 
                            + GameTree.treeSize(this.state.renderableTree) + ' to ' 
                            + GameTree.treeSize(this.props.tree) + '.');
            }
                    
            let ourNewTree = prepareTreeForTreebeard(this.props.tree);
            // if (this.state.renderableTree) {
            //     ourNewTree = overlayViewState(ourNewTree, this.state.renderableTree);
            // }

            console.log('GameTreeView: componentDidUpdate: ourNewTree is ' + ourNewTree);
            let newSelectedNode = null;
            if (this.state.selectedNode !== null) {
                newSelectedNode = GameTree.findNodeById(ourNewTree, this.state.selectedNode.id);
            }
            this.setState({
                selectedNode: newSelectedNode,
                renderableTree: ourNewTree
            });
        }
    }
}



function hasTreeSizeChanged(oldTree, newTree) {
    return (GameTree.treeSize(oldTree) !== GameTree.treeSize(newTree));
}

// Add properties that Treebeard needs to the nodes in the tree.
// All nodes with children default to 'expanded'.  
// 
// Returns a new tree.  Arguments are not modified.
function prepareTreeForTreebeard(sudokuTree) {
    const ourTree = clone(sudokuTree);

    GameTree.walkTree(ourTree,
        (node) => {
            node.name = 'Board ' + node.data.board.serialNumber;
            node.active = false;
            node.toggled = true;
        });
    return ourTree;
}

// Copy the properties from an existing tree to a new one
// for all the nodes whose serial numbers are in both trees.
// 
// Returns a new tree.  Arguments are not modified.
//
// NOTE: this would be a lot faster if we made a couple of 
// node-finder structures.  As it is, this is O(n^2).

function overlayViewState(newTree, oldTree) {
    const ourTree = clone(newTree);
    const viewStateProperties = ['active'];
    GameTree.walkTree(oldTree,
        (oldNode) => {
            const serial = oldNode.id;
            const newNode = GameTree.findNodeById(newTree, serial);
            if (newNode !== null) {
                for (const propName of viewStateProperties) {
                    newNode[propName] = oldNode[propName];
                }
            }
        }
        );
    return ourTree;
}


const GameTreeBoardHeader = ({onSelect, style, customStyles, node}) => {
    return (
        <GameTreeBoard
            board={node.data.board}
        />
    );
}

GameTreeBoardHeader.propTypes = {
    onSelect: PropTypes.func,
    style: PropTypes.object,
    node: PropTypes.object,
    customStyle: PropTypes.object
}

GameTreeBoardHeader.defaultProps = {
    customStyles: {}
}

export { GameTreeView };