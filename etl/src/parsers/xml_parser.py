from core.logger import Logger

MAX_SAMPLES = 10


class XmlParser:
    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger
        self._count = 0
        self._submission_ids: list[str] = []

    def handle(self, submission_id: int | str | None) -> None:
        self._count += 1
        self._add_sample(submission_id)

    async def report_file(self, file_name: str, db_file_id: int | None) -> None:
        if self._count:
            message = f"XML položky mimo eForms rozsah: {self._count}"
            if self._logger:
                await self._logger.log(
                    "warning",
                    f"{file_name}: {message}",
                    context={"submission_id_samples": self._submission_ids},
                    file_id=db_file_id,
                )
            print(f"XML handler: {file_name}: {message}.", flush=True)
        self._count = 0
        self._submission_ids.clear()

    def _add_sample(self, submission_id: int | str | None) -> None:
        if len(self._submission_ids) < MAX_SAMPLES:
            self._submission_ids.append(
                str(submission_id) if submission_id is not None else "bez submissionId"
            )
