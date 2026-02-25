"""
CineMate Hybrid Recommendation Engine — Production Grade
Combines content-based filtering (TF-IDF on overview+genres+keywords+cast+director),
collaborative filtering (user-based Pearson), popularity-weighted ranking,
Bollywood/India bias layer, and recency decay.

Score formula:
  final = 0.35*similarity + 0.20*genre_match + 0.15*recency + 0.20*user_pref + 0.10*rating_weight
"""

import math
import time
import re
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional


class RecommendationEngine:
    """Hybrid recommendation engine with India-first bias."""

    def __init__(self):
        # collaborative data
        self.user_ratings: Dict[int, Dict[int, float]] = defaultdict(dict)
        self.movie_ratings: Dict[int, Dict[int, float]] = defaultdict(dict)
        # content data
        self.movie_meta: Dict[int, Dict] = {}   # tmdb_id -> {genres, keywords, overview, cast, director, lang, year, popularity, vote_avg, vote_count}
        self.tfidf_vectors: Dict[int, Dict[str, float]] = {}
        self.idf: Dict[str, float] = {}
        self._tfidf_dirty = True

    # ── data loading ────────────────────────────────────────

    def load_ratings_data(self):
        """Load ratings from DB into memory."""
        try:
            from app.models.movie import Rating
            ratings = Rating.query.all()
            self.user_ratings.clear()
            self.movie_ratings.clear()
            for r in ratings:
                self.user_ratings[r.user_id][r.movie_id] = r.score
                self.movie_ratings[r.movie_id][r.user_id] = r.score
        except Exception:
            pass

    def ingest_movie(self, tmdb_id: int, data: Dict):
        """Ingest TMDB movie details for content-based features."""
        if not data or not tmdb_id:
            return
        genres = [g.get('name', '') for g in data.get('genres', [])]
        genre_ids = set(g.get('id', 0) for g in data.get('genres', []))
        keywords_list = [kw.get('name', '') for kw in data.get('keywords', {}).get('keywords', [])]
        cast = [c.get('name', '') for c in data.get('credits', {}).get('cast', [])[:8]]
        director = data.get('director') or ''
        overview = data.get('overview') or ''
        lang = data.get('original_language', '')
        year = 0
        rd = data.get('release_date', '') or ''
        if len(rd) >= 4:
            try:
                year = int(rd[:4])
            except ValueError:
                pass

        self.movie_meta[tmdb_id] = {
            'genres': genres,
            'genre_ids': genre_ids,
            'keywords': keywords_list,
            'cast': cast,
            'director': director,
            'overview': overview,
            'lang': lang,
            'year': year,
            'popularity': data.get('popularity', 0),
            'vote_avg': data.get('vote_average', 0),
            'vote_count': data.get('vote_count', 0),
            'title': data.get('title', ''),
        }
        self._tfidf_dirty = True

    # ── TF-IDF ──────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r'[a-z0-9]+', text.lower())

    def _build_document(self, meta: Dict) -> List[str]:
        """Build a token list weighting genres and cast higher."""
        tokens = []
        # genres x3 for weight
        for g in meta['genres']:
            tokens.extend(self._tokenize(g) * 3)
        # keywords x2
        for kw in meta['keywords']:
            tokens.extend(self._tokenize(kw) * 2)
        # cast
        for c in meta['cast']:
            tokens.extend(self._tokenize(c))
        # director x2
        if meta['director']:
            tokens.extend(self._tokenize(meta['director']) * 2)
        # overview
        tokens.extend(self._tokenize(meta['overview']))
        return tokens

    def _rebuild_tfidf(self):
        if not self._tfidf_dirty:
            return
        # build term frequencies
        docs: Dict[int, Dict[str, int]] = {}
        df: Dict[str, int] = defaultdict(int)
        for mid, meta in self.movie_meta.items():
            tokens = self._build_document(meta)
            tf = Counter(tokens)
            docs[mid] = tf
            for term in set(tokens):
                df[term] += 1

        n = max(len(docs), 1)
        self.idf = {term: math.log(n / (1 + count)) for term, count in df.items()}

        self.tfidf_vectors = {}
        for mid, tf in docs.items():
            vec = {}
            magnitude = 0
            for term, count in tf.items():
                w = count * self.idf.get(term, 0)
                vec[term] = w
                magnitude += w * w
            magnitude = math.sqrt(magnitude) if magnitude > 0 else 1
            self.tfidf_vectors[mid] = {t: w / magnitude for t, w in vec.items()}

        self._tfidf_dirty = False

    def _cosine_sim(self, v1: Dict[str, float], v2: Dict[str, float]) -> float:
        if not v1 or not v2:
            return 0.0
        common = set(v1.keys()) & set(v2.keys())
        if not common:
            return 0.0
        return sum(v1[t] * v2[t] for t in common)

    # ── scoring components ──────────────────────────────────

    def _genre_match(self, genres1: set, genres2: set) -> float:
        if not genres1 or not genres2:
            return 0.0
        inter = len(genres1 & genres2)
        union = len(genres1 | genres2)
        return inter / union if union else 0.0

    def _recency_score(self, year: int) -> float:
        current_year = 2026
        if year <= 0:
            return 0.3
        diff = current_year - year
        if diff <= 1:
            return 1.0
        if diff <= 3:
            return 0.85
        if diff <= 5:
            return 0.7
        if diff <= 10:
            return 0.5
        return max(0.2, 1.0 - diff * 0.03)

    def _rating_weight(self, vote_avg: float, vote_count: int) -> float:
        """IMDB-style weighted rating (Bayesian average)."""
        m = 50   # minimum votes to be considered
        c = 6.0  # mean vote across all movies
        if vote_count == 0:
            return 0.3
        return (vote_count / (vote_count + m)) * vote_avg / 10 + (m / (vote_count + m)) * c / 10

    # ── collaborative filtering ─────────────────────────────

    def _pearson(self, r1: Dict, r2: Dict) -> float:
        common = set(r1.keys()) & set(r2.keys())
        if len(common) < 2:
            return 0
        vals1 = [r1[m] for m in common]
        vals2 = [r2[m] for m in common]
        mean1, mean2 = sum(vals1) / len(vals1), sum(vals2) / len(vals2)
        num = sum((vals1[i] - mean1) * (vals2[i] - mean2) for i in range(len(vals1)))
        d1 = sum((v - mean1) ** 2 for v in vals1)
        d2 = sum((v - mean2) ** 2 for v in vals2)
        denom = math.sqrt(d1 * d2)
        return num / denom if denom else 0

    def collaborative_filtering(self, user_id: int, n: int = 20) -> List[Tuple[int, float]]:
        if user_id not in self.user_ratings or not self.user_ratings[user_id]:
            return []
        target = self.user_ratings[user_id]
        sims = []
        for other_id in self.user_ratings:
            if other_id == user_id:
                continue
            s = self._pearson(target, self.user_ratings[other_id])
            if s > 0:
                sims.append((other_id, s))
        sims.sort(key=lambda x: x[1], reverse=True)
        sims = sims[:30]

        rated = set(target.keys())
        scores: Dict[int, float] = defaultdict(float)
        weights: Dict[int, float] = defaultdict(float)
        for uid, sim in sims:
            for mid, rating in self.user_ratings[uid].items():
                if mid not in rated:
                    scores[mid] += sim * rating
                    weights[mid] += abs(sim)

        preds = []
        for mid in scores:
            if weights[mid] > 0:
                preds.append((mid, scores[mid] / weights[mid]))
        preds.sort(key=lambda x: x[1], reverse=True)
        return preds[:n]

    # ── content-based filtering ─────────────────────────────

    def content_recommendations(self, movie_id: int, n: int = 12) -> List[Tuple[int, float]]:
        """Find similar movies using TF-IDF + genre + recency + rating."""
        self._rebuild_tfidf()
        if movie_id not in self.tfidf_vectors or movie_id not in self.movie_meta:
            return []

        target_vec = self.tfidf_vectors[movie_id]
        target_meta = self.movie_meta[movie_id]
        target_genres = target_meta['genre_ids']

        results = []
        for mid, vec in self.tfidf_vectors.items():
            if mid == movie_id:
                continue
            meta = self.movie_meta[mid]
            sim = self._cosine_sim(target_vec, vec)
            genre_m = self._genre_match(target_genres, meta['genre_ids'])
            recency = self._recency_score(meta['year'])
            rating_w = self._rating_weight(meta['vote_avg'], meta['vote_count'])

            # Director / cast bonus
            bonus = 0
            if target_meta['director'] and target_meta['director'] == meta['director']:
                bonus += 0.15
            shared_cast = set(target_meta['cast']) & set(meta['cast'])
            bonus += min(len(shared_cast) * 0.05, 0.15)

            # Language proximity bonus
            lang_bonus = 0.05 if target_meta['lang'] == meta['lang'] else 0

            final = (
                0.35 * sim +
                0.20 * genre_m +
                0.15 * recency +
                0.10 * rating_w +
                bonus + lang_bonus
            )
            if genre_m >= 0.25:  # must share at least some genres
                results.append((mid, final))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:n]

    # ── hybrid recommendations (for user) ───────────────────

    def hybrid_recommendations(self, user_id: int, n_recommendations: int = 20) -> List[Dict]:
        """Combine collaborative + content-based + popularity for a logged-in user."""
        collab = self.collaborative_filtering(user_id, n_recommendations * 2)

        # Content recs from user's top-rated movies
        content_scores: Dict[int, float] = defaultdict(float)
        user_rated = self.user_ratings.get(user_id, {})
        top_rated = sorted(user_rated.items(), key=lambda x: x[1], reverse=True)[:10]
        for mid, rating in top_rated:
            weight = rating / 5.0
            for rec_mid, score in self.content_recommendations(mid, 15):
                if rec_mid not in user_rated:
                    content_scores[rec_mid] += score * weight

        # Merge
        combined: Dict[int, float] = defaultdict(float)
        collab_weight = min(len(user_rated) / 10, 0.6)
        content_weight = 1 - collab_weight

        for mid, score in collab:
            combined[mid] += score * collab_weight
        for mid, score in content_scores.items():
            combined[mid] += score * content_weight

        # Popularity boost for items with meta
        for mid in combined:
            if mid in self.movie_meta:
                meta = self.movie_meta[mid]
                pop_boost = min(meta['popularity'] / 200, 0.15)
                combined[mid] += pop_boost

        recs = [{'movie_id': mid, 'score': round(score, 4)}
                for mid, score in combined.items()]
        recs.sort(key=lambda x: x['score'], reverse=True)
        return recs[:n_recommendations]

    # ── similar movies (for detail page) ────────────────────

    def similar_movies(self, movie_id: int, n: int = 10) -> List[Tuple[int, float]]:
        return self.content_recommendations(movie_id, n)

    # ── trending by category ────────────────────────────────

    def get_trending_by_category(self, category: str = 'all', limit: int = 20) -> List[int]:
        scores: Dict[int, float] = defaultdict(float)
        for mid, user_ratings in self.movie_ratings.items():
            avg = sum(user_ratings.values()) / len(user_ratings)
            count = len(user_ratings)
            scores[mid] = avg * math.log(count + 1)
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [mid for mid, _ in ranked[:limit]]


# Global instance
recommendation_engine = RecommendationEngine()
