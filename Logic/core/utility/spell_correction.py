import collections


class SpellCorrection:
    def __init__(self, all_documents):
        """
        Initialize the SpellCorrection

        Parameters
        ----------
        all_documents : list of str
            The input documents.
        """
        self.all_shingled_words, self.word_counter = self.shingling_and_counting(all_documents)

    def shingle_word(self, word, k=2):
        """
        Convert a word into a set of shingles.

        Parameters
        ----------
        word : str
            The input word.
        k : int
            The size of each shingle.

        Returns
        -------
        set
            A set of shingles.
        """
        shingles = set()
        for i in range(len(word) - k + 1):
            shingles.add(word[i:i + k])
        return shingles

    def jaccard_score(self, first_set, second_set):
        """
        Calculate jaccard score.

        Parameters
        ----------
        first_set : set
            First set of shingles.
        second_set : set
            Second set of shingles.

        Returns
        -------
        float
            Jaccard score.
        """
        intersection = len(first_set.intersection(second_set))
        union = len(first_set.union(second_set))
        return intersection / union if union != 0 else 0

    def shingling_and_counting(self, all_documents):
        """
        Shingle all words of the corpus and count TF of each word.

        Parameters
        ----------
        all_documents : list of str
            The input documents.

        Returns
        -------
        all_shingled_words : dict
            A dictionary from words to their shingle sets.
        word_counter : dict
            A dictionary from words to their TFs.
        """
        all_shingled_words = dict()
        word_counter = collections.defaultdict(int)

        for document in all_documents:
            words = document.split()
            for word in words:
                shingles = self.shingle_word(word)
                all_shingled_words[word] = shingles
                word_counter[word] += 1

        return all_shingled_words, word_counter

    def find_nearest_words(self, word):
        """
        Find correct form of a misspelled word.

        Parameters
        ----------
        word : str
            The misspelled word.

        Returns
        -------
        list of str
            5 nearest words.
        """
        top5_candidates = []

        if word not in self.all_shingled_words:
            return top5_candidates

        word_shingles = self.all_shingled_words[word]
        word_tf = self.word_counter[word]

        for candidate, candidate_shingles in self.all_shingled_words.items():
            if candidate == word:
                continue

            jaccard_similarity = self.jaccard_score(word_shingles, candidate_shingles)
            candidate_tf = self.word_counter[candidate]

            # Normalize TF
            normalized_tf = candidate_tf / word_tf

            # Multiply Jaccard score by normalized TF
            score = jaccard_similarity * normalized_tf

            top5_candidates.append((candidate, score))

        # Sort candidates by score and return top 5
        top5_candidates.sort(key=lambda x: x[1], reverse=True)
        return [candidate[0] for candidate in top5_candidates[:5]]

    def spell_check(self, query):
        """
        Find correct form of a misspelled query.

        Parameters
        ----------
        query : str
            The misspelled query.

        Returns
        -------
        str
            Correct form of the query.
        """
        corrected_query = ""

        words = query.split()
        for word in words:
            nearest_words = self.find_nearest_words(word)
            if nearest_words:
                corrected_query += max(nearest_words, key=self.word_counter.get) + " "
            else:
                corrected_query += word + " "

        return corrected_query.strip()
