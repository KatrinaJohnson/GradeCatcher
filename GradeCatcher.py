import pygame, sys, os, time, random, math
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
    for i in range(animation_frame_count): #iterate 0 through the animation_frame_count parameter
        full_file_name = file_name_part + ' ('+str(i+1) + ').png' # build the file name based on the sequencing 
        image = pygame.image.load(full_file_name) # create image from the file
        xSize = int(image.get_width() * scale) # calculate the new image width based on the scale parameter
        ySize = int(image.get_height() * scale) # calculate the new image height based on the scale parameter
        image = pygame.transform.scale(image,(int(xSize), int(ySize))) # scale the image
        if animation_frame_count == 1:
            return image # return a single image object if only one frame
        images.append(image) # add the image to the images list
    return images # return the image list

def Draw_Animation_Utility(img_ndx, images, xPos, yPos, plyr_frozen):
    img = None # declare our empty image object
    if not plyr_frozen:
        if img_ndx >= len(images)-1: # if img_ndx is going past the end of the images list reset back to first frame
            img_ndx = 0 # reset back to the first image (0)
        elif frame_count % 2 == 0: # increment img_ndx every other frame so animation is slowed down  
            img_ndx += 1 #increment img_ndx by +1
    img = images[img_ndx] # get 
    if img != None:
        GameScreen.blit(img, (xPos, yPos))
    return (img_ndx, plyr_frozen)

# Check to see if two images are touching each other
def Detect_Hit_Utility(xPos_A,yPos_A,image_A, xPos_B,yPos_B,image_B):
    # get the average radius for A and B
    radius_A = int((image_A.get_width() + image_A.get_height()) / 4)
    radius_B = int((image_B.get_width() + image_B.get_height()) / 4)
    # get the center position for A and B
    xCenter_A = xPos_A + int(image_A.get_width() / 2)
    yCenter_A = yPos_A + int(image_A.get_height() / 2)
    xCenter_B = xPos_B + int(image_B.get_width() / 2)
    yCenter_B = yPos_B + int(image_B.get_height() / 2)    
    # get the distance between the center of A and B
    distance = math.dist([xCenter_A,yCenter_A],[xCenter_B,yCenter_B])
    # If the distance between point A and B is less than A radius and B radius then A and B are touching!
    if (distance < radius_A + radius_B):
        return True
    else: #otherwise A and B are not touching
        return False 

# Initialization section -------------------------------------------------------------------------------------------------------
os.environ['SDL_VIDEO_CENTERED'] = '1' #make sure the game window centered
pygame.init() # initialize game engine 
frame_count = 0 # frame counterDestroy_Player starts at 0
screen_height = 360 # screen width should be set to match the background image height
screen_width = 600 # screen width should be set to match the background image width
score_value = 0 # used for tracking and displaying the score   
score_font = pygame.font.Font('Quadrit.ttf', 32)# Citation: https://all-free-download.com/font/
GameScreen = pygame.display.set_mode(size=(screen_width, screen_height)) # create the Game Screen to draw on
clock = pygame.time.Clock() # create clock for limiting frame rate 
Game_Frames_Per_Second = float(60) # set the game's prefered frame rate in frames/seconds
pygame.display.set_caption('Grade Chaser!') #set the game window's title name
background_XPos1 = 0 # set initial background #1's x-Position (used for scrolling)
background_XPos2 = screen_width # set initial background #2's x-Position (used for scrolling)
background_speed_default = 4
background_speed = 4 # speed in pixels per frame that the background scrolls in 
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
ENEMY_COUNT = 6
REWARD_COUNT = 1
actors = []
ACTOR_PROPERTY_ALIVE = 1 
ACTOR_PROPERTY_XPOS = 2 
ACTOR_PROPERTY_YPOS = 3
ACTOR_PROPERTY_XSPEED = 4 
ACTOR_PROPERTY_YSPEED = 5
ACTOR_PROPERTY_STATE = 6
ACTOR_PROPERTY_TYPE = 7
ACTOR_PROPERTY_IMAGE = 8
ACTOR_TYPE_ENEMY = 0 #For ACTOR_PROPERTY_TYPE: use for marking an actor as an enemy 
ACTOR_TYPE_REWARD = 1

