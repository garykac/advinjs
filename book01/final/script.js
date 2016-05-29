// Global variables.
var _game = {};
var _player = {};
var _levels = [];

function setup() {
	window.addEventListener("load", handle_load, false);
	window.addEventListener("keydown", handle_keydown, false);
	window.addEventListener("keyup", handle_keyup, false);
}

// Handle the load event (which is sent when the page has finished loading).
function handle_load(event) {
	init();
	start_level(0);
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
	init_level0_title();
	init_level1();
	init_level2();
	init_level3();
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

	_game.imagedir = "images/";
	_game.imagedir_player = _game.imagedir + "player/";
	_game.imagedir_backgrounds = _game.imagedir + "backgrounds/";
	_game.imagedir_monsters = _game.imagedir + "monsters/";
	_game.imagedir_items = _game.imagedir + "items/";

	// Game state.
	_game.game_over = false;
	_game.game_win = false;
	_game.current_level = 0;
	_game.next_level = 1;
	_game.in_transition = false;
	_game.reset_health = false;
	_game.player_lives = 3;

	// Global world parameters.
	_game.friction = 0.15;
	_game.gravity = 0.5;

	// Health meter.
	_game.meter_x = 10;
	_game.meter_y = 10;
	_game.meter_width = 150;
	_game.meter_height = 20;

	// Status images
	_game.img_key = new Image();
	_game.img_key.src = _game.imagedir_items + "key.png";
	_game.img_coin = new Image();
	_game.img_coin.src = _game.imagedir_items + "coin.png";
	_game.img_player = new Image();
	_game.img_player.src = _game.imagedir_player + "icon.png";
}

// Initialize player data.
function init_player() {
	// Player x,y are initialized by the level.
	_player.x = 0;
	_player.y = 0;

	// Player width, height and origin are initialized by the current sprite.
	_player.width = 0;
	_player.height = 0;
	_player.origin_x = 0;
	_player.origin_y = 0;

	_player.platform = null;
	_player.health_max = 50;
	_player.health = _player.health_max;
	_player.is_touching_monster = false;
	_player.coins = 0;
	_player.dir = 1;

	_player.velocity_x = 0;
	_player.velocity_x_delta = 0.8;
	_player.velocity_x_max = 3.5;
	_player.velocity_y = 0;
	_player.velocity_y_jump = -10;
	_player.velocity_y_max = 10;

	_player.sprite = init_player_sprite("normal", 20, 24);
	_player.sprite_sad = init_player_sprite("sad", 30, 17);
	_player.sprite_ooo = init_player_sprite("ooo", 20, 24);
	_player.sprite_happy = init_player_sprite("happy", 20, 24);
	_player.sprite_glasses = init_player_sprite("glasses", 20, 24);
	update_player_sprite();
}

function init_player_sprite(name, width, height, origin_x, origin_y) {
	var sprite = {};
	sprite.width = width;
	sprite.height = height;
	sprite.origin_x = width / 2;
	sprite.origin_y = height;
	sprite.img = new Image();
	sprite.img.src = _game.imagedir_player + name + ".png";
	return sprite;
}

function update_player_sprite() {
	var sprite;
	if (_player.health <= 0) {
		sprite = _player.sprite_sad;
	} else if (_player.x <= (_game.meter_x + _game.meter_width)
				&& _player.y <= (_game.meter_y + _game.meter_height + 20)) {
		sprite = _player.sprite_glasses;
	} else if (_game.game_win) {
		sprite = _player.sprite_happy;
	} else if (_player.is_touching_monster) {
		sprite = _player.sprite_ooo;
	} else {
		sprite = _player.sprite;
	}

	// Update the player width, height and origin based on the current sprite.
	_player.width = sprite.width;
	_player.height = sprite.height;
	_player.origin_x = sprite.origin_x;
	_player.origin_y = sprite.origin_y;

	return sprite;
}

function init_level_defaults(level) {
	level.type = "game";
	level.delay_start = 120;
	level.delay_end = 120;
	level.complete = false;
	level.player_has_key = false;

	level.player_start_x = 0;
	level.player_start_y = 0;

	level.platforms = [];
	level.monsters = [];
	level.items = [];
}

