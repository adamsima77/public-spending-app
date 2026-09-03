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