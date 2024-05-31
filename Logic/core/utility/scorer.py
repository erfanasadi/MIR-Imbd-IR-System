import math


class Scorer:

    def __init__(self, index, number_of_documents):
        """
        Initializes the Scorer.

        Parameters
        ----------
        index : dict
            The index to score the documents with.
        number_of_documents : int
            The number of documents in the index.
        """

        self.index = index
        self.N = number_of_documents
        self.wheres = ["summaries", "genres", "stars"]
        self.where = ""

    def get_list_of_documents(self, query):
        """
        Returns a list of documents that contain at least one of the terms in the query.

        Parameters
        ----------
        query: List[str]
            The query to be scored

        Returns
        -------
        list
            A list of documents that contain at least one of the terms in the query.
        """
        list_of_documents = set()

        for term in query:
            for where in self.wheres:
                self.where = where
                if term in self.index[self.where]:
                    list_of_documents.update(self.index[self.where][term].keys())
        return list(list_of_documents)

    def get_idf(self, term):
        """
        Returns the inverse document frequency of a term.

        Parameters
        ----------
        term : str
            The term to get the inverse document frequency for.

        Returns
        -------
        float
            The inverse document frequency of the term.
        """
        df = len(self.index[self.where][term])
        if df == 0:
            return 0
        return self.N / df

    def get_query_tfs(self, query):
        """
        Returns the term frequencies of the terms in the query.

        Parameters
        ----------
        query : List[str]
            The query to get the term frequencies for.

        Returns
        -------
        dict
            A dictionary of the term frequencies of the terms in the query.
        """


        query_tfs[term] = 0
        for term in query:
            query_tfs[term] = query_tfs[term] + 1
        return query_tfs

    def calculate_tf_idf(self, term_freq, inverse_doc_freq):
        """
        Calculate TF-IDF score.

        Parameters
        ----------
        term_freq : float
            Term frequency.
        inverse_doc_freq : float
            Inverse document frequency.

        Returns
        -------
        float
            TF-IDF score.
        """
        return term_freq * inverse_doc_freq

    def compute_scores_with_vector_space_model(self, query, method):
        """
        Compute scores with vector space model.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c))
            The method to use for searching.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """
        scores = {}
        
        # Create term frequencies for the query
        query_tfs = {}
        for term in query:
            query_tfs[term] = query.count(term)
            
        # Iterate through all documents and compute scores
        for document_id in self.get_list_of_documents(query):
            scores[document_id] = {}
           
            for where in self.wheres:
                self.where = where
                score = self.get_vector_space_model_score(query, query_tfs, document_id, method)
                
                scores[document_id][self.where] = score

        return scores

    def get_vector_space_model_score(self, query, query_tfs, document_id, method):
        """
        Returns the Vector Space Model score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        query_tfs : dict
            The term frequencies of the terms in the query.
        document_id : str
            The document to calculate the score for.
        method : str ((n|l)(n|t)(n|c).(n|l)(n|t)(n|c))
            The method to use for the document and query.

        Returns
        -------
        float
            The Vector Space Model score of the document for the query.
        """
        
        # Parse the method and compute the score
        score = 0
        # Parse the method for document
        doc_tf = method[0:1]
        doc_idf = method[1:2]
        doc_normalization = method[2:3]
        # Parse the method for query
        query_tf = method[3:4]
        query_idf = method[4:5]
        query_normalization = method[4:5]
        tf_q = {}
        idf_q = {}
        tf_d = {}
        idf_d = {}
        score_d = {}
        score_q = {}
        for term in query_tfs:
           
            if term in self.index[self.where].keys():
                    
                    # Compute the score based on the method
                    if query_tf == 'n':
                        
                        tf_q[term] = query_tfs[term]
                        
                    else :
                        
                        tf_q[term] = 1+math.log(int(query_tfs[term]))
                        

                    if query_idf == 'n':
                        # no idf
                        idf_q[term] = 1
                    else:
                        idf_q[term] = self.get_idf(term)
                    
                    score_q[term] = tf_q[term] * idf_q[term]
                   
                    # Compute the score based on the method
                    #first check if term in doc
                    if document_id in self.index[self.where][term]:
                        #if term in doc
                        # Compute the score based on the method

                        if doc_tf == 'n':
                          tf_d[term] = self.index[self.where][term][document_id]
                        else:
                        
                           tf_d[term] = 1+math.log(self.index[self.where][term][document_id])
                        
                        if doc_idf == 'n':
                          # no idf
                          idf_d[term] = 1
                        else:
                          idf_d[term] = self.get_idf(term)
                        
                        score_d[term] = tf_d[term] * idf_d[term]
                        
                    else:
                        score_d[term] = 0 
            else:
                score_q[term] = 0
                score_d[term] = 0 
        # Compute the score based on the method
                    
        if query_normalization == 'c':
            score_all = math.sqrt(sum([i ** 2 for i in score_q.values()]))
            for term in query_tfs:
                score_q[term] = score_q[term] / score_all
        if doc_normalization == 'c':
            
            score_all = math.sqrt(sum([i ** 2 for i in score_d.values()]))
            if score_all != 0:
             for term in query_tfs:
                
                score_d[term] = score_d[term] / score_all
        for term in query_tfs:
            
            score += score_q[term] * score_d[term]

        return score

    def compute_scores_with_okapi_bm25(self, query, average_document_field_length, document_lengths):
        """
        Compute scores with Okapi BM25.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        dict
            A dictionary of the document IDs and their scores.
        """
        scores = {}
        for document_id in self.get_list_of_documents(query):
            score = self.get_okapi_bm25_score(query, document_id, average_document_field_length, document_lengths)
            scores[document_id] = score
        return scores

    def get_okapi_bm25_score(self, query, document_id, average_document_field_length, document_lengths):
        """
        Returns the Okapi BM25 score of a document for a query.

        Parameters
        ----------
        query: List[str]
            The query to be scored
        document_id : str
            The document to calculate the score for.
        average_document_field_length : float
            The average length of the documents in the index.
        document_lengths : dict
            A dictionary of the document lengths. The keys are the document IDs, and the values are
            the document's length in that field.

        Returns
        -------
        float
            The Okapi BM25 score of the document for the query.
        """
        # TODO: Implement Okapi BM25 scoring logic
        k1 = 1.5
        b = 0.75
        score = 0.0

        for term in query:
            if term in self.index and document_id in self.index[term]:
                tf = self.index[term][document_id]
                df = len(self.index[term])
                idf = self.get_idf(term)
                doc_length = document_lengths.get(document_id, average_document_field_length)
                score += idf * (
                        (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_length / average_document_field_length))))

        return score
