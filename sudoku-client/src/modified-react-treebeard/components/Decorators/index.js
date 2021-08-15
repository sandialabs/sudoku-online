import Container from './Container';
import Header from './Header';
import Loading from './Loading';
import Toggle from './Toggle';

const decorators = { 
    Container,
    Header,
    Loading,
    Toggle
};

// The compiler is unhappy if we export an object literal.
// We give it a name first just to fix that warning.
export default decorators;

export {
    Container,
    Header,
    Loading,
    Toggle
};
