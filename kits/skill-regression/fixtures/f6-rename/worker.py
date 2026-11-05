def retry(job):
    tmp = 0
    while tmp < 3:
        if job():
            return True
        tmp += 1
    return False
