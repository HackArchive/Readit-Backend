
month = 30 # days
day = 24 #hours
hour = 60 #min 


def month_to_minutes(months):
    '''
        Convert no of months to minutes
    '''
    return months * month * day * hour 

def days_to_minutes(days):
    '''
        Convert no of days to minutes
    '''
    return days * day * hour

def hours_to_minutes(hours):
    '''
        Convert no of hours to minutes
    '''
    return hours * hour
