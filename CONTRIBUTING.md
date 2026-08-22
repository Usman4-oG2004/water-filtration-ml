# Contributing Guide

Thank you for your interest in contributing to the Water Filtration ML project.

## Branch Strategy

- main — production only, merge via PR from develop
- develop — integration branch, all features merge here first
- feature/<name> — one branch per feature

## How to Contribute

1. Fork or clone the repository
2. Create a feature branch from develop
3. Make your changes with clear commit messages
4. Open a Pull Request into develop
5. Ensure all CI checks pass before requesting review

## Commit Message Format

- feat: new feature
- fix: bug fix
- ci: CI/CD changes
- docs: documentation only
- chore: maintenance

## Code Style

- All Python files must pass Pylint with score 7.0 or above
- Use descriptive variable names
- Add inline comments for non-obvious ML logic
