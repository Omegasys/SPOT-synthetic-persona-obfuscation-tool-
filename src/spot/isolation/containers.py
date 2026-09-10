"""SPOT container isolation policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ContainerConfig:
    """Configuration for an optional container backend."""

    enabled: bool = False

    runtime: str = "none"

    image: str | None = None

    read_only_root: bool = True
    no_new_privileges: bool = True

    network_disabled: bool = False

    memory_limit_mb: int = 1024
    cpu_limit: float = 1.0

    allowed_mounts: List[str] = field(
        default_factory=list
    )

    privileged: bool = False


@dataclass
class Container:
    """Metadata describing an isolated container."""

    container_id: str
    image: str
    running: bool = False


class ContainerManager:
    """Manage declarative container isolation.

    SPOT does not require Docker, Podman, or another container
    runtime. When enabled, a future backend may translate this
    policy into a runtime-specific configuration.
    """

    SUPPORTED_RUNTIMES = {
        "none",
        "podman",
        "docker",
    }

    def __init__(
        self,
        config: ContainerConfig | None = None,
    ) -> None:
        self.config = (
            config
            or ContainerConfig()
        )

        self.containers: Dict[
            str,
            Container,
        ] = {}

    def validate(self) -> None:
        """Validate container configuration."""
        if (
            self.config.runtime
            not in self.SUPPORTED_RUNTIMES
        ):
            raise ValueError(
                "Unsupported container runtime: "
                f"{self.config.runtime}"
            )

        if not self.config.enabled:
            return

        if self.config.runtime == "none":
            raise ValueError(
                "A container runtime is required when "
                "container isolation is enabled."
            )

        if not self.config.image:
            raise ValueError(
                "A container image is required."
            )

        if self.config.privileged:
            raise PermissionError(
                "Privileged containers are not permitted by SPOT."
            )

        if self.config.memory_limit_mb < 128:
            raise ValueError(
                "Container memory limit is too low."
            )

        if self.config.cpu_limit <= 0:
            raise ValueError(
                "Container CPU limit must be positive."
            )

    def create(
        self,
        container_id: str,
    ) -> Container:
        """Create container metadata."""
        self.validate()

        if not self.config.enabled:
            raise RuntimeError(
                "Container isolation is disabled."
            )

        if container_id in self.containers:
            raise ValueError(
                f"Container already exists: {container_id}"
            )

        container = Container(
            container_id=container_id,
            image=self.config.image or "",
        )

        self.containers[container_id] = container

        return container

    def start(
        self,
        container_id: str,
    ) -> Container:
        """Mark a container as running."""
        container = self.require(container_id)

        if container.running:
            return container

        container.running = True
        return container

    def stop(
        self,
        container_id: str,
    ) -> Container:
        """Mark a container as stopped."""
        container = self.require(container_id)

        container.running = False
        return container

    def require(
        self,
        container_id: str,
    ) -> Container:
        """Return a container or raise an error."""
        container = self.containers.get(container_id)

        if container is None:
            raise KeyError(
                f"Unknown container: {container_id}"
            )

        return container

    def remove(
        self,
        container_id: str,
    ) -> None:
        """Remove a stopped container."""
        container = self.require(container_id)

        if container.running:
            raise RuntimeError(
                "Cannot remove a running container."
            )

        del self.containers[container_id]

    def running(self) -> List[Container]:
        """Return running containers."""
        return [
            container
            for container in self.containers.values()
            if container.running
        ]

    def stop_all(self) -> None:
        """Stop all containers."""
        for container in self.containers.values():
            container.running = False
