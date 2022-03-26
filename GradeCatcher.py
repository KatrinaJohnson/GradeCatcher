import pygame, os, time, random, math
from pygame.locals import *
# ------------------------------------------------------------------------------------------------------------------------------
# Utility functions ------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------

# Loads a single numbered image file and returns that as an image object
def Load_Image_Utility(file_name_part, scale, file_number):
    full_file_name = file_name_part + ' ('+str(file_number) + ').png' # build the file name based on the sequencing 
    image = pygame.image.load(full_file_name) # create image from the file
    xSize = int(image.get_width() * scale) # calculate the new image width based on the scale parameter
    ySize = int(image.get_height() * scale) # calculate the new image height based on the scale parameter
    image = pygame.transform.scale(image,(int(xSize), int(ySize))) # scale the image
    return image # return a single image object if only one frame

# Loads numbered image files and returns a list of images
def Load_Images_Utility(file_name_part, scale, animation_frame_count):
    images = [] #create an empty list for our images
    for i in range(animation_frame_count): #iterate through the animation_frame_count parameter
        image = Load_Image_Utility(file_name_part, scale, i+1) #load each image from file
        images.append(image) # add the image to the images list
    return images # return the image list

# Draws a specific image from an image list at an x/y coordinate  
def Draw_Animation_Utility(img_ndx, images, xPos, yPos, plyr_frozen):
    if not plyr_frozen: #don't change the img_ndx if the player is frozen
        if img_ndx >= len(images)-1: # if img_ndx is going past the end of the images list reset back to first frame
            img_ndx = 0 # reset back to the first image (0)
        elif frame_count % 2 == 0: # increment img_ndx every other frame so animation is slowed down  
            img_ndx += 1 #increment img_ndx by +1
    GameScreen.blit(images[img_ndx], (xPos, yPos))
    return img_ndx

# Check to see if two images are touching each other
def Detect_Hit_Utility(xPos_A,yPos_A,image_A, xPos_B,yPos_B,image_B):
    # get the minumim radius for A and B#sys.exit() #call system exit function
    radius_A = min(int(image_A.get_height() / 2), int(image_A.get_width() / 2)) #calculate a circle's radius that fits inside image A  
    radius_B = min(int(image_B.get_height() / 2), int(image_B.get_height() / 2)) #calculate a circle's radius that fits inside image B
    # get the center x,y positions for object A and B
    xCenter_A = xPos_A + int(image_A.get_width() / 2) #x center Position for Object A  
    yCenter_A = yPos_A + int(image_A.get_height() / 2) #y center Position for Object A
    xCenter_B = xPos_B + int(image_B.get_width() / 2)#x center Position for Object B
    yCenter_B = yPos_B + int(image_B.get_height() / 2) #y center Position for Object A
    distance = math.dist([xCenter_A,yCenter_A],[xCenter_B,yCenter_B]) # get distance between the center of A and B
    # If the distance between point A and B is less than A radius + B radius then A and B are touching!
    if (distance < radius_A + radius_B): # If the distance between point A and B is less than A radius + B radius then A and B are touching!
        return True
    else: #otherwise A and B are not touching
        return False 

