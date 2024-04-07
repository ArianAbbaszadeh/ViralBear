from datetime import *
import os 

#csv reading
import pandas as pd
from schedule import *

class Channel:
    def __init__(self, channel_dict = None, name = None) -> None:
        if channel_dict is None and name is not None:
            channel_dict = get_channels_dict(name)
        else:
            ValueError("No parameter given")

        self.name = channel_dict["NAME"]
        self.cookies = channel_dict["COOKIES_PATH"]
        self.schedule = channel_dict["SCHEDULE"] 
        self.genre = channel_dict["GENRE"]  

    def __str__(self) -> str:
        tmp = f'NAME: {self.name}\n'
        tmp += f'COOKIES_PATH: {self.cookies}\n'
        tmp += f'SCHEDULE_PATH: {self.schedule}\n'
        tmp += f'GENRE: {self.genre}\n'
        return tmp
    
class Schedule():
    def __init__(self, channel: Channel):
        file = f"caches/{channel.name}.csv"
        if not os.path.isfile(file):
            init = pd.DataFrame(columns=['ID', 'TITLE', 'CHANNEL', 'SCHEDULE', 'UPLOAD'])
            init.to_csv(file, index= False)
        self.data = pd.read_csv(file, dtype= {'ID': str}, index_col= 'ID')
        self.channel = channel
        self.file = file
    
    #####################################
    ### SCHEDULE OPERATORS            ###
    #####################################

    def add_video(self, id, title):
        video = {'TITLE': title,
                 'CHANNEL': self.channel.name,
                 'SCHEDULE': self.get_next_post_time(),
                 'UPLOAD': 'W'}
        
        self.data.loc[id] = video
        self.data.to_csv(self.file)

    def remove_video(self, id):
        self.data = self.data.drop(id, axis= 0)
        self.data.to_csv(self.file)

    def get_next_post_time(self):
        current = datetime.now()
        #if there is already an item in cached, set current to the latest time in the cached
        if len(self.data) and datetime.now() < datetime.strptime(self.data.tail()["SCHEDULE"].values[0], '%Y-%m-%d %H:%M'):
            current = datetime.strptime(self.data.tail()["SCHEDULE"].values[0], '%Y-%m-%d %H:%M') #make it work per channelnot for thentire csv

        #create list of times to post
        times: list
        with open(self.channel.schedule) as schedule:
            times = schedule.read().split("\n")

        times = [item.split("_") for item in times]

        #if it is past the last posting time of the day, make the current time tomorrow 
        if current.hour > int(times[datetime.weekday(current)][-1]):
            current = (current+timedelta(days = 1)).replace(hour= 0, minute= 0, second= 0, microsecond=0)
            
        #now that we are on the correct day, find the posting time that has not been reached yet
        for time in times[datetime.weekday(current)]:
            if current.hour < int(time):
                current = current.replace(hour = int(time))
                break
        return current.strftime('%Y-%m-%d %H:%M')
    

    def set_posted(self, id, set_to_posted=True):
        try:
            self.data.at[id, "UPLOAD"] = 'S' if set_to_posted else 'W'
        except:
            print("video ID not found")

        self.data.to_csv(self.file)
        print(f"Status for video {id} has been set to {'S' if set_to_posted else 'W'}.")
    
    #####################################
    ### VIDEO OPERATORS               ###
    #####################################
    def get_videos_by_day(self, day: datetime):
        #print(datetime.strptime(self.data["SCHEDULE"].values[0], '%Y-%m-%d %H:%M').date())
        videos = self.data.to_dict('records')
        return [video for video in videos if datetime.strptime(video["SCHEDULE"], '%Y-%m-%d %H:%M').date() == day.date() and video["UPLOAD"] != 'S']

if __name__ == "__main__":
    channels_dict = {'NAME': 'TIKTOK_1', 
                     'COOKIES_PATH': 'cookies/cookies1.txt',
                     'SCHEDULE': 'schedule.txt',
                     'GENRE': 'RYAN'}
    channel = Channel(channels_dict)
    schedule = Schedule(channel)
    print(schedule.get_videos_by_day(datetime.today()))

    
   