// LogicalOpreatorPanel: View and select logical operators to apply
// 
// Andy Wilson 
// 27 July 2020
// 
// The Sudoku client has two separate sets of operations the user can
// invoke: logical operators (heuristics) and actions (assignment/pivot).
// Each operation has a name and a description and can be selected from a list.  
// 
// This component provides a view of the list of logical operators.  Unlike the 
// cell actions, any number of operators (including zero) can be selected at any
// time.  Also, it is possible for this list to be frozen and unavailable for 
// change.
// 
// Detailed descriptive text is  in a panel below (or beside?) the check boxes.  I still need to decide
// how to populate this.
// 
// Props:
//     operators: List of LogicalOperator objects, detailed below.
//     canChange: boolean, whether or not the user can change the selections
//     selectionChanged: Function to call when the user changes the set of selected
//         operators.  Takes one argument: the currently active operators as a set of
//         LogicalOperator objects.
//         
// Example Action object:
// {
//   "cost":100,
//   "description":"Return one board with the assignment and another (backup) with the exclusion.",
//   "internal_name":"assign",
//   "user_name":"Assign: assign given value to cell."
// }

import React from 'react';
import {Checkbox} from './Checkbox';

class LogicalOperatorPanel extends React.Component {
	constructor(props) {
		super(props);

		const locator = {};
		if (this.props.operators !== null) {
			for (let operator of this.props.operators) {
				locator[operator.internal_name] = operator;
			}
		}

		this.state = {
			selectedOperatorNames: new Set(),
			};

		this.locator = locator;
	}

	renderOperatorList() {
		let checkBoxes =
			this.props.operators.map(
				operator => {
					return this.makeCheckBox(operator);
				});


		return (
			<div id='logicalOperators'>
				<h3>Available Logical Operators</h3>
				{checkBoxes}
			</div>
			);
	}
	
	renderSelectedOperatorDocumentation() {
		return (
			<div id="operatorDocumentation">
				Documentation forthcoming.
			</div>
		);
	}

	render() {
		if (this.props.operators === undefined ||
			this.props.operators === null ||
			this.props.operators.length === 0) {
			return (
				<div id='logicalOperators'>
					Waiting for operator list...
				</div>
				);
		
		} else {
			const operatorListPanel = this.renderOperatorList();
			const operatorDescriptionPanel = this.renderSelectedOperatorDocumentation();
			return (
				<div id='logicalOperators'>
					{operatorListPanel}
					{operatorDescriptionPanel}
				</div>
				);
		}
	}

	makeCheckBox(operator) {
		const labelText = operator.user_name + ' (Cost: ' + operator.cost + ')';
		const internalName = operator.internal_name;
		console.log('Creating checkbox with internal name ' + internalName);
		return (
			<Checkbox
				label={labelText}
				name={internalName}
				key={internalName}
				isSelected={(this.state.selectedOperatorNames.has(internalName))}
				onCheckboxChange={changeEvent => {this.handleCheckBoxChange(changeEvent);}}
				/>

				);
	}

	handleCheckBoxChange(changeEvent) {
		const {name} = changeEvent.target;
		console.log('handleCheckBoxChange: ' + name + ' toggled');
		console.log('target:');
		console.log(changeEvent.target);
		if (this.state.selectedOperatorNames.has(name)) {
			this.removeOperationFromSelection(name);
		} else {
			this.addOperationToSelection(name);
		}
	}

	addOperationToSelection(name) {
		const newSelection = this.state.selectedOperatorNames.add(name); 
		this.setState({
			selectedOperatorNames: newSelection
		});
		// We don't just take this from this.state because state updates 
		// are asynchronous.  If we want the just-updated value, we have to
		// pass it ourselves.
		this.announceSelectedOperators(newSelection);
	}

	removeOperationFromSelection(name) {
		const newSelection = this.state.selectedOperatorNames.delete(name);
		this.setState({
			selectedOperatorNames: newSelection
		});
		// We don't just take this from this.state because state updates 
		// are asynchronous.  If we want the just-updated value, we have to
		// pass it ourselves.
		this.announceSelectedOperators(newSelection);
	}	

	announceSelectedOperators(operatorNames) {
		const operators = [];
		console.log('announceSelectedOperators called');
		return;
		for (const name of operatorNames) {
			operators.push(this.locator[name]);
		}
		this.props.selectionChanged(operators);
	}
}

export { LogicalOperatorPanel };
