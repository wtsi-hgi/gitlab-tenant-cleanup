# Change Log
## 1.3.0 - 2017-02-22
### Added
- Helper to get open port.
- Manager to control temp files.
- Code to help with creating unittests that run the same tests on multiple types.
- Function to help use tests that can either test all classes or just the "latest" one, depending on the setting of an 
environment variable.
- Function to extract version numbers from strings.

## 1.2.0 - 2016-09-19
### Added
- Code to help with using Docker.
- Random string generator.

## 1.1.0 - 2016-06-13
### Added
- Counting lock.
- Exception suppression decorator.
- Support for hosting on PyPI.

### Removed
- Unused JSON serialisation code and subsequent dependency on `hgijson`.

### Changed
- Fixed thread-safety issue in `Metadata` ([#8](https://github.com/wtsi-hgi/python-common/issues/8)).

## 1.0.0 - 2016-04-18
### Added
- First stable release.
