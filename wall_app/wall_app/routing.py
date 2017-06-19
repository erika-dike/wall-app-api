from channels import route
from core.consumers import connect_post, disconnect_post


"""
The channel routing defines what channels get handled by what consumers
including optional matching on message attributes. WebSocket messages of all
types have a 'path' attribute, so we're using that to route the socket.
While this is under stream/ compared to the HTML page, we could have it on the
same URL if we wanted; Daphne separatees by protocol as it negotiates with a
browser.
"""
channel_routing = [
    # Called when incoming WebSockets connect
    route('websocket.connect',
          connect_post,
          path=r'^/api/v1/core/posts/stream/$'),

    # Called when the client closes the socket
    route('websocket.disconnect',
          disconnect_post,
          path=r'^/api/v1/core/posts/stream/$'),

    # Called when the client sends message on the WebSocket
    # route('websocket.receive', save_post, path=r'^/posts/stream/$'),
]
