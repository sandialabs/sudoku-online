import React, { useEffect } from 'react';
import ReactDOM from 'react-dom';

import SudokuMain from './SudokuMain';
import './index.css';


import {
    BrowserRouter as Router,
    Switch,
    Route
} from 'react-router-dom';

import '@fontsource/roboto';

const deploy = true;

// In development mode, change this to the address of the server 
let serverAddress = "http://localhost:5000";

// In deployment mode, the server and client are both accessible through
// the same server namespace -- client at /, server at /sudoku.
// 
// See README.deployment and the config files in config_files_for_deployment.
// Note that 'npm serve -s' after your build will NOT work.
if (deploy) {
    serverAddress = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port;
}

const App = () => {
    // This effect runs after the first render.
    useEffect(() => {
        document.title = "SNL Sudoku"
    }, []);

    return (
        <Router>
            <div key={6}>
                <Switch>
                    <Route path="/game/:gameName">
                        <SudokuMain 
                            key={2} degree={3}
                            gameNameInUrl={true}
                            serverAddress={serverAddress}
                            />
                    </Route>

                    <Route path="/">
                        <SudokuMain 
                            gameNameInUrl={false}
                            serverAddress={serverAddress}
                            key={2} degree={3} 
                            blankFrontPage={deploy}
                            />
                    </Route>

                </Switch>
            </div>
        </Router>
    );
}

ReactDOM.render(
    <App />,
    document.getElementById('root')
);
