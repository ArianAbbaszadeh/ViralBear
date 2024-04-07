from datetime import *
import os 

#csv reading
import pandas as pd

def get_datetime(str, format) -> datetime:
    return datetime.strptime(str, format)

def isPast(schedule: datetime):
    now = datetime.now()
    return schedule < now

def get_schedule(name):
    channels = pd.read_csv("channels.csv")
    return channels[channels['NAME'] == name]['SCHEDULE']
    
#adds a channel, cokies_path, and 
def new_channel(name, cookies_path, schedule = "7_8_16\n3_7_22\n2_4_6\n7_8_23\n9_12_19\n5_13_15\n11_19_20"):
    # Read the existing CSV file
    try:
        channels = pd.read_csv("channels.csv")
    except FileNotFoundError:
        channels = pd.DataFrame(columns=['NAME', 'COOKIES_PATH', 'SCHEDULE'])

    if name in channels['NAME'].values:
        print(f"Channel {name} already exists.")
        return

    channel_schedule_file = f'{name}_schedule.txt'
    with open("schedules/" + channel_schedule_file, 'w') as file:
        file.write(schedule)
    
    new_channel_row = {
        'NAME': name,
        'COOKIES_PATH': cookies_path,
        'SCHEDULE': channel_schedule_file
    }

    # Append the new row to the channels DataFrame
    channels = channels.append(new_channel_row, ignore_index=True)

    # Save the updated DataFrame to the CSV file
    channels.to_csv('channels.csv', index=False)
    print(f"Channel {name} has been added successfully.")

#make it delete from a file
def delete_channel(name):
    verify = input("ARE YOU SURE?(YES): ")
    if verify == "YES":
        cached = pd.read_csv("channels.csv")
        cached = cached.drop(columns= [name])
        cached.to_csv('channels.csv', index= False)

        channel_schedule_file = f'{name}_schedule.txt'
        try:
            os.remove("schedules/" + channel_schedule_file)
            print(f"Channel {name} and its corresponding schedule file have been deleted.")
        except FileNotFoundError:
            print(f"Channel {name} deleted, but corresponding schedule file was not found.")
    else:
        print(f"Channel {name} does not exist.")
    
def new_video(id, title, channel):
    cached = pd.read_csv("cached.csv")
    video = {'ID': id,
             'TITLE': title,
             'CHANNEL': channel,
             'SCHEDULE': get_next_post_time(get_schedule(channel)),
             'UPLOAD' : 'W'}
    
    cached = cached.add(video)
    cached.to_csv("cached.csv")

def get_next_post_time(schedule_file = 'schedule.txt'):
    cached = pd.read_csv("cached.csv")
    current = datetime.now()
    #if there is already an item in cached, set current to the latest time in the cached
    if len(cached) and datetime.now() < datetime(cached.tail()["SCHEDULE"]):
        current = datetime(cached.tail()["SCHEDULE"]) #make it work per channelnot for thentire csv

    #create list of times to post
    times: list
    with open(schedule_file) as schedule:
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

def get_channels_dict(name):
    channels = pd.read_csv("channels.csv")
    channels = channels.to_dict('records')
    channel = [channel for channel in channels if channel["NAME"] == name]
    if len(channel) == 1:
        return channel[0]       
    print("Channel name does not exist")

def set_posted(video_id, set_to_posted=True):
    try:
        
        ['UPLOAD'] == "S" if set_to_posted else "F"
    except:
        print("video ID not found")

    cached.to_csv('cached.csv', index=False)
    print(f"Status for video {video_id} has been set to {'S' if set_to_posted else 'F'}.")

def get_channels_and_cookies():
    channels_df = pd.read_csv("channels.csv")
    channels_and_cookies = {row['NAME']: row['COOKIES_PATH'] for index, row in channels_df.iterrows()}
    return channels_and_cookies

if __name__ == "__main__":
    print(get_next_post_time())