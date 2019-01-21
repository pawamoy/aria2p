# Contributing
Contributions are welcome, and they are greatly appreciated!

Every little bit helps, and credit will always be given.

## Types of Contributions

### Bug Reports, Feature Requests, and Feedback
Create a new [GitHub issue][1] or [GitLab issue][2]! Try to be as descriptive as possible.

### Bug Fixes, New Features and Documentation
This project is developed using [`poetry`](https://github.com/sdispater/poetry).
Follow the recommended installation method:

```bash
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```

1. Fork the repository [on GitHub][3] or [on GitLab][4];
1. Clone it on your machine;
1. Go into the directory, and run `poetry install` to setup the development environment;
1. Create a new branch with `git checkout -b bug-fix-or-feature-name`;
1. Code!
1. **Write tests. Run them all.** The commands to run the tests are:
   ```bash
   poetry run pytest  # to run all tests sequentially
   poetry run pytest -v  # to print one test per line
   poetry run pytest -n 4  # to run tests in parallel (4 workers)
   poetry run pytest tests/test_api.py  # to run tests in a specific file
   ```
  
   `pytest` provides the `-k` option to select tests based on their names:
   
   ```bash
   poetry run pytest -k "api and remove"
   poetry run pytest -k "utils or stats"
   ``` 
   
   See the [documentation for the `-k` option][5] for more examples.

7. When the tests pass, commit;
8. Push;
9. ...and finally, create a new [pull request][6] / [merge request][7]!
   Make sure to follow the guidelines.

## Merge/Pull Request Guidelines
Make sure to have atomic commits and contextual commit messages!

[Check out this awesome blog post by Chris Beams for more information.][8]

[1]: https://github.com/pawamoy/aria2p/issues/new
[2]: https://gitlab.com/pawamoy/aria2p/issues/new
[3]: https://github.com/pawamoy/aria2p
[4]: https://gitlab.com/pawamoy/aria2p
[5]: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name
[6]: https://github.com/pawamoy/aria2p/compare
[7]: https://gitlab.com/pawamoy/aria2p/compare
[8]: http://chris.beams.io/posts/git-commit/
