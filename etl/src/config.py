from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SPARQL_ENDPOINT: str
    MAX_WORKERS: int
    CHUNK_SIZE: int

    DATABASE_URL: str

    DOWNLOAD_DIR_NAME: str
    STATE_DIR_NAME: str
    LOGS_DIR_NAME: str

    DOWNLOADED_LINKS_FILE_NAME: str
    ERROR_LOG_FILE_NAME: str
    ACTIVITY_LOG_FILE_NAME: str
    BACKEND_URL: str 
    PYTHON_ACCESS_KEY: str   

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# 1. Inštancia s načítanými dátami z .env
settings = Settings()

# 2. Základný adresár projektu
BASE_DIR = Path(__file__).resolve().parent.parent

# 3. Cesty vytvorené z premenných z .env
DOWNLOAD_DIR = BASE_DIR / settings.DOWNLOAD_DIR_NAME
STATE_DIR = BASE_DIR / settings.STATE_DIR_NAME
LOGS_DIR = BASE_DIR / settings.LOGS_DIR_NAME

# Súbory
DOWNLOADED_LINKS_LOG_FILE = STATE_DIR / settings.DOWNLOADED_LINKS_FILE_NAME
ERROR_LOG = LOGS_DIR / settings.ERROR_LOG_FILE_NAME
ACTIVITY_LOG = LOGS_DIR / settings.ACTIVITY_LOG_FILE_NAME

# SPARQL Query (ostáva ako viacriadkový string v Pythone)
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