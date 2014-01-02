<?php 
// used by webapp for human parsing?
// make sure i'm not duplicating fluent values!!!

$allFluents = Array(

	"water" => Array(
		Array( //FLUENT  //TRIGGER
			"display_name" => "Agent Thirst",
			"name" => "thirst",
			"values" => Array("agent became thirsty"=>"not_thirsty", "agent became not thirsty"=>"thirsty_not", "agent stayed thirsty"=>"thirsty", "agent stayed not thirsty"=>"not")
		),
		Array( //FLUENT
			"display_name" => "Cup Now Contains", 
			"name" => "cup",
			"values" => Array("more water"=>"more", "less water"=>"less", "same"=>"same")
		),
		Array( //ACTION
			"display_name" => "Agent Drink Action",
			"name" => "water_action",
			"values" => Array("agent drank"=>"act_drink", "agent did not drink"=>"act_no_drink")
		),
	),

	"waterstream" => Array(
		Array( //FLUENT
			"display_name" => "Water Stream",
			"name" => "waterstream",
			"values" => Array("water was on"=>"water_on", "water remained off"=>"water_off"),
		),
		Array( //TRIGGER
			"display_name" => "Agent Thirst",
			"name" => "thirst",
			"values" => Array("agent became thirsty"=>"not_thirsty", "agent became not thirsty"=>"thirsty_not", "agent stayed thirsty"=>"thirsty", "agent stayed not thirsty"=>"not")
		),
		Array( //FLUENT
			"display_name" => "Cup Now Contains", 
			"name" => "cup",
			"values" => Array("more water"=>"more", "less water"=>"less", "same"=>"same")
		),
		Array( //ACTION
			"display_name" => "Agent Dispense Action",
			"name" => "dispense",
			"values" => Array("agent dispensed water to cup"=>"act_dispensed", "agent did not"=>"act_no_dispense"),
		),
	), 

	"door" => Array(
		Array( //FLUENT
			"display_name" => "Door",
			"name" => "door",
			"values" => Array("became open"=>"closed_open", "became closed"=>"open_closed", "stayed open"=>"open", "stayed closed"=>"closed"),
		),
		Array( //ACTION
			"display_name" => "Agent Door Action",
			"name" => "door_action",
			"values" => Array("an agent opened the door"=>"act_opened", "an agent closed the door"=>"act_closed", "no agent did either"=>"act_not_opened_closed")
		),
	),

	"doorlock" => Array(
		Array( //FLUENT //TRIGGER
			"display_name" => "Door Lock <br /> (compare <br />  beginning <br /> of segment <br /> to end, <br /> ignore <br /> middle)",
			"name" => "doorlock",
			"values" => Array("became unlocked"=>"lock_unlocked", "became locked"=>"unlocked_lock", "stayed locked"=>"locked", "stayed unlocked"=>"unlocked"),
		),
		Array( //ACTION
			"display_name" => "Agent Lock Action",
			"name" => "doorlock_action",
			"values" => Array("an agent knocked"=>"act_knock", "no agent knocked"=>"act_none")
		),
	),

	"phone" => Array(
		Array( //FLUENT
			"display_name" => "Phone Status", 
			"name" => "phone",
			"values" => Array("became active (started call)"=>"off_active", "became inactive (ended call)"=>"active_off", "stayed active/in call"=>"active", "stayed inactive/off call"=>"off") 
		),
		Array( //TRIGGER
			"display_name" => "Phone Ringing", 
			"name" => "ringer",
			"values" => Array("phone rang"=>"ring", "phone did not ring"=>"no_ring")
		),
		Array( //ACTION
			"display_name" => "Agent Phone Action",
			"name" => "phone_action",
			"values" => Array("agent used phone"=>"act_received_call", "agent did not use phone"=>"act_no_call",) 
		),
	),

	"trash" => Array(
		Array( //FLUENT
			"display_name" => "Trashcan Now Contains", // what means "last time"?
			"name" => "trash",
			"values" => Array("more trash"=>"more", "less trash"=>"less", "no change"=>"same")
		),
		Array( //ACTION
			"display_name" => "Agent Trash Action", 
			"name" => "trash_action", 
			"values" => Array("agent threw trash out"=>"act_benddown", "agent did not"=>"act_no_benddown")
		),
	),

	"screen" => Array(
		Array( //FLUENT
			"display_name" => "Monitor Display",
			"name" => "screen",
			"values" => Array("turned on"=>"off_on", "turned off/dimmed"=>"on_off", "stayed on"=>"on", "stayed off/dim"=>"off"),
		),
		Array( //ACTION
			"display_name" => "Agent Computer Action",
			"name" => "screen_action",
			"values" => Array("agent used mouse/trackpad or keyboard"=>"act_mousekeyboard", "agent did not"=>"act_no_mousekeyboard")
		),
	),

	"elevator" => Array(
		Array( //FLUENT
			"display_name" => "Elevator",
			"name" => "elevator",
			"values" => Array("became open"=>"closed_open", "became closed"=>"open_closed", "stayed open"=>"open", "stayed closed"=>"closed"),
		),
		Array( //ACTION
			"display_name" => "Agent Elevator Action",
			"name" => "elevator_action", 
			"values" => Array("agent pushed button to call elevator"=>"act_pushbutton", "agent did not"=>"act_no_pushbutton")
		),
	),

	"light" => Array(
		Array( //FLUENT
			"display_name" => "Light in Room",
			"name" => "light",
			"values" => Array("turned on"=>"off_on", "turned off"=>"on_off", "stayed on"=>"on", "stayed off"=>"off"),
		),
		Array( //ACTION
			"display_name" => "Agent Light Action",
			"name" => "light_action", 
			"values" => Array("agent flipped light switch"=>"act_pushbutton", "agent did not"=>"act_no_pushbutton")
		),
	),

);
