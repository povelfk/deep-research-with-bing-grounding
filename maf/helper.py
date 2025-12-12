import datetime
import os

def save_report(report):
    """Saves the final report to a markdown file."""

    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)

    current_datatime = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
    with open(f"reports/report_{current_datatime}.md", "w", encoding="utf-8") as f:
        f.write(report)

def main():
    save_report("hej")


if __name__ == '__main__':
    main()