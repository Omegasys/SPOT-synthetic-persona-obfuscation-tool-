"""SPOT synthetic shopping activity."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List


@dataclass
class ShoppingActivity:
    """Prepare synthetic product-browsing activity.

    This module does not place orders, submit payment information,
    create accounts, or perform purchases.
    """

    name: str = "shopping"

    def prepare(
        self,
        categories: Iterable[str] | None = None,
        products: Iterable[str] | None = None,
        max_items: int = 5,
        **_: Any,
    ) -> Dict[str, Any]:
        """Prepare synthetic shopping research."""
        if max_items < 1:
            raise ValueError(
                "max_items must be at least 1."
            )

        selected_categories = [
            str(item)
            for item in (categories or [])
            if item
        ][:max_items]

        selected_products = [
            str(item)
            for item in (products or [])
            if item
        ][:max_items]

        return {
            "type": self.name,
            "categories": selected_categories,
            "products": selected_products,
            "max_items": max_items,
            "research_only": True,
            "synthetic": True,
            "allows_purchase": False,
            "allows_payment": False,
            "requires_execution": True,
        }
