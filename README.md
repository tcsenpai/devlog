# Devlog

Devlog is a powerful tool that automatically generates (b)log posts from your Git commit history, providing a natural language summary of your development progress.

## Description

Devlog retrieves all the commit messages in a repository (local or remote), groups them by customizable time periods, and generates blog posts in natural language. This tool is perfect for developers who want to maintain a development log or changelog without the manual effort of writing blog posts.

## Features

- Supports both local and remote Git repositories
- Customizable time periods for grouping commits
- Natural language generation for readable blog posts
- Output formats: Markdown and HTML

## Installation and usage

This project uses [uv](https://github.com/astral-sh/uv) to manage the environment and dependencies.
Please [install it](https://github.com/astral-sh/uv) first.

Once you have uv installed, you can install the dependencies with following commands:

```bash
uv venv
```

## Usage

```bash
uv run src/devlog/__init__.py
```

Alternatively, you can skip the virtual environment and run the script directly with:

```bash
pip install -r requirements.txt
python src/devlog/__init__.py
```

## Configuration

Create a `.env` file in the root directory by copying the `env.example` file and set the following environment variables:

```bash
OLLAMA_URL=<your-local-ollam-url>
GIT_REPO=<your-repo-path-or-url>
GIT_TOKEN=<your-git-token>
DEFAULT_BRANCH=<your-default-branch>
GROUP_COMMITS_DAYS=<number-of-days-to-group-commits>
```

## License

This project is licensed under the WTFPL License. See the `LICENSE` file for more details.