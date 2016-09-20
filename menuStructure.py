import getConfig

URL = "sampleData.json"
LAYOUT_URL = "layout.json"

thisData = dict()
thisData = getConfig.getData(URL)
thisLayout = getConfig.get_layout(LAYOUT_URL)

tracker = 0

def iterateLayout(thisLayout):
    global tracker

    for key in thisLayout:
        if isinstance(thisLayout[key], dict):
            line = "Sub Menu" + key
            print (" " * tracker * 4) + line
            tracker += 1
            iterateLayout(thisLayout[key])
        else:
            line = key + " " + thisLayout[key][0] + " " + thisLayout[key][1]
            print (" " * tracker * 4) + line
        if(thisLayout.keys().index(key) == len(thisLayout.keys()) - 1):
            tracker -= 1

iterateLayout(thisLayout)
