"""Progress tracking for resume support."""

from __future__ import annotations

import json
from pathlib import Path
from dataclasses import dataclass, field


PROGRESS_FILE = ".msa-nim-progress.json"


@dataclass
class JobState:
    completed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def is_done(self, job_key: str) -> bool:
        return job_key in self.completed

    def mark_done(self, job_key: str):
        if job_key not in self.completed:
            self.completed.append(job_key)

    def mark_failed(self, job_key: str):
        if job_key not in self.failed:
            self.failed.append(job_key)

    def to_dict(self) -> dict:
        return {"completed": self.completed, "failed": self.failed}

    @classmethod
    def from_dict(cls, d: dict) -> JobState:
        return cls(completed=d.get("completed", []), failed=d.get("failed", []))


class ProgressTracker:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.progress_path = out_dir / PROGRESS_FILE
        self.state = self._load()

    def _load(self) -> JobState:
        if self.progress_path.exists():
            try:
                with open(self.progress_path, "r") as f:
                    return JobState.from_dict(json.load(f))
            except Exception:
                pass
        return JobState()

    def save(self):
        self.out_dir.mkdir(parents=True, exist_ok=True)
        with open(self.progress_path, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def is_done(self, job_key: str) -> bool:
        return self.state.is_done(job_key)

    def mark_done(self, job_key: str):
        self.state.mark_done(job_key)
        self.save()

    def mark_failed(self, job_key: str):
        self.state.mark_failed(job_key)
        self.save()
