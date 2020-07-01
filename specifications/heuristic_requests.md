# Request/Response format for heuristics

Communication between the client and the server will be over HTTP using JSON as the format.  

## Request Format

A request will look like this:

```json
{
    'board': <JSON representation of board - see board.md>
    'action': {
        'action': 'selectValueForCell',
        'cell': [0,4],
        'value': 3
    },
    'heuristic': 'include/exclude'
}
```

The contents of the 'action' field might change.  The important elements are 'cell' and 'value'.  

We will need to either nail down the list of available heuristics or provide a way for the client to get them from the server.  Right now I have implemented `include/exclude` and I am aware of `pivot`.  

## Response Format

The response to a heuristic request is a list of boards.  Is this always going to be sufficient?

 