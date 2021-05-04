// ButtonWithAlertDialog
//
// Button that opens an "Are you sure?" dialog to confirm.
//
// This component is right out of the React documentation for Dialog:
//
// https://material-ui.com/components/dialogs/
//
// Required Props:
//    buttonText (string): Text to go on action button
//    dialogTitle (string): Title string for confirmation dialog
//    dialogText (string): Content text for confirmation dialog
//    handleConfirmation (function): Callback for "yes, take this action"
//
// Props:
//    buttonId (string): CSS ID for main button (defaults to
//        "alert-button")
//    buttonVariant (string): MaterialUI button variant; defaults to 
//        "outlined"
//    buttonColor (string): MaterialUI color spec; defaults to "primary"
//    
//    dialogAriaLabel {string}: Aria label for confirmation dialog
//    dialogAriaDescription {string}: Aria text description for 
//        confirmation dialog
//    dialogId {string}: CSS ID for dialog box (defaults to 
//        "alert-dialog")
// 
//    dialogTitleId (string): CSS id for title element of dialog box
//        (defaults to "alert-dialog-title")
//
//    okButtonColor (string): MaterialUI button color for OK
//        button in confirmation dialog (defaults to "primary")
//    okButtonId (string): CSS ID for "OK" button in dialog
//        (defaults to "alert-button-ok")
//    okButtonText (string): Text for OK button (defaults to "OK")
//    okButtonVariant (string): MaterialUI button variant for OK 
//        button in confirmation dialog (defaults to "contained")
//
//    cancelButtonColor (string): MaterialUI button color for
//        Cancel button in confirmation dialog (defaults to "primary")
//    cancelButtonId (string): CSS ID for "Cancel" button in
//        confirmation dialog (defaults to "alert-button-cancel")
//    cancelButtonText (string): String to display on cancel
//        button in confirmation dialog (defaults to "cancel")
//    cancelButtonVariant (string): MaterialUI button variant for
//        Cancel button (defaults to "contained")

import React from 'react';
import { Button } from '@material-ui/core';
import {
    Dialog, 
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle
} from '@material-ui/core';

import PropTypes from 'prop-types';



function ButtonWithAlertDialog(props) {
    const [open, setOpen] = React.useState(false);

    const handleClickOpen = () => setOpen(true);
    const handleCancel = () => setOpen(false);
    const handleOk = () => { setOpen(false); props.handleConfirmation(); }
     return (
        <div>
          <Button variant={props.buttonVariant} 
                  color={props.buttonColor} 
                  onClick={handleClickOpen}
                  >
            {props.buttonText}
          </Button>
          <Dialog
            open={open}
            onClose={handleCancel}
            aria-labelledby={props.dialogAriaLabel}
            aria-describedby={props.dialogAriaDescription}
            id={props.dialogId}
          >
            <DialogTitle id={props.dialogTitleId}>
                {props.dialogTitle}
            </DialogTitle>
            <DialogContent>
              <DialogContentText>
                {props.dialogText}
              </DialogContentText>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCancel} 
                      color={props.cancelButtonColor}
                      id={props.cancelButtonId}
                      variant={props.cancelButtonVariant}>
                {props.cancelButtonText}
              </Button>
              <Button onClick={handleOk} 
                      color={props.okButtonColor}
                      id={props.okButtonId}
                      variant={props.okButtonVariant} 
                      autoFocus>
                {props.okButtonText}
              </Button>
            </DialogActions>
          </Dialog>
        </div>
      );
}

ButtonWithAlertDialog.propTypes = {
    buttonText: PropTypes.string.isRequired,
    dialogText: PropTypes.string.isRequired,
    dialogTitle: PropTypes.string.isRequired,
    handleConfirmation: PropTypes.func.isRequired,

    buttonColor: PropTypes.string,
    buttonId: PropTypes.string,
    buttonVariant: PropTypes.string,

    dialogTitleId: PropTypes.string,

    cancelButtonColor: PropTypes.string,
    cancelButtonId: PropTypes.string,
    cancelButtonText: PropTypes.string,
    cancelButtonVariant: PropTypes.string,

    okButtonColor: PropTypes.string,
    okButtonId: PropTypes.string,
    okButtonText: PropTypes.string,
    okButtonVariant: PropTypes.string

};

ButtonWithAlertDialog.defaultProps = {
    buttonColor: "primary",
    buttonId: "button-with-alert",
    buttonVariant: "contained",
    
    dialogAriaLabel: "alert-dialog-title",
    dialogAriaDescription: "alert-dialog-description",

    dialogTitleId: "alert-dialog-title",

    cancelButtonColor: "primary",
    cancelButtonId: "alert-dialog-cancel",
    cancelButtonText: "Cancel",
    cancelButtonVariant: "contained",

    okButtonColor: "primary",
    okButtonId: "alert-dialog-ok",
    okButtonText: "OK",
    okButtonVariant: "contained"
};

export { ButtonWithAlertDialog };
export default ButtonWithAlertDialog;
