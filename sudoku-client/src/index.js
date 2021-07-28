import React from 'react';
import ReactDOM from 'react-dom';

import SudokuMain from './SudokuMain';
import './index.css';


import {
    BrowserRouter as Router,
    Switch,
    Route
} from 'react-router-dom';

import '@fontsource/roboto';

//const serverAddress = "http://localhost:5000/";
const serverAddress = window.location.protocol + '//' + window.location.hostname;

ReactDOM.render(
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
                        />
                </Route>

            </Switch>
        </div>
    </Router>,

  document.getElementById('root')
);
