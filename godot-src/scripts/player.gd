extends CharacterBody2D
@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D
@onready var jump_sound: AudioStreamPlayer2D = $jumpSound


const SPEED = 300.0
const JUMP_VELOCITY = -850.0
var alive = true
@onready var death_sound: AudioStreamPlayer2D = $DeathSound

var current_rl_action = 0

func get_rl_state() -> Array:
	var state = []
	# Position
	state.append(position.x / 1000.0)
	state.append(position.y / 1000.0)
	# Grounded
	state.append(1.0 if is_on_floor() else 0.0)
	# Vector to nearest reward
	var apples = get_tree().get_nodes_in_group("apples")
	var nearest_apple = null
	var nearest_apple_dist = 10000.0
	for apple in apples:
		if apple.monitoring:
			var dist = position.distance_to(apple.position)
			if dist < nearest_apple_dist:
				nearest_apple_dist = dist
				nearest_apple = apple
	
	if nearest_apple:
		state.append(clamp((nearest_apple.position.x - position.x) / 1000.0, -1.0, 1.0))
		state.append(clamp((nearest_apple.position.y - position.y) / 1000.0, -1.0, 1.0))
	else:
		state.append(0.0)
		state.append(0.0)
		
	# Vector to nearest enemy
	var enemies = get_tree().get_nodes_in_group("enemies")
	var nearest_enemy = null
	var nearest_enemy_dist = 10000.0
	for enemy in enemies:
		var dist = position.distance_to(enemy.position)
		if dist < nearest_enemy_dist:
			nearest_enemy_dist = dist
			nearest_enemy = enemy
			
	if nearest_enemy:
		state.append(clamp((nearest_enemy.position.x - position.x) / 1000.0, -1.0, 1.0))
		state.append(clamp((nearest_enemy.position.y - position.y) / 1000.0, -1.0, 1.0))
	else:
		state.append(0.0)
		state.append(0.0)
		
	return state

func _physics_process(delta: float) -> void:
	
	if !alive:
		return
		
	if position.y > 1000:
		die("fall")
		return

	# Add animation 
	if velocity.x > 1 or velocity.x < -1:
		animated_sprite_2d.animation = "running"
	else:
		animated_sprite_2d.animation = "idle"		
	
	# Add the gravity.
	if not is_on_floor():
		velocity += get_gravity() * delta
		animated_sprite_2d.animation = "jumping"

	var dir = 0.0
	var jump_pressed = false
	
	if RLBridge.is_connected:
		# Use RL Actions
		# 0: Nothing, 1: Right, 2: Left, 3: Jump, 4: Right+Jump, 5: Left+Jump
		if current_rl_action in [1, 4]: dir = 1.0
		elif current_rl_action in [2, 5]: dir = -1.0
		if current_rl_action in [3, 4, 5]: jump_pressed = true
	else:
		dir = Input.get_axis("left", "right")
		jump_pressed = Input.is_action_just_pressed("jump")

	# Handle jump.
	if jump_pressed and is_on_floor():
		velocity.y = JUMP_VELOCITY
		jump_sound.play()

	if dir:
		velocity.x = dir * SPEED
	else:
		velocity.x = move_toward(velocity.x, 0, SPEED)

	move_and_slide()
	
	# Animation direction 
	if dir == 1.0:
		animated_sprite_2d.flip_h = false
	elif dir == -1.0:
		animated_sprite_2d.flip_h = true
		
func die(reason: String = "unknown") -> void:
	death_sound.play()
	animated_sprite_2d.animation = "dying"
	alive = false
	if RLBridge.is_connected:
		RLBridge.add_reward(-10.0)
		RLBridge.cause_of_death = reason
		RLBridge.is_done = true
		get_parent().get_parent()._send_rl_state()
		
