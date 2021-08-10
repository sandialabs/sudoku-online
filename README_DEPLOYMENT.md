# How to Deploy Sudoku Online

## What You'll Need

You will need a web server on a host with a Python interpreter.  You must be able to install packages into the Python environment that the web server can access.

You will also need a workstation with Node and NPM installed.  This workstation does not need to be the same as the machine hosting the web server.

## Client

To deploy the client, you will first create a release build, then move the releaseable code over to the web server, then configure the web server to do the right thing with game routing.

### Creating a Release Build

1.  Clone the code.

2.  Install all the dependencies:
    1. `cd sudoku-online/sudoku-client`
    2. `npm install`

3.  Build the release package:
    1. `npm run build`

### Deploying the Release Build

1. Copy the contents of the `build` folder created by `npm run build` into the root directory of the WWW tree on the web server.  NOTE: If we ever want to relocate this, it requires minor changes to the client code.

### Server Configuration

The Sudoku client uses parameters passed in the URL to identify the game it should load.  To the server, these look like requests for nonexistent files.  We work around this by telling the server that requests for nonexistent files should actually go to /index.html.  

1. Edit the file `nginx.conf` on the web server.  Find the location { } section corresponding to the directory containing the client code.  Add the following snippet:

```
    if (!-e $request_filename) {
        rewrite ^(.*)$ /index.html break;
    }
```

2. Check `nginx.conf` for syntax errors by running `nginx -t`.  

3. If `nginx` is running, tell it to reload its configuration file by running `nginx -s reload`.  

4. Test your server by pointing a web browser to `http[s]://my_server.example.com/game/logical_operator_mturk_test_suite`.

