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

class CellActionPanel extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			selectedAction: null,
		}
	}

	renderActionList() {
		let radioButtons = 
			this.props.actions.map(
				action => {
					return this.makeRadioButton(action.internal_name, action.user_name, action.cost);
				}
			);
	
		return (
			<div id='cellActions'>
				<h3>Available Cell Actions</h3>
				<div id='cellActionList'>
					{radioButtons}

					<br />
					<button
						onClick={() => this.executeActionButtonPressed()}
						>
						Execute Cell Action 
					</button>
				</div>
			</div>
			);
	}
	
	renderSelectedActionDocumentation() {
		let costText = 'No cost';
		let nameText = 'No action selected';
		let descriptionText = '(select a cell action to see description)';

		if (this.state.selectedAction !== null) {
			console.log('Selected action is not null.  Populating description panel.');
			nameText = this.state.selectedAction.user_name;
			costText = this.state.selectedAction.cost;
			descriptionText = this.state.selectedAction.description;
		}

		return (
			<div id="selectedActionDescription">
				<h4>Currently Selected Action</h4>
				<ul>
					<li><strong>Name:</strong> {nameText}</li>
					<li><strong>Cost:</strong> {costText}</li>
					<li><strong>Description:</strong> {descriptionText}</li>
				</ul>
			</div>
		);
	}

	render() {
		if (this.props.actions === undefined ||
			this.props.actions === null ||
			this.props.actions.length === 0) {
			return (
				<div id='cellActionList'>
					Waiting for action list...
				</div>
				);
		
		} else {
			const actionListPanel = this.renderActionList();
			const actionDescriptionPanel = this.renderSelectedActionDocumentation();
			return (
				<div id='cellActionPanel'>
					{actionListPanel}
					{actionDescriptionPanel}
				</div>
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

	makeRadioButton(internalName, userText, cost) {
		console.log('makeRadioButton: internalName ' + internalName + ', userText ' + userText );
		return (
			<div className='cellActionForm' key={internalName}>
			  <label>
			    <input
			      type='radio'
			      name='selectCellAction'
			      value={internalName}
			      checked={(this.state.selectedAction !== null && this.state.selectedAction.internal_name === internalName)}
			      onChange={event => {this.handleActionSelection(event);}}
			      className='radio-button cellAction'
			      />
			    {userText} (Cost: {cost})
			  </label>
			</div>
			);
	}

	// Call the executeAction() function from the props with the
	executeActionButtonPressed() {
		if (this.props.executeAction) {
			this.props.executeAction(this.state.selectedAction);
		}
	}

	handleActionSelection(changeEvent) {
		if (this.state.selectedAction !== changeEvent.target.value) {
			console.log('DEBUG: Selected cell action changing to ' + changeEvent.target.value);
		}
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

export { CellActionPanel };
