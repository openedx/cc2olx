import argparse
import csv
import os
from pathlib import Path

import requests
from requests.auth import AuthBase

OAUTH_TOKEN_URL = "https://courses.edx.org/oauth2/access_token"
GENERATE_UPLOAD_LINK_BASE_URL = "https://studio.edx.org/generate_video_upload_link/"
TRANSCRIPT_UPLOAD_LINK = "https://studio.edx.org/transcript_upload/"
# OAUTH_TOKEN_URL = "https://courses.stage.edx.org/oauth2/access_token"
# GENERATE_UPLOAD_LINK_BASE_URL = "https://studio.stage.edx.org/generate_video_upload_link/"
# TRANSCRIPT_UPLOAD_LINK = "https://studio.stage.edx.org/transcript_upload/"

VIDEO_EXTENSION_CONTENT_TYPES = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
}


class SuppliedJwtAuth(AuthBase):
    """Attaches a supplied JWT to the given Request object."""

    def __init__(self, token):
        """Instantiate the auth class."""
        self.token = token

    def __call__(self, r):
        """Update the request headers."""
        r.headers["Authorization"] = f"JWT {self.token}"
        return r


def get_access_token():
    oauth_url = OAUTH_TOKEN_URL
    client_id = os.environ["CC2OLX_CLIENT"]
    client_secret = os.environ["CC2OLX_SECRET"]

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "token_type": "jwt",
    }

    # Call OAuth Access Token API to get an access token
    response = requests.post(
        oauth_url,
        data=data,
        headers={
            "User-Agent": "cc2olx",
        },
    )

    response.raise_for_status()
    data = response.json()
    return data["access_token"]


def parse_args(args=None):
    """Set up and return command line arguments for the video upload tool."""
    parser = argparse.ArgumentParser(description="Upload video files to edX via Studio's video encoding pipeline.")
    parser.add_argument(
        "course_id",
        metavar="course-id",
        help="course ID of the course run to which to upload videos, as it appears in Studio",
    )
    parser.add_argument(
        "directory",
        help="directory containing videos to upload to Studio",
    )
    parser.add_argument(
        "input_csv",
        metavar="input-csv",
        help="path to a CSV file with metadata about the video files",
    )
    parser.add_argument(
        "--output-csv",
        "-o",
        help="path to where the output CSV should be stored; this will overwrite existing files",
    )
    return parser.parse_args(args)


def make_generate_upload_link_request(url, data, filename, access_token):
    """
    Make a POST request against the Studio generate upload link API and return the
    response. If errors occur during the API call, log to the console.

    Arguments:
        * url: the URL against which to make the POST request
        * data: a dictionary to be passed in the POST request as a json parameter
        * filename: the filename for the file we are calling the API with - used for logging
        * access_token: access token to be able to make authenticated calls to the Studio API

    Returns:
        * response: the response object from the POST API call
    """
    s = requests.Session()
    s.auth = SuppliedJwtAuth(access_token)

    try:
        response = s.post(url, json=data)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(
            "An HTTP error occurred calling the Studio generate upload link API "
            "for video: {}: {}".format(filename, repr(error))
        )
    except requests.exceptions.ConnectionError as error:
        print(
            "A Connection error occurred calling the Studio generate upload link API "
            "for video {}: {}".format(filename, error)
        )
    except requests.exceptions.Timeout as error:
        print(
            "A Timeout error occurred calling the Studio generate upload link API "
            "for video {}: {}".format(filename, error)
        )
    except requests.exceptions.RequestException as error:
        print(
            "An unknown error occurred calling the Studio generate upload link API "
            "for video {}: {}".format(filename, error)
        )

    return response


def upload_transcript(filename, edx_video_id, language_code):
    """
    Make a POST request against the Studio upload transcript API and return the
    response. If errors occur during the API call, log to the console.

    Arguments:
        * filename: the transcript filename
        * edx_video_id: the video ID of the video this transcript is for
        * language_code: the language of the transcript

    Returns:
        * response: the response object from the POST API call
    """
    data = {"edx_video_id": edx_video_id, "language_code": language_code, "new_language_code": language_code}
    files = {"file": open(filename, "rb")}

    try:
        response = requests.post(TRANSCRIPT_UPLOAD_LINK, data=data, files=files)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(
            "An HTTP error occurred calling the Studio transcript upload link API "
            "for transcript: {}: {}".format(filename, repr(error))
        )
    if response.status_code == 201:
        print(f"Successfully uploaded transcript {filename}.")
    else:
        print(f"Transcript {filename} was unable to be uploaded.")

    return response


