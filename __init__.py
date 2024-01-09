from os.path import join, dirname

from json_database import JsonStorage

from ovos_utils.ocp import MediaType, PlaybackType
from ovos_workshop.decorators.ocp import ocp_search, ocp_featured_media
from ovos_workshop.skills.common_play import OVOSCommonPlaybackSkill


class FilmChestVintageCartoonsSkill(OVOSCommonPlaybackSkill):
    def __init__(self, *args, **kwargs):
        self.supported_media = [MediaType.CARTOON]
        self.skill_icon = join(dirname(__file__), "res", "filmchest.gif")
        path = join(dirname(__file__), "classic_cartoons.json")
        self.archive = {v["streams"][0]: v for v in JsonStorage(path).values()
                        if v["streams"]}
        super().__init__(*args, **kwargs)
        self.load_ocp_keywords()

    def load_ocp_keywords(self):
        titles = []

        for url, data in self.archive.items():
            t = data["title"].split("|")[0].split("(")[0].strip()
            titles.append(t.strip())
            if ":" in t:
                t1, t2 = t.split(":")
                titles.append(t1.strip())
                titles.append(t2.strip())
            if "-" in t:
                t1, t2 = t.split("-")
                titles.append(t1.strip())
                titles.append(t2.strip())

        self.register_ocp_keyword(MediaType.CARTOON,
                                  "cartoon_name", titles)
        self.register_ocp_keyword(MediaType.CARTOON,
                                  "cartoon_streaming_provider",
                                  ["FilmChestVintageCartoons",
                                   "FilmChest",
                                   "FilmChest Vintage Cartoons",
                                   "FilmChest Cartoons"])

    def get_playlist(self, score=50, num_entries=25):
        pl = self.featured_media()[:num_entries]
        return {
            "match_confidence": score,
            "media_type": MediaType.MOVIE,
            "playlist": pl,
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "image": self.skill_icon,
            "title": "FilmChest Vintage Cartoons (Cartoon Playlist)",
            "author": "Internet Archive"
        }

    @ocp_search()
    def search_db(self, phrase, media_type):
        base_score = 15 if media_type == MediaType.CARTOON else 0
        entities = self.ocp_voc_match(phrase)

        title = entities.get("cartoon_name")
        skill = "cartoon_streaming_provider" in entities  # skill matched

        base_score += 35 * len(entities)

        if title:
            candidates = self.archive.values()

            if title:
                base_score += 35
                candidates = [video for video in self.archive.values()
                              if title.lower() in video["title"].lower()]

            for video in candidates:
                yield {
                    "title": video["title"],
                    "match_confidence": min(100, base_score),
                    "media_type": MediaType.CARTOON,
                    "uri": video["streams"][0],
                    "playback": PlaybackType.VIDEO,
                    "skill_icon": self.skill_icon,
                    "skill_id": self.skill_id,
                    "image": video["images"][0] if video["images"] else self.skill_icon
                }

        if skill:
            yield self.get_playlist()

    @ocp_featured_media()
    def featured_media(self):
        return [{
            "title": video["title"],
            "match_confidence": 70,
            "media_type": MediaType.MOVIE,
            "uri": video["streams"][0],
            "playback": PlaybackType.VIDEO,
            "skill_icon": self.skill_icon,
            "skill_id": self.skill_id
        } for video in self.archive.values()]


