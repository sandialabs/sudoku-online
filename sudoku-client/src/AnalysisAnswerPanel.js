// AnalysisAnswerPanel - Answer buttons for the Big Question
// 
// Our subjects are solving Sudoku puzzles in order to try to answer
// a question we've put to them.  This component contains the buttons
// for an answer.  The question itself is displayed separately.


import React from 'react';
import PropTypes from 'prop-types';

import { Paper } from '@material-ui/core';

import { FormControl, FormControlLabel, FormLabel } from '@material-ui/core';
import { Radio, RadioGroup } from '@material-ui/core';

class AnalysisAnswerPanel extends React.Component {
    render() {
        const radioButtons = this.props.answers.map(
            answer => (<FormControlLabel
                            key={answer}
                            value={answer}
                            control={<Radio />}
                            label={answer}
                            onChange={(event) => this.handleRadioChange(event)}
                            />)
            );

        return (
                <Paper>
                    <FormControl component="fieldset">
                        <FormLabel component="legend">Your Answer</FormLabel>
                        <RadioGroup aria-label="analysis-answer" 
                                    name="answer1"
                                    row>
                        {radioButtons}
                        </RadioGroup>
                    </FormControl>
                </Paper>
            );
    }

    handleRadioChange(event) {
        const newValue = event.currentTarget.value;
        if (this.props.handleAnswerChanged) {
            this.props.handleAnswerChanged(newValue);
        }
    }
}

AnalysisAnswerPanel.defaultProps = {
    answers: [ "Yes", "No" ]
}

AnalysisAnswerPanel.propTypes = {
    answers: PropTypes.array,
    handleAnswerChanged: PropTypes.func
};

export default AnalysisAnswerPanel;
export { AnalysisAnswerPanel };
