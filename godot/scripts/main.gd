extends Control

const SCENE_COLORS := {
	"warm": Color("#fff1d6"),
	"green": Color("#e8f3e3"),
	"violet": Color("#eee9fb"),
	"stone": Color("#e9e8e6"),
	"amber": Color("#ffedc5")
}

var state: Dictionary = {}
var scenes: Dictionary = {}
var scene_grid: HBoxContainer
var status_label: Label
var description_label: Label

func _ready() -> void:
	build_shell()
	GameClient.http.request_completed.connect(_on_api_response)
	GameClient.get_state()

func build_shell() -> void:
	var background := ColorRect.new()
	background.color = Color("#fbfaf7")
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 56)
	margin.add_theme_constant_override("margin_right", 56)
	margin.add_theme_constant_override("margin_top", 38)
	margin.add_theme_constant_override("margin_bottom", 38)
	add_child(margin)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 18)
	margin.add_child(column)

	var title := Label.new()
	title.text = "疫病推理游戏"
	title.add_theme_font_size_override("font_size", 40)
	column.add_child(title)

	status_label = Label.new()
	status_label.add_theme_font_size_override("font_size", 18)
	column.add_child(status_label)

	description_label = Label.new()
	description_label.add_theme_font_size_override("font_size", 20)
	column.add_child(description_label)

	scene_grid = HBoxContainer.new()
	scene_grid.add_theme_constant_override("separation", 16)
	column.add_child(scene_grid)

	var lower := HBoxContainer.new()
	lower.add_theme_constant_override("separation", 24)
	column.add_child(lower)

	var evidence_panel := PanelContainer.new()
	evidence_panel.custom_minimum_size = Vector2(420, 260)
	lower.add_child(evidence_panel)
	var evidence_text := Label.new()
	evidence_text.text = "场景证据\n\n点击场景卡片移动。\n移动会消耗 1 点行动力。\n当前版本先接入规则和场景导航。"
	evidence_text.add_theme_font_size_override("font_size", 19)
	evidence_panel.add_child(evidence_text)

	var dialogue_panel := PanelContainer.new()
	dialogue_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lower.add_child(dialogue_panel)
	var dialogue_text := Label.new()
	dialogue_text.text = "对话区\n\n下一步接入 NPC Agent 对话。"
	dialogue_text.add_theme_font_size_override("font_size", 19)
	dialogue_panel.add_child(dialogue_text)

func render_scenes() -> void:
	for child in scene_grid.get_children():
		child.queue_free()
	for scene_id in scenes:
		var scene: Dictionary = scenes[scene_id]
		var card := PanelContainer.new()
		card.custom_minimum_size = Vector2(220, 250)
		var style := StyleBoxFlat.new()
		style.bg_color = SCENE_COLORS.get(scene.get("tone", "stone"), Color.WHITE)
		style.corner_radius_top_left = 16
		style.corner_radius_top_right = 16
		style.corner_radius_bottom_left = 16
		style.corner_radius_bottom_right = 16
		style.border_width_left = 3 if scene_id == state.get("current_scene", "") else 1
		style.border_width_top = style.border_width_left
		style.border_width_right = style.border_width_left
		style.border_width_bottom = style.border_width_left
		style.border_color = Color("#8b5e34")
		card.add_theme_stylebox_override("panel", style)
		scene_grid.add_child(card)

		var content := VBoxContainer.new()
		content.add_theme_constant_override("separation", 10)
		card.add_child(content)
		var icon := Label.new()
		icon.text = scene.get("symbol", "•")
		icon.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		icon.add_theme_font_size_override("font_size", 42)
		content.add_child(icon)
		var name := Label.new()
		name.text = scene.get("name", scene_id)
		name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name.add_theme_font_size_override("font_size", 25)
		content.add_child(name)
		var move := Button.new()
		move.text = "当前位置" if scene_id == state.get("current_scene", "") else "前往"
		move.disabled = scene_id == state.get("current_scene", "")
		move.pressed.connect(func() -> void: GameClient.move_to(scene_id))
		content.add_child(move)

func _on_api_response(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if response_code != 200:
		status_label.text = "后端连接失败：" + str(response_code)
		return
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if parsed is Dictionary and parsed.has("npc_states"):
		state = parsed
		scenes = load_scene_data()
		status_label.text = "第 %d 天 · %s · 行动力 %d/%d · 当前场景：%s" % [state.get("day", 1), "白天" if state.get("phase") == "day" else "夜晚", state.get("action_points", 0), state.get("max_action_points", 3), state.get("current_scene", "camp")]
		description_label.text = scenes.get(state.get("current_scene", "camp"), {}).get("description", "")
		render_scenes()

func load_scene_data() -> Dictionary:
	var file := FileAccess.open("res://scenes.json", FileAccess.READ)
	if file == null:
		return {}
	var parsed = JSON.parse_string(file.get_as_text())
	var result := {}
	for scene in parsed:
		result[scene["scene_id"]] = scene
	return result
