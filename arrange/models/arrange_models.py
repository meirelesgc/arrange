import locale
from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Arrange(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    doc_id: UUID
    output: Optional[dict] = None
    status: Literal['STANDBY', 'IN-PROCESS', 'FAILED', 'DONE']
    type: Literal['DETAILS', 'PATIENTS', 'METRICS']
    duration: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


def try_parse_date(value: str) -> date:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
    # fmt: off
    fmts = ['%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%Y-%m-%d %H:%M',
        '%d DE %B DE %Y',]
    # fmt: on
    for fmt in fmts:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


class ArrangePatient(BaseModel):
    full_name: Optional[str] = Field(
        default=None, description='Full name of the patient.'
    )
    date_of_birth: Optional[date] = Field(
        default=None,
        description='Date of birth of the patient (formato: AAAA-MM-DD).',
    )
    gender: Optional[Literal['MALE', 'FEMALE']] = Field(
        default=None, description="Patient's gender, if available."
    )
    phone: Optional[str] = Field(
        default=None, description='Phone number for contact.'
    )
    email: Optional[str] = Field(
        default=None, description='Email address for contact.'
    )
    admission_date: Optional[date] = Field(
        default=None,
        description='Date of hospital admission (formato: AAAA-MM-DD).',
    )

    @field_validator('date_of_birth', 'admission_date', mode='before')
    @classmethod
    def parse_flexible_date(cls, v):
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            return try_parse_date(v)
        return None


class ArrangeDetails(BaseModel):
    hospital_name: Optional[str] = Field(
        default=None, description='Nome do hospital emissor do documento.'
    )
    cnpj: Optional[str] = Field(
        default=None,
        description='CNPJ da instituição responsável pelo documento.',
    )
    # fmt: off
    document_type: Optional[Literal[
            'MEDICAL_EVOLUTION', 'LABORATORY_EXAM', 'MEDICAL_PRESCRIPTION',
            'MEDICAL_REPORT', 'FOLLOW_UP_LETTER', 'DISCHARGE_SUMMARY',
            'MEDICAL_CERTIFICATE', 'CONSENT_TERMS', 'MEDICAL_RECORD',
        ]] = Field(
        default=None,
        description='Tipo do documento clínico (ex: Evolução, Carta de Acompanhamento).',
    )
    # fmt: on
    issued_by: Optional[str] = Field(
        default=None,
        description='Nome do profissional responsável pelo documento.',
    )
    printing_datetime: Optional[date] = Field(
        default=None,
        description='Data de emissão ou impressão do documento (formato: AAAA-MM-DD).',
    )

    @field_validator('printing_datetime', mode='before')
    @classmethod
    def parse_flexible_date(cls, v):
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            return try_parse_date(v)
        return None
