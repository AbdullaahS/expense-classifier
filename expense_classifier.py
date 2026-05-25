import anthropic
import csv
import json
import sys

client = anthropic.Anthropic()

def categorize_expenses(expenses_text):
    """Send expenses to Claude for categorization"""
    try:
        message = client.messages.create(
            model="claude-opus-4-20250514",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"Categorize these expenses: {expenses_text}"
                }
            ]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def read_csv_file(filepath):
    """Read expenses from CSV file"""
    expenses = []
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row:
                    expenses.append(row)
        return expenses
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found")
        sys.exit(1)

def format_expenses(expenses):
    """Format expenses for Claude"""
    formatted = ""
    for expense in expenses:
        desc = expense.get('description', 'Unknown')
        amount = expense.get('amount', '0')
        formatted += f"{desc} - £{amount}\n"
    return formatted

def export_to_json(expenses, result, filename="expenses_report.json"):
    """Export results to JSON file"""
    report = {
        "expenses": [
            {
                "description": exp.get('description', 'Unknown'),
                "amount": float(exp.get('amount', 0))
            }
            for exp in expenses
        ],
        "analysis": result,
        "exported_to": filename
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    return filename

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        print(f"Reading expenses from {csv_file}...")
        expenses = read_csv_file(csv_file)
        expenses_text = format_expenses(expenses)
    else:
        expenses = [
            {'description': 'Uber', 'amount': '12.50'},
            {'description': 'Lunch at Pret', 'amount': '8.99'},
            {'description': 'Coffee', 'amount': '3.50'},
            {'description': 'Train', 'amount': '45.00'}
        ]
        expenses_text = format_expenses(expenses)
        print("Using sample expenses")
    
    print("\nAnalyzing expenses...\n")
    result = categorize_expenses(expenses_text)
    print(result)
    
    # Export to JSON
    json_file = export_to_json(expenses, result)
    print(f"\n✓ Exported to {json_file}")