function init_level0_title() {
	var level = {};
	level.name = "";
	init_level_defaults(level);

	// Override the level defaults.
	level.type = "title";
	level.delay_start = 0;
	level.delay_end = 0;

	// Create the monsters.
	var height = 270;
	var x_min = -280;
	var x_max = 700;
	var monster_data = [
		// [x_start, y, width, height, x_min, x_max, movement, image]
		[-20, height, 20, 24, x_min, x_max, 1, "doppleganger"],
		[-140, height, 28, 26, x_min, x_max, 1, "rufus"],
		[-170, height, 26, 28, x_min, x_max, 1, "prescott"],
		[-205, height, 30, 30, x_min, x_max, 1, "henrietta"],
		[-235, height, 20, 24, x_min, x_max, 1, "vlad"],
		[-275, height-20, 40, 24, x_min, x_max, 1, [["falco1", 10], ["falco2", 10]]],
	];
	add_monsters(level, monster_data);

	_levels.push(level);
}

function init_level1() {
	var level = {};
	level.name = "Level 1";
	init_level_defaults(level);

	level.player_start_x = 20;
	level.player_start_y = 260;

	// Create the platforms.
	add_default_platforms(level);
	var platform_data = [
		// [x, y, width, height, pattern]
		[200, 290, 80, 20, "dirt"],
		[300, 240, 80, 20, "block"],
		[400, 170, 80, 20, "block"],
		[460, 110, 40, 20, "dirt"],
		[300, 70, 120, 20, "block"],
		[120, 120, 100, 20, "block"],
		[10, 190, 100, 20, "block"],
		[420, 270, 100, 20, "block"],
	];
	add_platforms(level, platform_data);

	// Create the monsters.
	var monster_data = [
		// [x, y, width, height, min_x, max_x, move_x, image]
		[350, 360, 20, 24, 60, 470, -1.0, "vlad"],
		[400, 360, 30, 30, 60, 470, 0.8, "henrietta"],
		[330, 240, 28, 26, 310, 370, -0.5, "rufus"],
		[130, 120, 26, 28, 130, 210, 1.0, "prescott"],
	];
	add_monsters(level, monster_data);

	// Create the items.
	var item_data = [
		// [x, y, width, height, type, image]
		[530, 358, 18, 20, "key", "key"],
		[50, 250, 20, 20, "coin", "coin"],
		[530, 190, 20, 20, "coin", "coin"],
		[230, 120, 20, 20, "coin", "coin"],
	];
	add_items(level, item_data);
	add_potion_item(level, 465, 270);

	level.goal = create_goal(35, 190, 2);

	_levels.push(level);
}

function init_level2() {
	var level = {};
	level.name = "Level 2";
	init_level_defaults(level);

	level.player_start_x = 20;
	level.player_start_y = 70;

	// Create the platforms.
	add_default_platforms(level);
	var platform_data = [
		// [x, y, width, height, pattern]
		[200, 20, 20, 4, "#ffffff"],
		[200, 24, 20, 96, "candycane"],
		[0, 120, 140, 20, "block"],
		[220, 110, 80, 10, "dirt"],
		[180, 120, 120, 20, "block"],
		[280, 140, 20, 20, "block"],
		[40, 190, 200, 10, "dirt"],
		[40, 230, 170, 10, "dirt"],
		[40, 240, 20, 40, "block"],
		[40, 280, 80, 20, "block"],
		[40, 300, 20, 20, "block"],
		[100, 300, 20, 20, "block"],
		[200, 300, 20, 20, "block"],
		[280, 244, 20, 112, "candycane"],
		[280, 240, 20, 4, "#804000"],
		[280, 356, 20, 4, "#804000"],
		[440, 164, 20, 112, "candycane"],
		[440, 160, 20, 4, "#804000"],
		[440, 276, 20, 4, "#804000"],
		[530, 310, 20, 20, "block-red"],
		[480, 260, 20, 20, "block-red"],
		[530, 210, 20, 20, "block-red"],
		[480, 160, 20, 20, "block-red"],
		[530, 110, 20, 20, "block-red"],
		[460, 60, 10, 10, "post"],
		[360, 80, 10, 10, "post"],
		[370, 80, 10, 10, "post"],
	];
	add_platforms(level, platform_data);

	// Create the monsters.
	var monster_data = [
		// [x, y, width, height, min_x, max_x, move_x, image]
		[380, 180, 40, 24, 330, 410, 0.5, [["falco1", 10], ["falco2", 10]]],
		[70, 190, 28, 26, 50, 230, -0.5, "rufus"],
		[400, 360, 26, 28, 320, 515, 1.0, "prescott"],
		[100, 360, 20, 24, 30, 270, -1.0, "vlad"],
	];
	add_monsters(level, monster_data);

	// The items.
	var item_data = [
		// [x, y, width, height, type, image]
		[80, 272, 18, 20, "key", "key"],
		[20, 280, 20, 20, "coin", "coin"],
		[420, 230, 20, 20, "coin", "coin"],
		[320, 140, 20, 20, "coin", "coin"],
	];
	add_items(level, item_data);
	add_potion_item(level, 55, 230);

	level.goal = create_goal(260, 110, 3);

	_levels.push(level);
}

