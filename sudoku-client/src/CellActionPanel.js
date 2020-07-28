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
//     actions: List of Action objects, detailed below.
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

import { Container } from '@material-ui/core';
import { FormControl, FormControlLabel, FormLabel } from '@material-ui/core';
import { Button } from '@material-ui/core';
import { List, ListItem } from '@material-ui/core';
import { Radio, RadioGroup } from '@material-ui/core';
import { Typography } from '@material-ui/core';

class CellActionPanel extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			selectedAction: props.defaultAction,
		}
	}

	renderActionList() {
		let radioButtons = this.makeRadioButtons();
		console.log('renderActionList: default action is ' + this.props.defaultAction.internal_name);
		console.log('renderActionList: Rendering ' + this.props.actions.length + ' actions');

		return (
			<Container>
				<FormControl component="fieldset">
					<FormLabel component="legend">Cell Action List</FormLabel>
					<RadioGroup defaultValue={this.props.defaultAction.internal_name}
								aria-label="cell-action"
								name="cell-action-radio-group"
								onChange={(event) => this.handleActionSelection(event)}
								>
						{radioButtons}
					</RadioGroup>
					<Button onClick={() => this.handleExecuteAction()}
							variant="contained"
							color="primary">
						Execute Selected Action
					</Button>
				</FormControl>
			</Container>
			);
	}

	makeRadioButtons() {
		return this.props.actions.map(
			(action) => this.makeMaterialRadioButton(
					action.internal_name,
					action.user_name + ': ' + action.short_description,
					action.cost
				));
	}	

	makeMaterialRadioButton(internalName, labelText, cost) {
		const fullLabelText = labelText + ' (Cost: ' + cost + ')';
		return (
			<FormControlLabel 
				value={internalName}
				control={<Radio />}
				label={fullLabelText}
				key={internalName}
				/>
				);
	}

	renderSelectedActionDocumentation() {
		let costText = 'No cost';
		let nameText = 'No action selected';
		let descriptionText = '(select a cell action to see description)';

		let action = null;
		if (this.state.selectedAction !== null) {
			action = this.state.selectedAction;
		} else if (this.props.defaultAction !== null) {
			action = this.props.defaultAction;
		}

		if (action !== null) {
			console.log('Selected action is not null.  Populating description panel.');
			nameText = action.user_name;
			costText = action.cost;
			descriptionText = action.description;
		}

		return (
			<Container>
				<Typography variant="h6">Currently Selected Action</Typography>
				<List>
					<ListItem><strong>Name:</strong> {nameText}</ListItem>
					<ListItem><strong>Cost:</strong> {costText}</ListItem>
					<ListItem><strong>Description:</strong> {descriptionText}</ListItem>
				</List>
			</Container>
		);
	}

	actionsUnavailable() {
		return (this.props.actions === undefined
				|| this.props.actions === null
				|| this.props.actions.length === 0);
	}

	render() {
		if (this.actionsUnavailable()) {
			return (
				<Container>
					Waiting for action list...
				</Container>
				);
		
		} else {
			const actionListPanel = this.renderActionList();
			const actionDescriptionPanel = this.renderSelectedActionDocumentation();
			return (
				<Container>
					{actionListPanel}
					{actionDescriptionPanel}
				</Container>
				);
		}
	}

	findActionObject(actionInternalName) {
		for (const action of this.props.actions) {
			if (action.internal_name === actionInternalName) {
				return action;
			}
		}
		console.log('ERROR: findActionObject: Couldn\'t find object for action ' + actionInternalName);
		return null;
	}

	// Call the executeAction() function from the props with the
	handleExecuteAction() {
		console.log('DEBUG: handleExecuteAction: Execute button pressed');
		if (this.props.executeAction) {
			this.props.executeAction(this.state.selectedAction);
		}
	}

	handleActionSelection(changeEvent) {
		console.log('DEBUG: handleActionSelection: Selected action is ' + changeEvent.target.value);
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

export { CellActionPanel };
