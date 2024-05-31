import re

import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize




class Preprocessor:

    def __init__(self, documents: list):
        """
        Initialize the class.

        Parameters
        ----------
        documents : list
            The list of documents to be preprocessed, path to stop words, or other parameters.
        """
        self.documents = documents
        with open('stopwords.txt', 'r') as f:
            self.stopwords = set(f.read().splitlines())
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

    def preprocess(self):
        """
        Preprocess the text using the methods in the class.

        Returns
        ----------
        List[str]
            The preprocessed documents.
        """
        preprocessed_documents = {}

        for document in self.documents:
            preprocessed_document = {}
            for attr, value in document.items():
                preprocessed_document[attr] = []
            for attr, value in document.items():

                if document[attr]:
                    if type(document[attr]) != type("s"):
                        for item in document[attr]:
                            if attr != "reviews":
                                item = self.normalize(item)

                                item = self.remove_links(item)
                                item = self.remove_punctuations(item)

                                # item =self.tokenize(item))
                                item = self.remove_stopwords(item)
                                preprocessed_document[attr].append(item)
                    else:
                        document[attr] = self.normalize(document[attr])
                        document[attr] = self.remove_links(document[attr])
                        document[attr] = self.remove_punctuations(document[attr])
                        document[attr] = self.remove_stopwords(document[attr])
                        preprocessed_document[attr]=document[attr]

            preprocessed_documents[document["id"]] = preprocessed_document
            print(list(preprocessed_documents))

        return list(preprocessed_documents)

    def normalize(self, text: str):
        """
        Normalize the text by converting it to a lower case, stemming, lemmatization, etc.

        Parameters
        ----------
        text : str
            The text to be normalized.

        Returns
        ----------
        str
            The normalized text.
        """
        # Convert text to lowercase
        text = text.lower()
        # Tokenize text
        tokens = word_tokenize(text)
        # Remove stopwords and non-alphabetic tokens
        tokens = [word for word in tokens if  word not in self.stopwords]
        # Lemmatize tokens
        tokens = [self.stemmer.stem(self.lemmatizer.lemmatize(word)) for word in tokens]
        return ' '.join(tokens)

    def remove_links(self, text: str):
        """
        Remove links from the text.

        Parameters
        ----------
        text : str
            The text to be processed.

        Returns
        ----------
        str
            The text with links removed.
        """
        # Remove various types of links using regular expressions
        patterns = [r'\S*http\S*', r'\S*www\S*', r'\S+\.ir\S*', r'\S+\.com\S*', r'\S+\.org\S*', r'\S*@\S*']
        for pattern in patterns:
            text = re.sub(pattern, '', text)
        return text

    def remove_punctuations(self, text: str):
        """
        Remove punctuations from the text.

        Parameters
        ----------
        text : str
            The text to be processed.

        Returns
        ----------
        str
            The text with punctuations removed.
        """
        # Remove punctuations using regular expression
        return re.sub(r'[^\w\s]', '', text)

    def tokenize(self, text: str):
        """
        Tokenize the words in the text.

        Parameters
        ----------
        text : str
            The text to be tokenized.

        Returns
        ----------
        list
            The list of words.
        """
        # For now, let's split text into words by whitespace
        return text.split(" ")

    def remove_stopwords(self, words: str):
        """
        Remove stopwords from the list of words.

        Parameters
        ----------
        words : list
            The list of words to remove stopwords from.

        Returns
        ----------
        list
            The list of words with stopwords removed.
        """
        words = words.split()
        # Remove stopwords from the list of words
        return " ".join(word for word in words if word not in self.stopwords)
