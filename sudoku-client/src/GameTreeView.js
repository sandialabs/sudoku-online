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
import { Treebeard, theme as defaultTheme, decorators as defaultDecorators } from './modified-react-treebeard';
import Header from './modified-react-treebeard/components/Decorators/Header';
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
        this.onSelect = this.onSelect.bind(this);

        // this.state = {
        //     renderableTree: prepareTreeForTreebeard(clone(this.props.tree)),
        //     selectedNode: null
        // };

        this.decorators = clone(defaultDecorators);
        //this.decorators.Header = GameTreeBoardHeader;

        this.treebeardBaseTheme = clone(defaultTheme);
        console.log('this.treebeardBaseTheme: ');
        console.log(this.treebeardBaseTheme);
        
        this.treebeardBaseTheme.tree.node.header.title.color = '#404040';
        this.treebeardBaseTheme.tree.base.backgroundColor = 'white';
        this.treebeardBaseTheme.tree.base.color = 'yellow';
        this.treebeardBaseTheme.tree.node.header.connector.borderBottom = 'solid 2px green';
        this.treebeardBaseTheme.tree.node.header.connector.borderLeft = 'solid 2px blue';

        /*
        this.theme.tree.node.header.base.backgroundColor = "yellow";
        // this.theme.tree.node.subtree = '50px';
        // this.theme.tree.node.activeLink.background = '#A0A0A0';
        */
       
        this.customStyles = { 
            header: {
                title: {
                    // This does in fact affect the title of the active tree node
                    color: 'red'
                }
            },
            base: {
                backgroundColor: 'white'
            }
        };
    }
    
    // The game tree will always be fully expanded.  Clicking on a node only
    // changes the active view.
    onToggle(node, toggled) {
        console.log('GTV.onToggle: Node ' + node.name + ' clicked');
        
        if (node.children) {
            node.toggled = toggled;    
            this.props.announceBoardToggled(node.data.board.serialNumber);
        }
    }

    onSelect(node) {
        console.log('onSelect: new selected node is...');
        console.log(node);
        this.props.changeActiveBoard(node.data.board.serialNumber);
    }

    render() {
        console.assert(this.props.gameTree !== undefined, 
            "GameTreeView: props.gameTree is undefined");
        const renderableTree = prepareTreeForTreebeard(
            this.props.gameTree,
            this.props.activeBoardId,
            this.props.expandedNodes
            );

        return (
            <Treebeard
                data={renderableTree}
                onToggle={this.onToggle}
                onSelect={this.onSelect}
                //decorators={this.decorators}
                style={this.treebeardBaseTheme}
                customStyles={this.customStyles}
            />
            );
     }

}




function hasTreeSizeChanged(oldTree, newTree) {
    return (GameTree.treeSize(oldTree) !== GameTree.treeSize(newTree));
}

// Add properties that Treebeard needs to the nodes in the tree.
// All nodes with children default to 'expanded'.  
// 
// Returns a new tree.  Arguments are not modified.
function prepareTreeForTreebeard(sudokuTree, activeNodeId, expandedNodes) {
    const ourTree = clone(sudokuTree);
    console.assert(sudokuTree !== undefined,
        "prepareTreeForTreebeard: tree is undefined"
        );

    const expandedNodesPlusActiveNodeAncestry = new Set(expandedNodes);
    const activeBoardAncestors = GameTree.findNodeAncestry(ourTree, activeNodeId);
    console.assert(activeBoardAncestors.found === true,
        "Couldn't find ancestors of active board");
    for (const node of activeBoardAncestors.path) {
        expandedNodesPlusActiveNodeAncestry.add(node.data.board.serialNumber);
    }       


    GameTree.walkTree(ourTree,
        (node) => {
            if (node.data.board.backtrackingBoard) {
                node.name = 'Backtrack: ' + node.data.board.serialNumber;
            } else {
                node.name = 'Action: ' + node.data.board.serialNumber;
            }
            if (node.data.board.serialNumber === activeNodeId) {
                node.selected = true;
                // might also need
                // node.active = true;
            } else {
                node.selected = false;
            }
            node.toggled = expandedNodesPlusActiveNodeAncestry.has(node.data.board.serialNumber);
        });

    // The root gets a distinguished name
    ourTree.name = 'Starting Board';
    return ourTree;
}

const GameTreeBoardHeader = ({onSelect, style, customStyles, node}) => {
    if (node.children === undefined
        || node.children === null
        || node.children.length === 0) {
        
        return (
            <GameTreeBoard
                board={node.data.board}
            />
            );
    } else {
        return (
            Header.Header(onSelect, style, customStyles, node)
        );
    }
}


function prettyPrintNode(node) {
    return node.name + ' (selected: ' + node.selected + ', toggled: ' + node.toggled + ', terminal: ' + nodeIsTerminal(node) + ')';
}

function prettyPrintTreeLevel(tree, indent) {
   let outstring = indent + prettyPrintNode(tree) + '\n';
   if (tree.children !== null &&
       tree.children !== undefined) {
     for (const child of tree.children) {
        outstring += prettyPrintTreeLevel(child, indent + '  ');
     }
   } 
   return outstring;
}

function prettyPrintTree(root) {
    return prettyPrintTreeLevel(root, '');
}

function nodeIsTerminal(node) {
    return (node.children === null ||
            node.children === undefined ||
            node.children.length === 0);
}

GameTreeBoardHeader.propTypes = {
    activeBoardId: PropTypes.number.isRequired,
    expandedNodes: PropTypes.object.isRequired,
    changeActiveBoard: PropTypes.func.isRequired,
    announceBoardToggled: PropTypes.func.isRequired,
    style: PropTypes.object,
    node: PropTypes.object,
    customStyle: PropTypes.object
}

GameTreeBoardHeader.defaultProps = {
    customStyles: {}
}

export { GameTreeView };