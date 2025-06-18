from enum import Enum

from pydantic import BaseModel, Field


class DetailOption(Enum):
    SIMPLE = 'einfach'
    EXTENDED = 'erweitert'


class ComputeInput(BaseModel):
    level_of_detail: DetailOption = Field(
        title='Detailgrad',
        description='Bitte wählen Sie, wie detailliert Sie die Ergebnisse haben möchten.',
        examples=[DetailOption.EXTENDED],
        default=DetailOption.EXTENDED,
    )
