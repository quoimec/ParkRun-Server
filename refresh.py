# !/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Pool

from models.event import Event
from models.master import Master


with Master.refresh(bucket="parkrun-au") as master, Pool(20) as pool:

    async_events = [
        event.get() for event in [
            pool.apply_async(
                master.refresh_event, 
                kwds={"bucket": master.bucket, "data": data}
            ) for data in list(master)
        ]
    ]
    
    master.events = [event for event in async_events if isinstance(event, Event)]
    
    exceptions = [event for event in async_events if not isinstance(event, Event)]
    
if len(exceptions) > 0:
    
    for e in exceptions:
        print(e)
        
    raise Exception(f"There were {len(exceptions)} exception(s) found while processing the master refresh")
