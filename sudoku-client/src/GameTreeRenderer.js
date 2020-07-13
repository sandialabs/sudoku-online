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
import { Treebeard, decorators } from 'react-treebeard';
import { clone } from 'ramda';

const static_data = {
    name: 'root',
    toggled: true,
    children: [
        {
            name: 'another_parent',
            children: [
                { name: 'child1' },
                { name: 'child2' }
            ]
        },
        {
            name: 'yet_another_parent',
            children: [
                {
                    name: 'nested parent',
                    children: [
                        { name: 'nested child 1' },
                        { name: 'nested child 2' }
                    ]
                }
            ]
        }
    ]
};

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
 */

class GameTreeRenderer extends Component {
    constructor(props){
        super(props);
        this.onToggle = this.onToggle.bind(this);
        this.state = {
            tree: clone(this.props.tree),
            selectedNode: null
        };
    }
    
    onToggle(node, toggled) {
        console.log('onToggle: selected node is ' + node.name + ', toggled is ' + node.toggled);
        const selectedNode = this.state.selectedNode;
        if (selectedNode) {
            selectedNode.active = false;
        }
        node.active = true;
        if (node.children) {
            node.toggled = toggled;
        }
        this.setState({selectedNode: node});
    }

    render() {
        console.log('GameTreeRenderer: this.props.tree:');
        console.log(this.props.tree);
        if (this.props.tree) {
            return (
                <div>
                    <div>Foo!</div>
                    <Treebeard
                        data={this.state.tree}
                        onToggle={this.onToggle}
                    />
                </div>
            );
        } else {
            return (
                <div>Game tree not yet available.</div>
                );
        }
    }

    componentDidUpdate(oldProps, oldState) {
        const oldTreeMaxId = maxBoardId(this.state.tree);
        const newTreeMaxId = maxBoardId(this.props.tree);
        if (newTreeMaxId > oldTreeMaxId) {
            console.log('GameTreeRenderer received new tree.');
            console.log('Maximum serial number in new tree is ' 
                + maxBoardId(this.props.tree) + '. '
                + 'Maximum serial number in state tree is ' 
                + maxBoardId(this.state.tree) + '. ');
            console.log(this.props.tree);

            this.setState({tree: updateTreeWithViewState(this.props.tree, oldState.tree)});
        }
    }
}


function updateTreeWithViewState(newTreeFromProps, oldTree) {
    const newTree = clone(newTreeFromProps);
    const oldTreeNodes = nodesBySerial(oldTree);
    const newTreeNodes = nodesBySerial(newTree);
    const newlyAddedNodes = newNodes(newTreeNodes, oldTreeNodes);
    
    copyStateFromOldTree(newTreeNodes, oldTreeNodes);
    for (let newNodeId in newlyAddedNodes) {
        initializeTreebeardNodeState(newlyAddedNodes[newNodeId]);
    }
    return newTree;
}


function maxBoardId(tree) {
    const hasChildArray = tree.hasOwnProperty('children');
    if ((!hasChildArray) || tree.children.length === 0) {
        return tree.boardSerial;
    } else {
        let maxSerial = tree.boardSerial;
        let child = null;
        for (child of tree.children) {
            const childMax = maxBoardId(child);
            if (childMax > maxSerial) {
                maxSerial = childMax;
            }
        }
        return maxSerial;
    }
}


function copyStateFromOldTree(newTreeNodes, oldTreeNodes) {
    let nodeId = null;
    for (nodeId in newTreeNodes) {
        if (oldTreeNodes.hasOwnProperty(nodeId)) {
            copyTreebeardProperties(newTreeNodes[nodeId], oldTreeNodes[nodeId]);
        }
    }
}

function copyTreebeardProperties(targetNode, sourceNode) {
    const stateProps = ['active', 'toggled', 'id', 'decorators'];
    let propName = null;
    for (propName of stateProps) {
        if (sourceNode.hasOwnProperty(propName)) {
            targetNode[propName] = sourceNode[propName];
        }
    }
}

function initializeTreebeardNodeState(node) {
    node.active = false;
}

function nodesBySerial(tree) {
    let nodes = {};
    nodes[tree.boardSerial] = tree;

    if (tree.hasOwnProperty('children')) {
        if (tree.children.length > 0) {
            for (let child of tree.children) {
                Object.assign(nodes, nodesBySerial(child));
            }
        }
    }
    return nodes;
}

function newNodes(newTreeNodes, oldTreeNodes) {
    let result = {};
    let nodeId = null;

    for (nodeId in newTreeNodes) {
        if (!oldTreeNodes.hasOwnProperty(nodeId)) {
            result[nodeId] = newTreeNodes[nodeId];
        }
    }
}
export { GameTreeRenderer };