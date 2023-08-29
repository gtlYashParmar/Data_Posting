import requests
import tempfile
import os
import logging
import json
from tqdm import tqdm
# ==============CONSTANTS==========================
FSD_SERVER_URL = "http://10.0.0.227:85/api/candidate/GetCandidateDetailsById"
LOCAL_URL = "http://localhost:8000/api/v1/candidate-viewset"
TOKEN = "4d428fb6f3206a4f05cb396aeef2b7a22601fb6d"
RESUMEX_SERVER_URL = "http://10.0.0.235:8026/api/v1/candidate-viewset"
LOG_FILENAME = "error_log.log"
logging.basicConfig(filename=LOG_FILENAME, level=logging.INFO)
# =================================================


def fetch_candidate_documents(candidate_id):
    response = requests.get(FSD_SERVER_URL, params={
                            "candidateId": candidate_id})

    if response.status_code != 200:
        logging.error(
            f"Failed to fetch candidate details for candidate {candidate_id}")
        return None

    return response.json().get("Documents", [])


def download_and_save_file(url, file_extension):
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to download file from URL: {url}")
        return None

    with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_file:
        temp_file.write(response.content)
        return temp_file.name


def upload_recordings_to_server(candidate_id, dest_id, recordings):
    headers = {
        "Authorization": f"Token {TOKEN}"
    }

    files = []
    for idx, recording_file in enumerate(recordings, 1):
        recording_extension = os.path.splitext(recording_file)[-1]
        recording_filename = f"recording_{candidate_id}_{idx}{recording_extension}"
        files.append(('recording_files', (recording_filename, open(recording_file, 'rb'), 'audio/mpeg')))

    response = requests.put(f"{RESUMEX_SERVER_URL}/{dest_id}/", files=files, headers=headers)


    if response.status_code == 200:
        logging.info(f"Files uploaded successfully for candidate {dest_id}")
    else:
        logging.error(f"Failed to upload files for candidate {dest_id}. Status code: {response.status_code}")


def main():
    with open("data.json", "r") as file:
        candidate_data = json.load(file)

    logging.info("Data migration started")

    success_candidates = []
    failed_candidates = []
    
    for source_id, destination_id in tqdm(candidate_data.items()):
        try:
            documents = fetch_candidate_documents(source_id)
            call_recordings = [
                download_and_save_file(
                    doc["Name"], os.path.splitext(doc["Name"])[-1].lower())
                for doc in documents if doc["documentType"] == "Call Recording"
            ]
            if not call_recordings:
                logging.warning(
                    f"No call recordings found for candidate {source_id}")
                continue

            upload_recordings_to_server(
                source_id, destination_id, call_recordings)
            success_candidates.append(source_id)

        except Exception as e:
            failed_candidates.append((source_id, str(e)))

    logging.info(f"Successful candidates: {success_candidates}")
    logging.error(f"Failed candidates: {failed_candidates}")

    with open("report.txt", "w") as report_file:
        report_file.write("Successful candidates:\n")
        for candidate_id in success_candidates:
            report_file.write(f"{candidate_id}\n")

        report_file.write("\nFailed candidates:\n")
        for candidate_id, error in failed_candidates:
            report_file.write(f"{candidate_id}: {error}\n")

    logging.info("Data migration completed")


if __name__ == "__main__":
    main()
