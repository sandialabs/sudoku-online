// GameInfoDialog - tell user that the game is over
// and ask him to close window
//


import React from 'react';
import { Dialog, DialogContent, DialogActions, DialogContentText, DialogTitle } from '@material-ui/core';
import { Button } from '@material-ui/core';
import PropTypes from 'prop-types';


function GameInfoDialog(props) {
    const [open, setInfoOpen] = React.useState(props.defaultState);

    const handleOpen = () => setInfoOpen(true);
    const handleOk = () => {
        setInfoOpen(false);
        if (props.handleConfirmation !== null) {
            props.handleConfirmation();
        }
    }

    if (props.registerOpen !== null) {
        props.registerOpen(handleOpen)
    }

    return (
        <Dialog open={open}
            onClose={handleOk}
            aria-labelledby="game-over-dialog-title"
        >
            <DialogTitle id="game-over-dialog-title">
                {props.dialogTitle}
            </DialogTitle>
            <DialogContent>
                <DialogContentText>
                    {props.dialogText}
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleOk}
                    color={props.okButtonColor}
                    id={props.okButtonId}
                    variant={props.okButtonVariant}
                    autoFocus>
                    {props.okButtonText}
                </Button>
            </DialogActions>
        </Dialog>
    )
};


GameInfoDialog.propTypes = {
    dialogText: PropTypes.string.isRequired,
    dialogTitle: PropTypes.string.isRequired,

    dialogTitleId: PropTypes.string,

    handleConfirmation: PropTypes.func,
    registerOpen: PropTypes.func,
    defaultState: PropTypes.bool,

    okButtonColor: PropTypes.string,
    okButtonId: PropTypes.string,
    okButtonText: PropTypes.string,
    okButtonVariant: PropTypes.string
};

GameInfoDialog.defaultProps = {
    dialogAriaLabel: "gameinfo-dialog-title",
    dialogAriaDescription: "gameinfo-dialog-description",
    dialogTitleId: "gameinfo-dialog-title-id",

    handleConfirmation: null,
    registerOpen: null,
    defaultState: false,

    okButtonColor: "primary",
    okButtonId: "info-dialog-ok",
    okButtonText: "OK",
    okButtonVariant: "contained"
};

export { GameInfoDialog };
export default GameInfoDialog;
