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


ReactDOM.render(
    <Router>
        <div key={6}>
            <Switch>
                <Route path="/">
                    <SudokuMain 
                        gameName="default"
                        key={2} degree={3} 
                        />
                </Route>

                <Route path="/game/:gameName">
                    <SudokuMain 
                        key={2} degree={3}
                        gameName="from_url"
                        />
                </Route>
            </Switch>
        </div>
    </Router>,

  document.getElementById('root')
);
