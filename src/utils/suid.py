"""Session ID utility functions."""

import uuid


def get_suid() -> str:
    """
    Generate a unique session ID (SUID) using UUID4.

    The value is a canonical RFC 4122 UUID (hex groups separated by
    hyphens) generated with uuid.uuid4().

    Returns:
        str: A UUID4 string suitable for use as a session identifier.
    """
    return str(uuid.uuid4())


def check_suid(suid: str) -> bool:
    """
    Check if given string is a proper session ID.

    Returns True if the string is a valid UUID, False otherwise.

    Parameters:
        suid (str): UUID value to validate — accepts a UUID string,
        or a llama-stack conversation ID (48-char hex, optionally with conv_ prefix).

    Notes:
        Validation accepts:
        1. Standard UUID format (e.g., '550e8400-e29b-41d4-a716-446655440000')
        2. 48-character hex string (llama-stack format)
        3. 'conv_' prefix + 48-character hex string (53 chars total)
    """
    if not isinstance(suid, str):
        return False

    # Strip 'conv_' prefix if present
    hex_part = suid[5:] if suid.startswith("conv_") else suid

    # Check for 48-char hex string (llama-stack conversation ID format)
    if len(hex_part) == 48:
        try:
            int(hex_part, 16)
            return True
        except ValueError:
            return False

    # Check for standard UUID format
    try:
        uuid.UUID(suid)
        return True
    except (ValueError, TypeError):
        return False


def normalize_conversation_id(conversation_id: str) -> str:
    """
    Normalize conversation ID by stripping 'conv_' prefix if present.

    Args:
        conversation_id: The conversation ID to normalize

    Returns:
        str: The normalized conversation ID without 'conv_' prefix
    """
    return (
        conversation_id[5:] if conversation_id.startswith("conv_") else conversation_id
    )


def to_llama_stack_conversation_id(conversation_id: str) -> str:
    """
    Convert a normalized conversation ID to llama-stack format with 'conv_' prefix.

    Args:
        conversation_id: The conversation ID to convert

    Returns:
        str: The conversation ID with 'conv_' prefix
    """
    return (
        f"conv_{conversation_id}"
        if not conversation_id.startswith("conv_")
        else conversation_id
    )
