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

1. Copy the contents of the `build` folder created by `npm run build` into the root directory of the WWW tree on the web server.  NOTE: If we ever want to relocate this, it requires minor changes to the client code.

### Server Configuration (nginx)

The Sudoku client uses parameters passed in the URL to identify the game it should load.  To the server, these look like requests for nonexistent files.  We work around this by telling the server that requests for nonexistent files should actually go to /index.html.  

1. Edit the file `nginx.conf` on the web server.  If you installed nginx with MacPorts, this file is in /opt/local/nginx/.  Find the location { } section corresponding to the directory containing the client code.  Add the following snippet:

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

Make a directory for it somewhere.  Say, ~/sudoku-deploy.  Copy the contents of sudoku-online/sudoku-server into that directory.


Add ~/Library/LaunchAgents/gunicorn.plist:

---- begin file ----

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>sudoku-server.plist</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/atwilso/sudoku-deploy/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/atwilso/sudoku-deploy/stderr.log</string>
    <key>WorkingDirectory</key>
    <string>/Users/atwilso/sudoku-deploy/</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string><![CDATA[/opt/local/bin:/opt/local/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin]]></string>
    </dict>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/local/bin/gunicorn-3.9</string>
        <string>--workers</string>
        <string>8</string>
        <string>--bind</string>
        <string>unix:/tmp/sudoku-server.sock</string>        
        <string>-m</string>
        <string>000</string>
        <string>wsgi:app</string>
    </array>
</dict>
</plist>


---- end file ----
