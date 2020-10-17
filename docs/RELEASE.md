# How to cut a release

1) Make code changes
1) Increment version in `setup.py`
1) Run black formatter with `make black`
1) Run unit tests with `make test`
1) Merge PR into master / Commit to master
1) Tag version in git with `git tag vX.X.X` & `git push --tags`
1) Clean up previous distribuionts with `make clean`
1) Publish to testpypi with `make publish-test` (optional)
1) Publish to pypi with `make publish-live`
