# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 18:26:18 2020

@author: Wilson
"""

import json, requests, time, random
from pytube import YouTube
from datetime import datetime
from sys import exit
import re, io

count = 0
countDL = 0
countSkip = 0
starttime = datetime.now()

#random timer wait
def wait(start, end):
    time.sleep(random.uniform(start,end))

#ffmpeg function to merge discrete video/audio tracks into one - must have ffmpeg-python pip installed and in windows
#Ensure that subdirectories videos\ProcessedVideos already exist
import ffmpeg
def AVprocess(v, a, d):
    input_video = ffmpeg.input(str(d) + str(v))
    input_audio = ffmpeg.input(str(d) + str(a))
    ffmpeg.output(input_audio, input_video, str(d) + 'ProcessedVideos/' + str(v)).run()

#YouTube Download Function
from os import path
def YouTubeDL(vID, vTitle, vEpisode):
    global countDL
    global countSkip
    fileName = str(str(vEpisode[0:3]).zfill(3) + "-" + str(vID) + "-" + vTitle)
    ytLink = str('https://www.youtube.com/watch?v=') + str(vID)
    if path.exists('./videos/' + fileName + '.mp4') or path.exists('./videos/ProcessedVideos/' + fileName + '1080p.mp4'):
        #checks video directory for Progressive video already existing to avoid repeated downloads
        print('SKIPPED - YouTube file ' + fileName + ' located at ' + ytLink + ' already exists in directory.')
        countSkip +=1
    else: #downloads and converts videos if not already downloaded
        wait(1,5) #random wait times to pause automation from violating YT TOS
        yt = YouTube(ytLink)
        #Progressive Video Download (<720p)
        video = yt.streams.filter(progressive='True').first()
        #fileName = (str(videoEpisode) + "-" + str(videoTitle) + "-" + videoID)
        video.download('./videos',fileName)
        #High Resolution Video/Audio Download
        video = yt.streams.filter(resolution='1080p').first()
        video.download('./videos',fileName + '1080p')
        audio = yt.streams.filter(abr='160kbps').first()
        audio.download('./videos',fileName + '160kbps')
        #English Caption Download
        try: #error handling for cases where subtitles may not exist or is erroronous
            captionFile = io.open('./videos/' + fileName + '.srt',mode='w',encoding='utf-8')
            #caption = yt.captions.get_by_language_code('en') old deprecated function
            caption = yt.captions['en'] #new dictionary call (untested)
            captionFile.write(caption.generate_srt_captions())
            captionFile.close()
        except: 
            Logging('Caption generation failed for video ' + videoID)
            pass
        #Combine High Resolution
        try:
            AVprocess(fileName+'1080p.mp4', fileName+'160kbps.webm', './videos/')
            countDL += 1
        except:
            Logging('AVprocess failed for video ' + videoID)
            pass
        #Writes same SRT file for Hi Resolution Video
        try:
            captionFile2 = io.open('./videos/ProcessedVideos/' + fileName + '1080p.srt',mode='w',encoding='utf-8') 
            captionFile2.write(caption.generate_srt_captions())
            captionFile2.close()
        except: 
            Logging('Caption generation failed for video' + videoID)
            pass

def Logging(text):
    Log = io.open('YTlog.txt',mode='a+',encoding='utf-8')
    Log.write(str(datetime.today().strftime('%m.%d.%Y-%H:%M:%S')) + " -  " + text + "\n")
    Log.close()

#URL must include valid Google YouTube Data API V3 API Key
#YouTube Playlist API returns different JSON structures
#url = 'https://www.googleapis.com/youtube/v3/playlistItems?playlistId=PLS-7gvHvjh_CW6pL2lSHtu0CO_iUAj8E9&maxResults=50&part=snippet&key=AIzaSyCGXnwsFt6S7sRq7zwuGPvDLU0zvKbgHwE'
url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId=UCpZqbJnB1yr3pzNgYGjWvfw&maxResults=50&order=date&q=gudetama%2Banimation%2Bepisode%2Bofficial%2Bupload%2B%E3%80%90Sanrio%2BOfficial%E3%80%91&type=video&key=[API KEY]'
response = requests.get(url)
data = json.loads(response.text)
videos = {}
vList = io.open('videoList.txt',mode='w',encoding='utf-8')

try:
    for x in range(len(data['items'])):
        #print(data['items'][x]['id']['videoId'])
        #links.append(str('https://www.youtube.com/watch?v=') + str(data['items'][x]['snippet']['resourceId']['videoId']))
        videoID = data['items'][x]['id']['videoId']
        videoTitle = data['items'][x]['snippet']['title']
        videos[videoID] = videoTitle #writes video ID/title as dictionary pair
        videoEpisode = re.sub('[^0-9]','', videoTitle) #extracts only digits from video title
        #videoList(videoID) #writes video ID into a link for reference
        vList.write(str('https://www.youtube.com/watch?v=') + str(videoID) + "\n")
        YouTubeDL(videoID, videoTitle, videoEpisode) #Downloads YouTube video
        count += 1
except KeyError:
    starttime = datetime.now() - starttime
    print('An API exception has occurred, this may be due to API quota limitation.')
    Logging(str(" -  An API exception has occurred" + str(count) + " videos found,  "
          + str(countDL) + " videos downloaded and processed. Process duration: " + str(starttime) + " seconds."))
    exit()

while 'nextPageToken' in data:
    try:
        paginationToken = data['nextPageToken']
        url2 = url + '&pageToken=' + paginationToken
        response = requests.get(url2)
        data = json.loads(response.text)
        for x in range(len(data['items'])):
            videoID = data['items'][x]['id']['videoId']
            videoTitle = data['items'][x]['snippet']['title']
            videos[videoID] = videoTitle
            videoEpisode = re.sub('[^0-9]','', videoTitle)
            #videoList(videoID) #writes video ID into a link for reference
            vList.write(str('https://www.youtube.com/watch?v=') + str(videoID) + "\n")
            YouTubeDL(videoID, videoTitle, videoEpisode) #Downloads YouTube video
            count += 1
    except KeyError:
        starttime = datetime.now() - starttime
        print('An API exception has occurred, this may be due to API quota limitation.')
        Logging(str(" -  An API exception has occurred" + str(count) + " videos found,  "
          + str(countDL) + " videos downloaded and processed. Process duration: " + str(starttime) + " seconds."))
        exit()

vList.close()

#End of Script Logging function
starttime = datetime.now() - starttime
Logging(str(str(count) + " videos found,  " + str(countSkip) + "videos skipped, and "
          + str(countDL) + " videos downloaded and processed. Process duration: " + str(starttime) + " seconds."))
print(str(count) + " videos found,  " + str(countSkip) + "videos skipped, and "
          + str(countDL) + " videos downloaded and processed. Process duration: " + str(starttime) + " seconds." + "\n")
