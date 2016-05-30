// Global variables.
var _game = {};
var _player1 = {};
var _player2 = {};
var _ball = {};

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
	init_player1();
	init_player2();
	init_ball();

	// Start game by showing the score.
	update_scores(0, 0);
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

	// How fast the player paddles move.
	_game.paddle_speed = 3;

	// How fast the ball moves (in x and y direction).
	_game.default_ball_speed = 2;
	_game.current_ball_speed = 0;

	// Current game state: 'score', 'playing', 'gameover'
	_game.state = 'playing';

	// Timer for tracking how long to display the score.
	_game.score_timer = 0;
	// How long to display score (in 60ths of a second).
	_game.score_timer_reset = 120;
}

// Initialize Player 1 data.
function init_player1() {
	_player1.width = 20;
	_player1.height = 80;
	_player1.x = 30;
	_player1.y = (_game.height - _player1.height) / 2.0;

	_player1.velocity_y = 0;
	_player1.score = 0;
}

// Initialize Player 2 data.
function init_player2() {
	_player2.width = 20;
	_player2.height = 80;
	_player2.x = 500;
	_player2.y = (_game.height - _player2.height) / 2.0;

	_player2.velocity_y = 0;
	_player2.score = 0;
}

// Initialize ball data.
function init_ball() {
	_ball.width = 20;
	_ball.height = 20;
	_ball.x = (_game.width - _ball.width) / 2.0;
	_ball.y = 0;

	_game.current_ball_speed = _game.default_ball_speed;
	_ball.velocity_x = _game.current_ball_speed;
	_ball.velocity_y = _game.current_ball_speed;
}

function update_scores(player1, player2) {
	// Update the scores.
	_player1.score += player1;
	_player2.score += player2;

	// Reset the ball.
	init_ball();

	// Which direction should the next ball be served?
	// It should come from the player who just scored the point.
	if (player2 > 0) {
		_ball.velocity_x *= -1;
	}

	// Has either player won?
	if (_player1.score >= 9 || _player2.score >= 9) {
		_game.state = 'gameover';
	} else {
		_game.state = 'score';
		_game.score_timer = _game.score_timer_reset;
	}
}

// Erase the canvas and draw all the objects.
function draw() {
	var canvas = document.getElementById("stage");
	var ctx = canvas.getContext("2d");

	erase(ctx);
	if (_game.state == 'playing') {
		draw_player1(ctx);
		draw_player2(ctx);
		draw_ball(ctx);
	} else if (_game.state == 'score') {
		draw_player1(ctx);
		draw_player2(ctx);
		draw_score(ctx);
		_game.score_timer--;
		if (_game.score_timer <= 0) {
			_game.state = 'playing';
		}
	} else {
		draw_score(ctx);
	}
}

// Erase the canvas by filling it with black.
function erase(ctx) {
	ctx.fillStyle = "#000000";
	ctx.fillRect(0, 0, _game.width, _game.height);
}

// Draw player 1.
function draw_player1(ctx) {
	ctx.fillStyle = "white";
	ctx.fillRect(_player1.x, _player1.y, _player1.width, _player1.height);
}

// Draw player 2.
function draw_player2(ctx) {
	ctx.fillStyle = "white";
	ctx.fillRect(_player2.x, _player2.y, _player2.width, _player2.height);
}

// Draw the ball.
function draw_ball(ctx) {
	ctx.fillStyle = "white";
	ctx.fillRect(_ball.x, _ball.y, _ball.width, _ball.height);
}

function draw_score(ctx) {
	var x_center = _game.width / 2;
	var y = 30;
	var number_width = 80;
	var padding = 40;

	draw_number(ctx, _player1.score, x_center - (number_width + padding), y);
	draw_number(ctx, _player2.score, x_center + padding, y);
}

// For a 7-segment number, which segments should be drawn to show each number:
// Each segment is numbered as follows:
//    -0-    0000     1  2222  3333  4  4  5555  6666  7777  8888  9999
//   5   1   0  0     1     2     3  4  4  5     6        7  8  8  9  9
//    -6-    0  0     1  2222  3333  4444  5555  6666     7  8888  9999
//   4   2   0  0     1  2        3     4     5  6  6     7  8  8     9
//    -3-    0000     1  2222  3333     4  5555  6666     7  8888  9999
// For example:
//   To show a '1', only the 1 and 2 segments are drawn.
//   To show a '2', the 0, 1, 6, 4 and 3 segments are drawn.
var _number_segments = [
	[true,	true,	true,	true,	true,	true,	false],	// 0
	[false,	true,	true,	false,	false,	false,	false],	// 1
	[true,	true,	false,	true,	true,	false,	true],	// 2
	[true,	true,	true,	true,	false,	false,	true],	// 3
	[false,	true,	true,	false,	false,	true,	true],	// 4
	[true,	false,	true,	true,	false,	true,	true],	// 5
	[true,	false,	true,	true,	true,	true,	true],	// 6
	[true,	true,	true,	false,	false,	false,	false],	// 7
	[true,	true,	true,	true,	true,	true,	true],	// 8
	[true,	true,	true,	true,	false,	true,	true],	// 9
];

