import pandas as pd
import re
NUM_HOURS = 24
MIN_NUM_AUDIOMOTHS = 2

# Make more robust for finding hour
#def extract_hour(time_list):
#    hour_list = []
#    for time in time_list:
#        time = time[12:14] + time[15:17]
#        hour_list.append(int(time)//100)
#    return hour_list
def extract_hour(data):
    hour_list = []
    hour_regex = "([0-2][0-9]:[0-5][0-9]){0}"
    for index, row in data.iterrows():
        if (hour := re.search("([0-2][0-9]:[0-5][0-9]){1}", str(row['StartDateTime']))) is not None:
            # print(hour.group())
            hour = (int(hour.group()[:2]+hour.group()[3:]))//100
            hour_list.append(hour)
        elif (hour := re.search("([0-2][0-9]:[0-5][0-9]){1}", str(row['Comment']))) is not None:
            # print(hour.group())
            hour = (int(hour.group()[:2]+hour.group()[3:]))//100
            hour_list.append(hour)
        else:
            data.drop(index)

    data['Hour'] = hour_list
    print(data)
    return data

#######################################################################################################
#    Takes in csv path and writes a new csv file with a stratified random sample of the original csv.
#    The first strata layer to be represented by each Audiomoth device.
#    The second strata layer to be represented by the hours of the day.
#    Return True/False if the stratified csv file was successful.
#    The CSV should have #Successful Audiomoths * 24 clips.
#    Each clip should represent a different hour of the day.
#######################################################################################################
def stratified_random_sample(path):
    try:
        data = pd.read_csv(path)
    except:
        print("Reading file failed")
        return False


    #Drop problematic recordings
    data = data[data['Error'].isna()]
    data = data[data['Duration']>=60]

    # print(type(data['Comment', 'StartDateTime']))
    # print(data['Comment', 'StartDateTime'])
    #From each audiomoth, randomly sample one clip from each hour
    data = extract_hour(data)
    print(data)
    data = data.groupby(['AudioMothCode','Hour'], as_index=False, group_keys=False).apply(lambda x: x.sample(1))
    print(data)
    #Drop audiomoths that did not have all hours
    data = data.groupby('AudioMothCode').filter(lambda x: len(x)==NUM_HOURS)
    data.pop('Hour')

    print(data)

    if(len(data)<MIN_NUM_AUDIOMOTHS*NUM_HOURS):
        print("Not enough data to sample")
        return False

    try:
        #data.to_csv(path[:-4]+"_Sample.csv", index=False)
        return True
    except:
        print("Writing file failed")
        return False
