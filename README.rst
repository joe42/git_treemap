Git Treemap 
===========

Git Treemap visualizes your git repository as an animated treemap. There are three views to choose from: 

1. Simple file view: Shows complete directory with files. Colors, and tile size corresponds to the file's size.
2. Git view: Shows recent commits. Colors correspond to the relative time to the most recent commit. Tile size corresponds to the number of changed lines.
3. Author view: Show recent commits of one particular author. Otherwise like git view.

Here is an example showing the git project started by Linus Torvalds: http://joe42.github.io/git_treemap/

Installation 
--------

To install Git Treemap on Ubuntu do the following::

    sudo apt-get install git
    sudo apt-get install python-setuptools
    sudo easy_install GitPython
    git clone git://github.com/joe42/git_treemap.git

Usage
------------

Change into the cloned directory and start treemap.py with a full path within any git repository::

    cd git_treemap
    python treemap.py /home/yourname/mygitrepository

This will create a file treemap.html with the treemap representation of mygitrepository.
Just view it in your browser.


Notes
------

Warning: Creating the treemap for repositories might take a long time, especially if they are large.
One work around is to create a treemap of a subdirectory within your repository. 
You can also simply delete directories in the repository you do not want to be displayed.

Git Treemap depends on InfoVis JavaScript Toolkit & GitPython.
Thanks to the authors for these great tools.
