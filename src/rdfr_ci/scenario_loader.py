
"""Scenario catalog loading and schema validation."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Literal
import yaml
from pydantic import BaseModel, Field, model_validator
from .risk import validate_weights

class Scenario(BaseModel):
    scenario_id: str
    title: str
    sector: str
    asset_type: str
    attack_description: str
    defensive_action: str
    reversibility: str
    blast_radius: str
    physical_process_effect: str
    E: float = Field(ge=0, le=1)
    D: float = Field(ge=0, le=1)
    A: float = Field(ge=0, le=1)
    F: float = Field(ge=0, le=1)
    C: float = Field(ge=0, le=1)
    weights: Dict[str,float]
    beta_vector: Dict[str,float]
    consequence_components: Dict[str,float] | None = None
    gate_states: Dict[str,str]
    gate_caps: Dict[str,int]
    provisional_authority: str | None = None
    final_authority: str | None = None
    binding_constraint: str | None = None
    boundary_margin: float | None = None
    assumptions: List[str] = []
    evidence_status: str
    illustrative_or_empirical: Literal['illustrative','empirical','pre_specified','future_work']

    @model_validator(mode='after')
    def validate_vectors(self):
        validate_weights(self.weights)
        if abs(sum(self.beta_vector.values())-1.0)>1e-9:
            raise ValueError('beta_vector must sum to 1')
        return self

    def values(self):
        return {k:getattr(self,k) for k in ('E','D','A','F','C')}

def load_catalog(path):
    data = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    if isinstance(data, dict) and 'scenarios' in data:
        data = data['scenarios']
    return [Scenario.model_validate(x) for x in data]
