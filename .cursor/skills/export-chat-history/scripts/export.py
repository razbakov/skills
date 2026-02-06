#!/usr/bin/env python3
"""
Export Cursor chat history for a project.

Usage:
    python export.py <project-path> <output-dir>
    
Example:
    python export.py /Users/me/Projects/myproject ./history/myproject
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path


def find_project_folder(project_path: str) -> Path:
    """Find the .cursor/projects folder for a given project path."""
    # Convert path to folder name format (slashes become dashes)
    normalized = project_path.rstrip('/').replace('/', '-')
    if normalized.startswith('-'):
        normalized = normalized[1:]
    
    cursor_projects = Path.home() / ".cursor/projects"
    
    # Look for matching folder
    for folder in cursor_projects.iterdir():
        if folder.is_dir() and normalized in folder.name:
            transcripts = folder / "agent-transcripts"
            if transcripts.exists():
                return transcripts
    
    return None


def slugify(text: str, max_len: int = 50) -> str:
    """Convert text to a filename-safe slug."""
    text = text.split('\n')[0][:max_len]
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text.strip().lower())
    return text or "session"


def export_transcripts(transcripts_dir: Path, output_dir: Path) -> int:
    """Export all transcripts to the output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    txt_files = sorted(
        transcripts_dir.glob("*.txt"),
        key=lambda f: f.stat().st_mtime
    )
    
    for txt_file in txt_files:
        mtime = datetime.fromtimestamp(txt_file.stat().st_mtime)
        content = txt_file.read_text()
        
        # Extract first query for filename
        match = re.search(
            r'<user_query>\s*(.+?)(?:\n|</user_query>)',
            content,
            re.DOTALL
        )
        first_query = match.group(1).strip() if match else "session"
        slug = slugify(first_query)
        
        filename = f"{mtime.strftime('%Y-%m-%d-%H%M')}-{slug}.md"
        
        md_content = f"# Chat: {slug}\n\n"
        md_content += f"**Date:** {mtime.strftime('%Y-%m-%d %H:%M')}\n"
        md_content += f"**Source:** {txt_file.name}\n\n---\n\n"
        md_content += content
        
        (output_dir / filename).write_text(md_content)
        print(f"Created: {filename}")
    
    return len(txt_files)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    project_path = sys.argv[1]
    output_dir = Path(sys.argv[2])
    
    transcripts_dir = find_project_folder(project_path)
    
    if not transcripts_dir:
        print(f"Error: No transcripts found for project: {project_path}")
        print("Check ~/.cursor/projects/ for available projects")
        sys.exit(1)
    
    print(f"Found transcripts: {transcripts_dir}")
    count = export_transcripts(transcripts_dir, output_dir)
    print(f"\nExported {count} sessions to {output_dir}")


if __name__ == "__main__":
    main()