def make_upload_video_request(url, data, headers, filename):
    """
    Make a PUT request against the AWS upload video API.
    If errors occur during the API call, log to the console.

    Arguments:
        * url: the URL against which to make the PUT request
        * data: a dictionary to be passed in the PUT request as a data parameter
        * headers: a dictionary of headers to be passed in the PUT request as a headers parameter
        * filename: the filename for the file we are calling the API with - used for logging

    Returns:
        * response: the response object from the PUT API call
    """
    try:
        response = requests.put(url, data=data, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as error:
        print(
            "An HTTP error occurred calling the upload video API "
            "for video: {} and the video was not uploaded: {}".format(filename, repr(error))
        )
    except requests.exceptions.ConnectionError as error:
        print(
            "A Connection error occurred calling the upload video API "
            "for video {} and the video was not uploaded: {}".format(filename, repr(error))
        )
    except requests.exceptions.Timeout as error:
        print(
            "A Timeout error occurred calling the upload video API "
            "for video {} and the video was not uploaded: {}".format(filename, repr(error))
        )
    except requests.exceptions.RequestException as error:
        print(
            "An unknown error occurred calling the upload video API "
            "for video {} and the video was not uploaded: {}".format(filename, repr(error))
        )

    if response.status_code == 200:
        print(f"Successfully uploaded video {filename}.")
    else:
        print(f"Video {filename} was unable to be uploaded.")


def write_upload_results_csv(input_csv_path, output_csv_path, file_data):
    """
    Write the results of the video uploads to a new CSV. Parse the input CSV at
    input_csv_path and write the results of the uploads to a new output CSV at output_csv_path.

    Arguments:
        * input_csv_path: path to the CSV file describing the videos in the directory
        * output_csv_path: path to a new output CSV file that will be created that includes results of the video uploads
        * file_data: a mapping from filename to data about the file to be include in the new CSV,
            namely the edx_video_id


    """
    with open(input_csv_path, encoding="utf-8") as input_csv, open(output_csv_path, "w") as output_csv:
        reader = csv.DictReader(input_csv)

        new_fieldnames = reader.fieldnames.copy()
        new_fieldnames.append("Edx Id")
        new_fieldnames.append("Languages")

        writer = csv.DictWriter(output_csv, new_fieldnames)
        writer.writeheader()

        for row in reader:
            filepath = row["Relative File Path"]
            try:
                data = file_data[filepath]
            except KeyError:
                print("The video {} is missing from the supplied directory. " "No video was uploaded.".format(filepath))
                continue

            new_row = row.copy()
            new_row["Edx Id"] = data["edx_video_id"]
            new_row["Languages"] = data["lang"]

            writer.writerow(new_row)


def main():
    args = parse_args()
    access_token = get_access_token()

    root = Path(args.directory)
    get_upload_link_url = GENERATE_UPLOAD_LINK_BASE_URL + args.course_id
    files_data = {}

    for dirpath, _, filenames in os.walk(args.directory):
        for filename in filenames:
            # construct filename this way to uniquely identify
            # the file within the root directory
            full_path = Path(dirpath, filename)
            relative_path = full_path.relative_to(root)
            extension = relative_path.suffix

            if extension in VIDEO_EXTENSION_CONTENT_TYPES:
                content_type = VIDEO_EXTENSION_CONTENT_TYPES.get(extension)

                request_data = {"files": [{"file_name": filename, "content_type": content_type}]}

                response = make_generate_upload_link_request(get_upload_link_url, request_data, filename, access_token)

                try:
                    data = response.json()
                except ValueError:
                    print(
                        "Unable to parse JSON for call to the Studio generate upload link API "
                        "for video {}.".format(filename)
                    )

                edx_video_id = None
                upload_url = None

                if "files" in data and data["files"]:
                    file_data = data["files"][0]

                    if "edx_video_id" in file_data:
                        edx_video_id = file_data["edx_video_id"]

                    if "upload_url" in file_data:
                        upload_url = file_data["upload_url"]

                if not upload_url or not edx_video_id:
                    print(
                        "Unable to upload video {}; either upload_url or edx_video_id "
                        "is missing in response from Studio generate upload link API."
                    )

                # upload video to presigned url if we have one
                if upload_url:
                    with full_path.open("rb") as f:
                        data = f.read()
                        headers = {"Content-Type": content_type}
                        make_upload_video_request(upload_url, data, headers, filename)

                files_data[str(relative_path)] = {"edx_video_id": edx_video_id}
                langs = []

                # Look for files with the same name as our video but with a ${LANG}.srt suffix
                for srt_path in sorted(full_path.parent.glob(full_path.stem + "*.srt")):
                    lang = srt_path.suffixes[0][1:]
                    langs.append(lang)
                    upload_transcript(srt_path, edx_video_id, lang)

                files_data[str(relative_path)]["lang"] = "-".join(langs)

    input_csv_path = Path(args.input_csv)

    output_csv_path = args.output_csv
    if not output_csv_path:
        output_csv_path = str(
            input_csv_path.parent.joinpath(input_csv_path.stem + "-upload-results" + input_csv_path.suffix)
        )

    write_upload_results_csv(str(input_csv_path), output_csv_path, files_data)


if __name__ == "__main__":
    main()
