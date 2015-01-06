import pygmaps
import webbrowser
mymap = pygmaps.maps(37.271, -79.941, 16)
mymap.addpoint(37.2697, -79.9530, "#0000FF")
mymap.draw('C:/Users/Stupid/Desktop/./mymap.html')
url = 'C:/Users/Stupid/Desktop/./mymap.html'
webbrowser.open_new_tab(url)
