import pandas as pd
NUM_HOURS = 24
MIN_NUM_AUDIOMOTHS = 2

def extract_hour(time_list):
    hour_list = []
    for time in time_list:
        time = time[12:14] + time[15:17]
        hour_list.append(int(time)//100)
    return hour_list

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

    #From each audiomoth, randomly sample one clip from each hour
    data['Hour'] = extract_hour(data['Comment'])
    data = data.groupby(['AudioMothCode','Hour'], as_index=False).apply(lambda x: x.sample(1))

    #Drop audiomoths that did not have all hours
    data = data.groupby('AudioMothCode').filter(lambda x: len(x)==NUM_HOURS)
    data.pop('Hour')

    if(len(data)<MIN_NUM_AUDIOMOTHS*NUM_HOURS):
        print("Not enough data to sample")
        return False

    try:
        data.to_csv(path[:-4]+"_Sample.csv", index=False)
        return True
    except:
        print("Writing file failed")
        return False
