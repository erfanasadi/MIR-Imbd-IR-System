from indexer.index_reader import Index_reader
from indexer.indexes_enum import Indexes, Index_types
from scorer import Scorer
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.tokenize import word_tokenize


class SearchEngine:
    def __init__(self):
        """
        Initializes the search engine.

        """
        path = './indexer/indexes/'

        self.document_indexes = {
            Indexes.STARS.value: Index_reader(path, Indexes.STARS).get_index(),
            Indexes.GENRES.value: Index_reader(path, Indexes.GENRES).get_index(),
            Indexes.SUMMARIES.value: Index_reader(path, Indexes.SUMMARIES).get_index()
        }
        self.tiered_index = {
            Indexes.STARS: Index_reader(path, Indexes.STARS, Index_types.TIERED).get_index(),
            Indexes.GENRES: Index_reader(path, Indexes.GENRES, Index_types.TIERED).get_index(),
            Indexes.SUMMARIES: Index_reader(path, Indexes.SUMMARIES, Index_types.TIERED).get_index()
        }
        self.document_lengths_index = {
            Indexes.STARS: Index_reader(path, Indexes.STARS, Index_types.DOCUMENT_LENGTH).get_index(),
            Indexes.GENRES: Index_reader(path, Indexes.GENRES, Index_types.DOCUMENT_LENGTH).get_index(),
            Indexes.SUMMARIES: Index_reader(path, Indexes.SUMMARIES, Index_types.DOCUMENT_LENGTH).get_index()
        }
        self.metadata_index = Index_reader(path, Indexes.DOCUMENTS, Index_types.METADATA).get_index()

    def search(self, query, method, weights, safe_ranking=True, max_results=10):
        """
        searches for the query in the indexes.

        Parameters
        ----------
        query : str
            The query to search for.
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c)) | OkapiBM25
            The method to use for searching.
        weights: dict
            The weights of the fields.
        safe_ranking : bool
            If True, the search engine will search in whole index and then rank the results. 
            If False, the search engine will search in tiered index.
        max_results : int
            The maximum number of results to return. If None, all results are returned.

        Returns
        -------
        list
            A list of tuples containing the document IDs and their scores sorted by their scores.
        """

        scores = {}
        if safe_ranking:
            self.find_scores_with_safe_ranking(query, method, weights, scores)
        else:
            self.find_scores_with_unsafe_ranking(query, method, weights, max_results, scores)

        

        

        result = sorted(scores, key=lambda x: x[1], reverse=True)
        if max_results is not None:
            result = result[:max_results]

        return result

    def aggregate_scores(self, weights, scores, final_scores):
        """
        Aggregates the scores of the fields.

        Parameters
        ----------
        weights : dict
            The weights of the fields.
        scores : dict
            The scores of the fields.
        final_scores : dict
            The final scores of the documents.
        """
        for doc_id in scores:
            final_scores[doc_id] = 0  # Initialize the final score for the document
            for field, weight in weights.items():
                final_scores[doc_id] += scores[doc_id][field] * weight  # Aggregate the weighted scores

    def find_scores_with_unsafe_ranking(self, query, method, weights, max_results, scores):
        """
        Finds the scores of the documents using the unsafe ranking method using the tiered index.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c)) | OkapiBM25
            The method to use for searching.
        weights: dict
            The weights of the fields.
        max_results : int
            The maximum number of results to return.
        scores : dict
            The scores of the documents.
        """
        for field in weights:
            for tier in ["first_tier", "second_tier", "third_tier"]:
                # Retrieve scores for each tier and update the scores dictionary
                tier_scores = self.tiered_index[field][tier]
                for doc_id, score in tier_scores.items():
                    scores.setdefault(doc_id, {}).setdefault(field, 0)
                    scores[doc_id][field] += score

    def find_scores_with_safe_ranking(self, query, method, weights, scores):
        """
        Finds the scores of the documents using the safe ranking method.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c)) | OkapiBM25
            The method to use for searching.
        weights: dict
            The weights of the fields.
        scores : dict
            The scores of the documents.
        """

        scorer = Scorer(self.document_indexes, self.metadata_index["document_count"])

        # Compute scores for each document based on the method
        if method == "OkapiBM25":
            # Use Okapi BM25 scoring method
            average_document_field_length = self.calculate_average_document_field_length()
            document_lengths = self.document_lengths_index
            scores.update(scorer.compute_scores_with_okapi_bm25(query, average_document_field_length, document_lengths))
        else:
            # Use Vector Space Model scoring method
            scores.update(scorer.compute_scores_with_vector_space_model(query, method))

        # Apply weights to the scores

        for doc_id in scores:
            for field, weight in weights.items():
                scores[doc_id][field.value] *= weight


def merge_scores(self, scores1, scores2):
    """
    Merges two dictionaries of scores.

    Parameters
    ----------
    scores1 : dict
        The first dictionary of scores.
    scores2 : dict
        The second dictionary of scores.

    Returns
    -------
    dict
        The merged dictionary of scores.
    """
    merged_scores = scores1.copy()  # Start with a copy of the first dictionary
    for doc_id, score_dict in scores2.items():
        merged_scores.setdefault(doc_id, {})
        for field, score in score_dict.items():
            merged_scores[doc_id].setdefault(field, 0)
            merged_scores[doc_id][field] += score  # Add the scores from the second dictionary
    return merged_scores


if __name__ == '__main__':
    search_engine = SearchEngine()
    query = "spider man in wonderland"
    method = "lnc.ltc"
    query = query.lower()
    # Tokenize text
    tokens = word_tokenize(query)
    # Remove stopwords and non-alphabetic tokens
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()
    with open('stopwords.txt', 'r') as f:
        stopwords = set(f.read().splitlines())
    tokens = [word for word in tokens if word not in stopwords]
    # Lemmatize tokens
    tokens = [stemmer.stem(lemmatizer.lemmatize(word)) for word in tokens]
    weights = {
        Indexes.STARS: 1,
        Indexes.GENRES: 1,
        Indexes.SUMMARIES: 1
    }
    result = search_engine.search(tokens, method, weights)

    print(result)
