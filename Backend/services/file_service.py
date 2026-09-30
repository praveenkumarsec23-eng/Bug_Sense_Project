from pathlib import Path


# =========================================================
# SUPPORTED SOURCE FILES
# =========================================================

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".java": "java",
    ".js": "javascript",
    ".ts": "typescript",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".cs": "csharp",
    ".php": "php"
}


MAX_FILE_SIZE = 1 * 1024 * 1024


# =========================================================
# CUSTOM FILE VALIDATION ERROR
# =========================================================

class SourceFileError(Exception):
    pass


# =========================================================
# GET FILE EXTENSION
# =========================================================

def get_file_extension(filename: str) -> str:

    if not filename:
        raise SourceFileError(
            "File name is missing"
        )

    return Path(filename).suffix.lower()


# =========================================================
# DETECT PROGRAMMING LANGUAGE
# =========================================================

def detect_language(filename: str) -> str:

    extension = get_file_extension(filename)

    language = SUPPORTED_EXTENSIONS.get(
        extension
    )

    if not language:
        raise SourceFileError(
            "Unsupported source file type"
        )

    return language


# =========================================================
# VALIDATE SOURCE FILE
# =========================================================

def validate_source_file(
    filename: str,
    file_content: bytes
):

    extension = get_file_extension(
        filename
    )

    if extension not in SUPPORTED_EXTENSIONS:
        raise SourceFileError(
            "Unsupported file type. "
            "Supported files: "
            ".py, .java, .js, .ts, .c, "
            ".cpp, .cc, .cxx, .cs, .php"
        )

    if not file_content:
        raise SourceFileError(
            "Uploaded source file is empty"
        )

    if len(file_content) > MAX_FILE_SIZE:
        raise SourceFileError(
            "Source file is too large. "
            "Maximum allowed size is 1 MB"
        )


# =========================================================
# DECODE SOURCE CODE
# =========================================================

def decode_source_code(
    file_content: bytes
) -> str:

    try:
        source_code = file_content.decode(
            "utf-8"
        )

    except UnicodeDecodeError:
        raise SourceFileError(
            "Unable to read source file. "
            "Please upload a UTF-8 encoded text file"
        )

    if not source_code.strip():
        raise SourceFileError(
            "Uploaded source file contains no code"
        )

    return source_code


# =========================================================
# PROCESS SOURCE FILE
# =========================================================

def process_source_file(
    filename: str,
    file_content: bytes
):

    validate_source_file(
        filename,
        file_content
    )

    language = detect_language(
        filename
    )

    source_code = decode_source_code(
        file_content
    )

    return {
        "filename": filename,
        "language": language,
        "code": source_code,
        "size": len(file_content)
    }