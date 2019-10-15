# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [v0.4.0](https://github.com/pawamoy/aria2p/releases/tag/v0.4.0) ([compare](https://github.com/pawamoy/aria2p/compare/v0.3.0...v0.4.0)) - 2019-10-13

### Added
- Add interactive interface (top command) (last commit: [d8a2db2](https://github.com/pawamoy/aria2p/commit/d8a2db2b2dba19c42056dbdb854cc6fc1a0b8efc)).
  Run the interactive interface with `aria2p top`. Hit "h" to show help.
  The interface is not finished, but I'm releasing it now to get early feedback.
- API: add option to remove files as well when removing downloads ([981dcc0](https://github.com/pawamoy/aria2p/commit/981dcc015f8baef5b3d2f0230b27376f482442fa)).

### Fixed
- Fix Download.move_up method (it was doing the inverse) ([96a287a](https://github.com/pawamoy/aria2p/commit/96a287ab4e563c27ffb56afbccc8901c02e4a9f2)).

## [v0.3.0](https://github.com/pawamoy/aria2p/releases/tag/v0.3.0) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.5...v0.3.0)) - 2019-10-11

### Added
- Add listen subcommand ([09195ae](https://github.com/pawamoy/aria2p/commit/09195aeb0146d8e3f4108c8fc7b7548485d1417b)).
- Implement notifications listener ([33ee9ae](https://github.com/pawamoy/aria2p/commit/33ee9ae72811a18b4430e5ff163e1df113b209af)).
- Provide function to enable/configure logger ([8620a09](https://github.com/pawamoy/aria2p/commit/8620a0928cdb9def7c661baf819eb4aea8d085c9)).

### Fixed
- Fix API pause_all and resume_all methods ([0bf2209](https://github.com/pawamoy/aria2p/commit/0bf2209553e138387d2597900f2a182275bd0fa5)).


## [v0.2.5](https://github.com/pawamoy/aria2p/releases/tag/v0.2.5) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.4...v0.2.5)) - 2019-08-09

### Fixed
- Use path for name when download is metadata ([d18af50](https://github.com/pawamoy/aria2p/commit/d18af5033d93fbc94b3c9d85e2fbb9e320328747)).


## [v0.2.4](https://github.com/pawamoy/aria2p/releases/tag/v0.2.4) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.3...v0.2.4)) - 2019-08-09

### Fixed
- Don't cause exception when download name is not ready ([604a0ab](https://github.com/pawamoy/aria2p/commit/604a0abb4db3acd6f061449b9667c44861b8843e)).


## [v0.2.3](https://github.com/pawamoy/aria2p/releases/tag/v0.2.3) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.2...v0.2.3)) - 2019-08-08

### Added
- Add some aliases ([14ef63a](https://github.com/pawamoy/aria2p/commit/14ef63afb39b60ee88201857520efd1dc350d410)).
- Add file moving and purge ability to Download class ([08d129a](https://github.com/pawamoy/aria2p/commit/08d129a429874fde313f45720bfd44cfb7ee1b49)).
- Add move/copy files methods to API ([e1d3994](https://github.com/pawamoy/aria2p/commit/e1d3994ed7969ba8a54edb3fe6bbf5cc2e1deb99)).
- Combine -all commands to normal ones, with -a, --all option, keep old ones as deprecated ([e5d287c](https://github.com/pawamoy/aria2p/commit/e5d287c7dfaaffa6c2999d261744f09c7806b5ce) and [939402f](https://github.com/pawamoy/aria2p/commit/939402f62539ef97aea2ffa2db1cc93b48f68d20)).
- Improve exceptions handling with `loguru` ([e0ded18](https://github.com/pawamoy/aria2p/commit/e0ded18c50945f9706bd34e4d021f4ebe030a043)).

### Fixed
- Cast return value in get method with argument ([5ee651a](https://github.com/pawamoy/aria2p/commit/5ee651a17e28502903103959bf1b7b9abd71eb60)).
- Fix Download.name and always initialize struct arguments to empty dictionaries ([874deb9](https://github.com/pawamoy/aria2p/commit/874deb98b0e61f1c5e115253974ca525ba313fdf)).
- Pass exceptions when download result cannot be removed ([9a7659e](https://github.com/pawamoy/aria2p/commit/9a7659e6763173b90f94b0711a65e43aec047c9c)).


## [v0.2.2](https://github.com/pawamoy/aria2p/releases/tag/v0.2.2) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.1...v0.2.2)) - 2019-02-21

### Documented
- Add configuration documentation ([9525743](https://github.com/pawamoy/aria2p/commit/952574341e55d53e6d5657d33cc4f47ffdb1f14e)).
- Add information in README ([840c4b5](https://github.com/pawamoy/aria2p/commit/840c4b5b56470d9966370c184e7af7f8b6a85da0)).
- Add credits ([6900eb2](https://github.com/pawamoy/aria2p/commit/6900eb2d596dea2244601969014442e42b2393c2)).

### Fixed
- Fix format of secret in params ([e01fd9c](https://github.com/pawamoy/aria2p/commit/e01fd9cd6af257cbc0feb5248ce86b1177d7151e)).
- Print warning when connection to remote fails ([57287fb](https://github.com/pawamoy/aria2p/commit/57287fb5ed0436925aea6f75baebdae58907467d)).


## [v0.2.1](https://github.com/pawamoy/aria2p/releases/tag/v0.2.1) ([compare](https://github.com/pawamoy/aria2p/compare/v0.2.0...v0.2.1)) - 2019-01-23

### Fixed
- Fix commands not being mapped properly ([f9a0b29](https://github.com/pawamoy/aria2p/commit/f9a0b29e51520d94494367fccf2486da4c377f3a)).


## [v0.2.0](https://github.com/pawamoy/aria2p/releases/tag/v0.2.0) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.7...v0.2.0)) - 2019-01-23

Version 0.2.0 adds subcommands to the CLI tool. The package now also provides documentation and tests.
Various improvements and fixes. Status is still alpha, things might break!

### Added
- Add subcommands to CLI ([93821cc](https://github.com/pawamoy/aria2p/commit/93821cc672e062554c3aa508e8dc490aab73c518)).

### Fixed
- Fix Download following API refactor ([37f3b71](https://github.com/pawamoy/aria2p/commit/37f3b71ad261b73846855c57f6fb97ff373c6550)).
- Fix encoding torrent content to base64/utf-8 ([a17eb92](https://github.com/pawamoy/aria2p/commit/a17eb92a6050b0dd007b74d47fb13cb6ecc21b8a)).


## [v0.1.7](https://github.com/pawamoy/aria2p/releases/tag/v0.1.7) ([compare](https://github.com/pawamoy/aria2p/compare/v0.1.6...v0.1.7)) - 2018-12-29

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
