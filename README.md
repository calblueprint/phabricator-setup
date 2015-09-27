Phabricator Guide
====
Phabricator is a platform for code review, much like GitHub Pull Requests. Phabricator, however, has a much more extensive and intuitive feature set.

Developer Setup
----
### Step 1: Install Arcanist
Phabricator is the web app that _hosts_ code reviews, but Arcanist (or `arc`) is the command line tool that interacts with Phab. To install `arc`, you'll need to clone the GitHub repo and add the program to your `$PATH`. We're going to accomplish this by symlinking the program to your path. (**IMPORTANT:** Ask you PL to explain this carefully if you don't know what this means!!!)

In your preferred directory (e.g. `~/.webdev`), run the following:

    git clone https://github.com/phacility/libphutil.git
    git clone https://github.com/calblueprint/arcanist.git
    ln -s $(pwd)/arcanist/bin/arc /usr/local/bin/arc

(This assumes `/usr/local/bin` is already in your path; it should be.) Restart your terminal. Now, when you type `arc`, you should see something like:

    Usage Exception: No command provided. Try 'arc help'.

If you instead see something like: `bash: command not found: arc`, something went wrong.

> NOTE: We use a fork of arcanist that adds ESLint as a linter (used for React apps). Shoutout to @nnarayen for implementing this.

### Step 2: Make a Phabricator account
> **NOTE:** Make sure that you've already authenticated an `@berkeley.edu` account with your GitHub before proceeding!

Go to [phab.calblueprint.org](http://phab.calblueprint.org) and authenticate with GitHub. Now, you'll need a Phab admin to activate your account. Your PL should already be an admin, so ask them to activate it for you.

### Step 3: Install Phabricator certificate
In your project directory (which your PL should have already configured to work with Phabricator properly), run the following:

	arc install-certificate

This should print a URL to your terminal. Follow the link, copy the code given, and paste it back in your terminal.

### Step 4: Configure local repo git conventions
Luckily, this step is automated. Navigate to the root of your repo and copy/paste the following into your terminal to curl and run an automated script that will set up your repo with some goodies that should streamline your workflow:

	curl https://raw.githubusercontent.com/calblueprint/phabricator-setup/master/bin/bp-phab-dev-setup.py > bp-phab-dev-setup.py && python bp-phab-dev-setup.py && (yes | rm -f bp-phab-dev-setup.py)

This script does the following automagically:

- Configures a git hook on `pre-commit`, which disables committing to master.
- Configures a git hook on `pre-push`, which disables pushing to master.
- Sets up a custom commit message template which defaults to adding your PL and teammates as Reviewer and CCs, respectively.
- Configures a git hook on `prepare-commit-msg` to disable committing with `-m`, in order for git to pick up the aforementioned commit template.
- Sets up your repo to automatically `rebase` on `git pull`.
- Configures `arc vdiff`, an alias for `arc diff --verbatim`.

### Step 5: Voila!
You should be configured to push diffs for code review onto Phabricator, yay! Read the next section to get a feel for the Phabricator workflow.

Developer Workflow
----
Phabricator best practice is to do all your work in branches. You do no development in the master branch; that is just a staging branch to push upstream (to GitHub).
Some of these rules are stricly enforced by the above configuration you did on your local repo.

1. When you want to start work on a new feature or change, create a local branch:

		git checkout -b cool-new-feature

2. Make a bunch of changes, and commit them as normal:

		git commit

3. When you're ready for a review, run:

		arc vdiff

	The aforementioned automated script should have set up this arc alias for you. We use `arc vdiff` instead of `arc diff` because we want to explicitly keep the format of our commit template.
	- **Super useful:** If you'd like to preview your diff before actually submitting it for review, use `arc diff --preview` instead!

4. Often, your PL will give you feedback on your review that will prompt you to make changes before you can push to master.  Make the changes/fixes as normal in your branch, and then use `git commit --amend` to amend your previous git commit. (This is normally bad GitHub practice, but becomes very useful and actually preferred when using Phabricator.)  Then, run `arc vdiff`. Your editor should open up with a message indicating that your are making a revision to an _existing_ Phab diff.
	>
	- If you need to force `arc` to assign the new commits to the correct Phab revision ID, use `arc diff --update <revision id>`
	- If you don't need to change your commit message on amend, you can use the `--no-edit` flag to skip editing it.

5. When you are ready to push, you'll want to rebase your changes into the master branch and do a git push from master up to GitHub. (See the note below on rebasing.) You can do this in one step, which will also update your commit message with Phabricator metadata: `arc land`
	- If you want to be explicit, you can run `arc land <to-branch>`

	> **Rebasing:** Phabricator projects should be set up to `rebase` instead of `merge` by default; this should have been set up by the aforemention automated script. Rebasing gives the illusion of a much cleaner commit history. Ask your PL to clarify the difference between `merge` and `rebase`, you should become somewhat familiar with the two.

If other people have committed changes that you want to incorporate into your branch (perhaps a bugfix that you need), you can just do `git pull --rebase` in your feature branch (or simply `git pull` if your repo has set up rebase by default).  Phabricator will do the right thing in ignoring these not-your changes.

See the Phabricator authors' workflow for more in-depth, detailed info [here](https://secure.phabricator.com/w/guides/arcanist_workflows/).


### Summary
	git checkout -b <feature branch>
	<edit edit edit>
	git commit
	arc vdiff

	<edit based on review feedback>
	git commit
	arc vdiff

	<maybe run git pull if you want some updates>
	<edit + commit + arc diff some more>

	arc land

(PLs) Project Setup
----
Read this section if you're a PL setting up your project with Phabricator.

### Step 1: Make an admin Phabricator account
> **NOTE:** Make sure that you've already authenticated an `@berkeley.edu` account with your GitHub before proceeding!

Go to [phab.calblueprint.org](http://phab.calblueprint.org) and authenticate with GitHub. Ask me (Aleks) or someone else that already has admin access to activate your account and give you admin privilege. You'll need admin privilege in order to activate your devs later.

### Step 2: Add an `.arcconfig` file to your project's repo.
(This part assumes you already have a GitHub repo.)
Either copy the file in this repo into the root directory of your project's repo, or make a new blank `.arcconfig` file pointing to our Phab.

Later on, you'll probably want to add linters and unit test engines to your `.arcconfig`. This lets you run lint and unit tests before making a Phab diff (which is awesome, because we can enforce good style and not deal with Hound). More information on this [here](https://secure.phabricator.com/book/phabricator/article/arcanist_new_project/).

> TODO(aleks): Write an actual guide for the above.

### Step 3: Install Phabricator certificate
After setting up the `.arcconfig` correctly, run the following:

	arc install-certificate

This should print a URL to your terminal. Follow the link, copy the code given, and paste it back in your terminal.

### Step 4: Configure local repo git conventions
See Step 4 of the Developer setup.

### Step 5: ???
### Step 6: Profit!
Prepare to enter code-review ~~hell~~ heaven!

**IMPORTANT:**

- Make sure your devs have git >= 2.0 installed!
- Make _absolute_ sure that all of your devs have curled and run the automated set-up script we've provided. There could be serious confusion otherwise.

This way, no dev can accidentally spoil your ~~beautiful~~ linear history.
