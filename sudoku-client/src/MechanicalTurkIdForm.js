// Text box component for Mechanical Turk ID

import React from 'react';
import PropTypes from 'prop-types';

import FormControl from '@material-ui/core/FormControl';
import FormHelperText from '@material-ui/core/FormHelperText';

import AccountCircle from '@material-ui/icons/AccountCircle';
import IconButton from '@material-ui/core/IconButton';
import Input from '@material-ui/core/Input';
import InputAdornment from '@material-ui/core/InputAdornment';
import InputLabel from '@material-ui/core/InputLabel';
import OutlinedInput from '@material-ui/core/OutlinedInput';
import TextField from '@material-ui/core/TextField';

function MechanicalTurkIdForm(props) {
    return (
        <form noValidate autoComplete="off">
            <TextField
                id="mechanical-turk-id"
                label="Your Mechanical Turk ID"
                variant="filled"
                onChange={ (event) => props.handleChange(event.target.value) }
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




