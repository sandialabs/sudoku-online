// Convenience functions for working with 2D arrays.
// 
// All of the exported functions treat their arguments as
// immutable.

import { clone } from 'ramda';

// Create a 2D array of some specified size with an optional
// fill value.
// 
// It is safe to pass in a reference for the fill value.  It
// will be cloned (deep copied) into each array cell.
function array2D(rows, columns, fillValue=null) {
	// This is equivalent to creating an array for rows,
	// then creating an array for each row.
	var array = new Array(rows).fill(0).map((dummy) => new Array(columns));
	var row, column;
	for (row = 0; row < rows; ++row) {
		for (column = 0; column < columns; ++column) {
			array[row][column] = clone(fillValue);
		}
	}
	return array;
}

// Return the dimensions of the specified array as a list
// [rows, columns].  An empty array will return [0,0].
function dimensions(array) {
	const rows = array.length;
	if (rows === 0) {
		return [0,0];
	} else {
		const columns = array[0].length;
		return [rows,columns];
	}
}

// Swap rows row1 and row2 in an array.  Returns a new array --
// argument is not modified.
function swapRows2D(array, row1, row2) {
	var newArray = clone(array);
	const tmp = newArray[row1];
	newArray[row1] = newArray[row2];
	newArray[row2] = tmp;
	return newArray;
}

// Swap columns col1 and col2 in an array.  Returns a new array --
// argument is not modified.
function swapColumns2D(array, col1, col2) {
	var newArray = clone(array);
	var row, tmp;
	const dims = dimensions(newArray);
	const rows = dims[0];

	for (row = 0; row < rows; ++row) {
		tmp = newArray[row][col1];
		newArray[row][col1] = newArray[row][col2];
		newArray[row][col2] = tmp;
	}

	return newArray;
}

// Rotate an array left by the specified number of elements.
// Rotation by a negative number is the same as rotating right.
// 
// Argument is considered immutable -- the array returned contains
// copies of the input.
function arrayRotateLeft(array, count) {
  	return arrayRotateLeftInPlace(clone(array), count);
}

// Rotate an array right by the specified number of elements.  
// Rotation by a negative number is the same as rotating right.
// 
// Argument is modified in place.  For a version that treats the
// array as immutable, see arrayRotateLeft.
function arrayRotateLeftInPlace(array, count) {
 	count -= array.length * Math.floor(count / array.length);
  	array.push.apply(array, array.splice(0, count));
  	return array;
}

// Rotate an array left by the specified number of elements.
// Rotation by a negative number is the same as rotating right.
// 
// Argument is considered immutable -- the array returned contains
// copies of the input.
function arrayRotateRight(array, count) {
	return arrayRotateLeft(array, -count);
}

// Rotate an array right by the specified number of elements.  
// Rotation by a negative number is the same as rotating right.
// 
// Argument is modified in place.  For a version that treats the
// array as immutable, see arrayRotateLeft.
function arrayRotateRightInPlace(array, count) {
	return arrayRotateLeftInPlace(array, -count);
}

// Lay out an array in row-major order.
function flatten(array) {
	let result = [];
	const rows = dimensions(array)[0];

	for (let r = 0; r < rows; ++r) {
		result.push(...array[r]);
	}
	return result;
}

// Reshape the elements of an existing array into a new array.
//
// Arguments:
//     inputArray: 1D array to reshape
//     rows (integer): Rows for the output
//     columns (integer): Columns for the output
//     deepCopy (boolean): if true, elements in the new array
//         will be copies of the originals.  If false, elements
//         in the new array will be the values from the original.
//         Defaults to true.
//         
// Throws:
//     InvalidShapeException: requested shape doesn't match number
//         of elements 
function reshape1Dto2D(inputArray, rows, columns, deepCopy=true) {
	if (inputArray.length !== rows*columns) {
		throw new InvalidShapeException(
			'Cannot reshape an array with length ' + inputArray.length 
			+ ' to one with dimensions ' + rows + ' x ' + columns 
			+ ': element counts do not match (' 
			+ inputArray.length + ' vs. ' + rows*columns + ')'
			 );
	}

	let result = array2D(rows, columns);
	let i = 0;
	for (let r = 0; r < rows; ++r) {
		for (let c = 0; c < columns; ++c) {
			if (deepCopy) {
				result[r][c] = clone(inputArray[i]);
			} else {
				result[r][c] = inputArray[i];
			}
			++i;
		}
	}
	return result;
}

function InvalidShapeException(message) {
	const error = new Error(message);
	return error;
}

InvalidShapeException.prototype = Object.create(Error.prototype);

export { 
	array2D, 
	dimensions,
	flatten, 
	reshape1Dto2D,
	swapRows2D, 
	swapColumns2D,
	arrayRotateLeft,
	arrayRotateRight,
	arrayRotateLeftInPlace,
	arrayRotateRightInPlace 
};
