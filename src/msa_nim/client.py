"""NVIDIA MSA-Search NIM API client with retry logic."""

from __future__ import annotations

import time
from dataclasses import dataclass

import requests


CLOUD_ENDPOINT = "https://health.api.nvidia.com/v1/biology/colabfold/msa-search/predict"

CLOUD_DATABASES = {
    "uniref30": "Uniref30_2302",
    "colabfold_envdb": "colabfold_envdb_202108",
    "pdb70": "PDB70_220313",
}

DEFAULT_MSA_DATABASES = [CLOUD_DATABASES["uniref30"], CLOUD_DATABASES["colabfold_envdb"]]


@dataclass
class MsaResult:
    job_id: str
    alignments: dict[str, str]
    raw: dict | None = None


class NimClient:
    def __init__(self, api_key: str, timeout: int = 900):
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _post_with_retry(
        self,
        url: str,
        payload: dict,
        max_retries: int = 5,
        backoff: float = 15.0,
    ) -> dict:
        """POST with exponential backoff.

        NVIDIA's free-tier cloud NIM allows ~1 concurrent request per
        short window.  429 returns no Retry-After header, so we use
        a conservative backoff (15s base, doubling on retry).
        """
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                resp = self.session.post(url, json=payload, timeout=self.timeout)
                if resp.status_code == 429:
                    wait = backoff * (2 ** (attempt - 1))
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError as e:
                last_err = e
                if e.response.status_code >= 500:
                    wait = backoff * (2 ** (attempt - 1))
                    time.sleep(wait)
                    continue
                raise
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_err = e
                wait = backoff * (2 ** (attempt - 1))
                time.sleep(wait)
                continue
        raise RuntimeError(f"Request failed after {max_retries} retries: {last_err}")

    def search_monomer(
        self,
        sequence: str,
        databases: list[str] | None = None,
    ) -> MsaResult:
        databases = databases or DEFAULT_MSA_DATABASES
        payload = {
            "sequence": sequence,
            "databases": databases,
            "output_alignment_formats": ["a3m"],
        }
        data = self._post_with_retry(CLOUD_ENDPOINT, payload)
        alignments = self._extract_alignments(data)
        return MsaResult(
            job_id="monomer",
            alignments=alignments,
            raw=data,
        )

    @staticmethod
    def _extract_alignments(data: dict) -> dict[str, str]:
        result = {}
        alignments = data.get("alignments", {})
        for db_name, db_data in alignments.items():
            a3m = db_data.get("a3m", {}).get("alignment")
            if a3m:
                result[db_name] = a3m
        return result
