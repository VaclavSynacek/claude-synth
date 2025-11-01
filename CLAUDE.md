# Use of Python

If you need any packages installed, always use uv and virual env. Assume this
the end result will be selfcontained git repository that should more or less
work on any system with only uv installed.


# Running bash scripts

The human prefers to see what the scripts are doing. You are running in tmux,
so use that to show the scirpt outputs - open a pane to the right from yours,
send scirpts to run there, possibly even long running scripts.

If you create any script, include sufficient amount of console printing so that
it is always clear what is going on. Especially for long running tasks. The
nicer the better.

Try not to use background bash tasks as their output is not shown well. You can
always tail the tmux panes if you need the output for further thinking.



