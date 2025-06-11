import os
import requests
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class MCPIntegration:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_username = os.getenv("GITHUB_USER")
        self.headers = {"Authorization": f"Bearer {self.github_token}"}

    def get_github_context(self) -> str:
        """Get GitHub user context including repositories and recent activity."""
        try:
            # Get user repositories
            repos_response = requests.get(
                f"https://api.github.com/users/{self.github_username}/repos",
                headers=self.headers
            )
            repos = [repo["name"] for repo in repos_response.json()] if repos_response.ok else []
            
            # Get user activity
            events_response = requests.get(
                f"https://api.github.com/users/{self.github_username}/events",
                headers=self.headers
            )
            events = [event["type"] for event in events_response.json()[:5]] if events_response.ok else []
            
            return (
                f"GitHub Information:\n"
                f"Username: {self.github_username}\n"
                f"Repositories: {', '.join(repos)}\n"
                f"Recent Activity: {', '.join(events)}\n"
            )
        except Exception as e:
            print(f"Error getting GitHub context: {str(e)}")
            return (
                f"GitHub Information:\n"
                f"Username: {self.github_username}\n"
                f"Repositories: None\n"
                f"Recent Activity: None\n"
            ) 