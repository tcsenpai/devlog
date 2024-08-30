import os
import shutil
from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

class GitOperations:
    def __init__(self, repo_path_or_url='.', token=None):
        self.repo_path_or_url = os.getenv('REPO_PATH_OR_URL', repo_path_or_url)
        self.token = os.getenv('GIT_TOKEN', token)
        self.temp_dir = None
        self.commits = []
        self.default_branch = os.getenv('DEFAULT_BRANCH', 'main')

    def list_commits(self):
        if self.repo_path_or_url.startswith('http://') or self.repo_path_or_url.startswith('https://'):
            self._clone_repo()
            repo_path = self.temp_dir
        else:
            repo_path = self.repo_path_or_url
        
        try:
            repo = Repo(repo_path)
            
            if os.path.isdir(repo_path):
                logger.info(f"Accessing repository at {repo_path}")
            
            commits = list(repo.iter_commits(self.default_branch))  # Change 'main' to your default branch name if different
            
            logger.info(f"Found {len(commits)} commits")
            
            for commit in commits:
                self.commits.append(commit)
                print(f"Commit: {commit.hexsha}")
                print(f"Author: {commit.author}")
                print(f"Date: {commit.committed_datetime}")
                print(f"Message: {commit.message}")
                print("-" * 40)
            
        except (GitCommandError, InvalidGitRepositoryError) as e:
            logger.error(f"Error: {e}")
        finally:
            self._cleanup()

    def _clone_repo(self):
        self.temp_dir = os.path.join(os.getcwd(), 'temp_repo')
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        logger.info(f"Cloning remote repository to {self.temp_dir}")
        
        if self.token:
            parts = self.repo_path_or_url.split('://')
            clone_url = f"{parts[0]}://{self.token}@{parts[1]}"
        else:
            clone_url = self.repo_path_or_url
        
        try:
            Repo.clone_from(clone_url, self.temp_dir)
        except GitCommandError as e:
            logger.error(f"Failed to clone repository: {e}")
            raise

    def _cleanup(self):
        if self.temp_dir and os.path.exists(self.temp_dir):
            logger.info(f"Cleaning up temporary directory {self.temp_dir}")
            shutil.rmtree(self.temp_dir)

    def group_commits_by_days(self, days=None):
        if days is None:
            days = int(os.getenv('GROUP_COMMITS_DAYS', 30))

        if not self.commits:
            self.list_commits()  # Ensure commits are loaded

        grouped_commits = defaultdict(list)
        
        # Sort commits by date (oldest first)
        sorted_commits = sorted(self.commits, key=lambda c: c.committed_datetime)
        
        if not sorted_commits:
            return []

        # Get the date of the oldest commit
        current_date = sorted_commits[0].committed_datetime.date()
        end_date = current_date + timedelta(days=days)
        group = []

        for commit in sorted_commits:
            commit_date = commit.committed_datetime.date()
            if commit_date <= end_date:
                group.append(commit)
            else:
                grouped_commits[f"{current_date} to {end_date}"] = group
                current_date = commit_date
                end_date = current_date + timedelta(days=days)
                group = [commit]

        # Add the last group
        if group:
            grouped_commits[f"{current_date} to {end_date}"] = group

        return dict(grouped_commits)