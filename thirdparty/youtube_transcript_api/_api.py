import requests
try: # pragma: no cover
    import http.cookiejar as cookiejar
    CookieLoadError = (FileNotFoundError, cookiejar.LoadError)
except ImportError: # pragma: no cover
    import cookielib as cookiejar
    CookieLoadError = IOError

from ._transcripts import TranscriptListFetcher

from ._errors import (
    CookiePathInvalid,
    CookiesInvalid
)


class YouTubeTranscriptApi(object):
    @classmethod
    def list_transcripts(cls, video_id, proxies=None, cookies=None, session=None):
        """
        Retrieves the list of transcripts which are available for a given video.

        :param video_id: the youtube video id
        :type video_id: str
        :param proxies: a dictionary mapping of http and https proxies to be used for the network requests
        :type proxies: {'http': str, 'https': str}
        :param cookies: a string of the path to a text file containing youtube authorization cookies
        :type cookies: str
        :param session: a requests.Session object to be used for making requests
        :type session: requests.Session
        :return: the list of available transcripts
        :rtype TranscriptList:
        """
        if session is None:
            session = requests.Session()
        
        if cookies:
            session.cookies = cls._load_cookies(cookies, video_id)
        session.proxies = proxies if proxies else {}
        
        return TranscriptListFetcher(session).fetch(video_id)

    @classmethod
    def get_transcript(cls, video_id, languages=('en',), proxies=None, cookies=None, preserve_formatting=False, ca_cert=None):
        """
        Retrieves the transcript for a single video.

        :param video_id: the youtube video id
        :type video_id: str
        :param languages: A list of language codes in a descending priority.
        :type languages: list[str]
        :param proxies: a dictionary mapping of http and https proxies to be used for the network requests
        :type proxies: {'http': str, 'https': str}
        :param cookies: a string of the path to a text file containing youtube authorization cookies
        :type cookies: str
        :param preserve_formatting: whether to keep select HTML text formatting
        :type preserve_formatting: bool
        :param ca_cert: path to a custom CA certificate file for HTTPS requests
        :type ca_cert: str
        :return: a list of dictionaries containing the 'text', 'start' and 'duration' keys
        :rtype [{'text': str, 'start': float, 'end': float}]:
        """
        assert isinstance(video_id, str), "`video_id` must be a string"
        
        with requests.Session() as session:
            if ca_cert:
                session.verify = True
                session.cert = ca_cert
            
            
            transcript_list = cls.list_transcripts(video_id, proxies, cookies, session=session)
            return transcript_list.find_transcript(languages).fetch(preserve_formatting=preserve_formatting)

    @classmethod
    def get_transcripts(cls, video_ids, languages=('en',), continue_after_error=False, proxies=None,
                        cookies=None, preserve_formatting=False):
        """
        Retrieves the transcripts for a list of videos.

        :param video_ids: a list of youtube video ids
        :type video_ids: list[str]
        :param languages: A list of language codes in a descending priority. For example, if this is set to ['de', 'en']
        it will first try to fetch the german transcript (de) and then fetch the english transcript (en) if it fails to
        do so.
        :type languages: list[str]
        :param continue_after_error: if this is set the execution won't be stopped, if an error occurs while retrieving
        one of the video transcripts
        :type continue_after_error: bool
        :param proxies: a dictionary mapping of http and https proxies to be used for the network requests
        :type proxies: {'http': str, 'https': str} - http://docs.python-requests.org/en/master/user/advanced/#proxies
        :param cookies: a string of the path to a text file containing youtube authorization cookies
        :type cookies: str
        :param preserve_formatting: whether to keep select HTML text formatting
        :type preserve_formatting: bool
        :return: a tuple containing a dictionary mapping video ids onto their corresponding transcripts, and a list of
        video ids, which could not be retrieved
        :rtype ({str: [{'text': str, 'start': float, 'end': float}]}, [str]}):
        """
        assert isinstance(video_ids, list), "`video_ids` must be a list of strings"

        data = {}
        unretrievable_videos = []

        for video_id in video_ids:
            try:
                data[video_id] = cls.get_transcript(video_id, languages, proxies, cookies, preserve_formatting, ca_cert=None)
            except Exception as exception:
                if not continue_after_error:
                    raise exception

                unretrievable_videos.append(video_id)

        return data, unretrievable_videos

    @classmethod
    def _load_cookies(cls, cookies, video_id):
        try:
            cookie_jar = cookiejar.MozillaCookieJar()
            cookie_jar.load(cookies)
            if not cookie_jar:
                raise CookiesInvalid(video_id)
            return cookie_jar
        except CookieLoadError:
            raise CookiePathInvalid(video_id)
