import os
questions = [
  {
    "question": "1. What is the website's fully qualified domain name that was targeted in the attack?",
    "answer": "infinitysolutions.scc"
  },
  {
    "question": "2. According to the evidence, what is the IP address associated with the attacker?",
    "answer": "105.51.2.220"
  },
  {
    "question": "3. What is the complete name of the attacker's Internet Service Provider (ISP)?",
    "answer": "Safaricom Limited"
  },
  {
    "question": "4. Specify the attacker's browser name and version. (Format: BrowserName_Version)",
    "answer": "Chrome_88.0.4324.96"
  },
  {
    "question": "5. Which operating system is being used by the attacker?",
    "answer": "Linux"
  },
  {
    "question": "6. Which tool and version did the attacker employ to execute the first stage of the attack? (Format: ToolName_Version)",
    "answer": "sqlmap_1.6.2"
  },
  {
    "question": "7. Identify the name of the technique used by the attacker in the initial phase of the attack. (Case-insensitive)",
    "answer": "SQL Injection"
  },
  {
    "question": "8. Which payload for the password field successfully bypassed the security in the first phase of the attack?",
    "answer": "' OR '1'='1'--"
  },
  {
    "question": "9. Which route did the attacker utilize during the second stage of the attack?",
    "answer": "/blog/admin"
  },
  {
    "question": "10. Which sensitive file did the attacker discover in the second phase of the attack?",
    "answer": "api_keys.txt"
  }
]



def main():
    correct = 0
    for q in questions:
        print(f'{q["question"]}')
        print("Answer: ", end='', flush=True)

        try:
            response = input().strip()
        except EOFError:
            print("\nNo input received. Exiting.")
            break

        if response.lower() == q["answer"].lower():
            print("Correct!\n")
            correct += 1
        else:
            print("Wrong answer.\n")
            break

    if correct == len(questions):
        print(f"Congratulations, here is your flag: {os.environ['FLAG']}")
    
    print("Thanks for playing!")

if __name__ == "__main__":
    main()