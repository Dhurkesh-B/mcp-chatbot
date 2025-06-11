import os
from typing import List, Dict
import json

class RAGIntegration:
    def __init__(self, file_path: str = "info.txt"):
        self.file_path = file_path
        self.content = self._load_content()
        self.sections = self._parse_sections()

    def _load_content(self) -> str:
        """Load content from the info.txt file"""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            return ""
        except Exception as e:
            print(f"Error loading content: {str(e)}")
            return ""

    def _parse_sections(self) -> Dict:
        """Parse the content into sections based on headers and natural breaks."""
        sections = {}
        current_section = "general"
        current_content = []
        
        for line in self.content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header (ends with ':' and next line is not empty)
            if line.endswith(':') and not line.startswith(' '):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                    current_content = []
                current_section = line[:-1].lower()
            else:
                current_content.append(line)
        
        # Save the last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
            
        return sections

    def get_context(self) -> str:
        """Get formatted context from all sections."""
        context = []
        
        for section, content in self.sections.items():
            if section != "general":
                context.append(f"{section.upper()}:")
            context.append(content)
            context.append("")  # Add spacing between sections
        
        return "\n".join(context) if context else "No information available."

    def search_content(self, query: str) -> Dict:
        """Search through all sections for relevant information."""
        relevant_info = []
        query_terms = query.lower().split()
        
        # Search in each section
        for section, content in self.sections.items():
            section_matches = []
            
            # Search through each line in the section
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Check if any query term matches
                if any(term in line.lower() for term in query_terms):
                    section_matches.append(line)
            
            # If matches found in this section, add them with section header
            if section_matches:
                if section != "general":
                    relevant_info.append(f"\n{section.upper()}:")
                relevant_info.extend(section_matches)
        
        # If no exact matches, try fuzzy matching
        if not relevant_info:
            for section, content in self.sections.items():
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if line contains any word that's similar to query terms
                    line_words = set(line.lower().split())
                    if any(any(term in word or word in term for word in line_words) for term in query_terms):
                        if section != "general":
                            relevant_info.append(f"\n{section.upper()}:")
                        relevant_info.append(line)
        
        return {
            "found": len(relevant_info) > 0,
            "content": "\n".join(relevant_info) if relevant_info else "No specific information found in the records."
        } 