function init_level3() {
	var level = {};
	level.name = "Level 3";
	init_level_defaults(level);

	level.player_start_x = 30;
	level.player_start_y = 80;

	// Create the platforms.
	add_default_platforms(level);
	var platform_data = [
		// [x, y, width, height, pattern]
		// Platform above player.
		[50, 35, 140, 20, "block2"],
		// Platforms around the left potion.
		[0, 120, 120, 20, "block2"],
		[0, 200, 60, 20, "block2"],
		[0, 140, 20, 60, "block2"],
		[100, 140, 20, 80, "block2"],
		// Platforms around the right potion.
		[180, 120, 120, 20, "block2"],
		[180, 200, 120, 20, "block2"],
		[180, 140, 20, 60, "block2"],
		[280, 180, 20, 20, "block2"],
		// Platform under hoard of monsters.
		[0, 260, 300, 20, "block2"],
		[480, 60, 40, 20, "block2"],
		[500, 80, 20, 160, "block2"],
		[300, 280, 200, 20, "block2"],
		[340, 220, 40, 20, "block2"],
		[340, 240, 20, 40, "block2"],
		[380, 160, 20, 40, "block2"],
		[480, 220, 20, 60, "block2"],
		[530, 280, 20, 20, "block2"],
		[0, 320, 250, 10, "dirt"],
	];
	add_platforms(level, platform_data);
	var moving_platform_data = [
		// [x, y, width, height, pattern, min_x, max_x, move_x]
		[400, 50, 30, 10, "wheel", 350, 490, -1],
		[350, 180, 20, 10, "wheel", 300, 480, 0.5],
	];
	add_moving_platforms(level, moving_platform_data);

	// Create the monsters.
	var monster_data = [
		// [x, y, width, height, min_x, max_x, move_x, image]
		[180, 260, 20, 24, 15, 280, -1.0, "vlad"],
		[120, 260, 30, 30, 15, 280, 0.8, "henrietta"],
		[20, 260, 28, 26, 15, 280, -0.5, "rufus"],
		[75, 260, 26, 28, 15, 280, 1.0, "prescott"],
		[200, 260, 28, 26, 15, 280, 0.5, "rufus"],
		[250, 260, 20, 24, 15, 280, 1.0, "vlad"],
		[80, 260, 26, 28, 15, 280, -1.0, "prescott"],
		[380, 130, 40, 24, 330, 460, 0.5, [["falco1", 10], ["falco2", 10]]],
	];
	add_monsters(level, monster_data);
	var eyes1 = [
		[110, 200],
		[540, 300],
		[120, 55],
		[130, 280],
		[10, 180],
		[350, 260],
	];
	add_eyeball_monsters(level, eyes1, 200, 100, 10);
	var eyes2 = [
		[390, 180],
		[270, 220],
		[490, 240],
		[510, 140],
		[290, 280],
		[10, 220],
		[250, 140],
		[180, 55],
	];
	add_eyeball_monsters(level, eyes2, 450, 100, 10);
	var projectile_monster_data = [
		// [x_start, y, width, height, min_x, max_x, move_x, image, projectile-info]
		[200, 360, 38, 24, 150, 450, 1.0,
			[["octoboss1", 10], ["octoboss2", 10], ["octoboss3", 10], ["octoboss2", 10]],
			[["ball-right", 2], ["ball-left", -2]]],
	];
	add_projectile_monsters(level, projectile_monster_data);

	var item_data = [
		// [x, y, width, height, type, image]
		[490, 100, 20, 20, "coin", "coin"],
		[370, 260, 20, 20, "coin", "coin"],
		[210, 160, 20, 20, "coin", "coin"],
		[20, 314, 21, 27, "finish", "gem"],
	];
	add_items(level, item_data);
	add_potion_item(level, 30, 200);
	add_potion_item(level, 230, 200);

	_levels.push(level);
}

// platform_data: [x, y, width, height, pattern]
function add_platforms(level, platform_data) {
	for (var i = 0; i < platform_data.length; i++) {
		var p = platform_data[i];
		var plat = create_platform(p[0], p[1], p[2], p[3], p[4]);
		level.platforms.push(plat);
	}
}

function add_default_platforms(level) {
	var platform_data = [
		// The bottom brick platform along the bottom of the stage.
		[0, 360, _game.width, 40, "brick"],
		// The left offstage 'wall' to keep the player on the stage.
		[-60, -_game.height, 60, 2*_game.height, "#000000"],
		// The right offstage 'wall' to keep the player on the stage.
		[_game.width, -_game.height, 60, 2*_game.height, "#000000"],
	];
	add_platforms(level, platform_data);
}

