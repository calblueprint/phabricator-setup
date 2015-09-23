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

### Step 4: Voila!
You should be configured to push diffs for code review onto Phabricator, yay! Read the next section to get a feel for the Phabricator workflow.

Developer Workflow
----
Phabricator best practice is to do all your work in branches. You do no development in the master branch; that is just a staging branch to push upstream (to GitHub).

1. When you want to start work on a new feature or change, create a local branch:

		git checkout -b cool-new-feature

2. Make a bunch of changes, and commit them as normal:

		git commit

3. When you're ready for a review, run:

		arc diff

	Or, if your PL has helped you set up an alias for Reviewers/CCs, run `arc <alias>`. In either case, fill out the sections and push your diff.
	- **Super useful:** If you'd like to preview your diff before actually submitting it for review, use `arc diff --preview` instead!

4. Often, your PL will give you feedback on your review that will prompt you to make changes before you can push to master.  Make the changes/fixes as normal in your branch, and then commit them when your done.  Then, run `arc diff` (or use your alias). Your editor should open up with a message indicating that your are making a revision to an _existing_ Phab diff.
	> If you need to force arc to assign the new commits to the correct Phab revision ID, use `arc diff --update <revision id>`

5. When you are ready to push, you'll want to rebase your changes into the master branch and do a git push from master up to GitHub. (See the note below on rebasing.) You can do this in one step, which will also update your commit message with phabricator metadata: `arc land`
	- If you want to be explicit, you can run `arc land <to-branch>`
	- If you accidentally did your changes in master instead of a branch, run `arc amend && git push` rather than `arc land`

	> **Rebasing:** Phabricator projects should be set up to `rebase` instead of `merge` by default; this should be set in your project repo's local `.gitconfig`. Rebasing gives the illusion of a much cleaner commit history. Ask your PL to clarify the difference between `merge` and `rebase`, you should become somewhat familiar with the two.

If other people have committed changes that you want to incorporate into your branch (perhaps a bugfix that you need), you can just do `git pull --rebase` in your feature branch (or simply `git pull` if your repo has set up rebase by default).  Phabricator will do the right thing in ignoring these not-your changes.

See the Phabricator authors' workflow for more in-depth, detailed info [here](https://secure.phabricator.com/w/guides/arcanist_workflows/).


### Summary
	git checkout -b <feature branch>
	<edit edit edit>
	git commit
	arc diff

	<edit based on review feedback>
	git commit
	arc diff

	<maybe run git pull if you want some updates>
	<edit + commit + arc diff some more>

	arc land master

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

### Step 3: ???
### Step 4: Profit!
Prepare to enter code-review ~~hell~~ heaven!

### Step 5 (Highly Recommended): `arc alias`
Chances are, your devs are _always_ going to be 1) adding you (PL) as the main Reviewer, 2) adding all the other devs as CCs. You should help your devs set up `arc diff` aliases to automagically set up these defaults.

For example, if `noah` is a PL for `samz`, `generic`, `qin`, and `aleks` (me), I would add the following alias:

	arc alias bpdiff diff -- --reviewers noah --cc samz,generic,qin

Now, when I use `arc bpdiff`, all of my reviewers/CCs are magically set up.

>
- Consider adding `--verbatim` to your alias too. This uses your commit message as the title of the Phab diff by default, without asking first.
- See `arc alias --help` for more details.

### Step 6 (Highly Recommended): `rebase` by default
Phabricator workflow works much better when feature branches are `rebased` onto master rather than `merged`. In fact, running `arc land` from a feature branch will actually rebase that branch onto master (among other fancy things).

> Rebasing gives the illusion of a much cleaner commit history because it _rewrites_ the history of master to appear to have a perfectly linear history (i.e., no branching and then merging). This makes it much easier to track and _revert_ changes. [Here](https://www.atlassian.com/git/tutorials/merging-vs-rebasing) is a good article describing the difference. **If you're still not sure what the difference is, please ask me (Aleks). It's important that you know `merge` and `rebase` clearly so that you can teach your devs!**

Devs should also use `git pull --rebase` instead of `git pull` so that new upstream changes are _rebased_ onto their local branch, as opposed to merged in. You (PL) should instruct your devs to configure their local repos to rebase on `git pull` (with no `--rebase` flag) by default: have them run the following in their local repo:

    git config pull.rebase true

> **IMPORTANT:** Make sure your devs have git >= 2.0 installed!

This way, no dev can accidentally spoil your ~~beautiful~~ linear history.
