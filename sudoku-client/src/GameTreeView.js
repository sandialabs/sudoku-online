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
// import Header from './modified-react-treebeard/components/Decorators/Header';
import { clone } from 'ramda';
import { GameTreeBoard } from './GameTreeBoard';
import PropTypes from 'prop-types';
import GameTree from './GameTree';


import { Div as TreeBeardDiv } from './modified-react-treebeard/components/common';

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

        this.decorators = clone(defaultDecorators);
        this.decorators.Header = GameTreeBoardHeader;

        this.treebeardBaseTheme = clone(defaultTheme);
        console.log('this.treebeardBaseTheme: ');
        console.log(this.treebeardBaseTheme);
        
        this.configureTreebeardTheme(this.treebeardBaseTheme);

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
    
    configureTreebeardTheme(theme) {
        theme.tree.node.header.title.color = '#404040';
        theme.tree.base.backgroundColor = 'white';
        theme.tree.base.color = 'yellow';
        theme.tree.node.header.connector.borderBottom = 'solid 2px green';
        theme.tree.node.header.connector.borderLeft = 'solid 2px blue';


    }

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
                decorators={this.decorators}
                style={this.treebeardBaseTheme}
                customStyles={this.customStyles}
            />
            );
     }

}



function cellToString(cell) {
    return String.fromCharCode(0x41 + cell[0]) + (cell[1] +1);
}

// Turn an action object into a human-readable name for the game tree.
function actionToName(action, board) {
    switch (action.action) {
        case 'assign': {
            return 'Assign:  ' + cellToString(action.cell) + ' \u2190 ' + (action.value +1);
        }
        case 'exclude': {
            return 'Exclude: ' + cellToString(action.cell) + ' \u2260 ' + (action.value +1);
        }
        case 'pivot': {
            return 'Pivot:   ' + cellToString(action.cell) + ' \u2190 ' + (board.assignments[action.cell[0]][action.cell[1]] +1);
        }
        // TODO: Logical operators are not yet implemented here
        case 'applyops': {
            return 'Operators: ' + action.operators;
        }
        // TODO: Logical operators are not yet implemented here
        default: {
            return 'Label not implemented for action type: ' + action.action;
        }
    }
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
            if (node.data.board.hasOwnProperty('action')) {
                node.name = actionToName(node.data.board.action, node.data.board);
            } else {
                node.name = 'UNIMPLEMENTED: ' + node.data.board.serialNumber;
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

const TreeBeardDefaultHeader = ({onSelect, node, style, customStyles}) => (
    <div style={style.base} onClick={onSelect}>
        <TreeBeardDiv style={node.selected ? {...style.title, ...customStyles.header.title} : style.title}>
            {node.name}
        </TreeBeardDiv>
    </div>
);

const GameTreeBoardHeader = ({onSelect, node, style, customStyles}) => {
    if (!nodeIsTerminal(node)) {
        return (
            <TreeBeardDefaultHeader
                onSelect={onSelect}
                style={style}
                node={node}
                customStyles={customStyles}
             />
             ); 
    } else {
        return (
            <div style={style.base} onClick={onSelect}>
                <TreeBeardDiv
                    style={node.selected ? {...style.title, ...customStyles.header.title} : style.title}
                    >
                    <GameTreeBoard board={node.data.board} name={node.name} />
                </TreeBeardDiv>
            </div>
            );
    }
}


function nodeIsTerminal(node) {
    return (node.children === null ||
            node.children === undefined ||
            node.children.length === 0);
}

GameTreeBoardHeader.propTypes = {
    //activeBoardId: PropTypes.number.isRequired,
    //expandedNodes: PropTypes.object.isRequired,
    //changeActiveBoard: PropTypes.func.isRequired,
    //announceBoardToggled: PropTypes.func.isRequired,
    style: PropTypes.object,
    node: PropTypes.object,
    customStyle: PropTypes.object
}

GameTreeBoardHeader.defaultProps = {
    customStyles: {}
}

export { GameTreeView };