// platform_data: [x, y, width, height, pattern, min_x, max_x, move_x]
function add_moving_platforms(level, platform_data) {
	for (var i = 0; i < platform_data.length; i++) {
		var p = platform_data[i];
		var plat = create_platform(p[0], p[1], p[2], p[3], p[4]);

		plat.moving = true;
		plat.min_x = platform_data[i][5];
		plat.max_x = platform_data[i][6];
		plat.move_x = platform_data[i][7];
		level.platforms.push(plat);
	}
}

function create_platform(x, y, width, height, pattern) {
	var p = {};
	p.x = x;
	p.y = y;
	p.width = width;
	p.height = height;
	p.origin_x = 0;
	p.origin_y = 0;
	p.dir = 1;
	p.moving = false;

	// If pattern begins with '#' then it's really a background color.
	if (pattern.charAt(0) == '#') {
		p.background_color = pattern;
	} else {
		p.pattern = new Image();
		p.pattern.src = _game.imagedir_backgrounds + pattern + ".png";
	}

	return p;
}

// monster_data: [x, y, width, height, min_x, max_x, move_x, image]
function add_monsters(level, monster_data) {
	for (var i = 0; i < monster_data.length; i++) {
		var m = monster_data[i];
		var monst = create_monster(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7]);
		level.monsters.push(monst);
	}
}

// monster_data: [x, y, width, height, min_x, max_x, move_x, image, projectile-info]
function add_projectile_monsters(level, monster_data) {
	for (var im = 0; im < monster_data.length; im++) {
		var m = monster_data[im];
		var monst = create_monster(m[0], m[1], m[2], m[3], m[4], m[5], m[6], m[7]);
		var projectiles = m[8];
		for (var ip = 0; ip < projectiles.length; ip++) {
			// projectile-info: [image-name speed]
			var p = {};
			p.active = false;
			p.x = 0;
			p.y = 0;
			p.origin_x = 0;
			p.origin_y = 0;
			p.width = 5;
			p.height = 5;
			p.img = new Image();
			p.img.src = _game.imagedir_monsters + projectiles[ip][0] + ".png";
			p.speed = projectiles[ip][1];
			monst.projectiles.push(p);
		}
		level.monsters.push(monst);
	}
}

function add_eyeball_monsters(level, eyes, pause, open, close) {
	var num_eyes = eyes.length;
	var blink_duration = open + close + open;
	var eye_loop = num_eyes * (blink_duration + pause);
	for (var i = 0; i < num_eyes; i++) {
		var sprites = [];
		var start_delay = pause/2 + (i * (blink_duration + pause));
		sprites.push(["eyes0", start_delay]);
		sprites.push(["eyes1", open]);
		sprites.push(["eyes2", close]);
		sprites.push(["eyes1", open]);
		sprites.push(["eyes0", eye_loop - blink_duration - start_delay]);

		var monst = create_monster(eyes[i][0], eyes[i][1], 20, 20, 0, 550, 0, sprites);
		level.monsters.push(monst);
	}
}

function create_monster(x, y, width, height, min_x, max_x, move_x, image) {
	var m = {};
	m.x = x;
	m.y = y;
	m.width = width;
	m.height = height;
	m.origin_x = m.width / 2;
	m.origin_y = m.height;
	m.min_x = min_x;
	m.max_x = max_x;
	m.move_x = move_x;
	m.dir = (move_x > 0) ? 1 : -1;
	m.projectiles = [];

	m.sprite = [];
	// If the image is specified as an array, then it defines a set of
	// images that need to be animated.
	if (image instanceof Array) {
		for (var j = 0; j < image.length; j++) {
			var image_name = image[j][0];
			var delay = image[j][1];
			var sprite = {};
			sprite.img = new Image();
			sprite.img.src = _game.imagedir_monsters + image_name + ".png";
			sprite.delay = delay;
			m.sprite.push(sprite);
		}
	} else {
		// Single non-animated image.
		var sprite = {};
		sprite.img = new Image();
		sprite.img.src = _game.imagedir_monsters + image + ".png";
		sprite.delay = 0;
		m.sprite.push(sprite);
	}
	m.curr_image = 0;
	m.current_animation_delay = 0;

	return m;
}

// item_data: [x, y, width, height, type, image]
function add_items(level, item_data) {
	for (var i = 0; i < item_data.length; i++) {
		var d = item_data[i];
		var item = create_item(d[0], d[1], d[2], d[3], d[4], d[5]);
		level.items.push(item);
	}
}

