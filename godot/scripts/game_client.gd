extends Node

const API_BASE := "http://127.0.0.1:8000"

var http: HTTPRequest

func _ready() -> void:
	http = HTTPRequest.new()
	add_child(http)

func get_state() -> void:
	http.request(API_BASE + "/state")

func move_to(scene_id: String) -> void:
	var payload := JSON.stringify({"scene_id": scene_id})
	http.request(API_BASE + "/move", ["Content-Type: application/json"], HTTPClient.METHOD_POST, payload)

func ask(agent_id: String, text: String) -> void:
	var payload := JSON.stringify({"agent_id": agent_id, "text": text})
	http.request(API_BASE + "/ask", ["Content-Type: application/json"], HTTPClient.METHOD_POST, payload)