# Initialization section -------------------------------------------------------------------------------------------------------
os.environ['SDL_VIDEO_CENTERED'] = '1' #make sure the game window centered. CITATION: https://stackoverflow.com/questions/38703791/how-do-i-place-the-pygame-screen-in-the-middle
pygame.init() # initialize game engine 
frame_count = 0 # frame counterDestroy_Player starts at 0
screen_height = 360 # screen width should be set to match the background image height
screen_width = 600 # screen width should be set to match the background image width
score_value = 0 # used for tracking and displaying the score   
score_font = pygame.font.Font('Quadrit.ttf', 32)# CITATION: https://all-free-download.com/font/
GameScreen = pygame.display.set_mode(size=(screen_width, screen_height)) # create the Game Screen to draw on
Game_Frames_Per_Second = float(60) # set the game's prefered frame rate in frames/seconds
pygame.display.set_caption('Grade Chaser!') #set the game window's title name
background_XPos1 = 0 # set initial background #1's x-Position (used for scrolling)
background_XPos2 = screen_width # set initial background #2's x-Position (used for scrolling)
background_speed_default = 4 # the default pixes per second that the background screen scrolls to the left (gets converted to negative) 
background_speed = background_speed_default # speed in pixels per frame that the background scrolls in 
back_ground_image = pygame.image.load("bg.jpg") #load background image. CITATION: https://stock.adobe.com/sk/search/images?k=2d+game+background
PLAYER_STATE_RUNNING = 0 # Set player_state to this when running 
PLAYER_STATE_JUMPING = 1 # Set player_state to this when jumping 
PLAYER_STATE_DYING = 2 # Set player_state to this when dying
PLAYER_STATE_DEAD = 3 # Set player_state to this after dying
player_state = PLAYER_STATE_RUNNING # current player state (can be running, jumping, or dying)
player_jump_speed_max = -20 # initial jump take off speed
player_jump_speed = 0 # Keeps track of current player state
player_image_index = 0 # Keeps track of current animation frame that is playing
player_img_scale = 1.0/8.0 # Scale down player images by 1/8th
#load player animation into image lists
player_running_images = Load_Images_Utility('Run',player_img_scale,20) #CITATION: https://www.gameart2d.com/cute-girl-free-sprites.html
player_jumping_images = Load_Images_Utility('Jump',player_img_scale,30) #CITATION: https://www.gameart2d.com/cute-girl-free-sprites.html
player_dying_images = Load_Images_Utility('Dead',player_img_scale,9) #CITATION: https://www.gameart2d.com/cute-girl-free-sprites.html
player_yGround = 205 #Player gound level (highest y-position) 
player_yPos = player_yGround #current player y-position
player_xPos = 50 #current player x-position
player_yMin = 10 #Maximum height player can jump 
player_frozen = False #if true then the player animation will stop moving
ENEMY_COUNT = 4 # constant number of different enemies to store in the actor list
REWARD_COUNT = 1 # constant number of rewards to store in the actor list
actors = [] #this is the list of actore (enemies and rewards)
# These "ACTOR_PROPERTY_" Constants are used for actor property dictionary look-up (from the actors list)
ACTOR_PROPERTY_ALIVE = 1 #constant - Look-up key for alive actor property  
ACTOR_PROPERTY_XPOS = 2 #constant - Look-up key for x-position actor property
ACTOR_PROPERTY_YPOS = 3 #constant - Look-up key for y-position actor property
ACTOR_PROPERTY_XSPEED = 4 #constant - Look-up key for  actor property
ACTOR_PROPERTY_YSPEED = 5 #constant - Look-up key for  actor property
ACTOR_PROPERTY_STATE = 6 #constant - Look-up key for  actor property
ACTOR_PROPERTY_TYPE = 7 #constant - Look-up key for  actor property
ACTOR_PROPERTY_IMAGE = 8 #constant - Look-up key for  actor property
ACTOR_TYPE_ENEMY = 0 #constant For ACTOR_PROPERTY_TYPE: use for marking an actor as an enemy 
ACTOR_TYPE_REWARD = 1 #constant For ACTOR_PROPERTY_TYPE: use for marking an actor as a reward
color_score = (128,255,128) # LIGHT GREEN - used for score font color
#CITATION for sound files generated from https://www.bfxr.net/
reward_sound = pygame.mixer.Sound("Reward.wav") # sound effect for when player touches a reward
gameover_sound = pygame.mixer.Sound("Death.wav") # sound effect for when game is over
jump_sound = pygame.mixer.Sound("Jump.wav") #sound effect for when player jumps

# ---------------------------------------------------------------------------------------------------------------------------------
# Game Functions --------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

# for Background - Moves background 1 & 2 left a number of pixels defined by the global speed variable: background_speed        
def Scroll_BackGround(xPos1, xPos2):
    if xPos1 <= screen_width * -1: #if image 1 has gone past the far left of the screen then reset it's position back to 0
        xPos1 = 0 # setting back to 0 puts background 1 back to filling the current screen
    if xPos2 <= 0: #if image 2 is now filling the screen then it's position back to offscreen on the right
        xPos2 = screen_width ## setting back to the far right off screen by changing the x-position equal to the screen's width
    xPos1 -= background_speed #move screen image 1 to the left at the default speed
    xPos2 -= background_speed #move screen image 2 to the left at the default speed
    return (xPos1, xPos2)

