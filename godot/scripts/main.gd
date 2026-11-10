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
var npc_list: VBoxContainer
var dialogue_label: Label
var question_input: LineEdit
var backdrop_text: Label
var selected_agent_id := ""
var agent_names := {
	"agent_wilson": "Wilson",
	"agent_willow": "Willow",
	"agent_wendy": "Wendy",
	"agent_wolfgang": "Wolfgang",
	"agent_maxwell": "Maxwell"
}

func _ready() -> void:
	apply_light_theme()
	build_shell()
	GameClient.http.request_completed.connect(_on_api_response)
	GameClient.get_state()

func apply_light_theme() -> void:
	var ui_theme := Theme.new()
	ui_theme.set_color("font_color", "Label", Color("#2d2a27"))
	ui_theme.set_color("font_color", "Button", Color("#2d2a27"))
	ui_theme.set_color("font_hover_color", "Button", Color.WHITE)
	ui_theme.set_color("font_pressed_color", "Button", Color.WHITE)
	ui_theme.set_color("font_disabled_color", "Button", Color("#8e8a84"))
	ui_theme.set_color("font_color", "LineEdit", Color("#2d2a27"))
	ui_theme.set_color("font_placeholder_color", "LineEdit", Color("#8e8a84"))
	ui_theme.set_stylebox("normal", "Button", make_style(Color("#fffdf8"), Color("#c8c0b5"), 1, 10))
	ui_theme.set_stylebox("hover", "Button", make_style(Color("#8b5e34"), Color("#8b5e34"), 1, 10))
	ui_theme.set_stylebox("pressed", "Button", make_style(Color("#6c4527"), Color("#6c4527"), 1, 10))
	ui_theme.set_stylebox("disabled", "Button", make_style(Color("#e1ded8"), Color("#d0cbc3"), 1, 10))
	ui_theme.set_stylebox("normal", "LineEdit", make_style(Color("#fffdf8"), Color("#c8c0b5"), 1, 8))
	ui_theme.set_stylebox("focus", "LineEdit", make_style(Color("#fffdf8"), Color("#8b5e34"), 2, 8))
	theme = ui_theme