function add_potion_item(level, x, y) {
	var val_images = [
		// [image, percentage]
		["potion-1", 0],
		["potion-2", 3],
		["potion-3", 10],
		["potion-4", 20],
		["potion-5", 30],
		["potion-6", 40],
		["potion-7", 50],
		["potion-8", 60],
		["potion-9", 70],
		["potion-10", 79],
		["potion-11", 86],
		["potion-12", 91],
		["potion-13", 94],
		["potion-14", 97],
		["potion-15", 100],
	];
	var item = create_item(x, y, 16, 23, "potion", val_images);
	item.value_max = 20;
	item.value = item.value_max;
	item.consume_rate = 0.25;
	item.replenish_rate = 0.01;
	level.items.push(item);
}

function create_item(x, y, width, height, type, image) {
	var d = {};
	d.x = x;
	d.y = y;
	d.width = width;
	d.height = height;
	d.origin_x = width / 2;
	d.origin_y = height;
	d.type = type;
	d.value_max = 0;
	d.value = 0;
	d.found = false;

	d.value_images = [];
	// If the image is specified as an array, then it defines a set of
	// images that are associated with different values for this item.
	if (image instanceof Array) {
		for (var j = 0; j < image.length; j++) {
			var image_name = image[j][0];
			var percent = image[j][1];
			var sprite = {};
			sprite.img = new Image();
			sprite.img.src = _game.imagedir_items + image_name + ".png";
			sprite.percent = percent;
			d.value_images.push(sprite);
		}
	} else {
		// Single non-animated image.
		var sprite = {};
		sprite.img = new Image();
		sprite.img.src = _game.imagedir_items + image + ".png";
		sprite.percent = 0;
		d.value_images.push(sprite);
	}
	return d;
}

function create_goal(x, y, next_level) {
	var goal = {};
	goal.x = x;
	goal.y = y;
	goal.width = 30;
	goal.height = 40;
	goal.origin_x = goal.width / 2;
	goal.origin_y = goal.height;
	goal.next_level = next_level;
	goal.img_open = new Image();
	goal.img_open.src = _game.imagedir_backgrounds + "gate-open.png";
	goal.img_closed = new Image();
	goal.img_closed.src = _game.imagedir_backgrounds + "gate-closed.png";
	return goal;
}

function start_level(level_id) {
	_game.current_level = level_id;

	var level = _levels[level_id];
	_player.x = level.player_start_x;
	_player.y = level.player_start_y;
	_player.velocity_x = 0;
	_player.velocity_y = 0;
	if (_game.reset_health) {
		_player.health = _player.health_max;
		_game.reset_health = false;
	}
	level.complete = false;

	_game.delay = level.delay_start;
	_game.in_transition = (_game.delay != 0);
	_game.transition_type = "level-start";
}

function complete_level(next_level) {
	var level = _levels[_game.current_level];

	if (level.complete)
		return;

	level.complete = true;
	_game.next_level = next_level;

	_game.delay = level.delay_end;
	_game.in_transition = (_game.delay != 0);
	_game.transition_type = "level-end";
}

function lose_life() {
	_game.player_lives--;
	if (_game.player_lives > 0) {
		_game.reset_health = true;
		_game.delay = _levels[_game.current_level].delay_end;
		_game.in_transition = (_game.delay != 0);
		_game.transition_type = "lose-life";

		// Player needs to restart the current level.
		_game.next_level = _game.current_level;
	} else {
		_game.game_over = true;
	}
}

function adjust_health(amount) {
	_player.health += amount;
	if (_player.health <= 0) {
		_player.health = 0;
		lose_life();
	}
	if (_player.health > _player.health_max) {
		_player.health = _player.health_max;
	}
}

function set_transform(ctx, obj) {
	var x = obj.x - obj.origin_x;
	var y = obj.y - obj.origin_y;

	// Adjust origin if we're facing left.
	if (obj.dir < 0)
		x += obj.width;

	// Translate origin to (x,y).
	ctx.setTransform(1, 0, 0, 1, x, y);

	// Flip the image if we're facing left.
	if (obj.dir < 0)
		ctx.scale(-1, 1);
}

function reset_transform(ctx) {
	// Reset transform to the identity matrix.
	ctx.setTransform(1, 0, 0, 1, 0, 0);
}

