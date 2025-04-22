from pydantic import BaseModel, Field, model_validator
from typing import List, Literal, Optional
from datetime import datetime

class SarekRunOptions(BaseModel):
    mode: Literal[
        "curated_germline",
        "curated_somatic",
        "advanced_germline",
        "advanced_somatic"
    ] = Field(..., description="Which pipeline mode to run")

    # Advanced-only fields
    aligner: Optional[Literal["bwa", "bwa-mem2", "dragmap"]]
    variant_callers: Optional[List[Literal[
        "HaplotypeCaller", "FreeBayes", "DeepVariant", "Strelka2", "Mutect2"
    ]]]
    svtools:    Optional[List[Literal["Manta", "TIDDIT", "indexcov"]]]
    cnvtools:   Optional[List[Literal["CNVKit", "Control-FREEC", "ASCAT"]]]
    annotators: Optional[List[Literal["VEP", "snpEff", "bcftools"]]]

    @model_validator(mode="after")
    def check_advanced_fields(self):
        if self.mode.startswith("curated"):
            # Clear out any advanced‑only fields
            object.__setattr__(self, "aligner",        None)
            object.__setattr__(self, "variant_callers", None)
            object.__setattr__(self, "svtools",         None)
            object.__setattr__(self, "cnvtools",        None)
            object.__setattr__(self, "annotators",      None)
        else:
            # Require at least one variant caller in “advanced” modes
            if not self.variant_callers:
                raise ValueError("advanced modes require at least one variant_caller")
        return self
class UploadRecordResponse(BaseModel):
    id: int
    analysis_type: str
    original_filename: str
    saved_path: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True