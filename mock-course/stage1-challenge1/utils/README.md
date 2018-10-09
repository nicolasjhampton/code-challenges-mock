# Python Code Challenge Utilities

This repo is intended to be used as a `git subtree` into specific [Python Code Challenges](https://github.com/treehouse/code-challenges-python).

## Sharing
This repo is meant to be a collection of shared Python tools.

Add this repository as a remote

```
git remote add utils https://github.com/treehouse/code-challenges-python-utilities
``` 



## Using as a subtree
Git subtrees are pretty handy.  To "install" it, create a new challenge and then use the following command to add it:

To add the repo as a shared resource
```
# The first 'utils' in the path is the name you'd like the directory called
# The second 'utils' at the end there is the remote origin 
git subtree add --prefix=path/to/your/code/utils --squash utils master
```

And to get the latest version
```
# The first 'utils' in the path is the name you'd like the directory called
# The second 'utils' at the end there is the remote origin 
git subtree pull --prefix=path/to/your/code/utils --squash utils master
```
