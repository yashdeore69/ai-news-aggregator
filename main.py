from app.runner import run_scrapers

def main(hours: int = 24):
    results = run_scrapers(hours=hours)

    print(f"Youtube videos : {len(results['youtube'])}")
    print(f"OpenAI articles : {len(results['openai'])}")
    print(f"Anthropic articles : {len(results['anthropic'])}")

    return results

if __name__ == "__main__":
    main(hours=150)
