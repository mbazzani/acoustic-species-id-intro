import pandas as pd
import re
NUM_HOURS = 24
MIN_NUM_AUDIOMOTHS = 2

# Returns time found in string rounded to the nearest hour
def extract_hour(string):
    string = re.search("([0-2][0-9]:[0-5][0-9]){1}", string)
    return int(string.group()[:2]+string.group()[3:])//100


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

    #Extract hour values from StartDateTime if present, or Comment otherwise
    start_times = data['StartDateTime'].transform((lambda x: extract_hour(x) if pd.notnull(x) else x))
    comment_times = data['Comment'].transform((lambda x: extract_hour(x) if pd.notnull(x) else x))
    data['Hour'] = start_times.combine_first(comment_times)

    #From each audiomoth, randomly sample one clip from each hour
    data = data.groupby(['AudioMothCode','Hour'], as_index=False, group_keys=False).apply(lambda x: x.sample(1))

    #Drop audiomoths that did not have all hours
    data = data.groupby('AudioMothCode').filter(lambda x: len(x)==NUM_HOURS)
    data.pop('Hour')

    print(data)

    if(len(data)<MIN_NUM_AUDIOMOTHS*NUM_HOURS):
        print("Not enough data to sample")
        return False

    try:
        data.to_csv(path[:-4]+"_Sample.csv", index=False)
        return True
    except:
        print("Writing file failed")
        return False
