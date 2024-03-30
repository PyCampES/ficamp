# Contributing

## Requirements

- `git`: [installation](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- `poetry`: [installation](https://python-poetry.org/docs/#installation)

## Local development

Create a Fork

Create a new branch with
```sh
git switch -c feat-my-new-feat
```

Initialize repository

```sh
python -m venv .venv
./scripts/install
```

Add your changes with tests

Format the code

```sh
./scripts/format
```

Run lints and tests

```sh
./scripts/test
./scripts/lint
```

Push your branch

```sh
git push origin feat-my-new-feat
```
