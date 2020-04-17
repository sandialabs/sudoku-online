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
	const [rows, columns] = dimensions(newArray);

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
	const [rows, columns] = dimensions(array);

	for (let r = 0; r < rows; ++r) {
		result.push(...array[r]);
	}
	return result;
}

export { 
	array2D, 
	dimensions,
	flatten, 
	swapRows2D, 
	swapColumns2D,
	arrayRotateLeft,
	arrayRotateRight,
	arrayRotateLeftInPlace,
	arrayRotateRightInPlace 
};
