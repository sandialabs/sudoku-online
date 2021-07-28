# How to Deploy Sudoku Online

## What You'll Need

You will need a web server on a host with a Python interpreter.  You must be able to install packages into the Python environment that the web server can access.

You will also need a workstation with Node and NPM installed.  This workstation does not need to be the same as the machine hosting the web server.

## Assumptions

We assume that you have root access on this server.

We assume that there are no other web servers running on this machine.

(If there are, you should probably just run this on a different port.)

## Client

To deploy the client, you will first create a release build, then move the releaseable code over to the web server, then configure the web server to do the right thing with game routing.

### Creating a Release Build

1.  Clone the code from `git@gitlab.sandia.gov:ASA/EUBA/sudoku-online`.  At some point we will migrate to CEE Gitlab and this URL will be out of date.

2.  Install all the dependencies:
    1. `cd sudoku-online/sudoku-client`
    2. `npm install`

3.  Build the release package:
    1. `npm run build`

### Deploying the Release Build

1. Copy the contents of the `build` folder created by `npm run build` into a directory called sudoku-client/ in the root of the WWW tree on the web server.  If you installed nginx with MacPorts, for example, this will be /opt/local/www/sudoku-client.  If you need to move this, change nginx.conf appropriately -- look for sudoku-client and you'll find the line to change.

### Web Server Configuration for Client Deployment

The Sudoku client uses parameters passed in the URL to identify the game it should load.  To the server, these look like requests for nonexistent files.  We work around this by telling the server that requests for nonexistent files should actually go to /index.html.  

The easiest thing to do here is to use `config_files_for_deployment/nginx.conf` from the repository.  This is a minimally modified default nginx config file.  Note that it assumes that the Sudoku server (the back-end game logic) is running under gunicorn with its socket at /tmp/sudoku-server.sock.

If you installed nginx with MacPorts, this config file goes in /opt/local/etc/nginx/nginx.conf.

```
    if (!-e $request_filename) {
        rewrite ^(.*)$ /index.html break;
    }
```

2. Check `nginx.conf` for syntax errors by running `nginx -t`.  

3. If `nginx` is running, tell it to reload its configuration file by running `nginx -s reload`.  

4. Test your server by pointing a web browser to `http[s]://my_server.example.com/game/logical_operator_mturk_test_suite`.

## Server

So far, we have been running the server using Flask in development mode.  For deployment, we will be running it under GUnicorn.

### Dependencies

Install Flask, Flask-CORS, and GUnicorn using your favorite package manager.  I recommend installing these at the OS level (for example, using MacPorts) instead of Anaconda since GUnicorn will not be using your Anaconda installation.

### Install Server Code

Note: this is Mac-specific at present.  It will not be difficult to adapt to Linux.  The caveat is that the UID that owns the gunicorn process must have write permission for the directory it runs from in order to save the data files.

Make a directory for it somewhere.  Say, ~/sudoku-deploy.  Copy the contents of sudoku-online/sudoku-server into that directory.

Grab the file config_files_for_deployment/sudoku-server.plist and put it in ~/Library/LaunchAgents.

**IMPORTANT**: Edit that file and change the paths that start with /Users/atwilso to point to wherever you have saved the files.

Start the service by running `launchctl load ~/Library/LaunchAgents/sudoku-server.plist`.  There will probably not be any output on the command line.  Look in `~/sudoku-deploy/{access,error}.log` to make sure it's running correctly.
