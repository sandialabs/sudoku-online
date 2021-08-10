// Text box component for Mechanical Turk ID

import React from 'react';
import PropTypes from 'prop-types';

import AccountCircle from '@material-ui/icons/AccountCircle';
import InputAdornment from '@material-ui/core/InputAdornment';
import TextField from '@material-ui/core/TextField';

function MechanicalTurkIdForm(props) {

    const ignoreEnter = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
        }
    }

    return (
        <form noValidate autoComplete="off">
            <TextField
                id="mechanical-turk-id"
                label="Your Mechanical Turk ID"
                variant="filled"
                onChange={ (event) => props.handleChange(event.target.value) }
                onKeyPress={ignoreEnter}
                onKeyDown={ignoreEnter}
                onKeyUp={ignoreEnter}
                InputProps={{
                    startAdornment: 
                        <InputAdornment position="start">
                            <AccountCircle />
                        </InputAdornment>
                }}

                />
        </form>
        );
}

MechanicalTurkIdForm.propTypes = {
    handleChange: PropTypes.func.isRequired
}

export default MechanicalTurkIdForm;

export { MechanicalTurkIdForm };