# for Background - Draws background 1 & 2 at their specified x Positions, for scrolling
def Draw_Background(xPos1, xPos2):
    GameScreen.blit(back_ground_image,(xPos1,0)) # Draw background image 1
    GameScreen.blit(back_ground_image,(xPos2,0)) # Draw background image 2 at its pre-calculated offset

# for Background - this shows the score at a fixed position on the screen
def ShowScore_Background(score): 
    score_text = score_font.render(str(score), True, color_score) #create score text object with score value set
    GameScreen.blit(score_text, (10, 310)) #draw score text

# for Player - control player's movement 
def Control_Player(event,plyr_state,plyr_yPos,plyr_jump_speed):
    # if player is running check to see if jump key is pressed and change state tojumping mode if we are
    if plyr_state == PLAYER_STATE_RUNNING: # when the player is running :
        if event != None: # if there is an event to check
            if event.type == pygame.KEYDOWN: # the event was a key down event type
                if event.key == pygame.K_SPACE: # the key pressed was the space-bar
                    plyr_state = PLAYER_STATE_JUMPING #set player status to jumping, weeeeee! 
                    plyr_jump_speed = player_jump_speed_max #set the player jump speed to take off speed! 
                    jump_sound.play() #start playing the jumping sound effect now
    #if we are jumping then move the player up or down
    elif plyr_state == PLAYER_STATE_JUMPING:
        plyr_yPos += plyr_jump_speed # set new player y-position
        plyr_jump_speed += 1 #change player jump speed so we go up and then we down
        if plyr_yPos >= player_yGround: #when the player hits the ground:
            plyr_state = PLAYER_STATE_RUNNING #put player back into running mode
            plyr_yPos = player_yGround #set player y-position to ground level in case they have gone past it 
            plyr_jump_speed = player_jump_speed_max #reset jump speed so we are ready for the next jump
    #oh no! the player is dying
    elif plyr_state == PLAYER_STATE_DYING: 
        plyr_yPos += abs(plyr_jump_speed) # set new player y-position
        plyr_jump_speed += 1 # while player is dying make sure they fall if they died in the air
        if plyr_yPos >= player_yGround: #when the dead player gets to the ground
            plyr_yPos = player_yGround #make sure the player is at ground level
            plyr_jump_speed = 0 #set jump speed to 0 to stop movement
    #rats! the player is dead
    elif plyr_state == PLAYER_STATE_DEAD: 
        plyr_yPos = player_yGround # set new player y-position
        plyr_jump_speed = 0 #jump speed is set to 0 

    return (plyr_state, plyr_yPos, plyr_jump_speed)

# for Player - destroy player - the game is over when the player when hit 
def Destroy_Player(plyr_img_ndx, plyr_state, bg_speed, actor_list):
    if (plyr_state == PLAYER_STATE_JUMPING) or (plyr_state == PLAYER_STATE_RUNNING): #if the player is not dead or dying
         for actor in actor_list: #loop through every actor
             if actor[ACTOR_PROPERTY_ALIVE]: #the actor is currently alive
                if actor[ACTOR_PROPERTY_TYPE] == ACTOR_TYPE_ENEMY: #the actor is an enemy
                    plyr_image = player_running_images[0] # any player image will do because animation pics are all the same size 
                    #check to see if the player and enemy touched
                    if Detect_Hit_Utility(player_xPos, player_yPos, plyr_image, actor[ACTOR_PROPERTY_XPOS],actor[ACTOR_PROPERTY_YPOS], actor[ACTOR_PROPERTY_IMAGE]):
                        plyr_state = PLAYER_STATE_DYING #player is put into dying state if an enemy was touched
                        gameover_sound.play() #start playing the game over sound effect

    elif plyr_state == PLAYER_STATE_DYING: #or if the player was already dyiny: 
        if plyr_img_ndx >= len(player_dying_images)-1: #if the last frame of the dying animation is reached (player is done dying and ready to be dead)
            plyr_state = PLAYER_STATE_DEAD #place player in dead state
            bg_speed = 0 #stop the background from scrolling by setting the scroll speed to 0
    return (plyr_img_ndx,plyr_state,bg_speed,actor_list)

