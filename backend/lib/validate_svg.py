# ============================================================
# PART 1 — IMPORTS
# ============================================================

import xml.etree.ElementTree as ET
import re

# ============================================================
# PART 2 — MAIN VALIDATION FUNCTION
# ============================================================

def validate_svg(svg_string):
    """
    Takes an SVG string and checks if it meets all requirements.
    Returns a dictionary: { "checks_passed": {...}, "all_passed": bool }
    """
    checks = {
        "is_valid_xml": False,
        "inside_viewbox": False,
        "has_title_and_labels": False,
        "has_animation": False,
        "no_external_resources": False 
    }

    # Clean markdown formatting
    clean_svg = re.sub(r'```xml|```svg|```', '', svg_string).strip()

    # CHECK 1: Can we parse it as XML?
    try:
        root = ET.fromstring(clean_svg)
        checks["is_valid_xml"] = True
    except ET.ParseError:
        return {"checks_passed": checks, "all_passed": False}

    # CHECK 5 (Custom): Ensure no <script> tags or EXTERNAL image links
    # We allow the standard xmlns="http://www.w3.org/2000/svg" but block external images
    has_script = re.search(r'<script', clean_svg, re.IGNORECASE)
    has_external_image = re.search(r'<image[^>]+href=["\']https?://', clean_svg, re.IGNORECASE)
    has_external_css = re.search(r'@import\s+url\(["\']?https?://', clean_svg, re.IGNORECASE)
    
    if not has_script and not has_external_image and not has_external_css:
        checks["no_external_resources"] = True

    # CHECK 2: ViewBox bounds check
    # We look for obviously out-of-bounds coordinates (ignoring paths and percentages)
    view_box = root.attrib.get("viewBox", "0 0 100 100")
    try:
        vb_parts = [float(x) for x in view_box.split()]
        max_x = vb_parts[2]
        max_y = vb_parts[3]
    except (ValueError, IndexError):
        return {"checks_passed": checks, "all_passed": False}

    inside_bounds = True
    for elem in root.iter():
        # Check explicit coordinates and sizes that are numbers (ignore percentages)
        for attr in ["x", "cx", "width"]:
            val = elem.attrib.get(attr)
            if val and re.match(r'^-?\d+(\.\d+)?$', val):
                if float(val) > (max_x * 1.5): # Allow some padding
                    inside_bounds = False
                    
        for attr in ["y", "cy", "height"]:
            val = elem.attrib.get(attr)
            if val and re.match(r'^-?\d+(\.\d+)?$', val):
                if float(val) > (max_y * 1.5): # Allow some padding
                    inside_bounds = False
                    
    checks["inside_viewbox"] = inside_bounds

    # CHECK 3: Has a title and at least 3 text labels
    has_title = False
    text_count = 0
    for elem in root.iter():
        if elem.tag.endswith("title"):
            has_title = True
        if elem.tag.endswith("text"):
            text_count += 1
    if has_title and text_count >= 3:
        checks["has_title_and_labels"] = True

    # CHECK 4: Has at least one animation
    has_smil = False
    for elem in root.iter():
        if elem.tag.endswith("animate") or elem.tag.endswith("animateTransform"):
            has_smil = True
    has_css_anim = "@keyframes" in clean_svg
    if has_smil or has_css_anim:
        checks["has_animation"] = True

    all_passed = all(checks.values())
    return {
        "checks_passed": checks,
        "all_passed": all_passed
    }