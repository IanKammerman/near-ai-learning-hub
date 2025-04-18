import os
import requests
import sys

def handle_message(message: str) -> str:
    """
    Handle incoming messages. Supports greeting and coin executive lookup.
    Commands:
      - "hello"
      - "executives <coin>"
    """
    message = message.strip()
    lower = message.lower()

    # Greeting
    if "hello" in lower:
        return "Hello, welcome to NEAR AI!"

    # Executives lookup via CoinGecko
    if lower.startswith("executives"):
        parts = message.split(None, 1)
        if len(parts) < 2 or not parts[1].strip():
            return "Please provide a coin name. Usage: 'executives <coin>'"
        coin = parts[1].strip().lower()

        url = f"https://api.coingecko.com/api/v3/coins/{coin}?localization=false"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
        except requests.RequestException as e:
            return f"Error fetching coin data: {e}"

        data = response.json()
        name = data.get("name", coin.title())
        symbol = data.get("symbol", "").upper()

        # Extract social links
        links = data.get("links", {})
        socials = {}
        homepage = links.get("homepage", [])
        if homepage and homepage[0]:
            socials['Homepage'] = homepage[0]
        for field in ['twitter_screen_name', 'facebook_username', 'subreddit_url', 'telegram_channel_identifier']:
            val = links.get(field)
            if val:
                key = field.replace('_', ' ').title()
                socials[key] = val if isinstance(val, str) else val

        # Extract team members
        team = data.get("team", [])
        execs = []
        for member in team:
            name_m = member.get('name')
            position = member.get('position')
            if name_m and position:
                execs.append(f"{name_m} - {position}")

        # Build output
        output = f"Coin: {name} ({symbol})\n"
        if socials:
            output += "Socials:\n"
            for k, v in socials.items():
                output += f"  {k}: {v}\n"
        else:
            output += "No social links available.\n"

        if execs:
            output += "Executives/Team:\n"
            for e in execs:
                output += f"  {e}\n"
        else:
            output += "No team information available on Coingecko API\n"

        return output

    return "I'm sorry, I didn't understand your message."


if __name__ == "__main__":
    # CLI: if first arg is not 'executives', assume it refers to the coin
    args = sys.argv[1:]
    if not args:
        user_input = input("Enter a message for the agent: ")
    else:
        # If user didn't prefix with 'executives', add it
        if args[0].lower() != "executives":
            user_input = "executives " + " ".join(args)
        else:
            user_input = " ".join(args)
    print(handle_message(user_input))
