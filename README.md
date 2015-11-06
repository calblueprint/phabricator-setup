Phabricator Guide
====
Phabricator is a platform for code review, much like GitHub Pull Requests. Phabricator, however, has a much more extensive and intuitive feature set. We'll be replacing Pull Requests with Phabricator Diffs!

###Table of Contents
1. [Developer Setup](#dev-setup)
2. [Developer Workflow](#dev-workflow)
3. [PL/Project Setup](#pl-setup)

<a name="dev-setup"></a>
Developer Setup
----
### Step 1: Install Arcanist
Phabricator is the web tool for _doing_ code reviews, but Arcanist (or `arc`) is the command line tool that interacts with Phab. To install `arc`, you'll need to clone the GitHub repo and add the program to your `$PATH`. We're going to accomplish this by symlinking the program to your path. (**IMPORTANT:** Ask you PL to explain this carefully if you don't know what this means!!!)

**IMPORTANT:** We'll be installing a few tools throughout this guide, so you'll need to pick/create a permanent directory to keep all of these tools. For example, you could create a folder called `~/.webdev` in your home directory. Alternatively, you can use the more "UNIX-compliant" directory `/usr/local/opt` (you may have to create this directory if it doesn't already exist).

Once you've chosen your preferred directory, `cd` to it:

	$ cd /usr/local/opt

Next, let's clone and configure some of our tools by running the following:

    $ git clone https://github.com/calblueprint/libphutil.git
    $ git clone https://github.com/calblueprint/arcanist.git
    $ ln -s $(pwd)/arcanist/bin/arc /usr/local/bin/arc

(The last command above assumes that `/usr/local/bin` is already in your `PATH`; it should be.) 

**Restart your terminal.** Now, when you run `arc`, you should see something like:

    Usage Exception: No command provided. Try 'arc help'.

If you instead see something like: `bash: command not found: arc`, something went wrong. Run through the steps again, or ask your PL for help.

> NOTE: We use a fork of both arcanist and libphutil. Make sure you clone our custom
forks, not the phalicity repos.

### Step 2: Clone and configure Traphic
We'll be using [Traphic](https://github.com/calblueprint/traphic.git) to enable Github-ready Continuous Integration for our projects. (**IMPORTANT:** If you don't know what continuous integration is, ask your PL!) Traphic is a small external library for Arcanist that automagically pushes your feature branches to GitHub whenever you create a diff for Phabricator. (More on this later.)

In your preferred directory (you should already be here), clone the Traphic repo:

    $ git clone https://github.com/calblueprint/traphic.git

Next, you'll need to export the environment variable `TRAPHIC_PATH` in your shell environment. Let's find out what kind of shell you're using to set this up correctly. Copy/paste/run the following in your terminal:

	$ echo $SHELL

Now, follow the directions that correspond to the output from the above command you just ran:

- Output: `/bin/bash`
	- You are running a `bash` shell! Open `~/.bash_profile` in your preferred editor and continue to the step after these bullets.
- Output: `/bin/zsh`
	- You are running a `zsh` shell! Open `~/.zshrc` in your preferred editor and continue to the step after these bullets.
- Output: something else
	- You probably know what you're doing. Open up your shell's environment setup file and continue.

At this point, you should have opened a configuration file for your shell in some editor. At the bottom of the file, paste the following line:

	export TRAPHIC_PATH=/replace/me/with/path/to/traphic/repo

**IMPORTANT:** As you may have noticed, you'll need to replace the path given above with the _absolute_ path to where you cloned your Traphic repo! For example: `/usr/local/opt/traphic`. Relative paths (i.e. `~/.webdev`) are not allowed!


> **SUPER IMPORTANT:** If you don't understand what "exporting an environment variable" actually means, please ask your PL to clarify!

Assuming your PL set up your project correctly, you should be good to go with Traphic.


### Step 3: Have your PL make you a Phabricator account
**IMPORTANT:** Make sure that you've already authenticated an `@berkeley.edu` account with your GitHub before proceeding!

Ask your PL to add you as a user on our Phabricator. _Ask your PL to set your Phabricator username to your Slack username, not your GitHub username!!!_

You should recieve an email with an authentication link. Follow that link, and you should be good to go.

### Step 4: Install Phabricator certificate
Navigate to the root of your project's directory, e.g.

	$ cd /path/to/project_homeless_connect

At this point, I'm assuming that your PL has already configured your project correctly. Just in case, `git pull` the latest changes from master and run `cat .arcconfig`. This should output a JSON configuration file. If you don't see any output at this point, then your PL may not have configured your project for Phabricator yet! Please bring this up with them.

Assuming everything is correctly configured, from the root of your repository, run the following:

	$ arc install-certificate

This should print a URL to your terminal. Follow the link, copy the code given, and paste it back in your terminal.

### Step 5: Configure local repo git conventions
Luckily, this step is automated. In the root of your repo and copy/paste the following into your terminal to curl and run an automated script that will set up your repo with some goodies that should streamline your workflow:

	$ python <(curl -sL http://git.io/vWg1q)

This script does the following automagically:

- Configures a git hook on `pre-commit`, which disables committing to master.
- Configures a git hook on `pre-push`, which disables pushing to master.
- Sets up a custom commit message template which defaults to adding your PL and teammates as Reviewer and CCs, respectively.
- Configures a git hook on `prepare-commit-msg` to disable committing with `-m`, in order for git to pick up the aforementioned commit template.
- Sets up your repo to automatically `rebase` on `git pull`.
- Configures `arc vdiff`, an alias for `arc diff --verbatim`.

Don't worry, all of these configuration will be local to _this_ git repo. None of your other git repos will be affected!

> **A NOTE FOR PLs:** These restrictions can be bypassed if there is an emergency! Please ping me (@aleks) on Slack for details if you forget how to.


### Step 6: Voila!
You should be configured to push diffs for code review on Phabricator, yay! Read the next section to get a feel for the Phabricator workflow.

<a name="dev-workflow"></a>
Developer Workflow
----
Phabricator best practice is to do all your work in branches. You do no development in the master branch; that is just a staging branch to push upstream (to GitHub).
Some of these rules are stricly enforced by the above configuration you did on your local repo.

1. When you want to start work on a new feature or change, create a local branch:

		$ git checkout -b cool-new-feature

2. Make a bunch of changes, and commit normally (don't use the `-m` flag):

		$ git commit

3. Now you should be ready for a review. Run:

		$ arc vdiff

	The automated script you just ran should have set up this arc alias for you. We use `arc vdiff` instead of `arc diff` because we want to explicitly keep the format of our commit template. (Run `arc diff --help` for more detail on this, or ask me @aleks).
	- **Super useful:** If you'd like to preview your diff before actually submitting it for review, use `arc diff --preview` instead!

4. Often, your PL will give you feedback on your review that will prompt you to make changes before you can push to master.  Make the changes/fixes as normal in your branch, and then use `git commit --amend` to amend your previous git commit. (This is normally bad GitHub practice, but becomes very useful and actually preferred when using Phabricator.)  Then, run `arc vdiff`. Your editor should open up with a message indicating that your are making a revision to an _existing_ Phab diff.
	>
	- If you don't need to change your commit message on amend, you can use the `--no-edit` flag to skip editing it.
	- If you need to force `arc` to assign the new commits to the correct Phab revision ID, use `arc diff --update <revision id>`

5. When you are ready to push, you'll want to rebase your changes into the master branch and do a git push from master up to GitHub. (See the note below on rebasing.) You can do this in one step, which will also update your commit message with Phabricator metadata: `arc land`
	- If you want to be explicit, you can run `arc land <to-branch>`

	> **Rebasing:** Our Phabricator projects are set up to `rebase` instead of `merge` by default; this should have been automatically configured. Rebasing gives the illusion of a much cleaner commit history. Ask your PL to clarify the difference between `merge` and `rebase`, you should become somewhat familiar with the two.

If other people have committed changes that you want to incorporate into your branch (perhaps a bugfix that you need), you can just do `git pull --rebase` in your feature branch (or simply `git pull` since your repo has set up rebase by default).  Phabricator will do the right thing in ignoring these not-your changes.

See the Phabricator authors' workflow for more in-depth, detailed info [here](https://secure.phabricator.com/w/guides/arcanist_workflows/).


### Summary
	$ git checkout -b <feature branch>
	<edit edit edit>
	$ git commit
	$ arc vdiff

	<edit based on review feedback>
	$ git commit
	$ arc vdiff

	<maybe run git pull if you want some updates>
	<edit + commit + arc diff some more>

	$ arc land

<a name="pl-setup"></a>
(PLs) Project Setup
----
Read this section if you're a PL setting up your project with Phabricator.

### Step 1: Make an admin Phabricator account
> **NOTE:** Make sure that you've already authenticated an `@berkeley.edu` account with your GitHub before proceeding!

Go to [phab.calblueprint.org](http://phab.calblueprint.org) and authenticate with GitHub. Ask me (@aleks) or someone else that already has admin access to activate your account and give you admin privilege. You'll need admin privilege in order to activate your devs later.

### Step 2: Add an `.arcconfig` file to your project's repo.
(This part assumes you already have a GitHub repo.)
Either copy the file in this repo into the root directory of your project's repo, or make a new blank `.arcconfig` file pointing to our Phab.

For convenience, we've pasted it here as well:

	{
	  "phabricator.uri": "http://phab.calblueprint.org",
	  "history.immutable": false,
	  "load": [
	    "$TRAPHIC_PATH"
	  ],
	  "arcanist_configuration": "TraphicConfiguration"
	}

Later on, you'll probably want to add linters and unit test engines to your configuration files. This lets you run lint and unit tests before making a
Phab diff (which is awesome, because we can enforce good style and not deal with Hound). More information on this
[here](https://secure.phabricator.com/book/phabricator/article/arcanist_new_project/).

For most Rails + React projects, we are probably going to want to set up default linters for both our Ruby and Javascript code.
Luckily, arcanist comes packaged with the Rubocop linter, but it unfortunately doesn't have great support for JSX code.
Therefore, the rest of this guide assumes that you have our forked copy of arcanist, since we've included a custom ESLinter for you.

From here, setting up the linters is very easy. For example, if you wanted to have linters for Ruby, Javascript, and CSS, you would create an
`.arclint` file in the root of your project directory like:

	{
	  "linters": {
	    "ruby": {
	      "type": "rubocop",
	      "include": "/\\.(rb|rake)$/",
	      "exclude": "(^db/)",
	      "rubocop.config": ".rubocop.yml"
	    },
	    "jsx": {
	      "type": "eslint",
	      "include": "/\\.(js|jsx)$/"
	    },
	    "csslint": {
	      "type": "csslint",
	      "include" : "(\\.css$)"
	    }
	  }
	}

> **NOTE**: Due to the way the linters are configured, you will have to define which paths to check in this file and NOT in a different config file.
  Therefore, the include / exclude rules you have defined in a `rubocop.yml` will not apply. However, all other rules will work as expected.
  
### Step 3: Configure Diffusion for your project
Phabricator uses a tool called Diffusion to track your GitHub project commits, assigning useful metadata to your diffs.
GitHub will still host all of our projects, Phabricator simply watches the GitHub repo. Diffusion needs to be
configured for things to work properly with Phabricator.

- Go to [http://phab.calblueprint.org/project/](http://phab.calblueprint.org/project/) and click the "New Project" button in the upper-right corner of the page.
- Choose your project name (e.g. "California Rangeland Trust") and a super short tag for your commits (e.g. `CRT`).
- You've just created a tag for your project. You can also do cute things like change your tag's color or icon. **IMPORTANT:** Later, once your devs have been set up, you'll want to add them as members of your project.
- Go to [http://phab.calblueprint.org/diffusion/](http://phab.calblueprint.org/diffusion/) and click the "New Repository" button in the upper-right corner of the page.
- Choose to "Import an Existing External Repository" and follow the instructions until the "Repository Ready!" step. At this point, choose "Configure More Options First"

	> If you missed this step, find your way back to your project's Diffusion settings page by
	going to your project's page in Diffusion and clicking "Edit Repository" on the right side
	of the project info card.

- In the first box, click "Edit Basic Information" on the right.
	- Add your previously-created project tag to this repository, and save your changes.
- Scroll down to the "Branches" section, and click the "Edit Branches" button.
	- In the "Track Only" box, paste the following:

			regexp(/^(?!TR\_D)/)

	- In the "Autoclose Only" box, paste the following:

    		master

	- Save changes.
- Scroll back up to the top of the page and press "Activate Repository", in the first box on the right. (You may have already done this earlier.)

All done!

### Step 4: Configure local repo
Follow the above [Developer Setup](#dev-setup) guide.

Brush up on [Phabricator workflow](#dev-workflow).

### Step 5: ???
### Step 6: Profit!
Prepare to enter code-review ~~hell~~ heaven!

**IMPORTANT:**

- Make sure your devs have git >= 2.0 installed!
- Make _absolute_ sure that all of your devs have curled and run the automated set-up script we've provided. There could be serious confusion otherwise.

This way, no dev can accidentally spoil your ~~beautiful~~ linear history.
