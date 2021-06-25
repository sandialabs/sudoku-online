// AnalysisAnswerPanel - Answer buttons for the Big Question
// 
// Our subjects are solving Sudoku puzzles in order to try to answer
// a question we've put to them.  This component contains the buttons
// for an answer.  The question itself is displayed separately.


import React from 'react';
import PropTypes from 'prop-types';

import { Typography, Grid, Paper } from '@material-ui/core';

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
                            />)
            );

        const handleChange = (event) => {
            if (this.props.handleAnswerChanged) {
                this.props.handleAnswerChanged(event.target.value);
            } else {
                console.log('AnalysisAnswerPanel: No answer handler');
            }
        }

            // return (
            // <Grid container xs={6}>
            //     <Grid item xs={2}>
            //         <Paper>
            //             <Typography key="answer_label">
            //                 Your Answer:
            //             </Typography>
            //         </Paper>
            //     </Grid>
            //     <Grid item xs={3}>
            //         <FormControl component="fieldset">
            //             <RadioGroup 
            //                 row
            //                 aria-label="analysisAnswer"
            //                 name="analysisAnswer1"
            //                 onChange={handleChange}
            //                 >
            //                 {radioButtons}
            //             </RadioGroup>
            //         </FormControl>
            //     </Grid>
            // </Grid>
            // );
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
