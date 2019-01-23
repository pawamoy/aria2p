# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v0.2.0](https://github.com/pawamoy/aria2p/tags/v0.2.0) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.7...v0.2.0)) - 2019-01-23

Version 0.2.0 adds subcommands to the CLI tool. The package now also provides documentation and tests.
Various improvements and fixes. Status is still alpha, things might break!

### Added
- Add subcommands to CLI ([93821cc](https://github.com/pawamoy/aria2p/commit/93821cc672e062554c3aa508e8dc490aab73c518)).

### Fixed
- Fix Download following API refactor ([bf1e1b7](https://github.com/pawamoy/aria2p/commit/bf1e1b700043cef8ff22ef56e672c79cf4b4459b)).
- Fix encoding torrent content to base64/utf-8 ([a17eb92](https://github.com/pawamoy/aria2p/commit/a17eb92a6050b0dd007b74d47fb13cb6ecc21b8a)).

## [v0.1.7](https://github.com/pawamoy/aria2p/tags/v0.1.7) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.6...v0.1.7)) - 2018-12-28

### Fixed
- Fix specifier for Python version (allow 3.6+) ([f451df9](https://github.com/pawamoy/aria2p/commit/f451df91ac76430543a990816019324acfbc67bb)).
  See issue [GH-1](https://github.com/pawamoy/aria2p/issues/1).


## [v0.1.6](https://github.com/pawamoy/aria2p/tags/v0.1.6) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.5...v0.1.6)) - 2018-12-26

### Added
- Add methods to Download to improve usability ([5fe4649](https://github.com/pawamoy/aria2p/commit/5fe4649d81eb8101e99e34145fe137284397dbe6)).
- Add refetch method for download objects ([c87e752](https://github.com/pawamoy/aria2p/commit/c87e7521987a5d24d180fe7aabf0d850d05bb0c2)).
- Add upload speed to display ([5c8be6c](https://github.com/pawamoy/aria2p/commit/5c8be6cda8951b5b4b959404a0c3999b5f71d522)).

### Misc
- Handle return code and exceptions better ([14f47f8](https://github.com/pawamoy/aria2p/commit/14f47f83b29eab547b64010de1e14366e13b2072)).
- Improve JSONRPC errors messages, use defaults ([a3692dc](https://github.com/pawamoy/aria2p/commit/a3692dce1ae76ed02f8f635a53a47bf513726b48)).
- Write documentation ([f5c9ffd](https://github.com/pawamoy/aria2p/commit/f5c9ffd3fb0b1094d90979b278f7e1990178d07f)).


## [v0.1.5](https://github.com/pawamoy/aria2p/tags/v0.1.5) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.4...v0.1.5)) - 2018-12-20

### Misc
- Improve basic display ([84ae386](https://github.com/pawamoy/aria2p/commit/84ae386de0115d4b8ea49b5f5053262ee78aa175)).


## [v0.1.4](https://github.com/pawamoy/aria2p/tags/v0.1.4) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.3...v0.1.4)) - 2018-12-20

### Added
- Add download speed and eta to display ([1dd23bc](https://github.com/pawamoy/aria2p/commit/1dd23bcc927a1c8c3bd1ce7fbb83bdf65703fbe4)).

### Fixed
- Fix error handling in client.post ([7f9e8aa](https://github.com/pawamoy/aria2p/commit/7f9e8aa4f00a5c96755726d5d5521caf96339000)).

### Misc
- Use dynamic get/set attr for options ([fa0b962](https://github.com/pawamoy/aria2p/commit/fa0b96277175c5267f1e7ed27c8143cb4f65ef14)).
- Use properties ([6efe3a6](https://github.com/pawamoy/aria2p/commit/6efe3a6774878a0ab2fbdfb6f70991841e006fcb)).


## [v0.1.3](https://github.com/pawamoy/aria2p/tags/v0.1.3) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.0...v0.1.3)) - 2018-12-17

### Misc
- Various tweaks and improvements for packaging the application.


## [v0.1.0](https://github.com/pawamoy/aria2p/tags/v0.1.0) ([compare](https://github.com/pawamoy/aria2p/compare/878497bb3eacfdd6e385e33470a4b99d2df3d3bd...v0.1.0)) - 2018-12-17

### Added
- Add pyproject.toml for black configuration ([dacb85e](https://github.com/pawamoy/aria2p/commit/dacb85e3c9b0e94f4816f8be5cfc501693c4e35a)).
- Add README ([683086c](https://github.com/pawamoy/aria2p/commit/683086c32e0411cef0996f17df7ed31a60cbdb12)).

### Misc
- Package with Poetry! ([648d0a5](https://github.com/pawamoy/aria2p/commit/648d0a5b3c68d3a06b5a0f7957b5861e42d7279d)).
- Hello Git(Hub|Lab) ([878497b](https://github.com/pawamoy/aria2p/commit/878497bb3eacfdd6e385e33470a4b99d2df3d3bd)).
