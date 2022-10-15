from datetime import timedelta


def timematter(x):
    s = timedelta(seconds=x)

    if s.days < 1:
        if s.seconds <= 60 * 60:
            out = f'{s.seconds//60}m {s.seconds - (s.seconds//60)*60}s'
        else:
            out = f'{s.seconds//(60*60)}h {int(s.seconds/60 - (s.seconds//3600)*60)}m {s.seconds - (s.seconds//60)*60}s'
    else:
        out = f'{s.days}d {s.seconds//(60*60)}h {int(s.seconds/60 - (s.seconds//3600)*60)}m {s.seconds - (s.seconds//60)*60}s'
    return out