if __name__ == "__main__":
    from ovos_utils.messagebus import FakeBus

    s = FilmChestVintageCartoonsSkill(bus=FakeBus(), skill_id="t.fake")
    for r in s.search_db("Betty Boop", MediaType.MOVIE):
        print(r)
        # {'title': 'betty boop - I heared (1932).', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/BettyBoop-IHeared1932/BettyBoop-IHeared1932..ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop Cartoons', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/BettyBoopCartoons/Betty_Boop_A_Song_a_Day_1936.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: A Song A Day', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_A_Song_A_Day_1936_457/Betty_Boop_A_Song_a_Day_1936.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: A Song A Day', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_A_Song_a_Day_1936/Betty_Boop_A_Song_a_Day_1936.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Baby Be Good', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Baby_Be_Good_1935/Betty_Boop_Baby_Be_Good_1935.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Is My Palm Read', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Is_My_Palm_Read_1932/Betty_Boop_Is_My_Palm_Read_1932_512kb.mp4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Is My Palm Read', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Is_My_Palm_Read_1932_832/Betty_Boop_Is_My_Palm_Read_1932.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Judge For a Day', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Judge_For_a_Day_1935/Betty_Boop_Judge_For_a_Day_1935.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: More Pep', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_More_Pep_1936/Betty_Boop_More_Pep_1936.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Mother Goose Land', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Mother_Goose_Land_1933/Betty_Boop_Mother_Goose_Land_1933.mpg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Poor Cinderella', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Poor_Cinderella_1934/Betty_Boop_Poor_Cinderella_1934.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: The Candid Candidate', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_The_Candid_Candidate_1937/The_Candid_Candidate_1937.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: The Candid Candidate', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_The_Candid_Candidate_1937_944/The_Candid_Candidate_1937.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: The Scared Crows', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_The_Scared_Crows_1939/Betty_Boop_The_Scared_Crows_1939.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Training Pigeons', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Training_Pigeons_1936/Betty_Boop_Training_Pigeons_1936.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop: Whoops! I'm a Cowboy", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_Whoops_Im_a_Cowboy_1937/Whoops_Im_a_Cowboy_1937_512kb.mp4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: A Language All My Own', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_a_Language_All_My_Own_1935/Betty_Boop_a_Language_All_My_Own_1935.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop and Little Jimmy', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_and_Little_Jimmy_1936/Betty_Boop_and_Little_Jimmy_1936.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop for President', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_for_President_1932/Betty_Boop_for_President_1932.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop with Henry, the Funniest Living American', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boop_with_Henry_1935/Betty_Boop_with_Henry_1935.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop's Crazy Inventions", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boops_Crazy_Inventions_1933/Betty_Boops_Crazy_Inventions_1933.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop's Ker-Choo", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boops_Ker-Cho_1932/Betty_Boops_Ker-Cho_1932.ogv', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop's Ker-Choo", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/Betty_Boops_Ker_Choo_1932/Betty_Boops_Ker-Cho_1933_512kb.mp4', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop And Grampy', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_and_grampy/bb_and_grampy.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop And The Little King', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_and_the_little_king/bb_and_the_little_king.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Bamboo Isle', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_bamboo_isle/bb_bamboo_isle.mpg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Be Human', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_be_human/bb_be_human.mpg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Betty in Blunderland', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_betty_in_blunderland/bb_betty_in_blunderland.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop's Big Boss", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_big_boss/bb_big_boss.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Chess Nuts', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_chess_nuts/bb_chess_nuts.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Happy You And Merry Me', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_happy_you/bb_happy_you.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: House Cleaning Blues', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_house_cleaning_blues/bb_house_cleaning_blues.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop: I'll Be Glad When You're Dead, You Rascal You", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_ill_be_glad_when_youre_dead/bb_ill_be_glad_when_youre_dead.mpg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Minnie The Moocher', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_minnie_the_moocher/bb_minnie_the_moocher.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Morning, Noon And Night', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_morning_noon_and_night/bb_morning_noon_and_night.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Musical Mountaineers', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_musical_mountaineers/bb_musical_mountaineers.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Not Now', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_not_now/bb_not_now.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: The Old Man Of The Mountain', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_old_man_of_the_mountain/bb_old_man_of_the_mountain.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Parade of the Wooden Soldiers', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_parade_of_the_wooden_soldiers/bb_parade_of_the_wooden_soldiers.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Poor Cinderella (1934)', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_poor_cinderella/bb_poor_cinderella.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': "Betty Boop's Rise To Fame", 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_rise_to_fame/bb_rise_to_fame.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: She Wronged Him Right', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_she_wronged_him_right/bb_she_wronged_him_right.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Snow White', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_snow_white/bb_snow_white.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Stop That Noise', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_stop_that_noise/bb_stop_that_noise.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: Swat The Fly', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_swat_the_fly/bb_swat_that_fly.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
        # {'title': 'Betty Boop: The Impractical Joker', 'match_confidence': 55, 'media_type': <MediaType.CARTOON: 21>, 'uri': 'https://archive.org/download/bb_the_impractical_joker/bb_the_impractical_joker.mpeg', 'playback': <PlaybackType.VIDEO: 1>, 'skill_icon': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png', 'skill_id': 't.fake', 'image': 'https://github.com/OpenVoiceOS/ovos-ocp-audio-plugin/raw/master/ovos_plugin_common_play/ocp/res/ui/images/ocp.png'}
