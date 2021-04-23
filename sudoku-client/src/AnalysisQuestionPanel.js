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
            console.log("UNIMPLEMENTED: handleChange");
        }


        let question = "How is a raven like a writing desk?";
        if (this.props.question) {
            question = this.props.question;
        }

        return (
            <Grid container key={1} id="analysisQuestionPanel">
                <Grid container>
                    <Grid item xs={2}>
                        <Typography 
                            key="question_label"
                            display="inline"
                            color="secondary"
                            >
                            The Question:
                        </Typography>
                    </Grid>
                    <Grid item xs={3}>
                        <Typography 
                            key="question_text"
                            display="inline"
                            color="primary"
                            align="right"
                            >
                            {question}
                        </Typography>
                    </Grid>
                </Grid>
                <Grid container>
                    <Grid item xs={2}>
                        <Typography
                            key="answer_label"
                            display="inline"
                            color="secondary"
                            align="right"
                            >
                            Your Answer:
                        </Typography>
                    </Grid>
                    <Grid item xs={8}>
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
                    </Grid>
                </Grid>
            </Grid>
            );
    }
}

AnalysisQuestionPanel.defaultProps = {
    question: "How is a raven like a writing desk?",
    answers: [ "Not at all", "Somewhat" ]
}

AnalysisQuestionPanel.propTypes = {
    question: PropTypes.string,
    answers: PropTypes.array,
    answerChanged: PropTypes.func
};

export default AnalysisQuestionPanel;
export { AnalysisQuestionPanel };