func make_style(background: Color, border: Color, border_width: int, radius: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = border
	style.border_width_left = border_width
	style.border_width_top = border_width
	style.border_width_right = border_width
	style.border_width_bottom = border_width
	style.corner_radius_top_left = radius
	style.corner_radius_top_right = radius
	style.corner_radius_bottom_left = radius
	style.corner_radius_bottom_right = radius
	style.content_margin_left = 12
	style.content_margin_right = 12
	style.content_margin_top = 8
	style.content_margin_bottom = 8
	return style

func build_shell() -> void:
	var background := ColorRect.new()
	background.color = Color("#fbfaf7")
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
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
	title.text = "暗影疫病：第一夜"
	title.add_theme_font_size_override("font_size", 40)
	column.add_child(title)

	status_label = Label.new()
	status_label.add_theme_font_size_override("font_size", 18)
	column.add_child(status_label)

	description_label = Label.new()
	description_label.add_theme_font_size_override("font_size", 20)
	column.add_child(description_label)

	var backdrop := PanelContainer.new()
	backdrop.custom_minimum_size = Vector2(0, 150)
	backdrop.add_theme_stylebox_override("panel", make_style(Color("#e8e2d8"), Color("#c8c0b5"), 1, 14))
	column.add_child(backdrop)
	backdrop_text = Label.new()
	backdrop_text.name = "BackdropText"
	backdrop_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	backdrop_text.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	backdrop_text.add_theme_font_size_override("font_size", 36)
	backdrop.add_child(backdrop_text)

	scene_grid = HBoxContainer.new()
	scene_grid.add_theme_constant_override("separation", 16)
	column.add_child(scene_grid)

	var lower := HBoxContainer.new()
	lower.add_theme_constant_override("separation", 24)
	column.add_child(lower)

	var evidence_panel := PanelContainer.new()
	evidence_panel.custom_minimum_size = Vector2(360, 260)
	evidence_panel.add_theme_stylebox_override("panel", make_style(Color("#f4efe6"), Color("#d9d0c4"), 1, 12))
	lower.add_child(evidence_panel)
	var evidence_column := VBoxContainer.new()
	evidence_panel.add_child(evidence_column)
	var evidence_title := Label.new()
	evidence_title.text = "当前场景中的角色"
	evidence_title.add_theme_font_size_override("font_size", 21)
	evidence_column.add_child(evidence_title)
	npc_list = VBoxContainer.new()
	evidence_column.add_child(npc_list)

	var dialogue_panel := PanelContainer.new()
	dialogue_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dialogue_panel.add_theme_stylebox_override("panel", make_style(Color("#f4efe6"), Color("#d9d0c4"), 1, 12))
	lower.add_child(dialogue_panel)
	var dialogue_column := VBoxContainer.new()
	dialogue_panel.add_child(dialogue_column)
	var dialogue_title := Label.new()
	dialogue_title.text = "Agent 对话"
	dialogue_title.add_theme_font_size_override("font_size", 21)
	dialogue_column.add_child(dialogue_title)
	dialogue_label = Label.new()
	dialogue_label.text = "点击左侧角色开始对话。"
	dialogue_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dialogue_label.custom_minimum_size = Vector2(0, 130)
	dialogue_label.add_theme_font_size_override("font_size", 19)
	dialogue_column.add_child(dialogue_label)
	question_input = LineEdit.new()
	question_input.placeholder_text = "输入你想问的问题"
	dialogue_column.add_child(question_input)
	var ask_button := Button.new()
	ask_button.text = "发送问题（消耗 1 点行动力）"
	ask_button.pressed.connect(_ask_selected_agent)
	dialogue_column.add_child(ask_button)

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
		var is_current: bool = scene_id == state.get("current_scene", "")
		var is_reachable: bool = scene_id in scenes.get(state.get("current_scene", ""), {}).get("connections", [])
		move.text = "当前位置" if is_current else ("前往" if is_reachable else "不可直达")
		move.disabled = is_current or not is_reachable
		var target_scene_id: String = scene_id
		move.pressed.connect(Callable(self, "_on_move_pressed").bind(target_scene_id))
		move.focus_entered.connect(Callable(self, "_on_scene_focus").bind(target_scene_id))
		content.add_child(move)

	for child in npc_list.get_children():
		child.queue_free()
	var nearby_agents: Array[String] = []
	for agent_id in state.get("npc_states", {}):
		if state["npc_states"][agent_id].get("scene") == state.get("current_scene", "camp"):
			nearby_agents.append(agent_id)
	for agent_id in nearby_agents:
		var npc_button := Button.new()
		var target_agent_id: String = agent_id
		npc_button.text = agent_names.get(target_agent_id, target_agent_id)
		npc_button.focus_mode = Control.FOCUS_ALL
		npc_button.pressed.connect(Callable(self, "_on_npc_selected").bind(target_agent_id))
		npc_button.focus_entered.connect(Callable(self, "_on_npc_selected").bind(target_agent_id))
		npc_list.add_child(npc_button)

func _on_move_pressed(scene_id: String) -> void:
	status_label.text = "正在前往 %s……" % scenes.get(scene_id, {}).get("name", scene_id)
	GameClient.move_to(scene_id)

func _on_scene_focus(scene_id: String) -> void:
	status_label.text = "已选择前往 %s，点击按钮确认移动。" % scenes.get(scene_id, {}).get("name", scene_id)

func _on_npc_selected(agent_id: String) -> void:
	selected_agent_id = agent_id
	dialogue_label.text = "你正在和 %s 对话。请输入问题。" % agent_names.get(agent_id, agent_id)
	question_input.grab_focus()

func _on_api_response(_result: int, response_code: int, _headers: PackedStringArray, body: PackedByteArray) -> void:
	if response_code != 200:
		status_label.text = "后端连接失败：" + str(response_code)
		question_input.editable = true
		return
	var parsed = JSON.parse_string(body.get_string_from_utf8())
	if parsed is Dictionary and parsed.has("npc_states"):
		state = parsed
		scenes = load_scene_data()
		status_label.text = "第 %d 天 · %s · 行动力 %d/%d · 当前场景：%s" % [state.get("day", 1), "白天" if state.get("phase") == "day" else "夜晚", state.get("action_points", 0), state.get("max_action_points", 3), state.get("current_scene", "camp")]
		description_label.text = scenes.get(state.get("current_scene", "camp"), {}).get("description", "")
		render_scenes()
		backdrop_text.text = "%s  %s" % [scenes.get(state.get("current_scene", "camp"), {}).get("symbol", ""), scenes.get(state.get("current_scene", "camp"), {}).get("name", "")]
	elif parsed is Dictionary and parsed.has("dialogue"):
		dialogue_label.text = parsed["dialogue"]
		question_input.editable = true
	elif parsed is Dictionary and parsed.has("valid"):
		question_input.editable = true
		if parsed["valid"]:
			GameClient.get_state()
		else:
			status_label.text = parsed.get("impact", "这个场景目前无法到达。")

func _ask_selected_agent() -> void:
	if selected_agent_id == "" or question_input.text.strip_edges() == "":
		dialogue_label.text = "请先选择一个 NPC，并输入问题。"
		return
	dialogue_label.text = "对方正在回忆……"
	question_input.editable = false
	GameClient.ask(selected_agent_id, question_input.text.strip_edges())
	question_input.clear()

func load_scene_data() -> Dictionary:
	var file := FileAccess.open("res://scenes.json", FileAccess.READ)
	if file == null:
		return {}
	var parsed = JSON.parse_string(file.get_as_text())
	var result := {}
	for scene in parsed:
		result[scene["scene_id"]] = scene
	return result
