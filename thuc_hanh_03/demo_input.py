from utils import tokenize_sentences

data= tokenize_sentences("window xp", stopwords=set(), remove_stopwords=False)

print(data)