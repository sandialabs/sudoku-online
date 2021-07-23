// LogicalOperatorInfoDialog - tell user about selecting ops
//
// If we are using a board that has the "select_ops_upfront" modifier
// set, the user must select a set of logical operators before making 
// any moves.  Since it can be a little confusing to start a game and
// have all the moves grayed out, this dialog will pop up to tell
// the user what to do.


import React from 'react';
import { Dialog, DialogContentText, DialogTitle } from '@material-ui/core';
import { Typography } from '@material-ui/core';
import PropTypes from 'prop-types';


class SelectLogicalOperatorInfoDialog extends React.PureComponent {
    constructor(props) {
        super(props);
        this.announceClose = this.announceClose.bind(this);

        render() {
        return (
            <Dialog onClose={this.props.announceClose}
                    open={true}
                    aria-labeledby="select-ops-dialog-title"
                    >
                <DialogTitle id="select-ops-dialog-title">
                    Info: Selecting Logical Operators
                </DialogTitle>
                <DialogContentText>
                    <div>
                        For this Sudoku board we ask you to select the logical 
                        operators you want to apply before you begin to make 
                        moves on the board.  To make your selection, check all
                        the box next to each operator you want to apply, then 
                        select "Confirm Operator Selection".  Once you confirm
                        your selection, the logical operators will remain 
                        unchanged until you submit this board and move to the
                        next one.  <b>Laura and Shelley:
                        we will substitute your instructions here.</b> 
                    </div>
                    <div>
                        To exit this dialog, press Escape or click outside it.
                    </div>
                </DialogContentText>
            )
    }
}

SelectLogicalOperatorInfoDialog.propTypes = {
    announceClose: PropType.func.isRequired
};