# Contributing
Contributions are welcome, and they are greatly appreciated!

Every little bit helps, and credit will always be given.

## Types of Contributions

### Bug Reports, Feature Requests, and Feedback
Create a new [GitHub issue][1]! Try to be as descriptive as possible.

### Bug Fixes, New Features and Documentation
This project is developed using [`poetry`](https://github.com/sdispater/poetry).
Follow the recommended installation method:

```bash
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
```

1. Fork the repository [on GitHub][2];
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
   
    See the [documentation for the `-k` option][3] for more examples.

1. When the tests pass, commit;
1. Push;
1. ...and finally, create a new [pull request][4]!
   Make sure to follow the guidelines.

## Merge/Pull Request Guidelines
Make sure to have atomic commits and contextual commit messages!

[Check out this awesome blog post by Chris Beams for more information.][5]

[1]: https://github.com/pawamoy/aria2p/issues/new
[2]: https://github.com/pawamoy/aria2p
[3]: https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name
[4]: https://github.com/pawamoy/aria2p/compare
[5]: http://chris.beams.io/posts/git-commit/
