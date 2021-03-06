// CellActionPanel: View and select heuristics (logical operators)
// 
// Andy Wilson 
// 22 July 2020
// 
// The Sudoku client has two separate sets of operations the user can
// invoke: logical operators (heuristics) and actions (assignment/pivot).
// Each operation has a name and a description and can be selected from a list.  
// 
// This component provides a view of the list of actions.  Only one action can 
// be performed at a time; therefore, this display uses a list of radio buttons.
// Detailed descriptive text is  in a panel below (or beside?) the radio buttons.
// 
// Props:
//     allActions: List of Action objects, detailed below.
//     permittedActions: Actions permitted for the currently active board.
//     selectedActionChanged (optional): Function to call when the user selects a different heuristic
//     defaultAction: Which action to highlight when the radio buttons are created
//     executeAction: Function to call when the user presses the "Execute" button
//   
// Example Action object:
// {
//   "cost":100,
//   "description":"Return one board with the assignment and another (backup) with the exclusion.",
//   "internal_name":"assign",
//   "user_name":"Assign: assign given value to cell."
// }

import React from 'react';

import { FormControl, FormControlLabel } from '@material-ui/core';
import { Button } from '@material-ui/core';
import { Paper } from '@material-ui/core';
import { Radio, RadioGroup } from '@material-ui/core';
import { Tooltip } from '@material-ui/core';
import { Typography } from '@material-ui/core';

import PropTypes from 'prop-types';


class CellActionPanel extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			selectedAction: props.defaultAction,
		}
	}

	renderActionList() {
		let radioButtons = this.makeRadioButtons();
		let buttonText = "Execute Selected Action";
		
		const anyActionsEnabled = (
			this.props.permittedActions['assign'] === true
			|| this.props.permittedActions['exclude'] === true
			|| this.props.permittedActions['pivot'] === true
			|| this.props.permittedActions['applyops'] === true
			);

		const someActionCanExecute = (
			this.props.actionsCanExecute 
			&& anyActionsEnabled
			);

		const thisActionCanExecute = (
			this.props.permittedActions[this.state.selectedAction.internal_name] === true
			)

		if (!someActionCanExecute) {
			buttonText = this.props.disabledReason;
		} else if (!thisActionCanExecute) {
			buttonText = 'Please select an available action';
		}

		const enableExecuteButton = (someActionCanExecute && thisActionCanExecute);

		return (
			<FormControl component="fieldset">
				<RadioGroup defaultValue={this.props.defaultAction.internal_name}
							aria-label="cell-action"
							name="cell-action-radio-group"
							onChange={(event) => this.handleActionSelection(event)}
							>
					{radioButtons}
				</RadioGroup>
				<Button onClick={() => this.handleExecuteAction()}
						variant="contained"
						color="primary"
						disabled={!enableExecuteButton}>
					{buttonText}
				</Button>
			</FormControl>
			);
	}

	makeRadioButtons() {
		return this.props.allActions.map(
			(action) => this.makeMaterialRadioButton(action)
			);
	}	

	makeMaterialRadioButton(action) {
		const actionPermitted = (
			this.props.permittedActions[action.internal_name] === true
			);
		
		const fullLabelText = action.user_name + ' (Cost: ' + action.cost + '): ' + action.short_description;
		let forbiddenText = 'This action is not permitted right now';

		if (action.internal_name === 'assign'
			|| action.internal_name === 'exclude') {
			forbiddenText = 'You must select a value in an unassigned square in order to execute this operation.';
		} else if (action.internal_name === 'pivot') {
			forbiddenText = 'You must select an unassigned square to execute this operation.';
		} else if (action.internal_name === 'applyops') {
			forbiddenText = 'You must select at least one operator to apply.';
		}

		let toolTipText = action.user_name + ': ' + action.description;

		if (!actionPermitted) {
			toolTipText = forbiddenText;
		}
		
		return (
			<Tooltip title={toolTipText} key={action.internal_name}>
				<FormControlLabel
					value={action.internal_name}
					disabled={(actionPermitted === false)}
					control={<Radio />}
					label={fullLabelText}
					/>
			</Tooltip>
		);
	}

	actionsAvailable() {
		return (this.props.allActions !== undefined
				&& this.props.allActions !== null
				&& this.props.allActions.length !== 0);
	}

	render() {
		if (!this.actionsAvailable()) {
			return (
				<Paper>
					Waiting for action list...
				</Paper>
				);
		
		} else {
			const actionListPanel = this.renderActionList();
			return (
				<Paper name='cellActions'>
					<Typography variant="h5">Cell Actions</Typography>
					{actionListPanel}
				</Paper>
				);
		}
	}

	findActionObject(actionInternalName) {
		for (const action of this.props.allActions) {
			if (action.internal_name === actionInternalName) {
				return action;
			}
		}
		console.log('ERROR: findActionObject: Couldn\'t find object for action ' + actionInternalName);
		return null;
	}

	handleExecuteAction() {
		console.log('DEBUG: handleExecuteAction: selectedAction is ' + this.state.selectedAction + ', defaultAction is ' + this.props.defaultAction);
		if (this.props.executeAction) {
			let action = this.state.selectedAction;
			if (action === null) {
				action = this.props.defaultAction;
			} 
			this.props.executeAction(action);
		}
	}

	handleActionSelection(changeEvent) {
		if (this.state.selectedAction !== changeEvent.target.value) {
			const action = this.findActionObject(changeEvent.target.value);
			if (action !== null) {
				this.setState({
					'selectedAction': action
					});
			} else {
				console.log("ERROR: Couldn't find action object for new selected action " + changeEvent.target.value);
			}
		}	
	}
}

CellActionPanel.propTypes = {
	allActions: PropTypes.array.isRequired,
	permittedActions: PropTypes.object.isRequired,
	selectedActionChanged: PropTypes.func,
	defaultAction: PropTypes.object,
	executeAction: PropTypes.func.isRequired,
	actionsCanExecute: PropTypes.bool.isRequired,
	disabledReason: PropTypes.string,
};

export { CellActionPanel };
