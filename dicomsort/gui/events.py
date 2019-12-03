from wx import PostEvent
from wx.lib.newevent import NewEvent

PathEvent, EVT_PATH = NewEvent()
PopulateEvent, EVT_POPULATE_FIELDS = NewEvent()
SortEvent, EVT_SORT = NewEvent()
CounterEvent, EVT_COUNTER = NewEvent()
UpdateEvent, EVT_UPDATE = NewEvent()

post_event = PostEvent
