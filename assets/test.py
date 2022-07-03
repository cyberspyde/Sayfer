from transformers import pipeline

pipe = pipeline("text-classification", model="roberta-large-mnli")
answer = pipe("Oh my god I love you")

print(answer)