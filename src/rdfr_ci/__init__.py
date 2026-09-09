"""RDFR-CI reference implementation and evaluation harness."""
from .risk import composite_risk, validate_weights
from .authority import AuthorityState, authority_from_score, boundary_margin, authority_ceiling
from .forensic import forensic_quality, forensic_risk
from .consequence import consequence_risk
from .ai_risk import ai_specific_risk
from .exposure import tail_var_exposure, normalized_exposure
from .agent_authority import child_authority, capability_intersection
from .gates import GateStatus, GateDecision, final_authority
__all__=["composite_risk","validate_weights","AuthorityState","authority_from_score","boundary_margin","authority_ceiling","forensic_quality","forensic_risk","consequence_risk","ai_specific_risk","tail_var_exposure","normalized_exposure","child_authority","capability_intersection","GateStatus","GateDecision","final_authority"]
__version__="1.3.0"
