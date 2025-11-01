# Use of Python

If you need any packages installed, always use uv and virual env. Assume this
the end result will be selfcontained git repository that should more or less
work on any system with only uv installed.


# Running bash scripts

The human prefers to see what the scripts are doing. 

If you create any script, include sufficient amount of console printing so that
it is always clear what is going on. Especially for long running tasks. The
nicer the better.

Try not to use background bash tasks as their output is not shown well.

You can use new console windows with tmux inside so that you can get to the
output of the script it there are any errors printed there.

If you are openning a new terminal window, do not use xterm, but rather `zutty
-font firacode -fontize 19` as this is what the human is used to.


