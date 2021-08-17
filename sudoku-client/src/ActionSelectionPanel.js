// ActionSelectionPanel - interface components to let user select
// what to do to the board / a single cell at each step


import React, { useState } from 'react';
import PropTypes from 'prop-types';

import { Grid, Paper } from '@material-ui/core';


import { CellActionPanel } from './CellActionPanel';
import { LogicalOperatorPanel } from './LogicalOperatorPanel';


function ActionSelectionPanel(props) {


    let defaultAction = null;
        if (props.cellActions !== null && props.cellActions.length > 0) {
            defaultAction = props.cellActions[0];
        }

    const [selectedCellAction, setSelectedCellAction] = useState(defaultAction);
    const [selectedLogicalOperators, setSelectedLogicalOperators] = useState([]);
    const [logicalOperatorsFrozen, setLogicalOperatorsFrozen] = useState(false);

    const logicalOperatorSelectionChanged = (opList) => {
        setSelectedLogicalOperators(opList);
        props.logicalOperatorSelectionChangedCallback(opList);
    }

    const selectedActionChanged = (action) => {
        console.log('ActionSelectionPanel: Selected action changed to ' + action.internal_name);
        console.log(action);
        setSelectedCellAction(action);
    }

    const logicalOpsCost = _logicalOperatorCost(selectedLogicalOperators);

    return (
        <Grid item>
            <Paper>
                <CellActionPanel
                    allActions={props.cellActions}
                    defaultAction={defaultAction}
                    permittedActions={props.permittedActions}
                    actionsCanExecute={props.actionsCanExecute}
                    selectedActionChanged={selectedActionChanged}
                    executeAction={() => props.executeActionCallback(selectedCellAction, selectedLogicalOperators)}
                    disabledReason={props.disabledReason}
                    logicalOperatorCost={logicalOpsCost}
                    key={props.resetCount}
                />
            </Paper>
            <Paper>
                <LogicalOperatorPanel
                    operators={props.logicalOperators}
                    selectionChanged={logicalOperatorSelectionChanged}
                    selectLogicalOperatorsUpFront={props.selectLogicalOperatorsUpFront}
                    logicalOperatorsFrozen={logicalOperatorsFrozen}
                    confirmOperatorSelection={() => {
                        console.log("SudokuGame: Confirming logical operator selection.");
                        setLogicalOperatorsFrozen(true);
                        props.logicalOperatorsFrozenCallback(true);
                    }}
                    key={props.resetCount}
                />
            </Paper>
        </Grid>        
        );

}

ActionSelectionPanel.propTypes = {
    actionsCanExecute: PropTypes.bool.isRequired,
    cellActions: PropTypes.array.isRequired,
    disabledReason: PropTypes.string.isRequired,
    executeActionCallback: PropTypes.func.isRequired,
    logicalOperators: PropTypes.array.isRequired,
    logicalOperatorSelectionChangedCallback: PropTypes.func.isRequired,
    logicalOperatorsFrozenCallback: PropTypes.func.isRequired,
    selectLogicalOperatorsUpFront: PropTypes.bool.isRequired,
}


function _logicalOperatorCost(selectedOperators) {
    if (selectedOperators.length === 0) {
        return 0;
    }
    const sumReduce = (accumulator, currentValue) => accumulator + currentValue;
    const logicalOperatorCosts = selectedOperators.map(
        (op) => op.cost
        );
    const logicalOperatorTotalCost = logicalOperatorCosts.reduce(sumReduce);
    return logicalOperatorTotalCost;
}

export { ActionSelectionPanel };
