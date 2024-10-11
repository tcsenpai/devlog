import os
import shutil
from git import Repo, GitCommandError
from git.exc import InvalidGitRepositoryError
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import json
from dateutil.parser import parse
from dateutil.tz import tzutc

logger = logging.getLogger(__name__)

class GitOperations:
    def __init__(self, repo_path_or_url='.', token=None):
        self.repo_path_or_url = os.getenv('REPO_PATH_OR_URL', repo_path_or_url)
        self.token = os.getenv('GIT_TOKEN', token)
        self.temp_dir = None
        self.commits = []
        self.default_branch = os.getenv('DEFAULT_BRANCH', 'main')
        self.cache_file = os.path.join(os.getcwd(), 'commit_cache.json')
        self.commit_cache = self._load_cache()
        self.skip_processed = os.getenv('SKIP_PROCESSED_COMMITS', 'false').lower() == 'true'

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.commit_cache, f)

    def elaborate_commit(self, commit):
        if commit.hexsha in self.commit_cache:
            return self.commit_cache[commit.hexsha]

        elaborated_commit = {
            'hexsha': commit.hexsha,
            'author': str(commit.author),
            'date': commit.committed_datetime.isoformat(),
            'message': commit.message.strip()
        }

        self.commit_cache[commit.hexsha] = elaborated_commit
        self._save_cache()
        return elaborated_commit

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
                self.commits.append(self.elaborate_commit(commit))
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

    def group_commits_by_days(self, days=None, start_date=None, end_date=None):
        if days is None:
            days = int(os.getenv('GROUP_COMMITS_DAYS', 30))

        if not self.commits:
            self.list_commits()  # Ensure commits are loaded

        grouped_commits = defaultdict(list)
        
        # Convert start_date and end_date to UTC aware datetimes
        if start_date:
            start_date = start_date.replace(tzinfo=tzutc())
        if end_date:
            end_date = end_date.replace(tzinfo=tzutc())

        # Filter commits based on date range and skip processed commits if enabled
        filtered_commits = []
        for commit in self.commits:
            commit_date = parse(commit['date']).replace(tzinfo=tzutc())
            if (start_date is None or commit_date >= start_date) and \
               (end_date is None or commit_date <= end_date):
                if not self.skip_processed or commit['hexsha'] not in self.commit_cache:
                    filtered_commits.append(commit)
                    if self.skip_processed:
                        self.commit_cache[commit['hexsha']] = True
        
        # Sort commits by date (oldest first)
        sorted_commits = sorted(filtered_commits, key=lambda c: c['date'])
        
        if not sorted_commits:
            return {}

        # Group commits by days
        current_date = parse(sorted_commits[0]['date']).replace(tzinfo=tzutc()).date()
        end_group_date = current_date + timedelta(days=days)
        group = []

        for commit in sorted_commits:
            commit_date = parse(commit['date']).replace(tzinfo=tzutc()).date()
            if commit_date <= end_group_date:
                group.append(commit)
            else:
                grouped_commits[f"{current_date} to {end_group_date}"] = group
                current_date = commit_date
                end_group_date = current_date + timedelta(days=days)
                group = [commit]

        # Add the last group
        if group:
            grouped_commits[f"{current_date} to {end_group_date}"] = group

        # Save the updated cache
        if self.skip_processed:
            self._save_cache()

        return dict(grouped_commits)

    def delete_cache(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            logger.info(f"Deleted cache file: {self.cache_file}")
        self.commit_cache = {}