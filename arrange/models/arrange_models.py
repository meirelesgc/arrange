from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Arrange(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    doc_id: UUID
    output: Optional[dict] = None
    status: Literal['STANDBY', 'IN-PROCESS', 'FAILED', 'DONE']
    type: Literal['DETAILS', 'PATIENTS', 'METRICS']
    duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class ArrangePatient(BaseModel):
    """
    Patient-identifying and demographic information extracted from clinical
    documents.
    """

    full_name: Optional[str] = Field(
        default=None, description='Full name of the patient.'
    )
    date_of_birth: Optional[date] = Field(
        default=None, description='Date of birth of the patient.'
    )
    gender: Optional[str] = Field(
        default=None, description="Patient's gender, if available."
    )
    phone: Optional[str] = Field(
        default=None, description='Phone number for contact.'
    )
    email: Optional[str] = Field(
        default=None, description='Email address for contact.'
    )
    insurance: Optional[str] = Field(
        default=None, description='Health insurance or coverage information.'
    )
    admission_date: Optional[date] = Field(
        default=None, description='Date of hospital admission.'
    )


class ArrangeDetails(BaseModel):
    """
    Metadados essenciais para identificação e rastreabilidade de um documento
    clínico.
    """

    hospital_name: Optional[str] = Field(
        default=None, description='Nome do hospital emissor do documento.'
    )
    cnpj: Optional[str] = Field(
        default=None,
        description='CNPJ da instituição responsável pelo documento.',
    )
    document_type: Optional[str] = Field(
        default=None,
        description=(
            'Tipo do documento clínico '
            '(ex: Evolução, Carta de Acompanhamento).'
        ),
    )
    issued_by: Optional[str] = Field(
        default=None,
        description='Nome do profissional responsável pelo documento.',
    )
    printing_datetime: Optional[datetime] = Field(
        default=None,
        description=(
            'Data e hora de emissão ou impressão do documento'
            '(formato: AAAA-MM-DD HH:MM:SS).'
        ),
    )