// Erase the canvas and draw all the objects.
function draw() {
	var canvas = document.getElementById("stage");
	var ctx = canvas.getContext("2d");

	erase(ctx);
	draw_platforms(ctx);
	draw_goal(ctx);
	draw_monsters(ctx);
	draw_items(ctx);
	draw_player(ctx);
	draw_status(ctx);

	if (_game.game_over) {
		// Dim out the stage by drawing a transparent black rectangle over it.
		ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
		ctx.fillRect(0, 0, _game.width, _game.height);

		ctx.fillStyle = "black";
		ctx.font = "48px Helvetica";
		if (_game.game_win) {
			ctx.fillText("You Win!", 155, 150);
		} else {
			ctx.fillText("Game Over", 140, 150);
		}
	}
}

// Erase the canvas by filling it with white.
function erase(ctx) {
	ctx.fillStyle = "#ffffff";
	ctx.fillRect(0, 0, _game.width, _game.height);
}

// Draw the platforms.
function draw_platforms(ctx) {
	var level = _levels[_game.current_level];
	var platforms = level.platforms;
	for (var i = 0; i < platforms.length; i++) {
		var platform = platforms[i];

		set_transform(ctx, platform);
		if (platform.background_color) {
			ctx.fillStyle = platform.background_color;
			ctx.fillRect(0, 0, platform.width, platform.height);
			ctx.strokeStyle = "rgba(0,0,0,0.5)";
			ctx.strokeRect(0, 0, platform.width, platform.height);
		} else {
			var pat = ctx.createPattern(platform.pattern, "repeat");
			ctx.fillStyle = pat;
			ctx.fillRect(0, 0, platform.width, platform.height);
		}
		reset_transform(ctx);
	}

	if (level.name != "") {
		ctx.fillStyle = "rgb(50, 50, 50)";
		ctx.font = "28px " + _game.font_family;
		ctx.fillText(level.name, 10, 390);
	}
}

function draw_monsters(ctx) {
	var level = _levels[_game.current_level];
	var monsters = level.monsters;
	for (var i = 0; i < monsters.length; i++) {
		var m = monsters[i];
		set_transform(ctx, m);
		ctx.drawImage(m.sprite[m.curr_image].img, 0, 0);
		reset_transform(ctx);

		// Draw this monster's projectiles.
		for (var ip = 0; ip < m.projectiles.length; ip++) {
			var p = m.projectiles[ip];
			if (p.active) {
				ctx.drawImage(p.img, p.x, p.y);
			}
		}
	}
}

function draw_items(ctx) {
	var level = _levels[_game.current_level];
	var items = level.items;
	for (var i = 0; i < items.length; i++) {
		var t = items[i];
		if (!t.found) {
			var index = 0;
			for (var ival = 0; ival < t.value_images.length; ival++) {
				var curr_percent = 100 * t.value / t.value_max;
				if (t.value_images[ival].percent >= curr_percent) {
					index = ival;
					break;
				}
			}
			set_transform(ctx, t);
			ctx.drawImage(t.value_images[index].img, 0, 0);
			reset_transform(ctx);
		}
	}
}

function draw_goal(ctx) {
	var level = _levels[_game.current_level];
	var goal = level.goal;
	if (goal) {
		var image = goal.img_closed;
		if (level.player_has_key) {
			image = goal.img_open;
		}
		set_transform(ctx, goal);
		ctx.drawImage(image, 0, 0);
		reset_transform(ctx);
	}
}

// Draw the player.
function draw_player(ctx) {
	var sprite = update_player_sprite();
	set_transform(ctx, _player);
	ctx.drawImage(sprite.img, 0, 0);
	reset_transform(ctx);
}

// Draw the player status information.
function draw_status(ctx) {
	var health = (_game.meter_width * _player.health) / _player.health_max;
	ctx.fillStyle = "rgba(0,255,0, 0.5)";
	ctx.fillRect(_game.meter_x, _game.meter_y, health, _game.meter_height);

	ctx.strokeStyle = "black";
	ctx.strokeRect(_game.meter_x, _game.meter_y, _game.meter_width, _game.meter_height);

	// If the player has the key, draw it in the status area.
	var level = _levels[_game.current_level];
	if (level.player_has_key) {
		ctx.drawImage(_game.img_key, _game.meter_width + 15, 11);
	}

	ctx.drawImage(_game.img_coin, _game.width - 58, 11);
	ctx.fillStyle = "#606060";
	ctx.font = "16px Helvetica";
	ctx.fillText("x" + _player.coins, _game.width - 37, 26);

	// Draw player icons to indicate how many extra lives remain.
	for (var i = 0; i < _game.player_lives-1; i++) {
		ctx.drawImage(_game.img_player, _game.width - 80 - (i * 20), 12);
	}
}

