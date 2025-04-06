import random

def next_track(queue:list,repeat):
    if len(queue) > 0:
        if repeat == "All":
            track = queue[0]
            queue.pop(0)
            queue.append(track)
        elif repeat == "None":
            queue.pop(0)
        
def previous_track(queue:list):
    track = queue[len(queue)-1]
    queue.pop(len(queue)-1)
    queue.insert(0,track)
        
def jump_track(queue:list,index,repeat):
    for i in range(0,index-2):
        if repeat == "All":
            track = queue[0]
            queue.pop(0)
            queue.append(track)
        else:
            queue.pop(0)
            
def add_track(list:list,track):
    list.append(track)
    
def delete_track(list:list,index):
    list.pop(index-1)
    
def clear_track(list:list):
    return []

def removedupe_track(list:list):
    for a in list:
        for i in range(0,list.count(a)-1):
            list.remove(a)

def shuffle_track(list:list):
    result = []
    times = len(list)
    for i in range(0, times):
        x = random.randint(0, len(list)-1)
        result.append(list[x])
        list.pop(x)
    return result