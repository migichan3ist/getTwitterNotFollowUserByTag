import tweepy
from datetime import datetime,timezone,date
import pytz
import pandas as pd
import inspect
import requests
import json
from bs4 import BeautifulSoup

#関数:　UTCをJSTに変換する
def change_time_JST(u_time):
    #イギリスのtimezoneを設定するために再定義する
    utc_time = datetime(u_time.year, u_time.month,u_time.day, \
    u_time.hour,u_time.minute,u_time.second, tzinfo=timezone.utc)
    #タイムゾーンを日本時刻に変換
    jst_time = utc_time.astimezone(pytz.timezone("Asia/Tokyo"))
    # 文字列で返す
    str_time = jst_time.strftime("%Y-%m-%d_%H:%M:%S")
    return str_time

# Slackに送る機能
WEB_HOOK_URL = "https://hooks.slack.com/services/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"

#今日の日付を取得
DATE_TODAY = date.today()
WHAT_DAY = DATE_TODAY.strftime('%A')

SEARCH_INFORMATION = {
    'Sunday': '#日本一周',
    'Monday': '#旅行好きな人と繋がりたい ',
    'Tuesday': '#国内旅行',
    'Wednesday': '#北海道愛のTwitter会',
    'Thursday': '#札幌Twitter会',
    'Friday': '#北海道',
    'Saturday': '#観光列車',
}

NUM_SEND = 40;

TWITTER_LABELS=[
    'user_id',
    'account_name',
    'num_follow',
    'num_followd',
    'is_follow',
    ]

LINE_GAP_FOLLOW_NUM = 100

searchkey = SEARCH_INFORMATION[WHAT_DAY]
item_num = 10000

api_key = ""
api_secret = ""
access_key = ""
access_secret = ""

auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth) 

#検索条件を元にツイートを抽出
tweets = tweepy.Cursor(api.search_tweets,q=searchkey,lang='ja').items(item_num)

#抽出したデータから必要な情報を取り出す
#取得したツイートを一つずつ取り出して必要な情報をtweet_dataに格納する
now_num_send = 0

tweet_data = []

tweet_user_list = []

requests.post(WEB_HOOK_URL, data=json.dumps({
    "type": "mrkdwn",
    "text": "TODAY SEARTH TAG : " + searchkey
}))

for tweet in tweets:
    #ツイート時刻とユーザのアカウント作成時刻を日本時刻にする
    tweet_time = change_time_JST(tweet.created_at)
    create_account_time = change_time_JST(tweet.user.created_at)
    #tweet_dataの配列に取得したい情報を入れていく
    tweet_data = [
        tweet.user.screen_name, # ユーザID
        tweet.user.name, # アカウント名
        tweet.user.friends_count, # フォロー数
        tweet.user.followers_count, # フォロワー数
        tweet.user.following, # 自分がフォローしているか？
    ]
    
    labeled_tweet_data = pd.Series(tweet_data, index=TWITTER_LABELS)

    if not labeled_tweet_data["is_follow"] :

        if set(tweet_user_list) != set(tweet_user_list + [labeled_tweet_data["account_name"]]):
        
            gap_follow_followed = labeled_tweet_data["num_follow"] - labeled_tweet_data["num_followd"]
            
            if gap_follow_followed >= 0 or abs(gap_follow_followed) < LINE_GAP_FOLLOW_NUM:
                
                url = "https://twitter.com/" + labeled_tweet_data["user_id"]
                requests.post(WEB_HOOK_URL, data=json.dumps({
                    "type": "mrkdwn",
                    "text": "ユーザー名：" + "<" + url + "|" + labeled_tweet_data["account_name"] + ">"
                }))

                tweet_user_list.append(labeled_tweet_data["account_name"])
                now_num_send += 1

    if now_num_send >= NUM_SEND : 
        break
