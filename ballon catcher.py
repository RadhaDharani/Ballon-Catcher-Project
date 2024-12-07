import pygame
import random
import sys
import numpy as np

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BALLOON_COLORS = [RED, GREEN, BLUE]
BALLOON_POINTS = {RED: 10, GREEN: 20, BLUE: 30}

# Balloon properties
BALLOON_RADIUS = 20
BALLOON_SPEED = 3
BALLOON_SPAWN_RATE = 25 #for every 25 frames one new ballon is created.

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balloon Catcher")

clock = pygame.time.Clock()
#controls frame rate

class BernoulliAPSBandit:
    def __init__(self, n_arms, eta=0.05):        
        self.n_arms = n_arms
        self.eta = eta
        self.exploration_weights = [1.0] * n_arms
        #list with n_arms elements with individual value=1
    
    def pull_arm(self):        
        normalized_weights = [w / sum(self.exploration_weights) for w in self.exploration_weights]
        cum_prob = [sum(normalized_weights[:i+1]) for i in range(self.n_arms)]
        #list with normalized_weights upto index i
        rand_num = random.random()
        location_index = next(i for i in range(len(cum_prob)) if cum_prob[i] > rand_num)
        return location_index
       
        
    def update_exploration_weights(self, chosen_location, reward):
        w_t = self.exploration_weights[chosen_location]
        w_t = max(w_t, 0.0001)
        #avoiding division by zero
        if reward == 1:
            self.exploration_weights[chosen_location] = (1 - np.exp(-self.eta)) / (1 - np.exp(-self.eta / w_t))
            #update exploration weight positively
            #np.exp(-self.eta) encouraging exploration
            #1-np.exp(-self.eta) encouraging exploitation
            #update exploration weight negatively
            #np.exp(-self.eta / w_t) prob of updating weights to discourage exploration
            #1 - np.exp(-self.eta / w_t) prob of not updating weights to discourage exploration
        else:
            self.exploration_weights[chosen_location] = (np.exp(self.eta) - 1) / (np.exp(self.eta / w_t) - 1)
        print(chosen_location)

        for i in range(self.n_arms):
            if i != chosen_location:
                adjustment = ((1 - self.exploration_weights[chosen_location]) / max(1 - w_t, 0.0001))
                self.exploration_weights[i] *= adjustment
      
        

class Cannon(pygame.sprite.Sprite): 
    def __init__(self): 
        super().__init__()  #calls constructor of superclass pygame.sprite.Sprite any initialization code in the superclass is executed.
        self.image = pygame.Surface((50, 20))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        
       
        #get cannon at the bottom in the center and 50 px from bottom

    def update(self):
        if self.rect.x > SCREEN_WIDTH:
            self.rect.x -= 10
        if self.rect.x < 0:
            self.rect.x += 10

class Balloon(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.image = pygame.Surface((BALLOON_RADIUS * 2, BALLOON_RADIUS * 2))#creates a surface for balloon image.
        pygame.draw.circle(self.image, color, (BALLOON_RADIUS, BALLOON_RADIUS), BALLOON_RADIUS)
        self.rect = self.image.get_rect(center=(random.randint(BALLOON_RADIUS, SCREEN_WIDTH - BALLOON_RADIUS), 0))
        #This line creates a rectangle that represents the position and size of the balloon.
        self.color = color
        

    def update(self):
        self.rect.y += BALLOON_SPEED #move balloon downwards
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()  #deletes balloon sprite from window

all_sprites = pygame.sprite.Group()   #used to manage and update multiple sprites
balloon_group = pygame.sprite.Group()   #used to manage and update balloon sprites.
cannon = Cannon()
all_sprites.add(cannon)   #cannon object is added to all sprites.cannon will be updated and drawn along.

arms = 2  # Number of arms representing left or right
eta = 0.05  # Learning rate
bandit = BernoulliAPSBandit(arms, eta)

score = 0
lives = 3

running = True
while running:
    reward=0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(WHITE)

    all_sprites.update()
    all_sprites.draw(screen)  #draws all the sprites onto the screen.

    font = pygame.font.Font(None, 36) #creates a font object 
    score_text = font.render("Score: " + str(score), True, BLACK)  #renders score_text onto the screen
    lives_text = font.render("Lives: " + str(lives), True, BLACK)
    screen.blit(score_text, (10, 10)) # draws the score_text surface on the screen at coordinates(10,10)
    screen.blit(lives_text, (10, 50))

    pygame.display.flip() #update contents of the entire display

    clock.tick(60)
    #if random.randint(0, BALLOON_SPAWN_RATE) == 0:
    arm_chosen = bandit.pull_arm()

    if arm_chosen == 0:
            cannon.rect.x -= 20  # Move left
    else:
            cannon.rect.x += 20  # Move right
    cannon.update()

    if random.randint(0, BALLOON_SPAWN_RATE) == 0:
       #selects a random colored balloon
      color = random.choice(BALLOON_COLORS)
            
      balloon = Balloon(color)  #balloon object is created with chosen color
      balloon_group.add(balloon)
      all_sprites.add(balloon)

    collisions = pygame.sprite.spritecollide(cannon, balloon_group, True) 
    for balloon in collisions:
        
        score += BALLOON_POINTS[balloon.color]
        reward = 1

    
    for balloon in balloon_group:
        if balloon.rect.bottom >= SCREEN_HEIGHT:
            lives -= 1
            balloon.kill()
            reward = 0
    if lives <= 0:
        running = False #game loop is exited
    for arm_chosen in range(2): 
         bandit.update_exploration_weights(arm_chosen, 1)
       
font = pygame.font.Font(None, 72)
game_over_text = font.render("Game Over", True, RED)
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - game_over_text.get_height() // 2))
pygame.display.flip()


pygame.time.wait(2000)
pygame.quit()
sys.exit()