function draw_number(ctx, number, x, y) {
	// Make sure number is between 0 and 9.
	if (number < 0) {
		number = 0;
	} else if (number > 9) {
		number = 9;
	}

	ctx.fillStyle = "white";
	if (_number_segments[number][0]) {
		ctx.fillRect(x, y, 80, 20);
	}
	if (_number_segments[number][1]) {
		ctx.fillRect(x+60, y, 20, 80);
	}
	if (_number_segments[number][2]) {
		ctx.fillRect(x+60, y+60, 20, 80);
	}
	if (_number_segments[number][3]) {
		ctx.fillRect(x, y+120, 80, 20);
	}
	if (_number_segments[number][4]) {
		ctx.fillRect(x, y+60, 20, 80);
	}
	if (_number_segments[number][5]) {
		ctx.fillRect(x, y, 20, 80);
	}
	if (_number_segments[number][6]) {
		ctx.fillRect(x, y+60, 80, 20);
	}
}

// Handle movement for Player 1.
function update_player1() {
	_player1.y += _player1.velocity_y;

	// Make sure paddle doesn't go off-screen.
	if (_player1.y < 0) {
		_player1.y = 0;
	} else if (_player1.y > _game.height - _player1.height) {
		_player1.y = _game.height - _player1.height;
	}
}

// Handle movement for Player 2.
function update_player2() {
	_player2.y += _player2.velocity_y;

	// Make sure paddle doesn't go off-screen.
	if (_player2.y < 0) {
		_player2.y = 0;
	} else if (_player2.y > _game.height - _player2.height) {
		_player2.y = _game.height - _player2.height;
	}
}

// Handle ball movement and collision.
function update_ball() {
	_ball.x += _ball.velocity_x;
	_ball.y += _ball.velocity_y;

	// Bounce off horizontal walls.
	if (_ball.y <= 0) {
		_ball.velocity_y *= -1;
	}
	if (_ball.y >= _game.height - _ball.height) {
		_ball.velocity_y *= -1;
	}

	// Bounce off vertical walls.
	if (_ball.x <= 0) {
		update_scores(0, 1);
	}
	if (_ball.x >= _game.width - _ball.width) {
		update_scores(1, 0);
	}

	// Bounce off paddles.
	var ball_speed2 = (_game.current_ball_speed / 2.0)
	if (_ball.velocity_x < 0
			&& _ball.x + ball_speed2 > _player1.x + _player1.width
			&& _ball.x - ball_speed2 <= _player1.x + _player1.width
			&& _ball.y + _ball.height >= _player1.y
			&& _ball.y <= _player1.y + _player1.height) {
		_game.current_ball_speed *= 1.05;
		_ball.velocity_x = _game.current_ball_speed;
	}
	if (_ball.velocity_x > 0
			&& _ball.x + _ball.width + ball_speed2 > _player2.x
			&& _ball.x + _ball.width - ball_speed2 <= _player2.x
			&& _ball.y + _ball.height >= _player2.y
			&& _ball.y <= _player2.y + _player2.height) {
		_game.current_ball_speed *= 1.05;
		_ball.velocity_x = -_game.current_ball_speed;
	}
}

function check_input() {
	_player1.velocity_y = 0;

	// Player 1 uses the WASD keys to move.
	// 'w' or 'a' to move up.
	if (_game.keymap[87] || _game.keymap[65]) {
		_player1.velocity_y = -_game.paddle_speed;
	}
	// 's' or 'd' to move up.
	if (_game.keymap[83] || _game.keymap[68]) {
		_player1.velocity_y = _game.paddle_speed;
	}

	_player2.velocity_y = 0;

	// Player 2 uses the Arrow keys to move.
	// Up arrow or Right arrow to move up.
	if (_game.keymap[38] || _game.keymap[39]) {
		_player2.velocity_y = -_game.paddle_speed;
	}
	// Down arrow or Left arrow to move up.
	if (_game.keymap[40] || _game.keymap[37]) {
		_player2.velocity_y = _game.paddle_speed;
	}
}

// This is called ~60 times per second to update the world.
function update_world() {
	if (_game.state == 'playing') {
		check_input();
		update_player1();
		update_player2();
		update_ball();
	}
	draw();

	requestAnimationFrame(update_world);
}

setup();
