// Global variables.
var _game = {};
var _player = {};

function setup() {
	window.addEventListener("load", handle_load, false);
	window.addEventListener("keydown", handle_keydown, false);
	window.addEventListener("keyup", handle_keyup, false);
}

// Handle the load event (which is sent when the page has finished loading).
function handle_load(event) {
	init();
	requestAnimationFrame(update_world);
}

function handle_keydown(event) {
	_game.keymap[event.keyCode] = true;
}

function handle_keyup(event) {
	_game.keymap[event.keyCode] = false;
}

// Initialize the game state.
function init() {
	init_game();
	init_player();
}

// Initialize general game state info.
function init_game() {
	var canvas = document.getElementById("stage");
	canvas.width = 550;
	canvas.height = 400;

	_game.width = canvas.width;
	_game.height = canvas.height;

	// The keymap keeps track of which keys are currently being pressed.
	_game.keymap = {};
}

// Initialize player data.
function init_player() {
	_player.x = 0;
	_player.y = 0;
	_player.width = 20;
	_player.height = 20;

	_player.velocity_x = 0;
	_player.velocity_y = 0;
}

// Erase the canvas and draw all the objects.
function draw() {
	var canvas = document.getElementById("stage");
	var ctx = canvas.getContext("2d");

	erase(ctx);
	draw_player(ctx);
}

// Erase the canvas by filling it with white.
function erase(ctx) {
	ctx.fillStyle = "#ffffff";
	ctx.fillRect(0, 0, _game.width, _game.height);
}

// Draw the player.
function draw_player(ctx) {
	ctx.fillStyle = "blue";
	ctx.fillRect(_player.x, _player.y, _player.width, _player.height);
}

// Handle input and move the player.
function update_player() {
	check_input();

	// Move the player to the new location.
	_player.x += _player.velocity_x;
	_player.y += _player.velocity_y;
}

function check_input() {
	_player.velocity_x = 0;
	_player.velocity_y = 0;

	// Left arrow or 'a' to move left.
	if (_game.keymap[37] || _game.keymap[65]) {
		_player.velocity_x = -1;
	}
	// Right arrow or 'd' to move right.
	if (_game.keymap[39] || _game.keymap[68]) {
		_player.velocity_x = 1;
	}
	// Up arrow or 'w' to move up.
	if (_game.keymap[38] || _game.keymap[87]) {
		_player.velocity_y = -1;
	}
	// Down arrow or 's' to move up.
	if (_game.keymap[40] || _game.keymap[83]) {
		_player.velocity_y = 1;
	}
}

// This is called ~60 times per second to update the world.
function update_world() {
	update_player();
	draw();

	requestAnimationFrame(update_world);
}

setup();
