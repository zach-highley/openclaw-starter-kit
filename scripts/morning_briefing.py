#!/usr/bin/env python3
"""
Morning Briefing Data Gatherer

Collects data for a comprehensive daily briefing:
  - Weather (wttr.in, free, no API key)
  - Stoic quote (embedded, rotated daily)
  - System health summary
  - Usage stats
  - Calendar events (if gog CLI configured)
  - Custom sections you define

Designed to feed data into your AI's morning cron job.
The AI adds personality/commentary on top of reliable data.

USAGE:
  python3 morning_briefing.py              # Full briefing (stdout)
  python3 morning_briefing.py --json       # JSON output
  python3 morning_briefing.py --section weather  # Single section
"""

import json
import subprocess
import sys
import hashlib
from datetime import datetime, date
from pathlib import Path

# === Config ===
CITY = "New+York"  # Change to your city (URL-encoded)
TEMP_UNIT = "u"     # "u" for Fahrenheit, "m" for Celsius

# === Stoic Quotes (rotated by date hash) ===
STOIC_QUOTES = [
    ("The happiness of your life depends upon the quality of your thoughts.", "Marcus Aurelius"),
    ("He who fears death will never do anything worthy of a living man.", "Seneca"),
    ("No man is free who is not master of himself.", "Epictetus"),
    ("Waste no more time arguing about what a good man should be. Be one.", "Marcus Aurelius"),
    ("It is not that we have a short time to live, but that we waste a great deal of it.", "Seneca"),
    ("First say to yourself what you would be; and then do what you have to do.", "Epictetus"),
    ("The soul becomes dyed with the color of its thoughts.", "Marcus Aurelius"),
    ("We suffer more often in imagination than in reality.", "Seneca"),
    ("Difficulties strengthen the mind, as labor does the body.", "Seneca"),
    ("You have power over your mind, not outside events. Realize this, and you will find strength.", "Marcus Aurelius"),
    ("Man is not worried by real problems so much as by his imagined anxieties about real problems.", "Epictetus"),
    ("Begin at once to live, and count each separate day as a separate life.", "Seneca"),
    ("The best revenge is not to be like your enemy.", "Marcus Aurelius"),
    ("No person is free who is not master of themselves.", "Epictetus"),
    ("It is not because things are difficult that we do not dare; it is because we do not dare that things are difficult.", "Seneca"),
    ("When you arise in the morning, think of what a precious privilege it is to be alive.", "Marcus Aurelius"),
    ("Wealth consists not in having great possessions, but in having few wants.", "Epictetus"),
    ("As is a tale, so is life: not how long it is, but how good it is, is what matters.", "Seneca"),
    ("Very little is needed to make a happy life; it is all within yourself.", "Marcus Aurelius"),
    ("He who laughs at himself never runs out of things to laugh at.", "Epictetus"),
    ("Luck is what happens when preparation meets opportunity.", "Seneca"),
    ("The impediment to action advances action. What stands in the way becomes the way.", "Marcus Aurelius"),
    ("Don't explain your philosophy. Embody it.", "Epictetus"),
    ("It is quality rather than quantity that matters.", "Seneca"),
    ("Dwell on the beauty of life. Watch the stars, and see yourself running with them.", "Marcus Aurelius"),
    ("Freedom is the only worthy goal in life. It is won by disregarding things that lie beyond our control.", "Epictetus"),
    ("True happiness is to enjoy the present, without anxious dependence upon the future.", "Seneca"),
    ("Accept the things to which fate binds you, and love the people with whom fate brings you together.", "Marcus Aurelius"),
    ("Make the best use of what is in your power, and take the rest as it happens.", "Epictetus"),
    ("Sometimes even to live is an act of courage.", "Seneca"),
    ("The universe is change; our life is what our thoughts make it.", "Marcus Aurelius"),
]

def get_daily_quote() -> dict:
    """Get today's stoic quote (deterministic rotation)."""
    today = date.today().isoformat()
    idx = int(hashlib.md5(today.encode()).hexdigest(), 16) % len(STOIC_QUOTES)
    quote, author = STOIC_QUOTES[idx]
    return {"quote": quote, "author": author}

def get_weather() -> dict:
    """Fetch weather from wttr.in (free, no API key)."""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10", f"wttr.in/{CITY}?format=j1&{TEMP_UNIT}"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            current = data.get("current_condition", [{}])[0]
            forecast = data.get("weather", [{}])[0]
            return {
                "ok": True,
                "temp": current.get("temp_F", current.get("temp_C", "?")),
                "feels_like": current.get("FeelsLikeF", current.get("FeelsLikeC", "?")),
                "condition": current.get("weatherDesc", [{}])[0].get("value", "Unknown"),
                "humidity": current.get("humidity", "?"),
                "wind": current.get("windspeedMiles", current.get("windspeedKmph", "?")),
                "high": forecast.get("maxtempF", forecast.get("maxtempC", "?")),
                "low": forecast.get("mintempF", forecast.get("mintempC", "?")),
            }
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "Failed to fetch weather"}

def get_usage() -> dict:
    """Check AI usage stats (if check_usage.py exists)."""
    script = Path.home() / "clawd/scripts/check_usage.py"
    if not script.exists():
        return {"ok": False, "error": "check_usage.py not found"}
    try:
        result = subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            return {"ok": True, **json.loads(result.stdout)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    return {"ok": False, "error": "Usage check failed"}

def get_system_health() -> dict:
    """Quick system health check."""
    try:
        script = Path.home() / "clawd/scripts/system_monitor.py"
        if script.exists():
            result = subprocess.run(
                ["python3", str(script)],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return {"ok": True, **json.loads(result.stdout)}
    except Exception:
        pass
    return {"ok": False, "error": "System monitor unavailable"}

def build_briefing() -> dict:
    """Build the full morning briefing data."""
    return {
        "date": date.today().isoformat(),
        "day": datetime.now().strftime("%A"),
        "weather": get_weather(),
        "stoic_quote": get_daily_quote(),
        "usage": get_usage(),
        "system": get_system_health(),
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Morning Briefing")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--section", help="Single section only")
    args = parser.parse_args()
    
    briefing = build_briefing()
    
    if args.section:
        section = briefing.get(args.section, {"error": f"Unknown section: {args.section}"})
        print(json.dumps(section, indent=2))
    elif args.json:
        print(json.dumps(briefing, indent=2))
    else:
        # Human-readable output
        print(f"=== Morning Briefing — {briefing['day']}, {briefing['date']} ===\n")
        
        w = briefing["weather"]
        if w.get("ok"):
            print(f"🌡️  Weather: {w['condition']}, {w['temp']}°F (feels {w['feels_like']}°F)")
            print(f"    High {w['high']}°F / Low {w['low']}°F | Humidity {w['humidity']}% | Wind {w['wind']} mph")
        else:
            print(f"🌡️  Weather: unavailable ({w.get('error', 'unknown')})")
        
        q = briefing["stoic_quote"]
        print(f"\n🏛️  \"{q['quote']}\" — {q['author']}")
        
        u = briefing["usage"]
        if u.get("ok"):
            p = u.get("primary", {})
            print(f"\n📊 Usage: {p.get('percent', '?')}% of 5-hour limit (resets {p.get('resets', '?')})")
        
        print()
