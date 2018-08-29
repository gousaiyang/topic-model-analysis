import colorlabels as cl

from scraper import twapi
from util import data_source_file, export_csv, merge_whitespaces

MAX_USERS_PER_REQ = 100


def retrieve_user_info(usernames):
    while usernames:
        users = twapi.UsersLookup(screen_name=usernames[:MAX_USERS_PER_REQ],
                                  include_entities=False)

        for user in users:
            yield {
                'id': user.id_str,
                'screen_name': user.screen_name,
                'name': merge_whitespaces(user.name),
                'favourites_count': user.favourites_count,
                'followers_count': user.followers_count,
                'friends_count': user.friends_count,
                'listed_count': user.listed_count,
                'statuses_count': user.statuses_count,
                'verified': user.verified,
                'created_at': user.created_at,
                'lang': user.lang,
                'location': merge_whitespaces(user.location),
                'avatar': user.profile_image_url_https,
                'description': merge_whitespaces(user.description)
            }

        usernames = usernames[MAX_USERS_PER_REQ:]


def user_info_retriever(usernames, csvfilename):
    cl.section('Twitter User Info Retriever')

    csvfilename = data_source_file(csvfilename)
    result = retrieve_user_info(usernames)
    export_csv(result, csvfilename)
