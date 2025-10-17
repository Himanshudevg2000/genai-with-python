import tiktoken

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hey There! My name is Himanshu Devgade"

tokens = enc.encode(text)

print("Tokens - ",tokens)

# tokens - [25216, 3274, 0, 3673, 1308, 382, 24218, 616, 6916, 11674, 70, 973]

decodedToken = enc.decode([25216, 3274, 0, 3673, 1308, 382, 24218, 616, 6916, 11674, 70, 973])

print("Decoded Tokens - ", decodedToken)