color_score = (128,255,128)

# ---------------------------------------------------------------------------------------------------------------------------------
# Game Functions --------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------

# for Background - Draws background 1 & 2 at there specified x Positions, for scrolling
def Draw_Background(xPos1, xPos2):
    GameScreen.blit(back_ground_image,(xPos1,0))
    GameScreen.blit(back_ground_image,(xPos2,0))

# for Background - Moves background 1 & 2 left a number of pixels defined by the global speed variable: background_speed        
def Scroll_BackGround(xPos1, xPos2):
    if xPos1 <= screen_width * -1:
        xPos1 = 0
    if xPos2 <= 0:
        xPos2 = screen_width
    xPos1 -= background_speed
    xPos2 -= background_speed
    return (xPos1, xPos2)

# for Background - this shows the score at a fixed position on the screen
def ShowScore_Background(score): 
    score_text = score_font.render(str(score), True, color_score) #create score text object with score value set
    GameScreen.blit(score_text, (10, 310)) #draw score text

# for Player - control player's movement 
def Control_Player(event,plyr_state,plyr_yPos,plyr_jump_speed):
    # if player is either running or jumping
    # get user input for jump key (space bar) and set player state to jumping mode if we are
    if plyr_state == PLAYER_STATE_RUNNING: 
        if event != None: # there is an event to check
            if event.type == pygame.KEYDOWN: # the event was a key down
                if event.key == pygame.K_SPACE: # the key pressed was the space-bar
                    plyr_state = PLAYER_STATE_JUMPING #set to jumping 
                    plyr_jump_speed = player_jump_speed_max
    #if we are jumping then move the player up or down
    if plyr_state == PLAYER_STATE_JUMPING:
        plyr_yPos += plyr_jump_speed # set new player y-position
        plyr_jump_speed += 1 #change player jump speed so we go up and then down
        if plyr_yPos >= player_yGround:
            plyr_state = PLAYER_STATE_RUNNING
            plyr_yPos = player_yGround
            plyr_jump_speed = player_jump_speed_max
    #oh no! the player is dying
    elif plyr_state == PLAYER_STATE_DYING: 
        plyr_yPos += abs(plyr_jump_speed) # set new player y-position
        plyr_jump_speed += 1 #change player jump speed so we go up and then down
        if plyr_yPos >= player_yGround:
            plyr_yPos = player_yGround
            plyr_jump_speed = 0
    #rats! the player is dead
    else: 
        plyr_yPos = player_yGround # set new player y-position
        plyr_jump_speed = 0
        plyr_state == PLAYER_STATE_DEAD

    return (plyr_state, plyr_yPos, plyr_jump_speed)

# for Player - kill the player when hit 
def Destroy_Player(plyr_img_ndx, plyr_state, bg_speed, actor_list):
    if (plyr_state == PLAYER_STATE_JUMPING) or (plyr_state == PLAYER_STATE_RUNNING):
         for actor in actor_list:
             if actor[ACTOR_PROPERTY_ALIVE]:
                if actor[ACTOR_PROPERTY_TYPE] == ACTOR_TYPE_ENEMY:
                    plyr_image = player_running_images[0] # any player image will do because animation pics are all the same size 
                    if Detect_Hit_Utility(player_xPos, player_yPos, plyr_image, actor[ACTOR_PROPERTY_XPOS],actor[ACTOR_PROPERTY_YPOS], actor[ACTOR_PROPERTY_IMAGE]):
                        plyr_state = PLAYER_STATE_DYING
                        plyr_img_ndx = 0
    if plyr_state == PLAYER_STATE_DYING:
        if plyr_img_ndx >= len(player_dying_images)-1:
            plyr_state = PLAYER_STATE_DEAD
            bg_speed = 0
    return (plyr_img_ndx,plyr_state,bg_speed,actor_list)

