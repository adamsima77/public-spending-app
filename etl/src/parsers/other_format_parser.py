from collections import Counter
from typing import Any

from core.logger import Logger

MAX_SAMPLES = 10
MAX_COMPONENT_KEYS = 30


class OtherFormatParser:
    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger
        self._counts: Counter[str] = Counter()
        self._forms: Counter[str] = Counter()
        self._submission_ids: dict[str, list[str]] = {}
        self._structure_samples: dict[str, list[dict[str, Any]]] = {}

    def handle_json(self, notice: dict[str, Any], submission_id: int | str | None) -> None:
        name = notice.get("name")
        form_name = name.strip() if isinstance(name, str) and name.strip() else None
        fields = self._find_values(notice.get("components"))
        structure = {
            "name": form_name,
            "component_keys": self._component_keys(notice.get("components")),
        }

        if form_name and "súhrnná správa" in form_name.casefold():
            category = "summary_report"
            form = form_name
        elif self._has_business_term_fields(notice.get("components")):
            category = "json_without_eforms_sdk"
            form_values = (
                fields.get("OPP-070-notice")
                or fields.get("BT-03-notice")
                or ([form_name] if form_name else [])
            )
            form = form_values[0] if form_values else "neznámy formulár"
        else:
            category = "unidentified_json"
            form = form_name or "neznámy JSON"

        self._record(category, form, submission_id, structure)

    def handle_unknown(self, submission_id: int | str | None, reason: str) -> None:
        self._record("unknown_format", reason, submission_id)

    async def report_file(self, file_name: str, db_file_id: int | None) -> None:
        if self._counts:
            context = {
                "categories": dict(self._counts),
                "form_types": dict(self._forms),
                "submission_id_samples": self._submission_ids,
                "structure_samples": self._structure_samples,
            }
            message = f"{file_name}: iné JSON/nezaradené položky: {dict(self._counts)}"
            if self._logger:
                await self._logger.log("warning", message, context=context, file_id=db_file_id)
            print(f"Formát handler: {message}.", flush=True)
        self._counts.clear()
        self._forms.clear()
        self._submission_ids.clear()
        self._structure_samples.clear()

    def _record(
        self,
        category: str,
        form: str,
        submission_id: int | str | None,
        structure: dict[str, Any] | None = None,
    ) -> None:
        self._counts[category] += 1
        self._forms[form] += 1
        sample = self._submission_ids.setdefault(category, [])
        if len(sample) < MAX_SAMPLES:
            sample.append(str(submission_id) if submission_id is not None else "bez submissionId")
        if structure is not None:
            structures = self._structure_samples.setdefault(category, [])
            if len(structures) < MAX_SAMPLES:
                structures.append(
                    {
                        "submission_id": (
                            str(submission_id) if submission_id is not None else None
                        ),
                        **structure,
                    }
                )

    @classmethod
    def _component_keys(cls, nodes: Any) -> list[str]:
        keys: list[str] = []
        seen: set[str] = set()

        def visit(node: Any) -> None:
            if len(keys) >= MAX_COMPONENT_KEYS:
                return
            if isinstance(node, list):
                for child in node:
                    visit(child)
            elif isinstance(node, dict):
                key = node.get("key")
                if isinstance(key, str) and key not in seen:
                    seen.add(key)
                    keys.append(key)
                visit(node.get("components"))

        visit(nodes)
        return keys

    @classmethod
    def _find_values(cls, nodes: Any) -> dict[str, list[str]]:
        values: dict[str, list[str]] = {}
        if isinstance(nodes, list):
            for node in nodes:
                for child_key, child_values in cls._find_values(node).items():
                    values.setdefault(child_key, []).extend(child_values)
        elif isinstance(nodes, dict):
            node_key = nodes.get("key")
            value = nodes.get("value")
            if isinstance(node_key, str) and isinstance(value, str):
                values.setdefault(node_key, []).append(value)
            for child_key, child_values in cls._find_values(nodes.get("components")).items():
                values.setdefault(child_key, []).extend(child_values)
        return values

    @classmethod
    def _has_business_term_fields(cls, nodes: Any) -> bool:
        if isinstance(nodes, list):
            return any(cls._has_business_term_fields(node) for node in nodes)
        if isinstance(nodes, dict):
            key = nodes.get("key")
            return (
                isinstance(key, str) and key.startswith("BT-")
            ) or cls._has_business_term_fields(nodes.get("components"))
        return False
