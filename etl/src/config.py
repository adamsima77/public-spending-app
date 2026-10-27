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
    "BT-165-Organization-Company": "company_size",
}

PROCEDURE_FIELDS = {
    "BT-22-Procedure": "reference",
    "BT-105-Procedure": "procedure_type",
    "BT-23-Procedure": "contract_type",
    "BT-21-Procedure": "title",
    "BT-24-Procedure": "description",
    "BT-262-Procedure": "main_cpv",
    "BT-27-Procedure_value": "estimated_value",
    "BT-27-Procedure_currency": "currency",
    "BT-5071-Procedure": "nuts_code",
    "BT-5131-Procedure": "place_of_performance",
    "BT-508-Procedure-Buyer": "buyer_profile_url",
    "BT-728-Procedure": "performance_note",
    "BT-04-notice": "identifier",
}

LOT_FIELDS = {
    "DL-Context-Lot": "lot_reference",
    "DL-Title-Lot": "title",
    "BT-21-Lot": "title",
    "BT-24-Lot": "description",
    "BT-27-Lot_value": "estimated_value",
    "BT-27-Lot_currency": "estimated_currency",
    "BT-262-Lot": "main_cpv",
    "BT-5071-Lot": "nuts_code",
    "BT-5131-Lot": "place_of_performance",
    "BT-539-Lot": "award_criterion",
    "BT-15-Lot": "document_url",
    "BT-18-Lot": "detail_url",
    "BT-36-Lot_value": "duration_value",
    "BT-36-Lot_measure": "duration_unit",
    "BT-271-Lot_value": "framework_max_value",
    "BT-271-Lot_currency": "framework_max_currency",
    "BT-60-Lot": "eu_funded",
    "BT-92-Lot": "eordering_allowed",
    "BT-93-Lot": "epayment_allowed",
    "BT-743-Lot": "einvoicing",
    "BT-63-Lot": "variants_allowed",
    "BT-736-Lot": "reserved_execution",
    "BT-71-Lot": "reserved_participation",
}

LOT_RESULT_FIELDS = {
    "BT-13713-LotResult": "lot_reference",
    "BT-142-LotResult": "award_outcome",
    "BT-144-LotResult": "non_award_reason",
    "BT-710-LotResult_value": "lowest_offer_value",
    "BT-710-LotResult_currency": "lowest_offer_currency",
    "BT-711-LotResult_value": "highest_offer_value",
    "BT-711-LotResult_currency": "highest_offer_currency",
    "OPT-320-LotResult": "tender_refs",
    "OPT-315-LotResult": "contract_refs",
}

SUBMISSION_STAT_FIELDS = {
    "BT-760-LotResult": "category_code",
    "BT-759-LotResult": "count",
}

LOT_TENDER_FIELDS = {
    "BT-13714-Tender": "lot_reference",
    "OPT-321-Tender": "tender_ref",
    "BT-720-Tender_value": "tender_value",
    "BT-720-Tender_currency": "tender_currency",
    "OPT-310-Tender": "tendering_party_ref",
    "BT-171-Tender": "rank",
    "BT-773-Tender": "subcontracting",
}

SETTLED_CONTRACT_FIELDS = {
    "BT-150-Contract": "contract_number",
    "BT-145-Contract": "conclusion_date",
    "OPT-316-Contract": "contract_ref",
    "BT-721-Contract": "title",
    "BT-151-Contract": "contract_url",
    "BT-3202-Contract": "tender_refs",
}

LIST_FIELDS = {"tender_refs", "contract_refs"}

ANCHOR_ORGANIZATION = "GR-Organisations_panel"
ANCHOR_LOT = "GR-Lot_well"
ANCHOR_LOT_RESULT = "GR-LotResult_panel"
ANCHOR_SUBMISSION_STAT = "GR-LotResult-ReceivedSubmissions_panel"
ANCHOR_LOT_TENDER = "GR-LotTender_panel"
ANCHOR_TENDERING_PARTY = "GR-TenderingParty_panel"
ANCHOR_SETTLED_CONTRACT = "GR-SettledContract_panel"
TENDERER_ORG_REF_KEY = "OPT-300-Tenderer"