# for Player - show the player on the screen
def Draw_Player(plyr_img_ndx, plyr_state, plyr_frozen):
    if plyr_state == PLAYER_STATE_RUNNING:
        plyr_img_ndx, plyr_frozen = Draw_Animation_Utility(plyr_img_ndx, player_running_images, player_xPos, player_yPos,plyr_frozen)
    elif plyr_state == PLAYER_STATE_JUMPING:
        plyr_img_ndx, plyr_frozen = Draw_Animation_Utility(plyr_img_ndx, player_jumping_images, player_xPos, player_yPos,plyr_frozen)
    elif plyr_state == PLAYER_STATE_DYING:
        plyr_img_ndx, plyr_frozen = Draw_Animation_Utility(plyr_img_ndx, player_dying_images, player_xPos, player_yPos,plyr_frozen)
    if plyr_state == PLAYER_STATE_DEAD:
        plyr_img_ndx = len(player_dying_images)-1
        plyr_frozen = True
        plyr_img_ndx, plyr_frozen = Draw_Animation_Utility(plyr_img_ndx, player_dying_images, player_xPos, player_yPos,plyr_frozen)
    return (plyr_img_ndx,plyr_state,plyr_frozen)

def Revive_Player(plyr_state, plyr_frozen, bg_speed, actor_list):
    actor_list = [] #clear actor list
    bg_speed = background_speed_default
    plyr_frozen = False
    return plyr_state, plyr_frozen, bg_speed, actor_list
    

# for Actors (enemies & rewards) - create new actors
def Spawn_Actors(actor_list):
    # populate actor list if there are no actors
    if actor_list != None:
        if len(actor_list) == 0:
            img_index = 0
            for e in range(ENEMY_COUNT):
                img_index = e+1 #add offset for image index parameter
                actor_list.append({ACTOR_PROPERTY_ALIVE:False,ACTOR_PROPERTY_XPOS:0,ACTOR_PROPERTY_YPOS:0,ACTOR_PROPERTY_XSPEED:0,ACTOR_PROPERTY_YSPEED:0,ACTOR_PROPERTY_TYPE:ACTOR_TYPE_ENEMY,ACTOR_PROPERTY_IMAGE:Load_Image_Utility('Jelly', player_img_scale, img_index)})
            for r in range(REWARD_COUNT):
                img_index = r+1 #add offset for image index parameter
                actor_list.append({ACTOR_PROPERTY_ALIVE   : False, 
                                   ACTOR_PROPERTY_XPOS    : 0, 
                                   ACTOR_PROPERTY_YPOS    : 0,
                                   ACTOR_PROPERTY_XSPEED  : 0, 
                                   ACTOR_PROPERTY_YSPEED  : 0,
                                   ACTOR_PROPERTY_TYPE    : ACTOR_TYPE_REWARD,
                                   ACTOR_PROPERTY_IMAGE   : Load_Image_Utility('Reward', 0.333, img_index)})

    # Start random spawning
    if frame_count % (random.randrange(4,10) * 10) == 0:
        actor_index = random.randrange(0,len(actor_list))
        actor = actor_list[actor_index]
        if not actor[ACTOR_PROPERTY_ALIVE]:
            actor[ACTOR_PROPERTY_ALIVE] = True
            actor[ACTOR_PROPERTY_XPOS] = screen_width # start off-screen to the right
            actor[ACTOR_PROPERTY_YPOS] = random.randrange(0,player_yGround) # random height from top to player ground level
            actor[ACTOR_PROPERTY_XSPEED] = random.randrange(-5,-2) * 2
        
        actor_list[actor_index] = actor 

    return actor_list

# for Actors (enemies & rewards) - Move actors around the screen
def Move_Actors(actor_list):
    if actor_list != None:
        for actor in actor_list:
            if actor[ACTOR_PROPERTY_ALIVE]:
                actor[ACTOR_PROPERTY_XPOS] += actor[ACTOR_PROPERTY_XSPEED]
    return actor_list

# for Actors (just enemies) - kill the enemy when they leave the screen or touch a reward
def Destroy_Enemies(actor_list):
    if actor_list != None: # if there is an actor list
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
    if actor_list != None:
        for actor in actor_list:
            if actor[ACTOR_PROPERTY_ALIVE]:
                GameScreen.blit(actor[ACTOR_PROPERTY_IMAGE], (actor[ACTOR_PROPERTY_XPOS], actor[ACTOR_PROPERTY_YPOS]))
    return actor_list

