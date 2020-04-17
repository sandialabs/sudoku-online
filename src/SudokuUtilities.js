// ECMAScript 6 has sets but is missing functions for set operations.
// This file provides equivalents.


export { setUnion, setIntersection, setDifference, newSerialNumber, initialMoveList };

function setUnion(a, b) {
	return new Set([...a, ...b]);
}

function setIntersection(a, b) {
	return new Set([...a].filter(x => b.has(x)));
}

function setDifference(a, b) {
	return new Set([...a].filter(x => !b.has(x)));
}

function setSymmetricDifference(a, b) {
	return setDifference(setUnion(a, b), setIntersection(a, b));
}

SerialNumbers = { }

/** Request a serial number for a named category
 *
 * A serial number is a monotonically increasing integer.  We allow
 * multiple categories of serial numbers by requiring the user 
 * to specify a category name:
 *
 * let serial1 = newSerialNumber("foo"); (returns 0)
 * let serial2 = newSerialNumber("foo"); (returns 1)
 * let serial3 = newSerialNumber("foo"); (returns 2)
 * let other_serial1 = newSerialNumber("bar"); (returns 0)
 * let serial4 = newSerialNumber("foo"); (returns 3)
 *
 * Serial numbers for different categories are not guaranteed
 * to be disjoint.
 */

function newSerialNumber(key) {
	let newSerial = 0;
	if (key in SerialNumbers) {
		newSerial = SerialNumbers[key] + 1;
	}
	SerialNumbers[key] = newSerial;
	return newSerial;
}

function initialMoveList(degree) {
	return [...Array(degree*degree).keys()];
}