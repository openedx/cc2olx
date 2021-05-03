import argparse
import json
import csv
import zipfile
from urllib.parse import parse_qs, urlparse

from lxml import html

import youtube_dl


def parse_args(args=None):
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Find and download videos from a CC course.")
    parser.add_argument("--config", "-c", help="JSON config file")
    parser.add_argument("--input", "-i", help="Input CC zip or HTML file", required=True)
    parser.add_argument("--output", "-o", default="out.csv", help="CSV output file")
    parser.add_argument("--downloads", "-d", default="downloads", help="Video download directory")
    parser.add_argument("--simulate", "-s", action="store_true", help="Simulate downloads")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose ytd downloads")

    return parser.parse_args(args)


def get_ydl_opts(args):
    """Set options to be used by Youtube DL"""

    if args.config:
        return json.load(open(args.config))

    return {
        "verbose": args.verbose,
        "simulate": args.simulate,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "outtmpl": f"{args.downloads}/%(title)s.%(ext)s",
    }


def download_videos(urls, opts):
    """
    Download a list of videos and optionally transcripts.
    Arguments:
        * videos: a list of URLs
        * opts: options for Youtube DL
    """

    relpaths = []

    def my_hook(d):
        """Youtube DL callback"""
        if d["status"] == "finished":
            fn = d["filename"]
            if not fn.endswith("m4a"):
                relpaths.append(fn)

    opts["progress_hooks"] = [my_hook]

    ydl = youtube_dl.YoutubeDL(opts)
    ydl.download(urls)

    return relpaths


def make_row(relpath, url):
    """Create an entry for the output CSV."""

    youtube_id = ""
    if "youtube.com" in url:
        youtube_id = url.split("=")[-1]

    return {
        "Relative File Path": relpath,
        "External Video Link": url,
        "Youtube Id": youtube_id,
    }


def extract_url(src):
    """Extract a downloadable video link from a src attribute."""
    if "youtube.com" in src:
        url = src.replace("/embed/", "/watch?v=").replace("?rel=0", "")
        return url
    elif "cdnapisec.kaltura.com" in src:
        # Skip playlist URLs
        if "playlist" in src:
            return ""
        return src
    return ""


def find_video_urls(input_html):
    """Find valid video URLs from iframes in an HTML file."""

    parsed_html = html.parse(input_html)
    iframes = parsed_html.xpath("//iframe")

    urls = []
    for iframe in iframes:
        src = iframe.attrib.get("src", "")
        url = extract_url(src)
        if url:
            urls.append(url)
    return urls


def write_csv(outfile, urls, relpaths):
    fieldnames = ["Relative File Path", "External Video Link", "Youtube Id"]
    with open(outfile, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for (r, u) in zip(relpaths, urls):
            row = make_row(r, u)
            writer.writerow(row)


def get_entry_id(src):
    """Extract Kaltura entry_id from embedding URL."""
    entry_id = None
    parsed_url = urlparse(src)
    query = parsed_url.query
    query_dict = parse_qs(query)
    entry_id_query = query_dict.get("entry_id")
    if entry_id_query:
        entry_id = entry_id_query[0]
    return entry_id


def reformat(url):
    if "kaltura" in url:
        netloc = url.split("embedIframeJs")[0].strip()
        entry_id = get_entry_id(url)
        url = f"{netloc}playManifest/entryId/{entry_id}/format/url/protocol/https"

    return url


def find_all_video_urls(name):
    """
    Extract video urls from a CC course or HTML file
    """
    urls = []
    if zipfile.is_zipfile(name):
        with zipfile.ZipFile(name) as z:
            for filename in z.namelist():
                if filename.endswith(".html"):
                    with z.open(filename) as f:
                        urls += find_video_urls(f)
    else:
        # If input is a single HTML for debugging
        urls += find_video_urls(name)

    return urls


def main():
    args = parse_args()
    ydl_opts = get_ydl_opts(args)

    urls = find_all_video_urls(args.input)
    relpaths = download_videos(urls, ydl_opts)

    # Remove download dir prefix from pathnames
    relpaths = [r.lstrip(f"{args.downloads}/") for r in relpaths]

    # Reformat URLs as expected by the cc2olx tool
    urls = [reformat(u) for u in urls]

    write_csv(args.output, urls, relpaths)


if __name__ == "__main__":
    main()
