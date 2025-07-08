import os
from openai import OpenAI
import sys

def main():
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        print("OpenAI API Key not found. Please ensure your OPENAI_API_KEY environment variable is set. Exiting...")
        sys.exit(1)

    print("Type your prompt and then press Enter. Type 'exit' to quit.")

    while True:
        try:
            user_input = input("Enter your prompt: ")
            if user_input.lower() == 'exit':
                print("Exiting application.")
                break

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": user_input}
                ]
            )
            print("\nAI Response:")
            print(response.choices[0].message.content)
            print("-" * 30)

        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please check your input or API key status.")
            print("-" * 30)

if __name__ == "__main__":
    main()