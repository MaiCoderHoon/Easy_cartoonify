"""
Data models and configuration settings for Easy Cartoonify.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Union
from easy_cartoonify.exceptions import InvalidConfigError


class CartoonStyle(str, Enum):
    """Supported cartoonization algorithms and aesthetic styles."""

    STYLE_1 = "style_1"          # Smooth painterly cartoon (legacy style 1)
    STYLE_2 = "style_2"          # Crisp vibrant cartoon (legacy style 2)
    CLASSIC = "classic"          # Classic comic book cartoon (bilateral + adaptive edges)
    PENCIL_GRAY = "pencil_gray"  # Monochromatic pencil sketch
    PENCIL_COLOR = "pencil_color"# Colored pencil sketch
    EDGE_PRESERVE = "edge_preserve"  # Edge-preserving photographic stylization

    @classmethod
    def from_input(cls, value: Union[str, int, "CartoonStyle"]) -> "CartoonStyle":
        """
        Normalize user input (numeric string, number, or style name) into a CartoonStyle.
        
        Supports legacy inputs "1" and "2", names like "classic", "style_1", etc.
        """
        if isinstance(value, cls):
            return value

        val_str = str(value).strip().lower()
        mapping = {
            "1": cls.STYLE_1,
            "style1": cls.STYLE_1,
            "style_1": cls.STYLE_1,
            "smooth": cls.STYLE_1,
            "2": cls.STYLE_2,
            "style2": cls.STYLE_2,
            "style_2": cls.STYLE_2,
            "vibrant": cls.STYLE_2,
            "3": cls.CLASSIC,
            "classic": cls.CLASSIC,
            "comic": cls.CLASSIC,
            "4": cls.PENCIL_GRAY,
            "sketch": cls.PENCIL_GRAY,
            "pencil": cls.PENCIL_GRAY,
            "pencil_gray": cls.PENCIL_GRAY,
            "5": cls.PENCIL_COLOR,
            "color_sketch": cls.PENCIL_COLOR,
            "pencil_color": cls.PENCIL_COLOR,
            "6": cls.EDGE_PRESERVE,
            "edge": cls.EDGE_PRESERVE,
            "edge_preserve": cls.EDGE_PRESERVE,
            "subtle": cls.EDGE_PRESERVE,
        }

        if val_str in mapping:
            return mapping[val_str]

        valid_options = ", ".join(sorted(set(mapping.keys())))
        raise InvalidConfigError(
            f"Invalid style '{value}'. Supported styles: {valid_options}"
        )


@dataclass
class CartoonConfig:
    """
    Configuration parameters for cartoonification pipelines.
    """

    style: CartoonStyle = CartoonStyle.STYLE_1

    # Stylization parameters (Styles 1 & 2)
    sigma_s: float = 150.0  # Spatial smoothing factor (0-200)
    sigma_r: float = 0.25   # Color range smoothing factor (0.0-1.0)

    # Classic cartoon parameters (Style 3)
    bilateral_d: int = 9                  # Neighborhood diameter
    bilateral_sigma_color: float = 75.0   # Filter sigma in the color space
    bilateral_sigma_space: float = 75.0   # Filter sigma in the coordinate space
    bilateral_passes: int = 5             # Number of bilateral filter iterations
    edge_block_size: int = 9              # Adaptive threshold neighborhood size (odd)
    edge_c: float = 2.0                   # Constant subtracted from mean

    # Pencil sketch parameters (Styles 4 & 5)
    sketch_sigma_s: float = 60.0
    sketch_sigma_r: float = 0.07
    sketch_shade_factor: float = 0.05

    def __post_init__(self) -> None:
        """Validate parameter boundaries."""
        if isinstance(self.style, (str, int)):
            self.style = CartoonStyle.from_input(self.style)

        if self.sigma_s <= 0 or self.sigma_s > 500:
            raise InvalidConfigError(f"sigma_s must be between 0 and 500, got {self.sigma_s}")

        if not (0.0 < self.sigma_r <= 1.0):
            raise InvalidConfigError(f"sigma_r must be between 0.0 and 1.0, got {self.sigma_r}")

        if self.bilateral_passes < 1 or self.bilateral_passes > 20:
            raise InvalidConfigError(f"bilateral_passes must be 1-20, got {self.bilateral_passes}")

        if self.edge_block_size % 2 == 0 or self.edge_block_size < 3:
            raise InvalidConfigError(
                f"edge_block_size must be an odd integer >= 3, got {self.edge_block_size}"
            )

    @classmethod
    def default_for_style(cls, style: Union[str, int, CartoonStyle]) -> "CartoonConfig":
        """Returns recommended tuned config for a specific style."""
        resolved_style = CartoonStyle.from_input(style)
        if resolved_style == CartoonStyle.STYLE_1:
            return cls(style=resolved_style, sigma_s=150.0, sigma_r=0.25)
        elif resolved_style == CartoonStyle.STYLE_2:
            return cls(style=resolved_style, sigma_s=60.0, sigma_r=0.50)
        elif resolved_style == CartoonStyle.CLASSIC:
            return cls(
                style=resolved_style,
                bilateral_d=9,
                bilateral_sigma_color=75.0,
                bilateral_sigma_space=75.0,
                bilateral_passes=5,
                edge_block_size=9,
                edge_c=2.0,
            )
        elif resolved_style in (CartoonStyle.PENCIL_GRAY, CartoonStyle.PENCIL_COLOR):
            return cls(
                style=resolved_style,
                sketch_sigma_s=60.0,
                sketch_sigma_r=0.07,
                sketch_shade_factor=0.05,
            )
        elif resolved_style == CartoonStyle.EDGE_PRESERVE:
            return cls(style=resolved_style, sigma_s=60.0, sigma_r=0.4)
        return cls(style=resolved_style)
