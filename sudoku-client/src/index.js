import React from 'react';
import ReactDOM from 'react-dom';

import SudokuMain from './SudokuMain';
import './index.css';


import '@fontsource/roboto';

// ReactDOM.render(
//   <React.StrictMode>
//     <p>
//     	Hi.  This is the Sudoku client app.
//     </p>
//     <SudokuGame />
//   </React.StrictMode>,
//   document.getElementById('root')
// );

ReactDOM.render(
	<div key={0}>
	    <p key={1}>
    	Hi.  This is the Sudoku client app.
    	</p>
    	<SudokuMain key={2} degree={3}/>
    </div>,
  document.getElementById('root')
);
