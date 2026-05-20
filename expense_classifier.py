import anthropic

client = anthropic.Anthropic()

sample_expenses = "Uber - £12.50\nLunch at Pret - £8.99\nCoffee - £3.50\nTrain - £45.00"

message = client.messages.create(
    model="claude-opus-4-20250514",
    max_tokens=500,
    messages=[
        {
            "role": "user",
            "content": f"Categorize these expenses: {sample_expenses}"
        }
    ]
)

print(message.content[0].text)