# for Reward Actors only - Reward is applied for specific Reward type (adds points to score) 
def Apply_Rewards(actor_list,score):
    if actor_list != None: #Before continuing make sure there is an actor list created
        if (player_state == PLAYER_STATE_RUNNING) or (player_state == PLAYER_STATE_JUMPING): #Player can only collect rewards when running or jumping
            for actor in actor_list: #for every actor in the actor list
                if actor[ACTOR_PROPERTY_TYPE] == ACTOR_TYPE_REWARD: #if the actor is a reward
                    if actor[ACTOR_PROPERTY_ALIVE]: #if the reward is active (alive)
                        if Detect_Hit_Utility(player_xPos,player_yPos,player_running_images[0],actor[ACTOR_PROPERTY_XPOS],actor[ACTOR_PROPERTY_YPOS], actor[ACTOR_PROPERTY_IMAGE]): #check to see if player touched the reward
                            score += 1 #Add a point to the score!
                            actor[ACTOR_PROPERTY_ALIVE] = False # make the reward disappear
    return actor_list, score

# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Main game Loop
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Playing_Game = True

#Playing theme song
pygame.mixer.music.load("Theme.mid") #CITATION: (SEED:2415448160) https://pernyblom.github.io/abundant-music/index.html
pygame.mixer.music.play(-1) # Play the theme song. Note: setting the the loop parameter to -1 makes it repeat forever 

# Citation - 3.2: Source Code for Hello World with Pygame. (2019). from https://eng.libretexts.org/Bookshelves/Computer_Science/Programming_Languages/Book%3A_Making_Games_with_Python_and_Pygame_(Sweigart)/03%3A_Pygame_Basics/3.02%3A_Source_Code_for_Hello_World_with_Pygame
while Playing_Game: # main game loop
    
    start_time = time.time_ns() #capture frame start time
    frame_count += 1 #Increment frame counter
    
    # capture game input events
    last_event = None
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # pressed escape
                Playing_Game = False    
        if event.type == pygame.QUIT: # closed window
            Playing_Game = False
        last_event = event #save last event to use in player control logic

    # Start main game logic ----------------------------------------------------------------------------------------------------------------------------------------------------------------
    # -- Do Background and Score Logic
    Draw_Background(background_XPos1, background_XPos2) #show the background
    background_XPos1, background_XPos2 = Scroll_BackGround(background_XPos1, background_XPos2) #scroll the background to the left
    ShowScore_Background(score_value) # Show score on top of the background
    
    # -- Do Player related functions
    player_state, player_yPos, player_jump_speed = Control_Player(event, player_state, player_yPos, player_jump_speed)
    player_img_ndx,player_state,background_speed,actors = Destroy_Player(player_image_index,player_state,background_speed, actors)
    player_image_index,player_state,player_frozen = Draw_Player(player_image_index,player_state,player_frozen)

    # -- Do Actor related functions
    actors = Spawn_Actors(actors)
    actors = Move_Actors(actors)
    actors = Destroy_Enemies(actors)
    actors,score_value = Apply_Rewards(actors,score_value)
    actors = Draw_Actors(actors)

    # Start main game logic ----------------------------------------------------------------------------------------------------------------------------------------------------------------

    # show the updated game frame on the screen
    pygame.display.update()

    #capture frame end time
    end_time = time.time_ns()
    
    # calculate time elapsed = Start Time minus End Time (in nanoseconds)
    elapsed_time = end_time - start_time 
    
    # calculate time to sleep = (1 / frame rate) - time elapsed so far (converted from nanoseconds to seconds)
    sleep_time = (1.0 / Game_Frames_Per_Second) - (float(elapsed_time)/float(1000000000))
    
    #Limit frame rate by resting until total elapsed time equals the frame rate duration 
    if sleep_time > 0.0: # do not sleep if time elapsed is too long, which makes the sleep_time go negative and have an error
        time.sleep(sleep_time)

# Clean up section ----------------------------------------------------------------------------------------------------------
pygame.mixer.music.stop()
pygame.quit()
sys.exit()