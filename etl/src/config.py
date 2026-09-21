from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SPARQL_ENDPOINT: str
    MAX_WORKERS: int
    CHUNK_SIZE: int
    DATABASE_URL: str
    REDIS_URL: str
    DOWNLOAD_DIR_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOAD_DIR = BASE_DIR / settings.DOWNLOAD_DIR_NAME

DOWNLOAD_LINKS_QUERY = """
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX dct:  <http://purl.org/dc/terms/>

SELECT ?downloadURL ?format
WHERE {
  ?dataset a dcat:Dataset ;
           dct:publisher <https://data.gov.sk/id/legal-subject/31797903> ;
           dct:title ?datasetTitle ;
           dcat:distribution ?distribution .

  ?distribution dct:format ?format ;
                dcat:downloadURL ?downloadURL .

  FILTER (
    CONTAINS(LCASE(STR(?datasetTitle)), "vestník") &&
    (CONTAINS(LCASE(STR(?format)), "csv") || CONTAINS(LCASE(STR(?format)), "json"))
  )
}
"""

NOTICE_FIELDS = {
    "BT-701-notice": "notice_id",
    "BT-757-notice": "notice_version",
    "BT-03-notice": "notice_type",
    "OPP-070-notice": "form_type",
    "DL-Metadata-Order": "title",
}
ORGANIZATION_FIELDS = {
    "BT-500-Organization-Company": "name",
    "BT-501-Organization-Company-CIN": "cin",
    "BT-501-Organization-Company-TIN": "tin",
    "BT-513-Organization-Company": "town",
    "BT-514-Organization-Company": "country",
}
PROCEDURE_FIELDS = {
    "BT-22-Procedure": "reference",
    "BT-21-Procedure": "title",
    "BT-24-Procedure": "description",
    "BT-262-Procedure": "main_cpv",
}
LOT_FIELDS = {
    "BT-22-Lot": "lot_reference",
    "BT-21-Lot": "title",
    "BT-262-Lot": "main_cpv",
    "BT-539-Lot": "award_criterion",
}

ANCHOR_ORGANIZATION = "GR-Organisations_panel"
ANCHOR_LOT = "GR-Lot"