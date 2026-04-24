from enum import Enum

from climatoology.base.i18n import N_
from pydantic import BaseModel, Field


class DetailOption(Enum):
    SIMPLE = N_('simple')
    EXTENDED = N_('extended')


class ComputeInput(BaseModel):
    level_of_detail: DetailOption = Field(
        title=N_('Degree of detail'),
        description=N_('Please choose how detailed you would like the results to be.'),
        examples=[DetailOption.EXTENDED],
        default=DetailOption.EXTENDED,
    )
