# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v0.2.4](https://github.com/pawamoy/aria2p/releases/tag/v0.2.4) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.3...v0.2.4)) - 2019-08-09

### Fixed
- Don't cause exception when download name is not ready ([a0da184](https://github.com/pawamoy/aria2p/commit/a0da1849e26ce71092a34f042af870afcb5abec9)).

## [v0.2.3](https://github.com/pawamoy/aria2p/releases/tag/v0.2.3) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.2...v0.2.3)) - 2019-08-07

### Added
- Add some aliases ([be454b2](https://github.com/pawamoy/aria2p/commit/be454b273f29b84e67ec48ef07849d28d3caf678)).
- Add file moving and purge ability to Download class ([9d821c0](https://github.com/pawamoy/aria2p/commit/9d821c0f492ec39477691e30c1d0bc1d8d882c12)).
- Add move/copy files methods to API ([380b09a](https://github.com/pawamoy/aria2p/commit/380b09afb639ae1de96bf810bbea5e49239a88aa)).
- Combine -all commands to normal ones, with -a, --all option, keep old ones as deprecated ([944d6c2](https://github.com/pawamoy/aria2p/commit/944d6c268818d0af75ec7e23b5dc2b07c6ba6892) and [f41f98a](https://github.com/pawamoy/aria2p/commit/f41f98ab759db51c8a4fe17c12fec51674c16569)).
- Improve exceptions handling with `loguru` ([c75d991](https://github.com/pawamoy/aria2p/commit/c75d9911698075b0cff774c4ef7d4b5cf8ede623)).

### Fixed
- Add missing aliases in subcommands dictionary ([be454b2](https://github.com/pawamoy/aria2p/commit/be454b273f29b84e67ec48ef07849d28d3caf678)).
- Cast return value in get method with argument ([d2bca2b](https://github.com/pawamoy/aria2p/commit/d2bca2b9241aa1e6b07932ae66fac0a326b0018d)).
- Pass exceptions when download result cannot be removed ([f346fe5](https://github.com/pawamoy/aria2p/commit/f346fe55d94817b2ce6a459d9db7e72f3785352b)).

## [v0.2.2](https://github.com/pawamoy/aria2p/releases/tag/v0.2.2) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.1...v0.2.2)) - 2019-02-21

### Documented
- Add configuration documentation ([c3643ea](https://github.com/pawamoy/aria2p/commit/c3643ea9e26edb8db33c019cf5059fb292232c2a)).
- Add information in README ([c7f4378](https://github.com/pawamoy/aria2p/commit/c7f4378d062aa0d2d13de01df494153e371d2d1c)).
- Add credits ([dc607fe](https://github.com/pawamoy/aria2p/commit/dc607fed97f8ca2ad43f31d10a04a65d0c1a0471), [8ec1f58](https://github.com/pawamoy/aria2p/commit/8ec1f58ed306d11f0501a60f701158d259be049a), [f89081c](https://github.com/pawamoy/aria2p/commit/f89081c8b2c248cd6fd51a59cb43d4306e64c646)).

### Fixed
- Fix format of secret in params ([8ff9075](https://github.com/pawamoy/aria2p/commit/8ff907588c7a87e96c1f99c3f4fd09c7e312be2b)). Issue [GH-4](https://github.com/pawamoy/aria2p/issues/4).
- Print warning when connection to remote fails ([ab9a604](https://github.com/pawamoy/aria2p/commit/ab9a6040e3f02fbaf3a4814532dd1b4b36b73dc2)). Issue [GH-2](https://github.com/pawamoy/aria2p/issues/2).

## [v0.2.1](https://github.com/pawamoy/aria2p/releases/tag/v0.2.1) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.0...v0.2.1)) - 2019-01-23

### Fixed
- Fix commands not being mapped properly ([4c286fc](https://github.com/pawamoy/aria2p/commit/4c286fcd8c9702a97f4bbdec7bbfab8c00672265)).

## [v0.2.0](https://github.com/pawamoy/aria2p/releases/tag/v0.2.0) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.7...v0.2.0)) - 2019-01-23

Version 0.2.0 adds subcommands to the CLI tool. The package now also provides documentation and tests.
Various improvements and fixes. Status is still alpha, things might break!

### Added
- Add subcommands to CLI ([93821cc](https://github.com/pawamoy/aria2p/commit/93821cc672e062554c3aa508e8dc490aab73c518)).

### Fixed
- Fix Download following API refactor ([bf1e1b7](https://github.com/pawamoy/aria2p/commit/bf1e1b700043cef8ff22ef56e672c79cf4b4459b)).
- Fix encoding torrent content to base64/utf-8 ([a17eb92](https://github.com/pawamoy/aria2p/commit/a17eb92a6050b0dd007b74d47fb13cb6ecc21b8a)).

## [v0.1.7](https://github.com/pawamoy/aria2p/releases/tag/v0.1.7) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.6...v0.1.7)) - 2018-12-28

### Fixed
- Fix specifier for Python version (allow 3.6+) ([f451df9](https://github.com/pawamoy/aria2p/commit/f451df91ac76430543a990816019324acfbc67bb)).
  See issue [GH-1](https://github.com/pawamoy/aria2p/issues/1).


## [v0.1.6](https://github.com/pawamoy/aria2p/releases/tag/v0.1.6) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.5...v0.1.6)) - 2018-12-26

### Added
- Add methods to Download to improve usability ([5fe4649](https://github.com/pawamoy/aria2p/commit/5fe4649d81eb8101e99e34145fe137284397dbe6)).
- Add refetch method for download objects ([c87e752](https://github.com/pawamoy/aria2p/commit/c87e7521987a5d24d180fe7aabf0d850d05bb0c2)).
- Add upload speed to display ([5c8be6c](https://github.com/pawamoy/aria2p/commit/5c8be6cda8951b5b4b959404a0c3999b5f71d522)).

### Misc
- Handle return code and exceptions better ([14f47f8](https://github.com/pawamoy/aria2p/commit/14f47f83b29eab547b64010de1e14366e13b2072)).
- Improve JSONRPC errors messages, use defaults ([a3692dc](https://github.com/pawamoy/aria2p/commit/a3692dce1ae76ed02f8f635a53a47bf513726b48)).
- Write documentation ([f5c9ffd](https://github.com/pawamoy/aria2p/commit/f5c9ffd3fb0b1094d90979b278f7e1990178d07f)).


## [v0.1.5](https://github.com/pawamoy/aria2p/releases/tag/v0.1.5) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.4...v0.1.5)) - 2018-12-20

### Misc
- Improve basic display ([84ae386](https://github.com/pawamoy/aria2p/commit/84ae386de0115d4b8ea49b5f5053262ee78aa175)).


## [v0.1.4](https://github.com/pawamoy/aria2p/releases/tag/v0.1.4) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.3...v0.1.4)) - 2018-12-20

### Added
- Add download speed and eta to display ([1dd23bc](https://github.com/pawamoy/aria2p/commit/1dd23bcc927a1c8c3bd1ce7fbb83bdf65703fbe4)).

### Fixed
- Fix error handling in client.post ([7f9e8aa](https://github.com/pawamoy/aria2p/commit/7f9e8aa4f00a5c96755726d5d5521caf96339000)).

### Misc
- Use dynamic get/set attr for options ([fa0b962](https://github.com/pawamoy/aria2p/commit/fa0b96277175c5267f1e7ed27c8143cb4f65ef14)).
- Use properties ([6efe3a6](https://github.com/pawamoy/aria2p/commit/6efe3a6774878a0ab2fbdfb6f70991841e006fcb)).


## [v0.1.3](https://github.com/pawamoy/aria2p/releases/tag/v0.1.3) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.0...v0.1.3)) - 2018-12-17

### Misc
- Various tweaks and improvements for packaging the application.


## [v0.1.0](https://github.com/pawamoy/aria2p/releases/tag/v0.1.0) ([compare](https://github.com/pawamoy/aria2p/compare/878497bb3eacfdd6e385e33470a4b99d2df3d3bd...v0.1.0)) - 2018-12-17

### Added
- Add pyproject.toml for black configuration ([dacb85e](https://github.com/pawamoy/aria2p/commit/dacb85e3c9b0e94f4816f8be5cfc501693c4e35a)).
- Add README ([683086c](https://github.com/pawamoy/aria2p/commit/683086c32e0411cef0996f17df7ed31a60cbdb12)).

### Misc
- Package with Poetry! ([648d0a5](https://github.com/pawamoy/aria2p/commit/648d0a5b3c68d3a06b5a0f7957b5861e42d7279d)).
- Hello Git(Hub|Lab) ([878497b](https://github.com/pawamoy/aria2p/commit/878497bb3eacfdd6e385e33470a4b99d2df3d3bd)).
