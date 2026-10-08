import hashlib
import json

from llama_cloud_services.parse.types import JobResult
from llama_index.core import Document

from reportlens.app.config import settings
from llama_parse import LlamaParse
from pathlib import Path
import os

class DocumentParser:
    def __init__(self):
        self.llama_parse_api_key = settings.llama_parse_api_key
        self.parser = LlamaParse(api_key=self.llama_parse_api_key, result_type="markdown", split_by_page=True)
        self.output_directory = settings.out_dir
        self.cache_directory = settings.cache_dir
        self._create_directory(self.cache_directory)

    async def aparse_pdf(self, file_paths: list[str]) -> list[JobResult]:
        cache_file = Path(self.cache_directory) / "cached_jobs.json"

        if self._check_file_exists(cache_file):
            with open(cache_file, "r") as f:
                cached_file_paths = json.load(f)
                valid_file_paths = [path for path in file_paths if Path(path).name not in cached_file_paths.keys()]
        else:
            valid_file_paths = file_paths

        if not valid_file_paths:
            return []

        parsed_jobs = await self.parser.aparse(valid_file_paths)
        for job in parsed_jobs:
            out_folder = Path(self.output_directory) / job.job_id
            self._create_directory(out_folder)
        return parsed_jobs

    async def ingest_doc(self, file_paths: list[str]) -> None:
        parsed_jobs = await self.aparse_pdf(file_paths)

        for job in parsed_jobs:
            out_folder = Path(self.output_directory) / job.job_id
            docs = await job.aget_markdown_documents(True)
            for j, doc in enumerate(docs):
                node_doc = {
                    "text": doc.text,
                    "metadata": {
                        "page_number": doc.metadata["page_number"],
                        "file_name": Path(job.file_name).name
                    }
                }
                with (Path(out_folder) / f"{job.job_id}-{j}.json").open("w") as f:
                    json.dump(node_doc, f, indent=2)
                    f.write("\n")
            self._store_cache({Path(job.file_name).name: job.job_id})

    def _create_directory(self, file_path: str) -> None:
        os.makedirs(file_path, exist_ok=True)

    def _store_cache(self, cached_jobs: dict[str, str]) -> None:
        cache_file = Path(self.cache_directory) / "cached_jobs.json"
        if cache_file.exists():
            with cache_file.open("r") as f:
                existing_jobs = json.load(f)
        else:
            existing_jobs = {}

        existing_jobs.update(cached_jobs)
        with cache_file.open("w") as f:
            json.dump(existing_jobs, f, indent=2)
            f.write("\n")

    def _check_file_exists(self, file_path: str) -> bool:
        return os.path.exists(file_path)