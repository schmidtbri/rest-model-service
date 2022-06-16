# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2022-06-16

## Added

- Added exception handler for validation errors.

## Changed

- Changed Error schema "message" field to "messages" and changed type from str to List[str]

## [0.3.0] - 2022-05-24

## Added

- Added ability to load logging configuration through the YAML configuration file.

## Changed

- The application used to raise a warning when it could not find the YAML configuration file and created an empty 
application. Now a warning is raised but no application is created.

## [0.2.1] - 2022-05-10

## Fixed

- Removed debugging statement from root of package.
- Removed newline character from version string.

## [0.2.0] - 2022-02-24

### Added

- Support for MLModelDecorator instances that wrap MLModel instances.
