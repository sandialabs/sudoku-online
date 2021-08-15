// Debug Info Panel
//
// This is just a text panel that will go into the Sudoku client
// as a convenient area to print debug info.  Not as explorable
// as the console log but a lot easier to see.

import React from 'react';
import PropTypes from 'prop-types';


import { Paper } from '@material-ui/core';

class DebugInfoPanel extends React.Component {
    render() {
        let gameConfiguration = "(no game specified)";
        let puzzleInfo = "(no puzzle specified)"
        let puzzleBoards = "(no puzzles available)"

        if (this.props.gameConfiguration !== undefined) {
            gameConfiguration = JSON.stringify(this.props.gameConfiguration, null, 4);
        }

        if (this.props.puzzleInfo !== undefined) {
            puzzleInfo = JSON.stringify(this.props.puzzleInfo, condenseBoardArrays, 4);
        }

        if (this.props.puzzles !== undefined) {
            puzzleBoards = [];
            let count = 0;
            this.props.puzzles.forEach(
                function(board) {
                    const boardAsString = JSON.stringify(board, condenseBoardArrays, 2); 
                    puzzleBoards.push(
                            <pre key={count}>{boardAsString}</pre>
                        );
                    count += 1;
                });
        }
        return (
            <div>
                <p>This is the Debug Panel.</p>
                <Paper elevation={3}>
                    <h3>Game Configuration</h3>
                    <pre>{gameConfiguration}</pre>

                </Paper>
                <Paper elevation={3}>
                    <h3>Puzzle Information</h3>
                    <pre>{puzzleInfo}</pre>
                    <div>Answer to analysis question: {this.props.answer}</div>
                </Paper>
                <Paper elevation={3}>
                    <h3>Game Boards</h3>
                    <div>{puzzleBoards}</div>
                </Paper>
            </div>
            );
    }
}

function condenseBoardArrays(key, value) {
    if (key === "accessibleCells"
        || key === "assignments"
        || key === "availableMoves"
        ) {
        return "[Array: " + value.length + " values]";
    } else {
        return value;
    } 
}

DebugInfoPanel.propTypes = {
    gameConfiguration: PropTypes.object,
    puzzleInfo: PropTypes.object,
    puzzles: PropTypes.array,
    answer: PropTypes.string
}

export default DebugInfoPanel;
export { DebugInfoPanel };
