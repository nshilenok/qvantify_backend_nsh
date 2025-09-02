from realtime.connection import Socket

SUPABASE_ID = "lwwyepvurqddbcbggdvm"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx3d3llcHZ1cnFkZGJjYmdnZHZtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY4ODA3Mzk5NSwiZXhwIjoyMDAzNjQ5OTk1fQ.pl8437JL73Lsk1a9UdY6sug25UvXKfum5-6iGZGBTf8"


def callback1(payload):
	status = payload['record']['user_id']

	if payload['record']['status'] == 0:
		print("Callback 1: ", status)

if __name__ == "__main__":
    URL = f"wss://{SUPABASE_ID}.supabase.co/realtime/v1/websocket?apikey={API_KEY}&vsn=1.0.0"
    s = Socket(URL)
    s.connect()

    channel_1 = s.set_channel("realtime:*")
    channel_1.join().on("UPDATE", callback1)
    s.listen()