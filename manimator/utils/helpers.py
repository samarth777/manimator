from fastapi import HTTPException
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
import base64
import requests


def read_base64_few_shot_file(filepath="./manimator/few_shot/few_shot_1.txt") -> str:
    """Reads and returns content of a few-shot example file, converting to base64 if needed.

    Args:
        filepath (str): Path to the few-shot example file. Defaults to "./manimator/few_shot/few_shot_1.txt"

    Returns:
        str: Base64 encoded content of the file

    Raises:
        FileNotFoundError: If the specified file cannot be found
    """

    try:
        with open(filepath, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fall back to generating base64 and saving it
        with open(filepath, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            base64_str = base64.b64encode(pdf_bytes).decode("utf-8")
            # Save for future use
            with open("./manimator/few_shot/few_shot_base64.txt", "w") as txt_file:
                txt_file.write(base64_str)
            return base64_str


def download_arxiv_pdf(url: str) -> bytes:
    """Downloads a PDF from an arXiv URL.

    Args:
        url (str): The arXiv URL to download the PDF from

    Returns:
        bytes: Raw PDF content

    Raises:
        HTTPException: If download fails or URL is invalid
    """

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to download arxiv PDF: {str(e)}"
        )


def compress_pdf(content: bytes, compression_level: int = 5) -> str:
    """Compresses a PDF and converts it to base64 encoded string.

    Args:
        content (bytes): Raw PDF content to compress
        compression_level (int): PDF compression level (1-9). Defaults to 5

    Returns:
        str: Base64 encoded compressed PDF content

    Note:
        Falls back to uncompressed base64 encoding if compression fails
    """

    try:
        reader = PdfReader(BytesIO(content))
        output = BytesIO()
        writer = PdfWriter(output)

        for page in reader.pages:
            writer.add_page(page)

        writer.set_compression(compression_level)
        writer.write(output)

        compressed_bytes = output.getvalue()
        return base64.b64encode(compressed_bytes).decode("utf-8")
    except Exception as e:
        return base64.b64encode(content).decode("utf-8")
