import os
import requests
from dotenv import load_dotenv
from app.linkedin_service import LinkedInService

load_dotenv()

class MCPIntegration:
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_user = os.getenv("GITHUB_USER")
        self.linkedin_service = LinkedInService()
        self.default_linkedin_user = "dhurkeshb"

    def get_github_context(self):
        """Get GitHub user context"""
        headers = {"Authorization": f"Bearer {self.github_token}"}
        
        # Get user repositories
        repos_response = requests.get(
            f"https://api.github.com/users/{self.github_user}/repos",
            headers=headers
        )
        repos = [repo["name"] for repo in repos_response.json()] if repos_response.ok else []
        
        # Get user activity
        events_response = requests.get(
            f"https://api.github.com/users/{self.github_user}/events",
            headers=headers
        )
        events = [event["type"] for event in events_response.json()[:5]] if events_response.ok else []
        
        return {
            "username": self.github_user,
            "repositories": repos,
            "recent_activity": events
        }

    def get_linkedin_context(self, username=None):
        """Get LinkedIn context for the specified or default user"""
        username = username or self.default_linkedin_user
        try:
            # Fetch and save posts
            self.linkedin_service.fetch_and_save_posts(username)
            
            # Get saved posts
            posts_data = self.linkedin_service.get_saved_posts(limit=5)
            posts = posts_data.get("posts", [])
            
            # Get top posts
            top_posts = self.linkedin_service.get_top_posts(metric="Like Count", top_n=3)
            
            # Format posts content
            recent_posts_content = []
            for post in posts:
                recent_posts_content.append(
                    f"Post: {post.get('Text', '')}\n"
                    f"Likes: {post.get('Like Count', 0)}\n"
                    f"Posted on: {post.get('Posted Date', '')}\n"
                )
            
            top_posts_content = []
            for post in top_posts.get("posts", []):
                top_posts_content.append(
                    f"Top Post: {post.get('Text', '')}\n"
                    f"Likes: {post.get('Like Count', 0)}\n"
                    f"Posted on: {post.get('Posted Date', '')}\n"
                )
            
            return {
                "username": username,
                "recent_posts": posts,
                "top_posts": top_posts.get("posts", []),
                "total_posts": posts_data.get("total_posts", 0),
                "recent_posts_content": recent_posts_content,
                "top_posts_content": top_posts_content
            }
        except Exception as e:
            print(f"Error getting LinkedIn context: {str(e)}")
            return {
                "username": username,
                "recent_posts": [],
                "top_posts": [],
                "total_posts": 0,
                "recent_posts_content": [],
                "top_posts_content": []
            }

    def get_combined_context(self):
        """Get combined context from both GitHub and LinkedIn"""
        github_context = self.get_github_context()
        linkedin_context = self.get_linkedin_context()

        context_str = (
            f"GitHub User: {github_context['username']}\n"
            f"Repositories: {', '.join(github_context['repositories'])}\n"
            f"Recent Activity: {', '.join(github_context['recent_activity'])}\n\n"
            f"LinkedIn User: {linkedin_context['username']}\n"
            f"Total Posts: {linkedin_context['total_posts']}\n"
            f"Recent Posts: {len(linkedin_context['recent_posts'])}\n"
            f"Top Posts: {len(linkedin_context['top_posts'])}\n\n"
            f"Recent Posts Content:\n"
            f"{''.join(linkedin_context['recent_posts_content'])}\n"
            f"Top Posts Content:\n"
            f"{''.join(linkedin_context['top_posts_content'])}\n"
        )

        return context_str 