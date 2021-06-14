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
import { Button } from '@material-ui/core';
import { Checkbox } from '@material-ui/core';
import { FormControlLabel, FormGroup } from '@material-ui/core';
import { Paper } from '@material-ui/core';
import { Tooltip } from '@material-ui/core';
import { Typography } from '@material-ui/core';

import PropTypes from 'prop-types';

class LogicalOperatorPanel extends React.Component {
	constructor(props) {
		super(props);

		this.state = {
			itemStatus: {} 
		};

		this.handleCheckBoxChange = this.handleCheckBoxChange.bind(this);
	}

	findOperatorByName(name) {
		for (const op of this.props.operators) {
			if (op.internal_name === name) {
				return op;
			}
		}
		console.log('ERROR: findOperatorByName: Couldn\'t find operator ' + name);
		return null;
	}

	operatorsAvailable() {
		return (this.props.operators !== undefined
				&& this.props.operators !== null
				&& this.props.operators.length > 0);	
	}

	renderOperatorList() {
		let checkBoxes =
			this.props.operators.map(
				operator => {
					return this.makeCheckBox(operator);
				});

		return (
			<FormGroup name='logicalOperatorCheckList'>
				{checkBoxes}
			</FormGroup>
			);
	}
	
	confirmLogicalOperators() {
		this.setState()
	}

	render() {
		if (!this.operatorsAvailable()) {
			return (
				<Paper name='logicalOperators'>
					Waiting for operator list...
				</Paper>
				);
		
		} else {
			const operatorListPanel = this.renderOperatorList();
			const executeOperatorsButton = this.makeExecuteOperatorsButton();

			if (this.props.selectLogicalOperatorsUpFront) {
				return (
					<Paper name='logicalOperators'>
						<Typography variant="h5">Specialized Operations</Typography>
						{operatorListPanel}
						{executeOperatorsButton}
					</Paper>
					);
			} else {
				return (
					<Paper name='logicalOperators' elevation={2}>
						<Typography variant='h5'>Specialized Operations</Typography>
						<Typography variant='body1'>(Execute using Apply Operators action)</Typography>
						{operatorListPanel}
					</Paper>
					);
			}
		}
	}

	makeCheckBox(operator) {
		const labelText = operator.user_name + ' (Cost: ' + operator.cost + ')';
		const tooltipText = operator.user_name + ': ' + operator.description;
		return (
			<Tooltip title={tooltipText} key={operator.internal_name}>
				<FormControlLabel
					control={
						<Checkbox 
							onChange={this.handleCheckBoxChange}
							name={operator.internal_name}
							disabled={this.props.logicalOperatorsFrozen}
						 	/>
						 }
					label={labelText}
					/>
			</Tooltip>
			);
	}

	handleCheckBoxChange(changeEvent, isChecked, value) {
		const itemName = changeEvent.target.name;
		const updatedItemStatus = {...this.state.itemStatus};
		updatedItemStatus[itemName] = isChecked;


		console.log('handleCheckBoxChange: ' + itemName + ' toggled to ' + isChecked);
	
		this.setState({
			itemStatus: updatedItemStatus
		});
		this.announceSelectedOperators(updatedItemStatus);
	}

	announceSelectedOperators(checkboxStatus) {
		const selectedOperatorNames = 
			Object.keys(checkboxStatus)
				  .filter(opName => checkboxStatus[opName]);
		const selectedOperators =
			selectedOperatorNames.map(opName => this.findOperatorByName(opName));
		console.log('announceSelectedOperators called');
		console.log('currently selected operators: ' + JSON.stringify(selectedOperatorNames));

		this.props.selectionChanged(selectedOperators);
	}

    makeExecuteOperatorsButton() {
    	let selectOperatorButtonText = "ERROR: LOGICAL OPERATOR BUTTON TEXT UNDEFINED";
    	let onClick = null;
    	let disabled = false;

    	if (this.props.selectLogicalOperatorsUpFront) {
    		selectOperatorButtonText = "Confirm Operator Selection";
			disabled = false;
			onClick = () => this.props.confirmOperatorSelection(); 
			if (this.props.logicalOperatorsFrozen) {
				selectOperatorButtonText = "Specialized Operators Frozen";
				disabled = true;
			}
		} else {
			selectOperatorButtonText = "Execute Specialized Operations";
			disabled = false;
			onClick = () => this.props.executeLogicalOperators();
		}

		return (
			<Button onClick={onClick}
				variant="contained"
				color="primary"
				disabled={disabled} >
				{selectOperatorButtonText}
			</Button>	
			);
    }
}

LogicalOperatorPanel.propTypes = {
	confirmOperatorSelection: PropTypes.func,
	logicalOperatorsFrozen: PropTypes.bool.isRequired,
	operators: PropTypes.array.isRequired,
	selectLogicalOperatorsUpFront: PropTypes.bool.isRequired,
	selectionChanged: PropTypes.func.isRequired,
	executeLogicalOperators: PropTypes.func.isRequired,

};

export { LogicalOperatorPanel };
