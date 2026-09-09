"""Scenario catalog loading, schema validation, and v1.3 policy-semantic normalization."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Literal
import copy
import yaml
from pydantic import BaseModel, Field, model_validator
from .risk import validate_weights

V13_UNKNOWN_CAPS={'G_S':2,'G_V':2,'G_FA':2,'G_A':1,'G_H':2}

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

def normalize_v13_record(record: dict, source_schema: str | None = None) -> dict:
    """Migrate legacy illustrative gate metadata without changing E/D/A/F/C values."""
    x=copy.deepcopy(record)
    states={k:str(v).lower() for k,v in x.get('gate_states',{}).items()}
    if source_schema in (None,'1.0','1.1','1.2','1.2.0','1.2.1'):
        states={k:('unknown' if v in ('fail','not_evaluated') else v) for k,v in states.items()}
    else:
        states={k:('unknown' if v=='not_evaluated' else v) for k,v in states.items()}
    x['gate_states']=states
    x['gate_caps']=dict(V13_UNKNOWN_CAPS)
    return x

def load_catalog(path):
    root=yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    schema=None; data=root
    if isinstance(root,dict) and 'scenarios' in root:
        schema=str(root.get('schema_version','')) or None; data=root['scenarios']
    return [Scenario.model_validate(normalize_v13_record(x,schema)) for x in data]
