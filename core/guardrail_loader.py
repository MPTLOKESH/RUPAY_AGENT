import re

def load_guardrail_data(filepath):
    """
    Parses the guardrails text file to extract:
    1. Categories (e.g., "HARASSMENT")
    2. Refusal Messages (e.g., "Sorry, but I can't assist...")
    
    Returns a dictionary:
    {
        "Category Name": "Refusal Message"
    }
    """
    guardrails = {}
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find flow blocks
        # 1. Capture Category Name from "flow bot refuse to respond about <category>"
        # 2. Capture Message from 'bot say "..."'
        
        # We look for the refusal flow specifically, as it maps Category -> Message
        # Example:
        # flow bot refuse to respond about harassment
        #   bot say "Sorry, but I can’t assist..."
        
        pattern = r"flow bot refuse to respond about (.+?)\n\s+bot say \"(.+?)\""
        matches = re.findall(pattern, content)
        
        for category_slug, message in matches:
            # Convert slug to Title Case for better matching (e.g., "human trafficking" -> "Human Trafficking")
            category_name = category_slug.replace("_", " ").title()
            guardrails[category_name] = message
            
        print(f"[GuardrailLoader] Loaded {len(guardrails)} categories from {filepath}")
        return guardrails

    except Exception as e:
        print(f"[GuardrailLoader] Error loading file: {e}")
        return {}
