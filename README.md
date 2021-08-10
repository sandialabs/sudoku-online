# Sudoku Online v.0.2

This is a web-based implementation of Sudoku.  The intent is to allow the user to play Sudoku through a web browser with certain restrictions on the moves they can make.  Server-side code will track and assist gameplay.

The instructions in this file will help you bootstrap an environment to run the client (React/JS/HTML) part of the application.  Once we have a web server that can run the analysis portion of the task, these instructions will change.

## To Install

### Step 0: Clone the repository

In these instructions we will pretend that you have cloned the repository into the directory `~/projects/EUBA/sudoku-online`.

### Step 1: Node.js and NPM

You'll need Node.js and NPM (Node Package Manager) installed to run this client.

Use your favorite package manager to install a relatively recent Node.js (version 8 or newer).  You will probably get NPM along with this for free.  Check this with the command "which npm" at a shell prompt.  If it's not there, then install it using the same package manager.

If for some reason you can't use a package manager and have to go to the source, Node.js is at <https://nodejs.org> and NPM is at <https://www.npmjs.com>.  This is a measure of last resort.

### Step 2: Configure NPM to save packages in your home directory

Much like Python installations, setting up an environment for Javascript development in your home directory is much simpler and cleaner than setting one up system-wide.  Put the following code in your .bashrc to avoid cluttering the system-wide installation:

```bash
# Tell NPM (Node Package Manager) to install packages into
# ${HOME}/.npm-packages to cut down on clutter.

export NPM_PACKAGES="${HOME}/.npm-packages"
export PATH="${PATH}:${NPM_PACKAGES}/bin"

if [ -z "${NODE_PATH}" ]; then
  export NODE_PATH="${NPM_PACKAGES}/lib/node_modules"
else
  export NODE_PATH="${NPM_PACKAGES}/lib/node_modules:${NODE_PATH}"
fi
```

### Step 3: Set up WWW proxy

NPM has its own way of keeping track of WWW proxy settings.  Create a file called `.npmrc` in your home directory and add the following two lines, customized for your home organization's configuration:

```
proxy=http://proxy.example.com:80
https-proxy=http://proxy.example.com:80
```

Someday there will be a unified, reliable way to handle proxy configuration in a cross-platform fashion.  This is not that day.

### Step 4: Upgrade NPM to the latest version

Older versions of NPM don't understand a few of the newer dependencies we use. Upgrade NPM with the following command:

```bash
npm install npm@latest -g
```

### Step 5: Install dependencies for Sudoku Online

A full list of the dependencies for the project, including versions, is already present in the source code.  The following two commands will download everything necessary.

```bash
cd ~/projects/EUBA/sudoku-online/sudoku-client
npm install
```

If you get a scary-looking error message that says there is something wrong with NPM itself, the problem is usually that it's trying to install into system-wide directories.  Make sure you've done Step 2.  Restart your shell if necessary.

You are now done with setup.

## Running the Sudoku Web App

There is a lightweight web server suited for development and debugging of React apps (this is one such) already installed in the dependencies.  To run it, run the following commands:

```bash
cd ~/projects/EUBA/sudoku-online/sudoku-client
npm start
```

This will usually open up a web browser on its own.  If not, do so yourself and go to the URL `localhost:3000`.

## Other Tasks

We don't need any of these yet but will eventually.

### To build the client files for distribution:

```bash
cd ~/projects/EUBA/sudoku-online/sudoku-client
npm run build
```

### To run the tests (once we have some):

```bash
cd ~/projects/EUBA/sudoku-online/sudoku-client
npm test
```
