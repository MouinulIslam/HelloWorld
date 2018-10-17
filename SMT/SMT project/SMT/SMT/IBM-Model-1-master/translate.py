import os
import json


current_dir = os.getcwd()

def tokenize(sentence):
    return sentence.split()


def translate(tokens, model):
    return [model[word] if word in model else word for word in tokens]


def main():
	model_file = current_dir + '/data/output.json'
	sentence = 'Subject Class: Female reproduction system'
	with open(model_file, 'r') as f:
		model = json.load(f)
	tokens = tokenize(sentence)
	translated_tokens = translate(tokens, model)
	print(" ".join(translated_tokens))

if __name__ == '__main__':
    main()
