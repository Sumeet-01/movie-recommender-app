"""
CineMate TMDB API Service — Production Grade
Supports movies + TV series, OTT providers, trailers, regional content,
trending/top-10, and intelligent similar-movie logic.
All endpoints use free TMDB API v3.
"""

import requests
import os
import time
from typing import List, Dict, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class TMDbService:
    """Production TMDB API service with retry, cache, regional + series support."""

    BASE_URL = 'https://api.themoviedb.org/3'
    IMAGE_BASE = 'https://image.tmdb.org/t/p'

    GENRE_MAP = {
        28: 'Action', 12: 'Adventure', 16: 'Animation', 35: 'Comedy',
        80: 'Crime', 99: 'Documentary', 18: 'Drama', 10751: 'Family',
        14: 'Fantasy', 36: 'History', 27: 'Horror', 10402: 'Music',
        9648: 'Mystery', 10749: 'Romance', 878: 'Sci-Fi', 10770: 'TV Movie',
        53: 'Thriller', 10752: 'War', 37: 'Western'
    }

    TV_GENRE_MAP = {
        10759: 'Action & Adventure', 16: 'Animation', 35: 'Comedy', 80: 'Crime',
        99: 'Documentary', 18: 'Drama', 10751: 'Family', 10762: 'Kids',
        9648: 'Mystery', 10763: 'News', 10764: 'Reality', 10765: 'Sci-Fi & Fantasy',
        10766: 'Soap', 10767: 'Talk', 10768: 'War & Politics', 37: 'Western'
    }

    OTT_PROVIDERS = {
        8:   {'name': 'Netflix',      'color': '#E50914'},
        119: {'name': 'Prime Video',   'color': '#00A8E1'},
        122: {'name': 'Hotstar',       'color': '#0c2e56'},
        220: {'name': 'JioCinema',     'color': '#E8118A'},
        232: {'name': 'Zee5',          'color': '#8230C6'},
        237: {'name': 'SonyLIV',       'color': '#070707'},
        350: {'name': 'Apple TV+',     'color': '#000000'},
        337: {'name': 'Disney+',       'color': '#113CCF'},
    }

    def __init__(self):
        self.api_key = os.environ.get('TMDB_API_KEY')
        if not self.api_key:
            raise ValueError("TMDB_API_KEY not found in environment variables.")

        self.session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5,
                      status_forcelist=[429, 500, 502, 503, 504],
                      allowed_methods=["GET"])
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))

        if self.api_key.startswith('eyJ'):
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })

        self._cache: Dict = {}
        self._cache_ttl: Dict[str, float] = {}

    # ── helpers ─────────────────────────────────────────────
    def _cached(self, key, ttl=1800):
        if key in self._cache and time.time() - self._cache_ttl.get(key, 0) < ttl:
            return self._cache[key]
        return None

    def _set_cache(self, key, value):
        self._cache[key] = value
        self._cache_ttl[key] = time.time()

    def _get(self, endpoint, params=None, timeout=15):
        if params is None:
            params = {}
        if not self.api_key.startswith('eyJ'):
            params['api_key'] = self.api_key

        cache_key = f"{endpoint}:{str(sorted(params.items()))}"
        cached = self._cached(cache_key)
        if cached is not None:
            return cached
        try:
            resp = self.session.get(f"{self.BASE_URL}/{endpoint}",
                                    params=params, timeout=timeout)
            resp.raise_for_status()
            data = resp.json()
            self._set_cache(cache_key, data)
            return data
        except Exception:
            return None

    def img(self, path, size='w500'):
        return f"{self.IMAGE_BASE}/{size}{path}" if path else None

    def _enrich(self, items, media_type='movie'):
        gmap = self.GENRE_MAP if media_type == 'movie' else self.TV_GENRE_MAP
        for m in items:
            m['poster_url'] = self.img(m.get('poster_path'), 'w500')
            m['backdrop_url'] = self.img(m.get('backdrop_path'), 'w780')
            m['genre_names'] = [gmap.get(g, '') for g in m.get('genre_ids', []) if g in gmap]
            if 'media_type' not in m:
                m['media_type'] = media_type
            if media_type == 'tv' and not m.get('title'):
                m['title'] = m.get('name', '')
            if media_type == 'tv' and not m.get('release_date'):
                m['release_date'] = m.get('first_air_date', '')
        return items

    def _results(self, data, media_type='movie'):
        if not data:
            return []
        return self._enrich(data.get('results', []), media_type)

    # ── MOVIES — core ──────────────────────────────────────
    def get_trending_movies(self, time_window='week', page=1):
        return self._results(self._get(f'trending/movie/{time_window}', {'page': page}))

    def get_popular_movies(self, page=1):
        return self._results(self._get('movie/popular', {'page': page}))

    def get_top_rated_movies(self, page=1):
        return self._results(self._get('movie/top_rated', {'page': page}))

    def get_now_playing_movies(self, page=1):
        return self._results(self._get('movie/now_playing', {'page': page, 'region': 'IN'}))

    def get_upcoming_movies(self, page=1):
        return self._results(self._get('movie/upcoming', {'page': page, 'region': 'IN'}))

    # ── MOVIES — regional ─────────────────────────────────
    def _regional(self, lang, page=1, sort_by='popularity.desc', extra=None):
        params = {'with_original_language': lang, 'sort_by': sort_by,
                  'page': page, 'vote_count.gte': 10}
        if extra:
            params.update(extra)
        return self._results(self._get('discover/movie', params))

    def get_bollywood_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('hi', page, sort_by)

    def get_tamil_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('ta', page, sort_by)

    def get_telugu_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('te', page, sort_by)

    def get_malayalam_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('ml', page, sort_by)

    def get_kannada_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('kn', page, sort_by)

    def get_korean_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('ko', page, sort_by)

    def get_anime_movies(self, page=1):
        return self._results(self._get('discover/movie', {
            'with_original_language': 'ja', 'with_genres': 16,
            'sort_by': 'popularity.desc', 'page': page
        }))

    def get_hollywood_movies(self, page=1, sort_by='popularity.desc'):
        return self._regional('en', page, sort_by)

    def get_south_indian_movies(self, page=1):
        all_movies = []
        for lang in ['ta', 'te', 'ml', 'kn']:
            all_movies.extend(self._regional(lang, page))
        seen = set()
        unique = []
        for m in sorted(all_movies, key=lambda x: x.get('popularity', 0), reverse=True):
            if m['id'] not in seen:
                seen.add(m['id'])
                unique.append(m)
        return unique[:20]

    # ── TV SERIES ──────────────────────────────────────────
    def get_trending_tv(self, time_window='week', page=1):
        return self._results(self._get(f'trending/tv/{time_window}', {'page': page}), 'tv')

    def get_popular_tv(self, page=1):
        return self._results(self._get('tv/popular', {'page': page}), 'tv')

    def get_top_rated_tv(self, page=1):
        return self._results(self._get('tv/top_rated', {'page': page}), 'tv')

    def get_tv_details(self, tv_id):
        data = self._get(f'tv/{tv_id}', {
            'append_to_response': 'credits,videos,similar,recommendations,watch/providers,keywords,content_ratings'
        })
        if data:
            data['poster_url'] = self.img(data.get('poster_path'), 'w500')
            data['backdrop_url'] = self.img(data.get('backdrop_path'), 'w1280')
            data['title'] = data.get('name', '')
            data['release_date'] = data.get('first_air_date', '')
            data['media_type'] = 'tv'
            data['ott_providers'] = self._extract_providers(data)
            data['trailers'] = self._extract_trailers(data)
            data['director'] = None
            crew = data.get('credits', {}).get('crew', [])
            for p in crew:
                if p.get('job') in ('Director', 'Executive Producer'):
                    data['director'] = p.get('name')
                    break
        return data

    def get_indian_tv(self, page=1):
        all_shows = []
        for lang in ['hi', 'ta', 'te', 'ml']:
            d = self._get('discover/tv', {
                'with_original_language': lang,
                'sort_by': 'popularity.desc',
                'page': page, 'vote_count.gte': 5
            })
            all_shows.extend(self._results(d, 'tv'))
        seen = set()
        unique = []
        for s in sorted(all_shows, key=lambda x: x.get('popularity', 0), reverse=True):
            if s['id'] not in seen:
                seen.add(s['id'])
                unique.append(s)
        return unique[:20]

    # ── TOP 10 / TRENDING (Netflix style) ──────────────────
    def get_top10_india(self):
        trending_all = self._get('trending/all/day', {'page': 1})
        if not trending_all:
            return []
        results = trending_all.get('results', [])
        indian_langs = {'hi', 'ta', 'te', 'ml', 'kn', 'bn', 'mr', 'pa'}
        for m in results:
            mt = m.get('media_type', 'movie')
            m['poster_url'] = self.img(m.get('poster_path'), 'w500')
            m['backdrop_url'] = self.img(m.get('backdrop_path'), 'w780')
            if mt == 'tv':
                m['title'] = m.get('name', m.get('title', ''))
                m['release_date'] = m.get('first_air_date', m.get('release_date', ''))
            gmap = self.GENRE_MAP if mt == 'movie' else self.TV_GENRE_MAP
            m['genre_names'] = [gmap.get(g, '') for g in m.get('genre_ids', []) if g in gmap]
        indian = [m for m in results if m.get('original_language') in indian_langs]
        others = [m for m in results if m.get('original_language') not in indian_langs]
        return (indian + others)[:10]

    def get_trending_bollywood(self):
        return self._regional('hi', 1, 'popularity.desc')[:10]

    def get_top10_series(self):
        return self.get_trending_tv('week')[:10]

    # ── MOVIE DETAILS with OTT + trailers ──────────────────
    def get_movie_details(self, movie_id):
        data = self._get(f'movie/{movie_id}', {
            'append_to_response': 'credits,videos,images,similar,recommendations,reviews,keywords,watch/providers'
        })
        if not data:
            return None
        data['poster_url'] = self.img(data.get('poster_path'), 'w500')
        data['backdrop_url'] = self.img(data.get('backdrop_path'), 'w1280')
        data['media_type'] = 'movie'
        data['ott_providers'] = self._extract_providers(data)
        data['trailers'] = self._extract_trailers(data)
        data['director'] = self._extract_director(data)
        return data

    def _extract_providers(self, data):
        wp = data.get('watch/providers', {}).get('results', {})
        region_data = wp.get('IN') or wp.get('US') or {}
        flatrate = region_data.get('flatrate', [])
        providers = []
        for p in flatrate:
            pid = p.get('provider_id')
            info = self.OTT_PROVIDERS.get(pid)
            providers.append({
                'id': pid,
                'name': info['name'] if info else p.get('provider_name', 'Unknown'),
                'logo': self.img(p.get('logo_path'), 'w92'),
                'color': info['color'] if info else '#555'
            })
        return providers

    def _extract_trailers(self, data):
        videos = data.get('videos', {}).get('results', [])
        trailers = [
            v for v in videos
            if v.get('site') == 'YouTube'
            and v.get('type') in ('Trailer', 'Teaser')
            and not v.get('name', '').lower().startswith('fan')
        ]
        trailers.sort(key=lambda v: (
            0 if 'official' in v.get('name', '').lower() else 1,
            0 if v.get('type') == 'Trailer' else 1
        ))
        return trailers[:4]

    def _extract_director(self, data):
        crew = data.get('credits', {}).get('crew', [])
        for person in crew:
            if person.get('job') == 'Director':
                return person.get('name')
        return None

    # ── SIMILAR MOVIES (intelligent) ───────────────────────
    def get_similar_movies(self, movie_id, page=1):
        recs = self._results(self._get(f'movie/{movie_id}/recommendations', {'page': page}))
        if len(recs) < 4:
            recs.extend(self._results(self._get(f'movie/{movie_id}/similar', {'page': page})))
        seen = set()
        unique = []
        for m in recs:
            if m['id'] not in seen and m.get('poster_url'):
                seen.add(m['id'])
                unique.append(m)
        return unique[:12]

    def get_movie_recommendations(self, movie_id, page=1):
        return self._results(self._get(f'movie/{movie_id}/recommendations', {'page': page}))

    def get_movie_credits(self, movie_id):
        return self._get(f'movie/{movie_id}/credits')

    def get_movie_videos(self, movie_id):
        d = self._get(f'movie/{movie_id}/videos')
        return d.get('results', []) if d else []

    # ── SEARCH ─────────────────────────────────────────────
    def search_movies(self, query, page=1, year=None):
        params = {'query': query, 'page': page}
        if year:
            params['year'] = year
        data = self._get('search/movie', params)
        return {
            'results': self._results(data),
            'total_results': data.get('total_results', 0) if data else 0,
            'total_pages': data.get('total_pages', 0) if data else 0,
            'page': page
        }

    def search_multi(self, query, page=1):
        data = self._get('search/multi', {'query': query, 'page': page})
        if not data:
            return {'results': [], 'total_results': 0, 'page': page}
        results = data.get('results', [])
        enriched = []
        for item in results:
            mt = item.get('media_type', 'movie')
            item['poster_url'] = self.img(item.get('poster_path') or item.get('profile_path'), 'w500')
            item['backdrop_url'] = self.img(item.get('backdrop_path'), 'w780')
            if mt == 'tv':
                item['title'] = item.get('name', '')
                item['release_date'] = item.get('first_air_date', '')
            gmap = self.GENRE_MAP if mt == 'movie' else self.TV_GENRE_MAP
            item['genre_names'] = [gmap.get(g, '') for g in item.get('genre_ids', []) if g in gmap]
            enriched.append(item)
        return {
            'results': enriched,
            'total_results': data.get('total_results', 0),
            'page': page
        }

    # ── DISCOVER & GENRES ──────────────────────────────────
    def get_genres(self):
        d = self._get('genre/movie/list')
        return d.get('genres', []) if d else []

    def get_tv_genres(self):
        d = self._get('genre/tv/list')
        return d.get('genres', []) if d else []

    def discover_movies(self, **filters):
        return self._results(self._get('discover/movie', filters))

    def get_movies_by_genre(self, genre_id, page=1, sort_by='popularity.desc'):
        return self._results(self._get('discover/movie', {
            'with_genres': genre_id, 'sort_by': sort_by, 'page': page
        }))

    def get_person_details(self, person_id):
        return self._get(f'person/{person_id}', {'append_to_response': 'movie_credits,images'})

    def get_multi_search(self, query, page=1):
        return self.search_multi(query, page)

    # ── UTILITY ────────────────────────────────────────────
    def get_image_url(self, path, size='original'):
        return self.img(path, size)

    def get_youtube_embed_url(self, key):
        return f"https://www.youtube.com/embed/{key}"

    def clear_cache(self):
        self._cache.clear()
        self._cache_ttl.clear()

    def health_check(self):
        try:
            return self._get('configuration', timeout=5) is not None
        except Exception:
            return False


# Global instance
tmdb_service = TMDbService()

