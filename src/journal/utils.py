import collections
import operator
import math


def find_similar_articles(text, other_articles):
    """Returns the top two."""
    words = text.split()
    this_counter = collections.Counter(words)
    articles = []
    for article in other_articles:
        other_counter = collections.Counter(article.unformatted_content.split())
        intersection = set(this_counter.keys()) & set(other_counter.keys())
        numerator = sum([this_counter[x] * other_counter[x] for x in intersection])

        this_sum = sum([v**2 for v in this_counter.values()])
        other_sum = sum([v**2 for v in other_counter.values()])
        denominator = math.sqrt(this_sum) * math.sqrt(other_sum)

        cosine = numerator / denominator if denominator else 0.0
        articles.append((cosine, article))
    articles.sort(key=operator.itemgetter(0), reverse=True)
    article_1 = articles[0][1] if len(articles) > 0 else None
    article_2 = articles[1][1] if len(articles) > 1 else None
    return (article_1, article_2)
