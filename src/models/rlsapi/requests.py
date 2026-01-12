"""Request models for the RHEL Lightspeed rlsapi v1 API.

This module defines the Pydantic models used for validating request data
for the /infer endpoint in the RHEL Lightspeed Command Line Assistant (CLA) API.
"""

from pydantic import Field, field_validator

from models.config import ConfigurationBase


class RlsapiV1Attachment(ConfigurationBase):
    """Model representing file attachment data in a RHEL Lightspeed request.

    Attributes:
        contents: File contents as string
        mimetype: MIME type of the attachment
    """

    contents: str = ""
    mimetype: str = ""


class RlsapiV1Terminal(ConfigurationBase):
    """Model representing terminal output in a RHEL Lightspeed request.

    Attributes:
        output: Terminal output text
    """

    output: str = ""


class RlsapiV1SystemInfo(ConfigurationBase):
    """Model representing system information in a RHEL Lightspeed request.

    Attributes:
        os: Operating system name
        version: OS version
        arch: System architecture
        system_id: Unique system identifier (can be set via 'id' alias)
    """

    os: str = ""
    version: str = ""
    arch: str = ""
    system_id: str = Field(default="", alias="id")


class RlsapiV1CLA(ConfigurationBase):
    """Model representing Command Line Assistant information.

    Attributes:
        nevra: NEVRA (Name-Epoch:Version-Release.Architecture) string
        version: CLA version
    """

    nevra: str = ""
    version: str = ""


class RlsapiV1Context(ConfigurationBase):
    """Model representing context information in a RHEL Lightspeed request.

    Attributes:
        stdin: Standard input content
        attachments: File attachment data
        terminal: Terminal output data
        systeminfo: System information
        cla: Command Line Assistant information
    """

    stdin: str = ""
    attachments: RlsapiV1Attachment = Field(default_factory=RlsapiV1Attachment)
    terminal: RlsapiV1Terminal = Field(default_factory=RlsapiV1Terminal)
    systeminfo: RlsapiV1SystemInfo = Field(default_factory=RlsapiV1SystemInfo)
    cla: RlsapiV1CLA = Field(default_factory=RlsapiV1CLA)


class RlsapiV1InferRequest(ConfigurationBase):
    """Model representing an inference request to the RHEL Lightspeed API.

    This is the main request model for the /infer endpoint, containing
    the user's question and associated context information.

    Example:
        request = RlsapiV1InferRequest(
            question="How do I list files?",
            context=RlsapiV1Context(
                systeminfo=RlsapiV1SystemInfo(os="RHEL", version="9.3"),
                terminal=RlsapiV1Terminal(output="bash: command not found"),
            ),
        )

    Attributes:
        question: The user's question or request
        context: Contextual information about the user's environment
        skip_rag: Whether to skip RAG (Retrieval Augmented Generation)
    """

    question: str = Field(..., min_length=1)
    context: RlsapiV1Context = Field(default_factory=RlsapiV1Context)
    skip_rag: bool = False

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate and strip the question field.

        Args:
            v: The question string to validate

        Returns:
            The stripped question string

        Raises:
            ValueError: If question is empty or whitespace-only
        """
        stripped = v.strip()
        if not stripped:
            raise ValueError("Question cannot be empty or whitespace-only")
        return stripped

    def get_input_source(self) -> str:
        """Get the combined input from all available sources.

        Combines question, stdin, attachment contents, and terminal output
        into a single string with double newlines as separators.
        Only non-empty sources are included.

        Returns:
            Combined input string from all available sources
        """
        sources = []

        # Add question (required field, already validated)
        sources.append(self.question)

        # Add optional context sources if they have content
        if self.context.stdin:
            sources.append(self.context.stdin)

        if self.context.attachments.contents:
            sources.append(self.context.attachments.contents)

        if self.context.terminal.output:
            sources.append(self.context.terminal.output)

        return "\n\n".join(sources)
