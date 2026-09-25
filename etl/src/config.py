from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SPARQL_ENDPOINT: str
    MAX_WORKERS: int
    CHUNK_SIZE: int
    DATABASE_URL: str
    REDIS_URL: str
    DOWNLOAD_DIR_NAME: str
    DISCORD_WEBHOOK: str

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
    "BT-03-notice": "form_type",
    "BT-02-notice": "notice_type",
    "BT-01-notice": "legal_basis",  
    "DL-Metadata-Order": "title",
    "BT-05-notice": "issue_date",
    "BT-145-Contract": "contract_conclusion_date"
}

ORGANIZATION_FIELDS = {
    "OPT-200-Organization-Company": "org_ref",
    "BT-500-Organization-Company": "name",
    "BT-501-Organization-Company-CIN": "cin",
    "BT-501-Organization-Company-TIN": "tin",
    "BT-503-Organization-Company": "phone",
    "BT-510(a)-Organization-Company": "street_name",
    "BT-510(b)-Organization-Company": "street_number",
    "BT-513-Organization-Company": "town",
    "BT-512-Organization-Company": "postal_code",
    "BT-507-Organization-Company": "nuts_code",
    "BT-514-Organization-Company": "country",
}

PROCEDURE_FIELDS = {
    "BT-22-Procedure": "reference",
    "BT-105-Procedure": "procedure_type",
    "BT-23-Procedure": "contract_type",
    "BT-21-Procedure": "title",
    "BT-24-Procedure": "description",
    "BT-262-Procedure": "main_cpv",
    "BT-27-Procedure_value": "total_value",
    "BT-27-Procedure_currency": "currency",
    "BT-5071-Procedure": "nuts_code",
    "BT-508-Procedure-Buyer": "buyer_profile_url",
}

LOT_FIELDS = {
    "DL-Context-Lot": "lot_reference",
    "DL-Title-Lot": "title",
    "BT-21-Lot": "title",
    "BT-24-Lot": "description",
    "BT-27-Lot_value": "value",
    "BT-27-Lot_currency": "currency",
    "BT-262-Lot": "main_cpv",
    "BT-5071-Lot": "nuts_code",
    "BT-539-Lot": "award_criterion",
    "BT-15-Lot": "document_url",
    "BT-18-Lot": "detail_url",
}

ANCHOR_ORGANIZATION = "GR-Organisations_panel"
ANCHOR_LOT = "GR-Lot"