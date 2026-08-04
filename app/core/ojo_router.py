"""Router facade for non-executing planning and runtime snapshots."""

from app.core.runtime_state import RuntimeState, create_runtime_state
from app.core.target_model import TargetRecord
from app.core.technique_registry import TechniqueRegistry, create_empty_registry
from app.core.x5_strategy_engine import StrategyPlan, X5StrategyEngine


class OjoRouter:
    """Coordinate registry-backed planning without starting jobs."""

    def __init__(self, registry: TechniqueRegistry | None = None) -> None:
        self.registry = registry or create_empty_registry()
        self.strategy_engine = X5StrategyEngine(self.registry)

    def plan_target(
        self,
        target: TargetRecord,
        confirmed: bool = False,
        allowlisted_target: bool = True,
        hardware_available: bool = True,
        network_available: bool = True,
        user_logic_available: bool = False,
    ) -> StrategyPlan:
        """Delegate target planning to the strategy engine."""
        return self.strategy_engine.plan_for_target(
            target=target,
            confirmed=confirmed,
            allowlisted_target=allowlisted_target,
            hardware_available=hardware_available,
            network_available=network_available,
            user_logic_available=user_logic_available,
        )

    def list_registered_technique_ids(self) -> list[str]:
        """Return registered technique ids."""
        return self.registry.list_ids()

    def get_runtime_state(self) -> RuntimeState:
        """Return a local runtime state snapshot."""
        return create_runtime_state()