function draw_title_screen() {
	// Check for spacebar press to exit title screen.
	if (_game.keymap[32]) {
		start_level(1);
	}

	update_monsters();

	var canvas = document.getElementById("stage");
	var ctx = canvas.getContext("2d");

	erase(ctx);
	ctx.fillStyle = "black";
	ctx.font = "28px " + _game.font_family;
	ctx.fillText("The Legend of", 75, 130);

	ctx.font = "64px " + _game.font_family;
	ctx.fillText("JavaScript", 115, 180);

	ctx.font = "20px " + _game.font_family;
	ctx.fillText("PRESS THE SPACE KEY TO START", 90, 350);

	draw_monsters(ctx);
}

function draw_transition_screen() {
	var level = _levels[_game.current_level];
	var type = _game.transition_type;

	// Countdown timer.
	_game.delay--;
	if (_game.delay <= 0) {
		_game.in_transition = false;
		if (type == "level-end" || type == "lose-life") {
			start_level(_game.next_level);
		}
	}

	if (type == "level-end" || type == "lose-life") {
		// Keep moving the player so that any jumps in-progress are completed.
		update_player();
		check_collisions();
	}

	draw();

	if (type == "lose-life")
		return;

	var canvas = document.getElementById("stage");
	var ctx = canvas.getContext("2d");

	// Dim the stage by drawing a transparent black rectangle over it.
	ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
	ctx.fillRect(0, 0, _game.width, _game.height);

	ctx.fillStyle = "white";
	ctx.font = "64px Helvetica";
	ctx.fillText(level.name, 160, 180);

	ctx.fillStyle = "white";
	ctx.font = "48px Helvetica";
	if (type == "level-end") {
		ctx.fillText("Complete!", 150, 250);
	} else {
		ctx.fillText("Get Ready!", 140, 250);
	}
}

function update_platforms() {
	var platforms = _levels[_game.current_level].platforms;
	for (var i = 0; i < platforms.length; i++) {
		var p = platforms[i];
		if (p.moving) {
			p.x += p.move_x;
			if (p.x <= p.min_x || p.x >= p.max_x) {
				p.move_x *= -1;
			}
		}
	}
}

function update_monsters() {
	var level = _levels[_game.current_level];
	var monsters = level.monsters;
	for (var i = 0; i < monsters.length; i++) {
		var m = monsters[i];
		m.x += m.move_x;
		if (m.x <= m.min_x || m.x >= m.max_x) {
			m.move_x *= -1;
			m.dir *= -1;
		}

		// Animate the monster.
		m.current_animation_delay++;
		if (m.current_animation_delay >= m.sprite[m.curr_image].delay) {
			m.current_animation_delay = 0;
			m.curr_image++;
			if (m.curr_image >= m.sprite.length)
				m.curr_image = 0;
		}

		// Move any monster projectiles.
		for (var ip = 0; ip < m.projectiles.length; ip++) {
			var p = m.projectiles[ip];
			if (!p.active) {
				p.x = m.x + 4 * p.speed;
				p.y = m.y - m.height/2;
				p.active = true;
			}
			p.x += p.speed;
			if ((p.x + p.width) < 0 || p.x > _game.width)
				p.active = false;
		}
	}
}

function update_items() {
	var items = _levels[_game.current_level].items;
	for (var i = 0; i < items.length; i++) {
		var item = items[i];
		if (item.type == "potion") {
			item.value += item.replenish_rate;
			if (item.value > item.value_max) {
				item.value = item.value_max;
			}
		}
	}
}

// Handle input and move the player.
function update_player() {
	if (!_game.game_over && !_game.in_transition) {
		check_input();
	}

	// Apply the global world effects on the player.
	_player.velocity_x *= (1.0 - _game.friction);
	_player.velocity_y += _game.gravity;
	if (_player.velocity_y > _player.velocity_y_max)
		_player.velocity_y = _player.velocity_y_max;

	// Move the player to the new location.
	_player.x += _player.velocity_x;
	_player.y += _player.velocity_y;

	// If the player is on a moving platform, then the player should move along
	// with the platform.
	if (_player.platform && _player.platform.moving) {
		_player.x += _player.platform.move_x;
	}
}

function check_input() {
	// Left arrow or 'a' to move left.
	if (_game.keymap[37] || _game.keymap[65]) {
		_player.dir = -1;
		_player.velocity_x -= _player.velocity_x_delta;
		if (_player.velocity_x < -_player.velocity_x_max) {
			_player.velocity_x = -_player.velocity_x_max;
		}
	}
	// Right arrow or 'd' to move right.
	if (_game.keymap[39] || _game.keymap[68]) {
		_player.dir = 1;
		_player.velocity_x += _player.velocity_x_delta;
		if (_player.velocity_x > _player.velocity_x_max) {
			_player.velocity_x = _player.velocity_x_max;
		}
	}
	// Up arrow, 'w'  and spacebar to jump.
	if (_game.keymap[38] || _game.keymap[87] || _game.keymap[32]) {
		// Only allow jumps if the player is on a platform.
		if (_player.platform) {
			_player.platform = null;
			_player.velocity_y = _player.velocity_y_jump;
		}
	}
}

