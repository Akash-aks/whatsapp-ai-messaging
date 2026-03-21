"""
GUI Styling Constants
Defines colors, fonts, and styling for the application
"""

class Colors:
    """Color palette for the application"""
    PRIMARY = "#0088cc"
    PRIMARY_DARK = "#006699"
    SECONDARY = "#25D366"  # WhatsApp green
    BACKGROUND = "#f5f5f5"
    SURFACE = "#ffffff"
    TEXT_PRIMARY = "#333333"
    TEXT_SECONDARY = "#666666"
    SUCCESS = "#28a745"
    WARNING = "#ffc107"
    ERROR = "#dc3545"
    INFO = "#17a2b8"
    BORDER = "#dddddd"
    HOVER = "#e9ecef"

class Fonts:
    """Font configurations"""
    FAMILY = "Segoe UI"
    SIZE_TITLE = 18
    SIZE_HEADING = 14
    SIZE_NORMAL = 10
    SIZE_SMALL = 9
    
    TITLE = (FAMILY, SIZE_TITLE, "bold")
    HEADING = (FAMILY, SIZE_HEADING, "bold")
    NORMAL = (FAMILY, SIZE_NORMAL)
    NORMAL_BOLD = (FAMILY, SIZE_NORMAL, "bold")
    SMALL = (FAMILY, SIZE_SMALL)

class Padding:
    """Padding constants"""
    SMALL = 5
    MEDIUM = 10
    LARGE = 20
    XLARGE = 30