# for Player - show the player on the screen
def Draw_Player(plyr_img_ndx, plyr_state, plyr_frozen):
    if plyr_state == PLAYER_STATE_RUNNING: #if the player is running draw the current frame at the frame index for the running animation
        plyr_img_ndx = Draw_Animation_Utility(plyr_img_ndx, player_running_images, player_xPos, player_yPos,plyr_frozen)
    elif plyr_state == PLAYER_STATE_JUMPING: #if the player is jumping draw the current frame at the frame index for the jumping animation
        plyr_img_ndx = Draw_Animation_Utility(plyr_img_ndx, player_jumping_images, player_xPos, player_yPos,plyr_frozen)
    elif plyr_state == PLAYER_STATE_DYING: #if the player is dying draw the current frame at the frame index for the dying animation
        plyr_img_ndx = Draw_Animation_Utility(plyr_img_ndx, player_dying_images, player_xPos, player_yPos,plyr_frozen)
    elif plyr_state == PLAYER_STATE_DEAD: #if the player is dead only show the last frame of the dying animation
        plyr_img_ndx = len(player_dying_images)-1 #find the last frame number
        plyr_frozen = True #player is frozen: passed out to player_frozen global variable
        plyr_img_ndx = Draw_Animation_Utility(plyr_img_ndx, player_dying_images, player_xPos, player_yPos,plyr_frozen) #keep drawing the same dead frame
    return (plyr_img_ndx,plyr_state,plyr_frozen)

# for Actors (enemies & rewards) - create new actors
def Spawn_Actors(actor_list):
    if len(actor_list) == 0: #check if there are any actors in the list, if not then add some actors
        for e in range(ENEMY_COUNT): #add all the different enemies
            img_index = e+1 #add offset +1 for image index parameter
            #add a new enemy actor to the actors list
            actor_list.append({ACTOR_PROPERTY_ALIVE  : False, #by default - enemy actor is not alive
                                ACTOR_PROPERTY_XPOS   : 0, #by default - new enemy actor's x-position is set to 0
                                ACTOR_PROPERTY_YPOS   : 0, #by default - new enemy actor's y-position is set to 0
                                ACTOR_PROPERTY_XSPEED : 0, #by default - new enemy actor's x-speed is set to 0
                                ACTOR_PROPERTY_YSPEED : 0, #by default - new enemy actor's y-speed is set to 0
                                ACTOR_PROPERTY_TYPE   : ACTOR_TYPE_ENEMY, #by default - new actor's type is an enemy 
                                ACTOR_PROPERTY_IMAGE  : Load_Image_Utility('Jelly', 0.25, img_index)}) #load the appropriate enemy image
        for r in range(REWARD_COUNT):
            img_index = r+1 #add offset for image index parameter
            #add a new reward actor to the actors list
            actor_list.append({ACTOR_PROPERTY_ALIVE   : False, #by default - reward actor is not alive
                                ACTOR_PROPERTY_XPOS    : 0, #by default - new reward actor's x-position is set to 0
                                ACTOR_PROPERTY_YPOS    : 0, #by default - new reward actor's y-position is set to 0
                                ACTOR_PROPERTY_XSPEED  : 0, #by default - new reward actor's x-speed is set to 0
                                ACTOR_PROPERTY_YSPEED  : 0, #by default - new reward actor's y-speed is set to 0
                                ACTOR_PROPERTY_TYPE    : ACTOR_TYPE_REWARD, #by default - new actor's type is a reward 
                                ACTOR_PROPERTY_IMAGE   : Load_Image_Utility('Reward', 0.333, img_index)}) #load the appropriate reward image

    # Start random spawning -------------------------------------------------------------------------------------
    if random.randrange(1,50) == 1: #1 in 50 chance per frame that a actor spawns
        actor_index = random.randrange(0,len(actor_list)) #pick a random actor
        actor = actor_list[actor_index] #get the actor
        if not actor[ACTOR_PROPERTY_ALIVE]: # if the actor is dead then 
            actor[ACTOR_PROPERTY_ALIVE] = True # set to alive
            actor[ACTOR_PROPERTY_XPOS] = screen_width # start off-screen to the right
            actor[ACTOR_PROPERTY_YPOS] = random.randrange(0,player_yGround) # random height from top to player ground level
            actor[ACTOR_PROPERTY_XSPEED] = random.randrange(-5,-2) * 2 #pick a random speed from (-5 to -2) * 2 
            actor_list[actor_index] = actor #update the actor list with the newly spawned actor  

    return actor_list #return the updated actor list

