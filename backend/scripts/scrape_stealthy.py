import sys
import argparse
from scrapling import StealthyFetcher

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="The URL to scrape")
    parser.add_argument("output", help="The output file for HTML")
    args = parser.parse_args()

    print(f"Initializing StealthyFetcher...", file=sys.stderr)
    fetcher = StealthyFetcher()
    
    print(f"Fetching {args.url}...", file=sys.stderr)
    response = fetcher.fetch(args.url)
    
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(response.text)
    
    print(f"Saved to {args.output}", file=sys.stderr)

if __name__ == "__main__":
    main()
