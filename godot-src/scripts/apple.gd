extends Area2D
@onready var animated_sprite_2d: AnimatedSprite2D = $AnimatedSprite2D
@onready var collected_sound: AudioStreamPlayer2D = $CollectedSound


# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	add_to_group("apples")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass


func _on_body_entered(body: Node2D) -> void:
	if body.name == "Player":
		animated_sprite_2d.animation = "collected"
		collected_sound.play()
		RLBridge.add_reward(10.0)
		# Disable collision to prevent multiple collections
		set_deferred("monitoring", false)
