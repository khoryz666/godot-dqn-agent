extends Node

signal action_received(action_id)
signal reset_requested()

var socket := WebSocketPeer.new()
var is_connected := false

var current_reward := 0.0
var total_score := 0.0
var is_done := false
var cause_of_death := ""
var prev_apple_dist = -1.0
var last_reconnect_time = 0.0

func add_reward(amount: float):
	current_reward += amount

func add_score(amount: float):
	current_reward += amount
	total_score += amount

func reset_episode():
	current_reward = 0.0
	total_score = 0.0
	is_done = false
	cause_of_death = ""
	prev_apple_dist = -1.0

func _ready():
	# Keep processing even when the game is paused
	process_mode = Node.PROCESS_MODE_ALWAYS
	connect_to_server()

func connect_to_server():
	print("RLBridge connecting to ws://127.0.0.1:11000...")
	var err = socket.connect_to_url("ws://127.0.0.1:11000")
	if err != OK:
		print("Unable to connect")

func _process(_delta):
	socket.poll()
	var state = socket.get_ready_state()
	
	if state == WebSocketPeer.STATE_OPEN:
		if not is_connected:
			print("Connected to Python RL Agent!")
			is_connected = true
			
		while socket.get_available_packet_count():
			var packet = socket.get_packet()
			var msg = packet.get_string_from_utf8()
			_handle_message(msg)
			
	elif state == WebSocketPeer.STATE_CLOSED:
		if is_connected:
			print("Disconnected from Python RL Agent.")
			is_connected = false
			
		var current_time = Time.get_ticks_msec() / 1000.0
		if current_time - last_reconnect_time > 1.0:
			last_reconnect_time = current_time
			connect_to_server()

func _handle_message(msg: String):
	var json = JSON.new()
	if json.parse(msg) == OK:
		var data = json.get_data()
		if typeof(data) == TYPE_DICTIONARY:
			if data.has("command") and data["command"] == "reset":
				reset_requested.emit()
			elif data.has("action"):
				action_received.emit(int(data["action"]))

func send_state(state: Array, reward: float, done: bool, score: float, info: Dictionary = {}):
	if socket.get_ready_state() == WebSocketPeer.STATE_OPEN:
		var dict = {
			"state": state,
			"reward": reward,
			"done": done,
			"score": score,
			"info": info
		}
		var msg = JSON.stringify(dict)
		socket.send_text(msg)
