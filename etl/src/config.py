from pathlib import Path

SPARQL_ENDPOINT = "https://data.slovensko.sk/api/sparql"
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

BASE_DIR = Path(__file__).resolve().parent.parent 
DOWNLOAD_DIR = BASE_DIR / "download"
CHUNK_SIZE = 8192

STATE_DIR = BASE_DIR / "state"
STATE_DIR.mkdir(exist_ok=True) 
DOWNLOADED_LINKS_LOG_FILE = STATE_DIR / "links.txt"

ERROR_LOG = BASE_DIR / "logs" / "error_log.txt"
ACTIVITY_LOG = BASE_DIR / "logs" / "activity_log.txt"

MAX_WORKERS = 7 