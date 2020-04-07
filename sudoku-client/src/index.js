import React from 'react';
import ReactDOM from 'react-dom';

import SudokuGame from './SudokuGame';
import './index.css';


ReactDOM.render(
  <React.StrictMode>
    <p>
    	Hi.  This is the Sudoku client app.
    </p>
    <SudokuGame />
  </React.StrictMode>,
  document.getElementById('root')
);
