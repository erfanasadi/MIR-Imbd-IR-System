import re
from collections import defaultdict


class Snippet:
    def __init__(self, number_of_words_on_each_side=5):
        """
        Initialize the Snippet

        Parameters
        ----------
        number_of_words_on_each_side : int
            The number of words on each side of the query word in the doc to be presented in the snippet.
        """
        self.number_of_words_on_each_side = number_of_words_on_each_side

    def remove_stop_words_from_query(self, query):
        """
        Remove stop words from the input string.

        Parameters
        ----------
        query : str
            The query that you need to delete stop words from.

        Returns
        -------
        str
            The query without stop words.
        """
        stop_words = set()
        with open('stopwords.txt', 'r') as f:
            stopwords = set(f.read().splitlines())
        query_words = query.split()
        query_without_stopwords = [word for word in query_words if word.lower() not in stop_words]
        return ' '.join(query_without_stopwords)

    def find_snippet(self, doc, query):
        """
        Find snippet in a doc based on a query.

        Parameters
        ----------
        doc : str
            The retrieved doc which the snippet should be extracted from that.
        query : str
            The query which the snippet should be extracted based on that.

        Returns
        -------
        final_snippet : str
            The final extracted snippet. IMPORTANT: The keyword should be wrapped by *** on both sides.
            For example: Sahwshank ***redemption*** is one of ... (for query: redemption)
        not_exist_words : list
            Words in the query which don't exist in the doc.
        """
        final_snippet = ""
        not_exist_words = []

        # Remove stop words from the query
        query = self.remove_stop_words_from_query(query)

        # Tokenize query and document
        query_tokens = query.split()
        document_tokens = re.findall(r'\b\w+\b', doc.lower())

        # Initialize snippet dictionary
        snippet_dict = defaultdict(list)

        # Find occurrences of query tokens in the document
        for token in query_tokens:
            indices = [i for i, x in enumerate(document_tokens) if x == token]
            for idx in indices:
                start_idx = max(0, idx - self.number_of_words_on_each_side)
                end_idx = min(len(document_tokens), idx + self.number_of_words_on_each_side + 1)
                window = ' '.join(document_tokens[start_idx:end_idx])
                snippet_dict[token].append(window)

        # Merge windows and identify missing tokens
        for token in query_tokens:
            if token in snippet_dict:
                final_snippet += ' ... '.join(snippet_dict[token]) + ' ... '
            else:
                not_exist_words.append(token)

        # Mark query tokens in the snippet
        for token in query_tokens:
            final_snippet = final_snippet.replace(token, f'***{token}***')

        return final_snippet.strip(), not_exist_words

if __name__ == '__main__':
 # Example usage:
 snippet_obj = Snippet()
 doc = "This code evaluates the performance of an information retrieval system. It calculates precision, recall, F1 score, MAP, NDCG, and MRR."
 query = "information retrieval system"
 final_snippet, not_exist_words = snippet_obj.find_snippet(doc, query)
 print("Snippet:", final_snippet)
 print("Words not present in the document:", not_exist_words)