# for Actors (enemies & rewards) - Move actors around the screen
def Move_Actors(actor_list):
    for actor in actor_list: #for every actor in the list
        if actor[ACTOR_PROPERTY_ALIVE]: #if the actor is alive
            actor[ACTOR_PROPERTY_XPOS] += actor[ACTOR_PROPERTY_XSPEED] #move the actor 
    return actor_list #return the actor list

# for Actors (enemies and rewards) - kill the enemy or reward when they leave the screen or destroy enemy when it touches a reward
def Destroy_Actors(actor_list):
    for actor in actor_list: #loop through each actor
        if actor[ACTOR_PROPERTY_ALIVE]: #if the actor is alive then
            if actor[ACTOR_PROPERTY_XPOS] < -actor[ACTOR_PROPERTY_IMAGE].get_width(): #if the actor went off the screen to the left
                actor[ACTOR_PROPERTY_ALIVE] = False # kill the actor
            elif actor[ACTOR_PROPERTY_TYPE] == ACTOR_TYPE_ENEMY: #otherwise if the actor is an enemy
                for reward in actor_list: #for each reward 
                    if reward[ACTOR_PROPERTY_ALIVE]: #make sure it is alive
                        if reward[ACTOR_PROPERTY_TYPE] == ACTOR_TYPE_REWARD: #and make sure its a reward
                            if Detect_Hit_Utility(actor[ACTOR_PROPERTY_XPOS],actor[ACTOR_PROPERTY_YPOS],actor[ACTOR_PROPERTY_IMAGE],reward[ACTOR_PROPERTY_XPOS],reward[ACTOR_PROPERTY_YPOS],reward[ACTOR_PROPERTY_IMAGE]): #check if enemy is ouching a reward
                                actor[ACTOR_PROPERTY_ALIVE] = False #kill the enemy if it touches a reward, otherwise enemies can hid behind rewards and kill the player
    return actor_list

# for Actors (enemies & rewards) - show the enemy on the screen 
def Draw_Actors(actor_list):
    for actor in actor_list: # for every actor in the list
        if actor[ACTOR_PROPERTY_ALIVE]: # if the actor is alive 
            GameScreen.blit(actor[ACTOR_PROPERTY_IMAGE], (actor[ACTOR_PROPERTY_XPOS], actor[ACTOR_PROPERTY_YPOS])) #draw actor

# for Reward Actors only - Reward is applied for specific Reward type (adds points to score) 
def Apply_Rewards(actor_list,score):
    if (player_state == PLAYER_STATE_RUNNING) or (player_state == PLAYER_STATE_JUMPING): #Player can only collect rewards when running or jumping
        for actor in actor_list: #for every actor in the actor list
            if actor[ACTOR_PROPERTY_TYPE] == ACTOR_TYPE_REWARD: #if the actor is a reward
                if actor[ACTOR_PROPERTY_ALIVE]: #if the reward is active (alive)
                    if Detect_Hit_Utility(player_xPos,player_yPos,player_running_images[0],actor[ACTOR_PROPERTY_XPOS],actor[ACTOR_PROPERTY_YPOS], actor[ACTOR_PROPERTY_IMAGE]): #check to see if player touched the reward
                        score += 1 #Add a point to the score!
                        actor[ACTOR_PROPERTY_ALIVE] = False # make the reward disappear
                        reward_sound.play()
    return actor_list, score

