extends Node2D

@onready var player = $LevelRoot/Player

func _ready() -> void:
	_setup_level()
	if RLBridge.is_connected or true: # Connect signals anyway just in case
		RLBridge.action_received.connect(_on_action_received)
		RLBridge.reset_requested.connect(_on_reset_requested)
		RLBridge.reset_episode()

var frame_skip = 4
var frame_counter = 0

func _physics_process(delta: float) -> void:
	if RLBridge.is_connected:
		RLBridge.add_reward(-0.01) # Small time penalty per physics frame
		frame_counter += 1
		
		# Only ask for a new decision every 4 frames
		if frame_counter >= frame_skip:
			frame_counter = 0
			# Wait for this physics frame to complete, then send state
			call_deferred("_send_rl_state")
			get_tree().paused = true

func _send_rl_state():
	var state = player.get_rl_state()
	
	# Check completion condition: 20 points means 2 apples eaten
	if RLBridge.total_score >= 20.0 and not RLBridge.is_done:
		RLBridge.is_done = true
		RLBridge.cause_of_death = "completed"
		RLBridge.add_reward(10.0) # Bonus for finishing the level

	var info = {
		"cause_of_death": RLBridge.cause_of_death,
		"distance_x": player.position.x
	}
	RLBridge.send_state(state, RLBridge.current_reward, RLBridge.is_done, RLBridge.total_score, info)
	RLBridge.current_reward = 0.0

func _on_action_received(action_id: int):
	player.current_rl_action = action_id
	get_tree().paused = false

func _on_reset_requested():
	get_tree().paused = false
	get_tree().reload_current_scene()
	RLBridge.reset_episode()

func _setup_level() -> void:
	var enemies = $LevelRoot.get_node_or_null("Enemies")
	if enemies:
		for enemy in enemies.get_children():
			if enemy.has_signal("player_died"):
				enemy.player_died.connect(_on_player_died)
	
func _on_player_died(body):
	body.die("snail")
