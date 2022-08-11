import pprint

from internetarchive import get_item

item = get_item("hooting_yard_2007-01-10")
pprint.pprint(item.item_metadata)
# delete(item.identifier)
