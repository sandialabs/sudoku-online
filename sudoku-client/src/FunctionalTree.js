// An attempt at writing a purely functional N-ary tree in Javascript
//

function makeTreeNode(id, data) {
	const node = {
		id: id,
		data: data,
		children: []
	};
	return node;
}

function findNodeById(node, targetId) {
	if (node.id === targetId) {
		return node;
	} else {
		for (const child of node.children) {
			const maybeNode = findNodeById(child, targetId);
			if (maybeNode) { 
				return maybeNode;
			}
		}
		return null;
	}
}

function isLeaf(node) {
	return (node.children.length === 0);
}


function findPathToNode(node, targetId) {
	if (node.id === targetId) {
		return { found: true, path: [] };
	} else if (isLeaf(node)) {
		return { found: false, path: null };
	} else {
		for (let i = 0; i < node.children.length; ++i) {
			if (node.children[i].id === targetId) {
				return {
					found: true,
					path: [i]
				};
			} else {
				const {found, path} = findPathToNode(node.children[i], targetId);
				if (found) {
					return {
						found: true,
						path: [i].concat(path)
					};
				}
			}
		}
	}
	return { found: false, path: null };
}


function addChild(node, parentId, childNode) {
	// Base case: are we looking directly at the parent?
	if (node.id === parentId) {
		const newNode = {};
		Object.assign(newNode, node);
		newNode.children = node.children.concat(childNode);
		return newNode;
	} else {
		// In order to preserve the functional property that
		// values are immutable, we have to return a new tree
		// where all of the ancestor nodes of the newly added
		// child have been replaced.  The most efficient way
		// I know of to do that is to find the path to the 
		// node where we want to attach the new child,
		// replace all the nodes along that path, and use the
		// rest of the nodes as-is.  
		//
		// The problem here is that since this is an N-ary
		// tree where nodes have arbitrary identifiers, 
		// finding the parent node is O(n) in the number of
		// nodes.  To get around that we would have to
		// wrap the tree in a container that also maintains
		// a map from node ID -> path to the node. 
		//
		// Knuth says that premature optimization is the root
		// of all evil, so we're going to just eat the O(n)
		// cost for now.
		const { found, path } = findPathToNode(node, parentId);
		if (!found) {
			throw new Error('FunctionalTree.addChild couldn\'t find node wih target ID ' + parentId,
				{ tree: node }
				);

		} else {
			return addChildAlongPath(node, path, childNode);
		}
	}
}

// Arguments:
// 
//     node: Root of subtree
//
//     path (array of integers): Path down through the subtree,
//         specified as a sequence of indices of children.  
//         For example, if the path is [1, 3, 4], then
//         the target node is at node.children[1].children[3].children[4].
//
//     nodeToAdd (node): Node to include as a child of the last node in
//         the path.

function addChildAlongPath(node, path, nodeToAdd) {
	if (path.length === 0) {
		// Our search has bottomed out.  We're at the node
		// where we need to add the child.
		const newNode = {};
		Object.assign(newNode, node);
		newNode.children = node.children.concat(nodeToAdd);
		return newNode;
	} else {
		const ancestorIndex = path[0];
		const childrenBefore = node.children.slice(0, ancestorIndex);
		const childrenAfter = node.children.slice(ancestorIndex+1, 
			                                      node.children.length);
		const modifiedChild = addChildAlongPath(
			node.children[ancestorIndex],
			path.slice(1, path.length),
			nodeToAdd
			);

		const newNode = {};
		Object.assign(newNode, node);
		newNode.children = [...childrenBefore, modifiedChild, ...childrenAfter];
		return newNode;
	}
}

function treeSize(node) {
	const childSizes = node.children.map(node => treeSize(node));
	return 1 + childSizes.reduce((a, b) => a+b, 0);
}

function walkTree(node, callback) {
	for (const child of node.children) {
		walkTree(child, callback);
	}
	callback(node);
}


const FunctionalTreeNamespace = {
	makeTreeNode: makeTreeNode, 
	addChild: addChild,
	isLeaf: isLeaf,
	findNodeById: findNodeById,
	findPathToNode: findPathToNode,
	treeSize: treeSize,
	walkTree: walkTree
};


export default FunctionalTreeNamespace;
export { makeTreeNode, addChild, isLeaf, findNodeById, treeSize, walkTree, findPathToNode };
