"""
file_manager_agent.py

An AI-powered agent that:
- Reads data/{modality}/*.metadata.json
- Uses LLaMA to infer a “topic” folder name from each summary
- Moves media + metadata into public/<topic>/ or secure/<topic>/
- Builds a master index with file paths, topics, and metadata
"""

import json
import shutil
import subprocess
import re
from pathlib import Path

class FileManagerAgent:
    def __init__(self,
                 data_root: Path = Path("data"),
                 public_dir: Path = None,
                 secure_dir: Path = None,
                 index_file: Path = None,
                 model_name: str = "llama3"):
        self.data_root  = data_root
        self.public_dir = public_dir or data_root / "public"
        self.secure_dir = secure_dir or data_root / "secure"
        self.index_file = index_file or data_root / "files_index.json"
        self.model_name = model_name

        # Ensure top-level public/secure exist
        for d in (self.public_dir, self.secure_dir):
            d.mkdir(parents=True, exist_ok=True)

    def load_json(self, path: Path) -> dict:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def infer_topic(self, summary: str) -> str:
        """
        Ask LLaMA to produce a 1–3-word topic name describing the summary.
        """
        prompt = f"""
Given this brief summary, suggest a concise folder name (1–3 words, lowercase, no spaces) for grouping files on the same topic:

\"\"\"{summary}\"\"\"

Folder name:
"""
        try:
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding="utf-8", check=True
            )
            # Extract the first line, sanitize it
            name = result.stdout.strip().splitlines()[0]
            # Remove non-alphanumeric / hyphen
            name = re.sub(r"[^\w-]", "", name.lower())
            return name or "misc"
        except Exception:
            return "misc"

    def process_modality(self, modality: str) -> list:
        """
        Process data/{modality}:
        - For each *.metadata.json
        - Extract summary & warning flag
        - Infer topic folder name
        - Move media + metadata into public/topic/ or secure/topic/
        - Return a record list
        """
        folder = self.data_root / modality
        records = []

        for meta_path in folder.glob("*.metadata.json"):
            data    = self.load_json(meta_path)
            summary = data.get("summary", "")
            warning = data.get("warning", False)
            base    = meta_path.stem

            # Step 1: infer topic name
            topic = self.infer_topic(summary)

            # Step 2: choose target
            root = self.secure_dir if warning else self.public_dir
            target = root / topic
            target.mkdir(parents=True, exist_ok=True)

            # Step 3: move media file
            orig = Path(data.get("filepath", "")).resolve()
            moved = None
            if orig.exists():
                moved = target / orig.name
                shutil.move(str(orig), str(moved))

            # Step 4: move metadata JSON
            dest_meta = target / meta_path.name
            shutil.move(str(meta_path), str(dest_meta))

            # Step 5: build a record
            rec = {
                "base":      base,
                "modality":  modality,
                "topic":     topic,
                "warning":   warning,
                "orig_path": str(moved.resolve()) if moved else None,
                "meta_path": str(dest_meta.resolve())
            }
            records.append(rec)

        return records

    def run(self):
        all_records = []
        for sub in ("audio", "images"):
            all_records += self.process_modality(sub)

        # Write master index
        self.index_file.write_text(
            json.dumps(all_records, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"✅ FileManagerAgent: {len(all_records)} files processed.")
        
if __name__ == "__main__":
    from pathlib import Path
    # Initialize agent; adjust model_name if needed
    agent = FileManagerAgent(
        data_root=Path("data"),
        model_name="llama3"
    )
    agent.run()