# Restart the game - used when the game is over to reset the game and play again
def Restart_Game(actor_list, score, plyr_frozen, bg_speed, plyr_state):
    actor_list = [] #clear actor list (this will automaticaly get recreated by the spawn function)
    score = 0 #reset score back to 0 (no cheating!)
    plyr_frozen = False #player is no longer frozen (allows player to move again)
    bg_speed = background_speed_default #restart background scrolling 
    plyr_state = PLAYER_STATE_RUNNING #player state is alive again!
    return (actor_list, score, plyr_frozen, bg_speed, plyr_state)

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Main Game Loop
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Playing_Game = True #used by the game while-loop to terminate the game program if it is set to True

# Citation - 3.2: Source Code for Hello World with Pygame. (2019). from https://eng.libretexts.org/Bookshelves/Computer_Science/Programming_Languages/Book%3A_Making_Games_with_Python_and_Pygame_(Sweigart)/03%3A_Pygame_Basics/3.02%3A_Source_Code_for_Hello_World_with_Pygame
while Playing_Game: # main game loop, when Playing_Game is set to False this ends the game program 

    start_time = time.time_ns() #capture frame start time
    frame_count += 1 #Increment frame counter
    
    # capture game input events
    last_event = None # declare empty variable for grabbing the last event in the event loop for player control
    for event in pygame.event.get(): # get pygame events for user input
        if event.type == pygame.KEYDOWN: # if the user pressed a key
            if event.key == pygame.K_ESCAPE: # the user pressed the escape key
                Playing_Game = False #set the playing_game variable to False so that the game-loop ends
            if player_state == PLAYER_STATE_DEAD: #revive the player if any key is pressed after player is in dead state
                actors,score_value,player_frozen,background_speed,player_state = Restart_Game(actors,score_value,player_frozen,background_speed,player_state)     
            last_event = event #save last event to use in player control function/logic 
        if event.type == pygame.QUIT: # user closed the window to end the game instead of pressing the escape key
            Playing_Game = False #set the playing_game variable to False so that the game-loop ends

    # Start main game logic ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # -- Do Background and Score Logic
    Draw_Background(background_XPos1, background_XPos2) #show the background
    background_XPos1, background_XPos2 = Scroll_BackGround(background_XPos1, background_XPos2) #scroll the background to the left
    ShowScore_Background(score_value) # Show score on top of the background
    
    # -- Do Player related functions
    player_state, player_yPos, player_jump_speed = Control_Player(last_event, player_state, player_yPos, player_jump_speed) # moves the player
    player_img_ndx,player_state,background_speed,actors = Destroy_Player(player_image_index,player_state,background_speed, actors) # handles killing player and game over
    player_image_index,player_state,player_frozen = Draw_Player(player_image_index,player_state,player_frozen) # draw and animate the player 

    # -- Do Actor related functions
    actors = Spawn_Actors(actors) #load the actors list (if it is empty) and spawn enemies and rewards
    actors = Move_Actors(actors) #moves around enemies and rewards
    actors = Destroy_Actors(actors) #destroys enemies when they go off screen, also destroy enemies when they touch a reward 
    actors,score_value = Apply_Rewards(actors,score_value) #handles reward collection when player touches reward (adds +1 to score)
    Draw_Actors(actors) #draw all actors

    # End of the main game logic ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    pygame.display.update() # this shows the updated game picture on the screen

    end_time = time.time_ns() #capture end frame end time
    elapsed_time = end_time - start_time # calculate time elapsed = Start Time - End Time (in nanoseconds) 
    
    # calculate sleep time = (1 / frame rate) - time elapsed since frame start (converted from nanoseconds to seconds)
    sleep_time = (1.0 / Game_Frames_Per_Second) - (float(elapsed_time)/float(1000000000)) #sleep_time is a fraction of 1 second (Ex. 0.5 = 1/2 second)
    
    #Limit frame rate by waiting until total elapsed time equals the frame rate duration 
    if sleep_time > 0.0: # if sleep time > 0 then go to sleep until a full 1/60th of second has elapsed 
        time.sleep(sleep_time) #wait for sleep time to even out the frame rate to 1/60th of a second

# Clean up section ----------------------------------------------------------------------------------------------------------
pygame.quit() #shut down pygame
