# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 13:56:17 2019

@author: wwech
"""

"""
Function to extract the various informations from a youtube about channels and videos using a youtube data API.
It has one class called Youtube_extract which have different functions to process various queries."""

import requests
import json
import os
import traceback
# from multiprocessing import Pool, Lock
import multiprocessing as mp
from functools import partial
import pandas as pd
import datetime
import shutil
from tqdm import tqdm
import time
from multiprocessing import Pool



class Youtube_extract(object):
    """
    This class is used to extract various information about videos and channels from youtube using youtube data API. It also provides a function to access search results and user comments on videos.
    Pass a path of a file in which all the keys are written down.
    It handles all the requests, responses and errors.
    It has two global functions; first one is "keychange" to change the key during the extraction if there would any errors like key-invalid or key-quota exceed and the second one is "request_handler" to handleall the responses and errors occurred during extraction.
    
    It has the following public functions:
        1.  keychange(): To change a key on invalid-key error or quota-exceed error. * Global Function; can't be access using class object. *
        2.  request_handler(): To handle all types of responses from the API. * Global Function; can't be access using class object. *
        3.  get_channel_details(): To get details of a channel using its id.
        4.  get_video_details(): To get details about the video using its id.
        5.  playlist(): To get the details of all the playlist of a channel.
        6.  single_channel_video_data(): To get all the video details as JSON format of a channel. It uses playlist() function inside.
        7.  all_channel_video_data(): To get all the video details as json format for all the channels provided in the channel list. 
        8.  search_results_extraction(): To get the details about the query provided as an input.
        9.  comment_extraction(): To get the comments of a youtube video.
        10. init(): To define a global lock used by process."""

    def __init__(self, key_path = None):
        """
        Constructor to initialize class variables.
        It takes a key_path argument which is passed by the user during class initialization.
        keyindex and keylist are two class variables.
        keylist has various keys to use in the extraction and keyindex indicates which key is in use using its index in the list."""
        self.keyindex = 0
#        with open(key_path, "r") as file:
#            self.keylist = [key.strip() for key in file.readlines()]
        self.keylist = ['AIzaSyBXu79WmxVrUuEf02A5IXshNZVNL59IW40','AIzaSyCItjSKR_I3AXr3ilSlU0bQNfb6HA60nq4','AIzaSyAEFVBLRROF7HGE-eORrAxWeURbU1tZ998',
        'AIzaSyCg3a9GEDsXpa-yzR6as9muOxnNQyBWSNA','AIzaSyCrzGl_nmnH68AuyhVuOwYtwGrwUh6HAwE','AIzaSyCZDq1wuhcidz2q0TB5erBEBss83jrxQyg','AIzaSyCXb6-7tB_MZDuIqaCrG3BHGuxdMvq3Wfs',
        'AIzaSyBg1FBuBQl-xi2wJUFoLmg-AY60DmS-guo','AIzaSyCITQISwxpMchmEN2UMXoqwVkAWjetm0Oc','AIzaSyC8n_YsHpFjPLt4_7sES_PTYzsBFgn7K9k','AIzaSyBWUajFFwTyww0DHlZBnqEkMmaRVTEcrcY',
        'AIzaSyDMjp-z3DH_S2BRFCcfnRlE1T55qRE6lCQ','AIzaSyDouKf0AZOj4KNXaTAVQQi_QmpRpNHP03A','AIzaSyAwXggWXK_gDOmmelvVSx4Cztmid6bmCEA','AIzaSyAM1RAjCd_W8lVcb53pkh8LkBunowhSHTA',
        'AIzaSyBuUYRPLmzrbfK7XTL9F3Q0FadHkhQ_-KA','AIzaSyDSEvf00-boovEMrhIv9vD__5tAjPLDoA8','AIzaSyCvqdi6-eYK9RkQmSXxdXT57AJvzVFY5k8','AIzaSyC9TDWLqhLyc4vzwOgs_C342WWHGF5-uf0',
        'AIzaSyDzanvcDte2vjMSnpGEUaZd0DW7Xb-axoU','AIzaSyDEc0Ql28e2ePEOMoahnkNRBDQu15nTyBk','AIzaSyDYzkxN6ksoFL148uPyO-wH47G3OalEKag','AIzaSyB0sheZQR7f1KV4fBJi5NaN5jejsNujKSg', 'AIzaSyBCx_s4xAMBGG1ncMp20EykJMf4mGMdwLw','AIzaSyAKwTmYwSX2OMVlfUfBnr53kDfh1iNqj4I','AIzaSyBuG0L3dA5Y62nutoHB2Hhvk-OA6EJK3Fg',
        'AIzaSyAcyo6AaTgnuzaW1TbjTrJChRdt-h1on2E','AIzaSyBcAiKz6BMl35rwV7BGT3DuztYQPtQUDJc','AIzaSyBLuKB_DU4NmGca6XGW5-BcYSxBB_2OmiA',
        'AIzaSyDCWWX_Jd1iGzXaUHs7y_6_zpgejzGG-V0', 'AIzaSyBuUYRPLmzrbfK7XTL9F3Q0FadHkhQ_-KA','AIzaSyDCWWX_Jd1iGzXaUHs7y_6_zpgejzGG-V0','AIzaSyBHiE5t86GKVX-YuKrV-09flVtZ1R1s6mA',
        'AIzaSyAaO1JqWWUkQ8ygQZZlSOuv4ZPvw1w5sJ4','AIzaSyAcyo6AaTgnuzaW1TbjTrJChRdt-h1on2E','AIzaSyAE9Z7Rot5-15x_nr1jeoORrSniUn5CQp0','AIzaSyBcAiKz6BMl35rwV7BGT3DuztYQPtQUDJc',
        'AIzaSyBuG0L3dA5Y62nutoHB2Hhvk-OA6EJK3Fg','AIzaSyCWTP0LHJM9wbN_r1NtsmDWJJSDSYu8UVY','AIzaSyCavNozQXAmu43IQp5ksdpWGIsmdYNunhw','AIzaSyANi91i0WifIsS3mQ0dS-A9u7UftcgKw_g',
        'AIzaSyD3WZOZ0m3vTVbInYKL-S9e5DdgpDOYEPU','AIzaSyDgqZ54-02e4ovkANlcQzwOwNDCShysCiM','AIzaSyBchj0Xv_PfZVKrWWzIznl1ydDzGITzLZA',
        'AIzaSyD-c05sMNbULYOo9D8Gaw_Q16QfSTBwcEs','AIzaSyC9gRiOvIWlonL_pZHIdPxUhOjn6cOFMR8','AIzaSyD88ZrGnD-kJYu4y8ZclvtJE59NUl2QYw4','AIzaSyDMoOVtszehKuLfUnKAYXPmWGYollIhqko',
        'AIzaSyCtNyBNJMIDl_cDUlXZraohg-2eU8hc8oQ','AIzaSyD0G9TkGLuZ0BfdpHqY6PRwvpJtb2WdRx0']
        #AIzaSyBHiE5t86GKVX-YuKrV-09flVtZ1R1s6mA
        #AIzaSyBtsUWrMb9wtn7yhx0-NcquACQ7E8o1VBo
    global keychange
    
    def keychange(self):
        """
        Function to change a key during invalid-key or quota-exceed error.
        It takes no parameter and returns a key from a keylist."""
        # if response.json()['error']['errors'][0]['reason']=='quotaExceeded':
        self.keyindex += 1
        if self.keyindex == len(self.keylist):
            self.keyindex = 0
            print('Keylist length reached')
        print('Changinf Key..')
        key = self.keylist[self.keyindex]
        print("Quota Exceeded", self.keyindex)
        return key
    # def error_check(self,response):
        
    global request_handler
    
    def request_handler(self, url, params, wait=10, ids=None):
        """
        Function to handle the get request. It handles all the responses whether success or error.
        It takes 4 parameters:
            url: URL of a page from which the data is to extracted.
            params: Parameters required in the HTTP request.
            wait: Time in seconds to wait before displaying a connection error.  The default value is 100.
        Returns a response which could be either information in JSON format(in case of a successful response) or a dictionary containing an error and its type."""
        responses = {}
        start = time.time()

        while True:
            try:
                result = requests.get(url, params)
                return result.json()
                # print(result.json(),result.url)
                # if result.status_code != 200:
                #     responses.update({'Interneterror':result.text})
                #     break
                # else: 
                #     return result.json()

            except requests.exceptions.Timeout as timeoutErr:
                print(timeoutErr)
                responses.update({'Interneterror':str(timeoutErr)})
                break

            except requests.exceptions.ConnectionError as connErr:
                print(connErr)
                if (time.time() - start) > wait:
                    responses.update({'Interneterror':str(connErr)})
                    break

            # handles all the other types of errors using generic RequestException class.
            except requests.exceptions.RequestException as err:
                print(err)
                responses.update({"Interneterror":str(err)})
                break
            except Exception as e:
                print(e)
        # print('outsi',result.json())
        return responses


    def get_channel_details(self, chan_ids_list, part='statistics'):
        """
        Function to get various details about the given channels that define in a given parameter.
        It takes 2 parameters:
            chan_ids_list: List of channels whose details are to be extracted.
            part: List of resource properties that the API response would include.
            It can be:
                ** auditDetails
                ** brandingSettings
                ** contentDetails
                ** contentOwnerDetails
                ** id
                ** localizations
                ** snippet
                ** statistics
                ** status
                ** topicDetails
                -- Default value is "snippet". --
        Returns a details as a dictionary."""

        chnl_details = {}
        key = self.keylist[self.keyindex]
        url_c = "https://www.googleapis.com/youtube/v3/channels"

        for ind, chan in enumerate(chan_ids_list):
            try:
                querystring = {"id": chan, "part": part,
                               "key": key}
                response = request_handler(self, url_c, params=querystring, wait=100)
                #print(response)
                # Error-handling
                if response.get('error'):
                    print(response.get('error'))
                    while response['error']['errors'][0]:
                        key = keychange(self)
                        
                        querystring = {"id": chan, "part": part,
                                   "key": key}
                        response = request_handler(self, url_c, params=querystring, wait=100)

                if response.get('error'):
                    #chnl_details.update({chan:[str(response), response.text]})
                    #
                    if response['error']['errors'][0]['reason'] == 'keyInvalid':
                        return [{chan:[str(response), response.text]}]
                    break

                if response.get('Interneterror'):
                    chnl_details.update({chan: str(response)})
                    continue

                chnl_details[chan] = response['items']

            except Exception as e:
                print(e, traceback.format_exc())

            if ind % 100 == 0:
                print(ind)
        
        return chnl_details

    def get_video_details(self, vid_ids_list, part='snippet'):
        """
        Function to get the details about a video. It has the following parameters:
            1. vid_ids_list: List of channels whose details are to be extracted.
            2. part: List of comma-separated resource-properties that the API response would include. 
               Possible values are:
                    ** contentDetails
                    ** fileDetails
                    ** processingDetails
                    ** liveStreamingDetails
                    ** processingDetails
                    ** id
                    ** recordingDetails
                    ** localizations
                    ** snippet
                    ** statistics
                    ** status
                    ** topicDetails
                    ** suggestions
                    ** player
                    -- Default value is: "snippet". -- 
        Returns a details as a dictionary."""
        vid_details = {}
        url_v = "https://www.googleapis.com/youtube/v3/videos"
        key = self.keylist[self.keyindex]

        for ind, vid in enumerate(vid_ids_list):
            try:
                querystring = {"id": vid ,"part": part,
                               "key": key}

                response = request_handler(self, url_v, params=querystring, wait=100, ids=vid)

                if response.get('error'):
                    while response['error']['errors'][0]['reason'] == 'quotaExceeded' or \
                          response['error']['errors'][0]['reason'] == 'dailyLimitExceeded':
                        key = keychange(self)
                        querystring = {"id": vid , "part": part,
                                   "key": key}

                        response = request_handler(self, url_v, params=querystring, wait=100, ids=vid)

                if response.get('error'):
                    vid_details.update({vid: [str(response), response.text]})
                    if response['error']['errors'][0]['reason'] == 'keyInvalid':
                        return [{vid: [str(response), response.text]}]
                    break
                                
                if response.get('Interneterror'):
                    vid_details.update({vid: str(response)})
                    continue

                vid_details[vid] = response['items']

            except Exception as e:
                print(e, traceback.format_exc())

            if ind % 100 == 0:
                print(ind)

        return vid_details

    def playlist(self, channel_list, limit, part='contentDetails', only_id=1):
        """
        Function to extract out details of a playlist of a channel.
        It takes the following parameters:
            1. channel_list: List of channels whose playlists' details needed.
            2. limit: Maximum number of videos-details extracted in a single call. Upper bound is 50.
            3. part: List of comma-separated resource-properties that the API response would include.
               Possible values are:
                       ** contentDetails
                       ** id
                       ** localizations
                       ** player
                       ** snippet
                       ** status
                       -- Default value is: "contentDetails" --
            4. only_id: -- Default value is: 1. --
        Returns a playlist details as a dictionary."""
        playlist_details = {}
        key = self.keylist[self.keyindex]
        url_pi = 'https://www.googleapis.com/youtube/v3/playlistItems/'

        if limit <= 50 and limit > 0:
            maxResults = limit
        else:
            maxResults = 50

        for chnlid in channel_list:
            vidcount = initial = 0
            nextPageToken = ''
            results = []
            # print('UU'+chnlid[2:])
            try:
                while nextPageToken or initial == 0:
                    querystring = {
                        'playlistId': 'UU' + chnlid[2:],
                        'part': part,
                        'key': key,
                        'pageToken': nextPageToken,
                        'maxResults': maxResults
                    }


                    response = request_handler(self, url_pi, params=querystring, wait=5) #ids=chnlid)
                    # print("#"*5, response.json())
                    # print(response.json())
                    if response.get('error'):
                        while response['error']['errors'][0]['reason'] == 'quotaExceeded' or \
                            response['error']['errors'][0]['reason'] == 'dailyLimitExceeded':
                            key = keychange(self)
                            querystring = {
                                'playlistId': 'UU' + chnlid[2:],
                                'part': part,
                                'key': key,
                                'pageToken': nextPageToken,
                                'maxResults': maxResults
                                }

                            response = request_handler(self, url_pi, params=querystring, wait=5, ids=chnlid)

                    if response.get('error'):
                        playlist_details.update({chnlid: 'error'})
                        if response['error']['errors'][0]['reason'] == 'keyInvalid':
                            return [{chnlid:'error'}]
                        break

                    if response.get('Interneterror'):
                        results.append(response)
                        #print(playlist_details)
                        break

                    if limit == -1:
                        limit = response['pageInfo']['totalResults']
                    # print(response,response.text)
                    
                    if only_id == 1:
                        for i in range(response['pageInfo']['resultsPerPage']):
                            try:
                                results.append(response['items'][i]['contentDetails']['videoId'])
                            except:
                                pass
                    else:
                        results.append(response['items'])
                    nextPageToken = response.get('nextPageToken')
                    vidcount += len(response['items'])
                    if vidcount >= limit:
                        break
                    print("Video id found: ", chnlid, " : ", vidcount)
                    #{'error':[]}
                    
                    initial += 1
                    
                playlist_details.update({chnlid:results})

            except Exception as e:
                print("Error: ", e, " : ", traceback.print_exc())
                playlist_details[chnlid] = 'error'
                break

        return playlist_details
    
    def single_channel_video_data(self, limit=50, vid_part='snippet', output_path='./', chanlid=None):
        """
        Functions to get data of all the video of a particular channel.
        It implicitly calls a get_video_details().
        All the parameters of this function are optional. It takes the following parameters:
            1. limit: Maximum number of videos-details extracted in a single call. -- Default value is 50. -- 
            2. vid_part: List of comma-separated resource-properties that the API response would include. 
               Possible values are:
                    ** contentDetails
                    ** fileDetails
                    ** processingDetails
                    ** liveStreamingDetails
                    ** processingDetails
                    ** id
                    ** recordingDetails
                    ** localizations
                    ** snippet
                    ** statistics
                    ** status
                    ** topicDetails
                    ** suggestions
                    ** player
                    -- Default value is: "snippet". -- 
            3. output_path: Path of a output directory where all the data would be saved. 
               -- Default value is: "./". --
            4. chanlid: Channel-id whose data are required. -- Default value is None. --
        It saves data in output_path. No return call."""
        all_result = {}
        print("finding vidids: ", chanlid, " : ", os.getpid())
        result = self.playlist([chanlid], limit)

        # print("playlist: ", result, " : ", os.getpid())
        print("finding channel meta: ", chanlid, " : ", os.getpid())
        all_result.update({chanlid: self.get_video_details(result[chanlid], part=vid_part)})
        print("doing json dump: ", chanlid, " : ", os.getpid())

        lock.acquire()
        with open(output_path + 'new_family_parenting.json', "a") as out_fp:
            json.dump(all_result, out_fp)
            out_fp.write("\n")
        lock.release()

    def all_channel_video_data(self, channel_list, limit=50, vid_part='snippet', output_path='./', \
                               error_file_name='../status/errors.txt'):
        """
        Function to return data of all the videos of input channels.
        It takes the following parameters: 
            1. channel_list: List of channels whose data are to be extracted.
            2. limit: Maximum number of videos-details extracted in a single call. -- Default value is 50. --
            3. vid_part: vid_part: List of comma-separated resource-properties that the API response would include. 
               Possible values are:
                    ** contentDetails
                    ** fileDetails
                    ** processingDetails
                    ** liveStreamingDetails
                    ** processingDetails
                    ** id
                    ** recordingDetails
                    ** localizations
                    ** snippet
                    ** statistics
                    ** status
                    ** topicDetails
                    ** suggestions
                    ** player
                    -- Default value is: "snippet". -- 
            4. output_path:  Path of a output directory where all the data would be saved. 
               -- Default value is: "./". --
            5. error_file_name: Name and path of a error-log file which is generated during the extraction.
            -- Default path is "../status/errors.txt". --
            """
        
        # chnl_details_file = open(output_path+"channel_details.csv", "a")
        # os.makedirs(output_path, exist_ok=True)
        dnload = partial(self.single_channel_video_data, limit, vid_part, output_path)
        l = mp.Lock()
        pool = mp.Pool(initializer=self.init, initargs=(l, ), processes=4)
        pool.map(dnload, channel_list)
        pool.close()
        # pool.join()

        # for i, chanlid in enumerate(channel_list):
        #     print("index: ", i, " : ", chanlid)
        #     all_result={}
        #     print("finding vidids")
        #     result = self.playlist([chanlid],limit)
        #     print("finding channel meta")
        #     all_result.update({chanlid: self.get_video_details(result[chanlid], part=vid_part)})
        #     print("doing json dump")
        #     json.dump(all_result, chnl_details_file)
        #     chnl_details_file.write("\n")
        # return all_result
     
    def search_results_extraction(self, queries, ChannelId=None, limit=None, order=None, nextPageToken=None, \
                                  publishedAfter=None, publishedBefore=None, topicId=None, \
                                  videoDuration=None, only_id=None, res_type=None, videoCategoryId=None, \
                                  regionCode=None, part="snippet"):
        """
        Function to get search results about a input queries.
        It takes only 1 user parameter named as queries. All other parameters are default-type. 
        Parameters are:
            1.  queries: List of queries for which results are required.
            2.  ChannelId: -- Default value is None. --
            3.  limit: Maximum number of videos-details extracted in a single call. -- Default value is None. --
            4.  order: 
            5.  nextPageToken: Token id of next page from search results.
            6.  publishedAfter: Date after which the search results need to be published.
            7.  publishedBefore: Date before which the search results need to be published.
            8.  topicId: The topicId parameter indicates that the API response should only contain resources associated with the specified topic. The value identifies a Freebase topic ID.Important: Due to the deprecation of Freebase and the Freebase API, the topicId parameter started working differently as of February 27, 2017. At that time, YouTube started supporting a small set of curated topic IDs, and you can only use that smaller set of IDs as values for this parameter.
            9.  videoDuration: The videoDuration parameter filters video search results based on their duration. If you specify a value for this parameter, you must also set the type parameter's value to video.
                    Acceptable values are:
                         1.any – Do not filter video search results based on their duration. This is the default value.
                         2.long – Only include videos longer than 20 minutes.
                         3.medium – Only include videos that are between four and 20 minutes long (inclusive).
                         4.short – Only include videos that are less than four minutes long.

            10. only_id: Whenever only_id=1, only video ids will be fetched.
            11. res_type: Specifies whether we want videos results only or channel results or playlist results only.
            12. videoCategoryId: The videoCategoryId parameter filters video search results based on their category. If you specify a value for this parameter, you must also set the type parameter's value to video.
            13. regionCode: The regionCode parameter instructs the API to return search results for videos that can be viewed in the specified country. The parameter value is an ISO 3166-1 alpha-2 country code.
            14. part: List of comma-separated resource-properties that the API response would include.
                    -- Default value is snippet. --
            """
        key = self.keylist[self.keyindex]
        url_s = "https://www.googleapis.com/youtube/v3/search"
        search_details = {}
            
        if limit <= 50 and limit > 0:
            maxResults = limit
        else:
            maxResults = 50
        
        if publishedAfter is not None:
            try:
                datetime.datetime.strptime(publishedAfter, "%Y-%m-%d")
            except:
                print("Incorrect date format! it should be yyyy-mm-dd.")

        elif publishedBefore is not None:
            try:
                datetime.datetime.strptime(publishedBefore,"%Y-%m-%d")
            except:
                print("Incorrect date format! it should be yyyy-mm-dd.")

        for query in queries:
            search_count = initial = 0
            results = []
            try:
                while nextPageToken or initial == 0:
                    
                    querystring = {"part": part,
                             "maxResults": maxResults,
                             "q": query,
                             "key": key,
                             "order": order,
                             "pageToken": nextPageToken,
                             "publishedAfter": publishedAfter,
                             "publishedBefore": publishedBefore,
                             "topicId": topicId,
                             "videoDuration": videoDuration,
                             "type": res_type,
                             "videoCategoryId": videoCategoryId,
                             "regionCode": regionCode
                             }

                    response = request_handler(self, url=url_s, params=querystring, wait=5,) #ids=query)
                    #print(response)
                
                    if response.get('error'):
                        while response['error']['errors'][0]['reason'] == 'quotaExceeded' or \
                              response['error']['errors'][0]['reason'] == 'dailyLimitExceeded':
                                key = keychange(self)
                                querystring = {"part": part,
                                      "maxResults": maxResults,
                                      "q": query,
                                      "key": key,
                                      "order": order,
                                      "pageToken": nextPageToken,
                                      "publishedAfter": publishedAfter,
                                      "publishedBefore": publishedBefore,
                                      "topicId": topicId,
                                      "videoDuration": videoDuration,
                                      "type": res_type,
                                      "videoCategoryId": videoCategoryId,
                                      "regionCode": regionCode
                                      }
                                   
                                response = request_handler(self, url_s, params=querystring, wait=5, ids=query)

                        search_details.update({query: 'error'})
                        if response['error']['errors'][0]['reason'] == 'keyInvalid':
                            return [{query: str(response)}]
                        break               

                    if response.get('Interneterror'):
                        results.append(response)
                        break

                    if limit == -1:
                        limit = response['pageInfo']['totalResults']
                        #print(limit)
                                               
                    if only_id == 1 and res_type == 'video':
                        for i in range(response['pageInfo']['resultsPerPage']):
                            try:        
                                results.append(response['items'][i]['id']['videoId'])
                            except:
                                pass

                    elif only_id == 1 and res_type == 'channel':
                        for i in range(response['pageInfo']['resultsPerPage']):
                            try:    
                                results.append(response['items'][i]['id']['channelId'])
                            except:
                                pass

                    elif only_id == 1 and res_type == 'playlist':
                        for i in range(response['pageInfo']['resultsPerPage']):
                            try:
                                results.append(response['items'][i]['id']['playlistId'])
                            except:
                                pass

                    elif only_id == 1:
                        print("res_type argument cannot be None when only_id=1")
                    else:
                        results.append(response['items'])
                    
                    nextPageToken = response.get('nextPageToken')
                    try:
                        search_count += len(response['items'])
                        if search_count >= limit:
                            break
                    except:
                        pass
                    
                    initial += 1
                    #print(initial)
                search_details.update({query: results})                  

            except Exception as e:
                print("Error: ", e, " : ", traceback.print_exc())
                search_details[query] = 'error'
                break

        return search_details
    
    def comment_extraction(self, part, Identity, limit=None, order=None, nextPageToken=None, searchTerms=None):
        """
        Function to extract comments from a particular video.
        It takes the following parameters:
            1. part: List of comma-separated resource-properties that the API response would include. 
            it can be:
                ** id
                ** snippet
            2. Identity: Specifies whether we want comments of a video, channel or a playlist. Based on that id can be video id/channel id/playlist id.
            3. limit: Maximum number of comments needed to extract. -- Default value is -1 to extract all the results. --
            4. order: Order in which the response would be listed. Possible values are:
                    ** time 
                    ** relevance
               -- Default value is time. --
            5. nextPageToken:
            6. searchTerms: API response would include only those comments which contain the searchTerms.
        Returns a comment details as dictionary."""
        key = self.keylist[self.keyindex]
        url_ct = "https://www.googleapis.com/youtube/v3/commentThreads"
        comment_details = {}

        if Identity.startswith("UC"):
            channelId = Identity
            ct_id = None
            videoId = None

        elif Identity.startswith("Ug"):
            ct_id = Identity
            channelId = None
            videoId = None

        elif len(Identity) == 11:
            videoId = Identity
            ct_id = None
            channelId = None

        else:
            return "Invalid input to Identity Parameter"       
        
        if limit != None and limit >= 1 and limit <= 100:
            maxResults = limit
        else:
            maxResults = 100
        
        comment_count = initial = 0
        
        try:
            while nextPageToken or initial == 0:
                querystring = {"part": part,
                              "channelId": channelId,
                              "id": ct_id,
                              "videoId": videoId,
                              "maxResults": maxResults,
                              "key": key,
                              "order": order,
                              "pageToken": nextPageToken,
                              "searchTerms": searchTerms
                            }

                response=request_handler(self, url_ct, params=querystring, wait=5)
                #print(response)                
                if response.get('error'):
                    while response['error']['errors'][0]['reason'] == 'quotaExceeded' or \
                          response['error']['errors'][0]['reason'] == 'dailyLimitExceeded':
                            key = keychange(self)
                            querystring = {"part": part,
                                          "channelId": channelId,
                                          "id": ct_id,
                                          "videoId": videoId,
                                          "key": key,
                                          "maxResults": maxResults,
                                          "order": order,
                                          "pageToken": nextPageToken,
                                          "searchTerms": searchTerms
                                        }
                            
                            response = request_handler(self, url_ct, params=querystring, wait=5)
                            if response.get('error'):
                                continue
                            else:
                                break
                           # print(response)
                if response.get('error'):
                    comment_details.update({Identity: [str(response)]})
                    if response['error']['errors'][0]['reason'] == 'keyInvalid':
                        return [{Identity: [str(response), response.text]}]
                    break
                
                if response.get('Interneterror'):
                    comment_details.update({Identity: response})
                    break
                # print(response)                    
                # if limit == -1:
                #     limit = response['pageInfo']['totalResults']
                nextPageToken = response.get("nextPageToken")
                
                try:
                    comment_count = comment_count + len(response['items'])
                    # print("total comment extracted",comment_count)
                    if comment_details.get(Identity):
                        comment_details[Identity].extend(response['items'])
                    else:
                        comment_details[Identity] = response['items']
                    if nextPageToken==None or (comment_count>= limit and limit!=-1):
                        break
                    

                except:
                    pass

                initial += 1

            # try:
            #     comment_details[Identity] = response['items']
            # except:
            #     pass

        except Exception as e:
            print(e,traceback.format_exc())

        return comment_details

    def init(self, l):
        """
        Function to specify a lock used by process."""
        global lock
        lock = l
    
    def reques_handler_2(self,ch_list):
        return self.get_channel_details([ch_list])
    
    def extract_data(self,class_ins):
        df = pd.read_csv('channel.csv')
        channel_list = df['channel']
        final_ch = 0
        part = partial(self.reques_handler_2)
        p = Pool(5)
        for j in tqdm(range(23730,48000,100)):
            print(j)
            pooled_data = p.map(part , channel_list[j:j+100])
            #print(pooled_data)

            for i in pooled_data:
                try: 
                    count = i[list(i.keys())[0]][0]['statistics'].get('videoCount',-1)
                    final_ch = count
                except Exception as e:
                    print(e)
                    final_ch = -1
                    
                with open('test.csv','a') as f:
                    f.write('%s,%s\n'%(list(i.keys())[0],final_ch))
                    f.flush()
            
    #_t = threading.Threading(target = reques_handler_2 , args = (channel_list[10001:20000],class_ins))
   
df = pd.DataFrame()
file_size =1000000;
i=2;
def comment_extract(data):
    global df;
    global i;
    if df.shape[0]>=file_size:
        print(i)
        try:
            df.columns =['textDisplay','textOriginal','likeCount','videoId']
        except Exception as e:
            print(e)
        df.to_csv("./output/output2_"+str(i)+".csv",index=False,sep='\t',encoding='utf-8')
        i+=1
        df=pd.DataFrame()
    for key,val in data.items():
        for every_val in val:
            #every_val['snippet']['topLevelComment']['snippet'].keys()
            try:
                az=every_val['snippet']['topLevelComment']['snippet']['textDisplay']
                ay=every_val['snippet']['topLevelComment']['snippet']['textOriginal']
                ax=every_val['snippet']['topLevelComment']['snippet']['likeCount']
                aq=every_val['snippet']['topLevelComment']['snippet']['videoId']
                df= df.append([[az,ay,ax,aq]],ignore_index=True)
            except Exception as e:
                print(e)         
            
if __name__ =='__main__':
    data = Youtube_extract()
#     #channels = pd.read_csv('channelinfo.csv')
#     with open("family_channels_10dec.txt", "r") as f:
#         channel_id = [i.strip() for i in f.readlines()]
# #     channel_id = ["UCUmRTV6d8HvUazVwOEY9daQ"]
#     with open("skip_channels.txt", "r") as f:
#         skip_channels = [i.strip() for i in f.readlines()]
#     for i in channel_id:
#         if i in skip_channels:
#             channel_id.remove(i)
#     print(channel_id)
#     exit()
#     data.all_channel_video_data(channel_id, limit=-1)
#     videoid = 'Diibn7TZ4Hg'
    chanel_ids = pd.read_csv('channels_identifier.csv')
    #print(chanel_ids['channelid'])
    
    for index,channel in enumerate(chanel_ids['channelid']):
        
        if index%500 == 0:
            print("{} profiles Downloaded".format(index))

        try:
            cmnt_data = data.get_channel_details(chan_ids_list = [channel],part = 'snippet')
            
            url = cmnt_data[channel][0]['snippet']['thumbnails']['default']['url']
            print(url)
            resp = requests.get(url, stream=True)
            with open('./profile2/'+channel+'.jpg', 'wb') as f:

            # # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                resp.raw.decode_content = True
                shutil.copyfileobj(resp.raw, f)
        # # Remove the image url response object.
                del resp
        except Exception as e:
            print("{} occured, {} could not be downloaded".format(e,channel))
    # 

    #print(len(id_s))
    #     coun += 1
    #url  = thumb[c_id][0]['snippet']['thumbnails']['default']['url']

    #print(a[0]['snippet']['topLevelComment']['snippet']['authorChannelId']['value'])
    #print(a[0]['id'])
    #id_s = []
    # urls = []
    # coun = 0
    # for i in a:
    #     #print('UC'+i['id'][2:])
    #     if coun%20 == 0:
    #         print(i)
    #     c_id = i['snippet']['topLevelComment']['snippet']['authorChannelId']['value']
    #     #id_s.append(i['id'])
    #     #print('id is ', i['id'])
    #     thumb = data.get_channel_details(chan_ids_list = [c_id], part = 'snippet')
    #     url  = thumb[c_id][0]['snippet']['thumbnails']['default']['url']
    # # Open the url image, set stream to True, this will return the stream content.
    #     resp = requests.get(url, stream=True)
    #     # Open a local file with wb ( write binary ) permission.
    #     local_file = open('tthumbnails/'+c_id+'.jpg', 'wb')
    # # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
    #     resp.raw.decode_content = True
    # # Copy the response stream raw data to local image file.
    #     shutil.copyfileobj(resp.raw, local_file)
    # # Remove the image url response object.
    #     del resp
    # #print(len(id_s))
    #     coun += 1
    #print(len(set(id_s)))
    #thumb = get_channel_details(chan_ids_list = id_s, part = 'snippet')

#     # Import requests, shutil python module.
#     #import requests


#     #with open('data.txt', 'w') as outfile:
#     #   json.dump(cmnt_data, outfile)

    #ChannelId='UCu-luPcM9OzpFRzOVAG7-cQ'
    #result = data.get_channel_details(chan_ids_list=list_of_channels,part='statistics')
    #print(result)
    #out=data.playlist(channel_list=list_of_channels,limit=10,part='contentDetails',only_id=1)
    #print(out)
    
    
    #vid_det_out=data.get_video_details(vid_ids_list=list_of_videos,part='snippet')
    #print(vid_det_out)
    
#    keywords = ["Indian Army", "Military Training", "Army Weapons", "Assault Rifles", "Army Tanks", "War Weapons",
#                "Fighting weapons", "Head-shot", "Distructive weapons"]
#    search_res_out = data.search_results_extraction(keywords, limit=4000, only_id=1, res_type='video', \
#                                                    part='snippet')
#
#    with open('video_ids.csv', 'w') as f:
#        for key in search_res_out.keys():
#            f.write("%s\n"%(search_res_out[key]))
    
    
    #comment_out=data.comment_extraction(part='snippet',Identity='UgyJub3Fx6KlpdSn8Ap4AaABAg',limit=-1)
    #print(comment_out)

        ###Write this result Data in your csv File
        #Result format dictionary {'UCTKdIhpaOFUbfSZXimBvYoQ': [{'statistics': {'subscriberCount': '3195', 'viewCount': '1087730', 'videoCount': '240', 'hiddenSubscriberCount': False, 'commentCount': '0'}, 'etag': '"XpPGQXPnxQJhLgs6enD_n8JR4Qk/qC3tc6gL7VtjqEEuSwFi4hoByW4"', 'kind': 'youtube#channel', 'id': 'UCTKdIhpaOFUbfSZXimBvYoQ'}]}

