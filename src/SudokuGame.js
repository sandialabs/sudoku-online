import React from 'react';
import ReactDOM from 'react-dom';
import './sudoku.css';

export { SudokuGame }

function initial_choices(degree) {
	return [...Array(degree*degree).keys()];
}


class SudokuGame extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			rootNode: makeGameTreeNode(props.degree)	
		};
	}	


}