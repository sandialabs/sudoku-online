// AnalysisQuestionPanel - Q&A for the Big Question
// 
// Our subjects are solving Sudoku puzzles in order to try to answer
// a question we've put to them.  This component handles the display
// of the question and the prompt for an answer.

import React from 'react';
import PropTypes from 'prop-types';

import { Typography, Grid, Paper } from '@material-ui/core';

import { FormControl, FormControlLabel, FormLabel } from '@material-ui/core';
import { Radio, RadioGroup } from '@material-ui/core';

class AnalysisQuestionPanel extends React.Component {
    render() {
        const radioButtons = this.props.answers.map(
            answer => (<FormControlLabel
                            key={answer}
                            value={answer}
                            control={<Radio />}
                            label={answer}
                            />)
            );

        console.log('AnalysisQuestionPanel: radio button array:');
        console.log(radioButtons);

        const handleChange = (event) => {
            if (this.props.handleAnswerChanged) {
                this.props.handleAnswerChanged(event.target.value);
            } else {
                console.log('AnalysisQuestionPanel: No answer handler');
            }
        }


        const question = this.props.question || "(question undefined)";

        const questionLabel = "The Question: \u00a0\u00a0";

        return (
            <Grid container 
                  alignItems="center"
                  key={1} 
                  id="analysisQuestionPanel" 
                  justify="flex-start"
                  alignItems="stretch"
                  spacing={1} >
                <Grid item xs={3}>
                    <Paper> 
                    <Typography 
                        key="question_label"
                        display="inline"
                        >
                        {questionLabel}
                    </Typography>
                    <Typography 
                        key="question_text"
                        display="inline"
                        color="primary"
                        >
                        {question}
                    </Typography>
                    </Paper>
                </Grid>
                <Grid item xs={6}>
                    <Paper>
                        <Typography
                            key="answer_label"
                            display="block"
                            >
                            Your Answer:
                        </Typography>

                        <FormControl component="fieldset">
                            <RadioGroup 
                                row
                                aria-label="analysisAnswer"
                                name="analysisAnswer1"
                                onChange={handleChange}
                                >
                                {radioButtons}
                            </RadioGroup>
                        </FormControl>
                    </Paper>
                </Grid>
            </Grid>
            );
    }
}

AnalysisQuestionPanel.defaultProps = {
    question: "Are these the droids you're looking for?",
    answers: [ "Yes", "No" ]
}

AnalysisQuestionPanel.propTypes = {
    question: PropTypes.string,
    answers: PropTypes.array,
    handleAnswerChanged: PropTypes.func
};

export default AnalysisQuestionPanel;
export { AnalysisQuestionPanel };