function check_collisions() {
	check_platform_collisions();
	if (!_game.game_over && !_game.in_transition) {
		check_monster_collisions();
	}
	check_item_collisions();
	check_goal_collisions();
}

function check_platform_collisions() {
	var level = _levels[_game.current_level];
	var platforms = level.platforms;
	_player.platform = null;
	for (var i = 0; i < platforms.length; i++) {
		var overlap = collide(platforms[i], _player);
		if (overlap) {
			// Adjust player location so it no longer overlaps with platform.
			_player.x += overlap[0];
			_player.y += overlap[1];

			var dir = overlap[2];
			if (dir == "left" || dir == "right") {
				// Smack into left/right side of platform.
				_player.velocity_x = 0;
			} else if (dir == "top") {
				// Land on top of platform.
				_player.platform = platforms[i];
				_player.velocity_y = 0;
			} else {
				// Bounce off bottom of platform.
				_player.velocity_y *= -1;
			}
		}
	}
}

function check_monster_collisions() {
	var level = _levels[_game.current_level];
	var monsters = level.monsters;
	var damage = 0;
	_player.is_touching_monster = false;
	for (var i = 0; i < monsters.length; i++) {
		var m = monsters[i];
		if (collide(m, _player)) {
			damage++;
			_player.is_touching_monster = true;
		}

		// Collision with monster projectiles.
		for (var ip = 0; ip < m.projectiles.length; ip++) {
			var p = m.projectiles[ip];
			if (p.active && collide(p, _player)) {
				damage += 5;
				p.active = false;
			}
		}
	}
	if (damage != 0) {
		adjust_health(-damage);
	}
}

function check_item_collisions() {
	var level = _levels[_game.current_level];
	var items = level.items;
	for (var i = 0; i < items.length; i++) {
		var item = items[i];
		if (!item.found) {
			if (collide(item, _player)) {
				if (item.type == "key") {
					level.player_has_key = true;
					item.found = true;
				} else if (item.type == "potion") {
					if (item.value >= item.consume_rate) {
						adjust_health(item.consume_rate);
						item.value -= item.consume_rate;
					}
				} else if (item.type == "coin") {
					_player.coins++;
					item.found = true;
				} else if (item.type == "finish") {
					item.found = true;
					_game.game_over = true;
					_game.game_win = true;
				}
			}
		}
	}
}

function check_goal_collisions() {
	var level = _levels[_game.current_level];
	var goal = level.goal;
	if (goal) {
		if (collide(goal, _player) && level.player_has_key) {
			complete_level(goal.next_level);
		}
	}
}

// If the 2 objects overlap, return a [dx, dy, dir] array containing the x,y
// overlap and the direction of the collision (relative to obj1).
// Return null if they don't overlap.
function collide(obj1, obj2) {
	var o1_center_x = obj1.x - obj1.origin_x + (obj1.width / 2);
	var o1_center_y = obj1.y - obj1.origin_y + (obj1.height / 2);

	var o2_center_x = obj2.x - obj2.origin_x + (obj2.width / 2);
	var o2_center_y = obj2.y - obj2.origin_y + (obj2.height / 2);

	var dx = o1_center_x - o2_center_x;
	var dy = o1_center_y - o2_center_y;

	var half_width = (obj1.width + obj2.width) / 2;
	var half_height = (obj1.height + obj2.height) / 2;

	// No overlap.
	if (half_width <= Math.abs(dx) || half_height <= Math.abs(dy))
		return null;

	var overlap_x = half_width - Math.abs(dx);
	var overlap_y = half_height - Math.abs(dy);

	if (overlap_x >= overlap_y) {
		if (dy > 0)
			return [0, -overlap_y, "top"];
		else
			return [0, overlap_y, "bottom"];
	} else {
		if (dx > 0)
			return [-overlap_x, 0, "left"];
		else
			return [overlap_x, 0, "right"];
	}
}

// This is called ~60 times per second to update the world.
function update_world() {
	var level = _levels[_game.current_level];

	if (_game.in_transition) {
		draw_transition_screen();
	} else if (level.type == "game") {
		update_monsters();
		update_platforms();
		update_items();
		update_player();
		check_collisions();
		draw();
	} else if (level.type == "title") {
		draw_title_screen();
	}

	requestAnimationFrame(update_world);
}

setup();
