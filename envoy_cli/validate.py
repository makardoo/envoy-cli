"""Validation utilities for .env files — check for missing keys, duplicates, and format issues."""

from typing import Dict, List, NamedTuple


class ValidationIssue(NamedTuple):
    level: str  # 'error' or 'warning'
    message: str


class ValidationResult(NamedTuple):
    valid: bool
    issues: List[ValidationIssue]


def _parse_lines(content: str) -> List[tuple]:
    """Return list of (lineno, key, value) tuples, skipping comments/blanks."""
    entries = []
    for i, line in enumerate(content.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            entries.append((i, None, stripped))
        else:
            key, _, value = stripped.partition("=")
            entries.append((i, key.strip(), value.strip()))
    return entries


def validate_env_content(content: str) -> ValidationResult:
    """Validate raw .env file content for common issues."""
    issues: List[ValidationIssue] = []
    seen_keys: Dict[str, int] = {}
    entries = _parse_lines(content)

    for lineno, key, value in entries:
        if key is None:
            issues.append(ValidationIssue(
                level="error",
                message=f"Line {lineno}: invalid format (no '=' found): '{value}'"
            ))
            continue

        if not key:
            issues.append(ValidationIssue(
                level="error",
                message=f"Line {lineno}: empty key name."
            ))
            continue

        if key in seen_keys:
            issues.append(ValidationIssue(
                level="warning",
                message=f"Line {lineno}: duplicate key '{key}' (first seen on line {seen_keys[key]})."
            ))
        else:
            seen_keys[key] = lineno

        if not value:
            issues.append(ValidationIssue(
                level="warning",
                message=f"Line {lineno}: key '{key}' has an empty value."
            ))

    errors = [i for i in issues if i.level == "error"]
    return ValidationResult(valid=len(errors) == 0, issues=issues)


def validate_against_schema(content: str, required_keys: List[str]) -> ValidationResult:
    """Check that all required keys are present in the env content."""
    base = validate_env_content(content)
    extra_issues = list(base.issues)

    entries = _parse_lines(content)
    present = {key for _, key, _ in entries if key}

    for req in required_keys:
        if req not in present:
            extra_issues.append(ValidationIssue(
                level="error",
                message=f"Required key '{req}' is missing."
            ))

    errors = [i for i in extra_issues if i.level == "error"]
    return ValidationResult(valid=len(errors) == 0, issues=extra_issues)
