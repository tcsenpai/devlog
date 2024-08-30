import argparse
import os
from dotenv import load_dotenv
import logging
from devlog.libs.gitoperations import GitOperations
from devlog.libs.ollamator import Ollamator
from devlog.libs.ghostwriter import write_weblog

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # Load environment variables from .env file
    load_dotenv()

    parser = argparse.ArgumentParser(description="List commits from a Git repository and process text with Ollama.")
    parser.add_argument("repo", nargs='?', default=None, help="Path to local repository or URL of remote repository")
    parser.add_argument("--token", help="Authentication token for remote repositories")
    parser.add_argument("--ollama-url", help="URL of the Ollama instance")
    args = parser.parse_args()

    # Prioritize command line arguments, then .env, then default values
    repo = args.repo or os.getenv('GIT_REPO') or '.'
    token = args.token or os.getenv('GIT_TOKEN')
    ollama_url = args.ollama_url or os.getenv('OLLAMA_URL') or 'http://localhost:11434'

    # Process Git repository
    git_ops = GitOperations(repo, token)
    #git_ops.list_commits()
    grouped_commits = git_ops.group_commits_by_days(14)

    # Initialize OllamaProcessor (but not using it yet)
    ollama_processor = Ollamator(ollama_url)

    # Process each commit message chunk
    total_chunks = len(grouped_commits)
    print(f"Total chunks: {total_chunks}")
    for date_range, commits in grouped_commits.items():
        total_commits = len(commits)
        commit_messages = ""
        for commit in commits:
            commit_messages += f"{commit.hexsha[:7]} - {commit.message.strip()}\n"
        print(commit_messages)
        print("\n")
        print(f"Total commits: {total_commits}")
        print(f"Commits from {date_range}:")
        print("- Processing...")

        devlog = ollama_processor.process_text(f"Date range: {date_range}\n\n{commit_messages}")
        
        # Prepare the weblog data
        weblog_data = {
            'date_range': date_range,
            'title': f"Development Update for {date_range}",
            'content': devlog
        }
        
        # Write the weblog
        write_weblog(weblog_data, 'output')
        
        print(devlog)
        print("\n == DEVLOG POST END == \n")
    
    #try:
    #    for commit in git_ops.commits:
    #        ollama_processor.process_text(commit.message)
    #except KeyboardInterrupt:
    #    logger.info("Interrupted by user")
    #except Exception as e:
    #    logger.error(f"Error processing commit message: {e}")

if __name__ == "__main__":
    main()