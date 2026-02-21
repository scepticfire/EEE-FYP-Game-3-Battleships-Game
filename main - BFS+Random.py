#  Module Imports
import pygame
import random


#  Module Initialization
pygame.init()


#  Game Assets and Objects
class Ship:
    def __init__(self, name, img, pos, size, numGuns=0, gunPath=None, gunsize=None, gunCoordsOffset=None):
        self.name = name
        self.pos = pos
        #  Load the Vertical image
        self.vImage = loadImage(img, size)
        self.vImageWidth = self.vImage.get_width()
        self.vImageHeight = self.vImage.get_height()
        self.vImageRect = self.vImage.get_rect()
        self.vImageRect.topleft = pos
        #  Load the Horizontal image
        self.hImage = pygame.transform.rotate(self.vImage, -90)
        self.hImageWidth = self.hImage.get_width()
        self.hImageHeight = self.hImage.get_height()
        self.hImageRect = self.hImage.get_rect()
        self.hImageRect.topleft = pos
        #  Image and Rectangle
        self.image = self.vImage
        self.rect = self.vImageRect
        self.rotation = False
        #  Ship is current selection
        self.active = False
        #  Load gun Images
        self.gunslist = []
        if numGuns > 0:
            self.gunCoordsOffset = gunCoordsOffset
            for num in range(numGuns):
                self.gunslist.append(
                    Guns(gunPath,
                         self.rect.center,
                         (size[0] * gunsize[0],
                          size[1] * gunsize[1]),
                         self.gunCoordsOffset[num])
                )


    def selectShipAndMove(self):
        """Selects the ship and moves it according to the mouse position"""
        while self.active == True:
            self.rect.center = get_logical_mouse_pos()
            updateGameScreen(GAMESCREEN, GAMESTATE)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.checkForCollisions(pFleet):
                        if event.button == 1:
                            self.hImageRect.center = self.vImageRect.center = self.rect.center
                            self.active = False

                    if event.button == 3:
                        self.rotateShip()


    def rotateShip(self, doRotation=False):
        """switch ship between vertical and horizontal"""
        if self.active or doRotation == True:
            if self.rotation == False:
                self.rotation = True
            else:
                self.rotation = False
            self.switchImageAndRect()


    def switchImageAndRect(self):
        """Switches from Horizontal to Vertical and vice versa"""
        if self.rotation == True:
            self.image = self.hImage
            self.rect = self.hImageRect
        else:
            self.image = self.vImage
            self.rect = self.vImageRect
        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def checkForCollisions(self, shiplist):
        """Check to make sure the ship is not colliding with any of the other ships"""
        slist = shiplist.copy()
        slist.remove(self)
        for item in slist:
            if self.rect.colliderect(item.rect):
                return True
        return False


    def checkForRotateCollisions(self, shiplist):
        """Check to make sure the ship is not going to collide with any other ship before rotating"""
        slist = shiplist.copy()
        slist.remove(self)
        for ship in slist:
            if self.rotation == True:
                if self.vImageRect.colliderect(ship.rect):
                    return True
            else:
                if self.hImageRect.colliderect(ship.rect):
                    return True
        return False


    def returnToDefaultPosition(self):
        """Returns the ship to its default position"""
        if self.rotation == True:
            self.rotateShip(True)

        self.rect.topleft = self.pos
        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def snapToGridEdge(self, gridCoords):
        if self.rect.topleft != self.pos:

            #  Check to see if the ships position is outside of the grid:
            if self.rect.left > gridCoords[0][-1][0] + 50 or \
                self.rect.right < gridCoords[0][0][0] or \
                self.rect.top > gridCoords[-1][0][1] + 50 or \
                self.rect.bottom < gridCoords[0][0][1]:
                self.returnToDefaultPosition()

            elif self.rect.right > gridCoords[0][-1][0]+50:
                self.rect.right = gridCoords[0][-1][0] + 50
            elif self.rect.left < gridCoords[0][0][0]:
                self.rect.left = gridCoords[0][0][0]
            elif self.rect.top < gridCoords[0][0][1]:
                self.rect.top = gridCoords[0][0][1]
            elif self.rect.bottom > gridCoords[-1][0][1] + 50:
                self.rect.bottom = gridCoords[-1][0][1] + 50
            self.vImageRect.center = self.hImageRect.center = self.rect.center


    def snapToGrid(self, gridCoords):
        for rowX in gridCoords:
            for cell in rowX:
                if self.rect.left >= cell[0] and self.rect.left < cell[0] + CELLSIZE \
                    and self.rect.top >= cell[1] and self.rect.top < cell[1] + CELLSIZE:
                    if self.rotation == False:
                        self.rect.topleft = (cell[0] + (CELLSIZE - self.image.get_width())//2, cell[1])
                    else:
                        self.rect.topleft = (cell[0], cell[1] + (CELLSIZE - self.image.get_height())//2)

        self.hImageRect.center = self.vImageRect.center = self.rect.center


    def draw(self, window):
        """Draw the ship to the screen"""
        window.blit(self.image, self.rect)
        #pygame.draw.rect(window, (255, 0, 0), self.rect, 1)
        for guns in self.gunslist:
            guns.draw(window, self)


class Guns:
    def __init__(self, imgPath, pos, size, offset):
        self.orig_image = loadImage(imgPath, size, True)
        self.image = self.orig_image
        self.offset = offset
        self.rect = self.image.get_rect(center=pos)


    def update(self, ship):
        """Updating the Guns Positions on the ship"""
        self.rotateGuns(ship)
        if ship.rotation == False:
            self.rect.center = (ship.rect.centerx, ship.rect.centery + (ship.image.get_height()//2 * self.offset))
        else:
            self.rect.center = (ship.rect.centerx + (ship.image.get_width()//2 * -self.offset), ship.rect.centery)


    def _update_image(self, angle):
        self.image = pygame.transform.rotate(self.orig_image, -angle)
        self.rect = self.image.get_rect(center=self.rect.center)


    def rotateGuns(self, ship):
        """Rotates the guns in relation to direction of the mouse cursor"""
        direction = pygame.math.Vector2(get_logical_mouse_pos()) - pygame.math.Vector2(self.rect.center)
        radius, angle = direction.as_polar()
        if not ship.rotation:
            if self.rect.centery <= ship.vImageRect.centery and angle <= 0:
                self._update_image(angle)
            if self.rect.centery >= ship.vImageRect.centery and angle > 0:
                self._update_image(angle)
        else:
            if self.rect.centerx <= ship.hImageRect.centerx and (angle <= -90 or angle >= 90):
                self._update_image(angle)
            if self.rect.centerx >= ship.hImageRect.centerx and (angle >= -90 and angle <= 90):
                self._update_image(angle)


    def draw(self, window, ship):
        self.update(ship)
        window.blit(self.image, self.rect)


class Button:
    def __init__(self, image, size, pos, msg):
        self.name = msg
        self.image = image
        self.imageLarger = self.image
        self.imageLarger = pygame.transform.scale(self.imageLarger, (size[0] + 10, size[1] + 10))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.radarUsed = 0
        self.active = False

        self.msg = self.addText(msg)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def addText(self, msg):
        """Add font to the button image"""
        font = pygame.font.SysFont('Stencil', 22)
        message = font.render(msg, 1, (255,255,255))
        return message


    def focusOnButton(self, window):
        """Brings attention to which button is being focussed on"""
        if self.active:
            if self.rect.collidepoint(get_logical_mouse_pos()):
                window.blit(self.imageLarger, (self.rect[0] - 5, self.rect[1] - 5, self.rect[2], self.rect[3]))
            else:
                window.blit(self.image, self.rect)


    def actionOnPress(self):
        """Which actions to take according to button selected"""
        if self.active:
            if self.name == 'Randomize':
                self.randomizeShipPositions(pFleet, pGameGrid)
                self.randomizeShipPositions(cFleet, cGameGrid)
            elif self.name == 'Reset':
                self.resetShips(pFleet)
            elif self.name == 'Deploy':
                self.deploymentPhase()
            elif self.name == 'Quit':
                pass
            elif self.name == 'Redeploy':
                self.restartTheGame()


    def randomizeShipPositions(self, shiplist, gameGrid):
        """Calls the randomize ships function"""
        if DEPLOYMENT == True:
            randomizeShipPositions(shiplist, gameGrid)


    def resetShips(self, shiplist):
        """Resets the ships to their default positions"""
        if DEPLOYMENT == True:
            for ship in shiplist:
                ship.returnToDefaultPosition()


    def deploymentPhase(self):
        pass


    def restartTheGame(self):
        TOKENS.clear()
        self.resetShips(pFleet)
        self.randomizeShipPositions(cFleet, cGameGrid)
        updateGameLogic(cGameGrid, cFleet, cGameLogic)
        updateGameLogic(pGameGrid, pFleet, pGameLogic)


    def updateButtons(self, gameStatus):
        """update the buttons as per the game stage"""
        if self.name == 'Deploy' and gameStatus == False:
            self.name = 'Redeploy'
        elif self.name == 'Redeploy' and gameStatus == True:
            self.name = 'Deploy'
        if self.name == 'Reset' and gameStatus == False:
            self.name = 'Radar Scan'
        elif self.name == 'Radar Scan' and gameStatus == True:
            self.name = 'Reset'
        if self.name == 'Randomize' and gameStatus == False:
            self.name = 'Quit'
        elif self.name == 'Quit' and gameStatus == True:
            self.name = 'Randomize'
        self.msg = self.addText(self.name)
        self.msgRect = self.msg.get_rect(center=self.rect.center)


    def draw(self, window):
        self.updateButtons(DEPLOYMENT)
        self.focusOnButton(window)
        window.blit(self.msg, self.msgRect)

    def drawOutline(self, window, color=(255, 0, 0), thickness=3):
        pygame.draw.rect(window, color, self.rect, thickness)


class Player:
    def __init__(self):
        self.turn = True


    def makeAttack(self, grid, logicgrid):
        """When its the player's turn, the player must make an attacking selection within the computer grid."""
        posX, posY = get_logical_mouse_pos()
        if posX >= grid[0][0][0] and posX <= grid[0][-1][0] + 50 and posY >= grid[0][0][1] and posY <= grid[-1][0][1] + 50:
            for i, rowX in enumerate(grid):
                for j, colX in enumerate(rowX):
                    if posX >= colX[0] and posX < colX[0] + 50 and posY >= colX[1] and posY <= colX[1] + 50:
                        if logicgrid[i][j] != ' ':
                            if logicgrid[i][j] == 'O':
                                TOKENS.append(Tokens(REDTOKEN, grid[i][j], 'Hit', None, None, None))
                                logicgrid[i][j] = 'T'
                                # SHOTSOUND.play()
                                # HITSOUND.play()
                                self.turn = False
                        else:
                            logicgrid[i][j] = 'X'
                            # SHOTSOUND.play()
                            # MISSSOUND.play()
                            TOKENS.append(Tokens(GREENTOKEN, grid[i][j], 'Miss', None, None, None))
                            self.turn = False

#Common AI Class
class ComputerAI:
    def __init__(self):
        self.turn = False
        self.steps = 0   

# BFS Combinations
class BFSRandom(ComputerAI):
    def __init__(self):
        super().__init__()
        self.visited = set()
        self.pending = []     # BFS frontier
        self.hunting = True

    def computerStatus(self, msg):
        image = pygame.font.SysFont('Stencil', 22)
        message = image.render(msg, 1, (0, 0, 0))
        return message

    def makeAttack(self, gamelogic):
        self.steps += 1
        # ---------- BFSRandom (KILL MODE) ----------
        if self.pending:
            x, y = self.pending.pop(0)

            if (x, y) in self.visited:
                return True

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':
                self._hit(x, y, gamelogic)
                self._bfs_expand(x, y)
            else:
                self._miss(x, y, gamelogic)

            self.turn = False
            return False

        # ---------- PROBABILITY HUNT ----------
        candidates = self._probability_hunt(gamelogic)

        if not candidates:
            return False

        x, y = candidates[0]   # highest probability

        self.visited.add((x, y))

        if gamelogic[x][y] == 'O':
            self._hit(x, y, gamelogic)
            self._bfs_expand(x, y)
        else:
            self._miss(x, y, gamelogic)

        self.turn = False
        return False

    # ---------------- BFS ----------------

    def _bfs_expand(self, x, y):
        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) not in self.visited:
                self.pending.append((nx, ny))

    # ---------------- Probability ----------------

    def _probability_hunt(self, grid):
        scores = []

        for i in range(10):
            for j in range(10):
                if (i, j) in self.visited:
                    continue
                if grid[i][j] not in (' ', 'O'):
                    continue

                # Parity optimization
                if (i + j) % 2 != 0:
                    continue

                score = self._score_cell(i, j, grid)
                scores.append(((i, j), score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos, _ in scores]

    def _score_cell(self, x, y, grid):
        """Count possible ship placements passing through this cell"""
        score = 0

        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                if grid[nx][ny] in (' ', 'O'):
                    score += 1

        return score

    # ---------------- Helpers ----------------

    def _hit(self, x, y, gamelogic):
        gamelogic[x][y] = 'T'
        TOKENS.append(Tokens(
            REDTOKEN, pGameGrid[x][y], 'Hit',
            FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
        ))

    def _miss(self, x, y, gamelogic):
        gamelogic[x][y] = 'X'
        TOKENS.append(Tokens(
            BLUETOKEN, pGameGrid[x][y], 'Miss',
            None, None, None
        ))

    def get_neighbors(self, x, y):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                yield nx, ny


class BFSLinearSearch(ComputerAI):
    def __init__(self):
        super().__init__()
        self.stack = []          # LINEAR SEARCH
        self.visited = set()     # visited cells
        self.hunting = True      # hunt vs linear search mode

    def makeAttack(self, gamelogic):
        self.steps += 1
        # --- LINEAR SEARCH MODE ---
        if self.stack:
            x, y = self.stack.pop()

            if (x, y) in self.visited:
                return True

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':  # HIT
                gamelogic[x][y] = 'T'
                TOKENS.append(Tokens(
                    REDTOKEN, pGameGrid[x][y], 'Hit',
                    FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
                ))

                neighbors = list(self.get_neighbors(x, y))
                random.shuffle(neighbors)
                for n in neighbors:
                    self.stack.append(n)

                # Push neighbors (LINEAR SEARCH)
                for nx, ny in self.get_neighbors(x, y):
                    if (nx, ny) not in self.visited:
                        self.stack.append((nx, ny))

                self.turn = False
                return False

            elif gamelogic[x][y] == ' ':
                gamelogic[x][y] = 'X'
                TOKENS.append(Tokens(
                    BLUETOKEN, pGameGrid[x][y], 'Miss',
                    None, None, None
                ))
                self.turn = False
                return False

        # --- HUNT MODE ---
        for i in range(10):
            for j in range(10):
                if (i, j) not in self.visited and gamelogic[i][j] in (' ', 'O'):
                    self.visited.add((i, j))

                    if gamelogic[i][j] == 'O':  # HIT
                        gamelogic[i][j] = 'T'
                        TOKENS.append(Tokens(
                            REDTOKEN, pGameGrid[i][j], 'Hit',
                            FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
                        ))

                        # Seed LINEAR SEARCH from hit
                        for nx, ny in self.get_neighbors(i, j):
                            self.stack.append((nx, ny))

                    else:  # MISS
                        gamelogic[i][j] = 'X'
                        TOKENS.append(Tokens(
                            BLUETOKEN, pGameGrid[i][j], 'Miss',
                            None, None, None
                        ))

                    self.turn = False
                    return False

        return False

    def get_neighbors(self, x, y):
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                yield nx, ny

class BFSBinarySearch(ComputerAI):
    def __init__(self):
        super().__init__()

        # --- BFS (kill mode) ---
        self.queue = []
        self.visited = set()
        self.hunting = True

        # --- Binary-search-style sweep ---
        self.start_col = random.choice([4, 5])   # E or F
        self.direction = random.choice([-1, 1])  # left or right

        self.row = 0
        self.col = self.start_col
        self.phase = 'primary'   # primary side → secondary side

    def makeAttack(self, gamelogic):
        self.steps += 1
        # ========== BFS KILL MODE ==========
        if self.queue:
            x, y = self.queue.pop(0)

            if (x, y) in self.visited:
                return True

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':
                self._hit(x, y, gamelogic)
                self._bfs_expand(x, y)
            else:
                self._miss(x, y, gamelogic)

            self.turn = False
            return False

        # ========== BINARY SWEEP MODE ==========
        while self.row < 10:

            if 0 <= self.col < 10:
                x, y = self.row, self.col
                self.col += self.direction
            else:
                # End reached → switch side
                if self.phase == 'primary':
                    self.phase = 'secondary'
                    self.col = 5 if self.start_col == 4 else 4
                    self.direction *= -1
                else:
                    # Finished both sides → next row
                    self.phase = 'primary'
                    self.col = self.start_col
                    self.direction *= -1
                    self.row += 1
                continue

            if (x, y) in self.visited:
                continue

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':
                self._hit(x, y, gamelogic)
                self._bfs_expand(x, y)
            else:
                self._miss(x, y, gamelogic)

            self.turn = False
            return False

        return False

    # ---------------- BFS helpers ----------------

    def _bfs_expand(self, x, y):
        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) not in self.visited:
                self.queue.append((nx, ny))

    def get_neighbors(self, x, y):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                yield nx, ny

    # ---------------- Token helpers ----------------

    def _hit(self, x, y, gamelogic):
        gamelogic[x][y] = 'T'
        TOKENS.append(Tokens(
            REDTOKEN, pGameGrid[x][y], 'Hit',
            FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
        ))

    def _miss(self, x, y, gamelogic):
        gamelogic[x][y] = 'X'
        TOKENS.append(Tokens(
            BLUETOKEN, pGameGrid[x][y], 'Miss',
            None, None, None
        ))

# DFS Combiniations
class DFSRandom(ComputerAI):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.visited = set()

    def makeAttack(self, gamelogic):
        self.steps += 1
        # ===== DFS KILL MODE =====
        if self.stack:
            x, y = self.stack.pop()

            if (x, y) in self.visited:
                return True

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':
                self._hit(x, y, gamelogic)
                self._dfs_expand(x, y)
            else:
                self._miss(x, y, gamelogic)

            self.turn = False
            return False

        # ===== RANDOM HUNT MODE =====
        while True:
            x = random.randint(0, 9)
            y = random.randint(0, 9)

            if (x, y) not in self.visited:
                break

        self.visited.add((x, y))

        if gamelogic[x][y] == 'O':
            self._hit(x, y, gamelogic)
            self._dfs_expand(x, y)
        else:
            self._miss(x, y, gamelogic)

        self.turn = False
        return False

    # -------- DFS helpers --------
    def _dfs_expand(self, x, y):
        for nx, ny in self.get_neighbors(x, y):
            if (nx, ny) not in self.visited:
                self.stack.append((nx, ny))

    def get_neighbors(self, x, y):
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 10 and 0 <= ny < 10:
                yield nx, ny

    # -------- Token helpers --------
    def _hit(self, x, y, gamelogic):
        gamelogic[x][y] = 'T'
        TOKENS.append(Tokens(
            REDTOKEN, pGameGrid[x][y], 'Hit',
            FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
        ))

    def _miss(self, x, y, gamelogic):
        gamelogic[x][y] = 'X'
        TOKENS.append(Tokens(
            BLUETOKEN, pGameGrid[x][y], 'Miss',
            None, None, None
        ))

class DFSLinearSearch(ComputerAI):
    def __init__(self):
        super().__init__()
        self.stack = []          # DFS stack
        self.visited = set()
        self.hunting = True

    def makeAttack(self, gamelogic):
        self.steps += 1
        # ===== DFS LINEAR MODE =====
        if self.stack:
            x, y, dx, dy = self.stack.pop()

            if (x, y) in self.visited:
                return True

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':  # HIT
                gamelogic[x][y] = 'T'
                TOKENS.append(Tokens(
                    REDTOKEN, pGameGrid[x][y], 'Hit',
                    FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
                ))

                # Continue deeper in SAME direction
                nx, ny = x + dx, y + dy
                if 0 <= nx < 10 and 0 <= ny < 10:
                    self.stack.append((nx, ny, dx, dy))

                self.turn = False
                return False

            elif gamelogic[x][y] == ' ':
                gamelogic[x][y] = 'X'
                TOKENS.append(Tokens(
                    BLUETOKEN, pGameGrid[x][y], 'Miss',
                    None, None, None
                ))
                self.turn = False
                return False

        # ===== LINEAR HUNT MODE =====
        for i in range(10):
            for j in range(10):
                if (i, j) not in self.visited and gamelogic[i][j] in (' ', 'O'):
                    self.visited.add((i, j))

                    if gamelogic[i][j] == 'O':  # HIT
                        gamelogic[i][j] = 'T'
                        TOKENS.append(Tokens(
                            REDTOKEN, pGameGrid[i][j], 'Hit',
                            FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
                        ))

                        # Seed DFS with ALL directions
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = i + dx, j + dy
                            if 0 <= nx < 10 and 0 <= ny < 10:
                                self.stack.append((nx, ny, dx, dy))

                    else:  # MISS
                        gamelogic[i][j] = 'X'
                        TOKENS.append(Tokens(
                            BLUETOKEN, pGameGrid[i][j], 'Miss',
                            None, None, None
                        ))

                    self.turn = False
                    return False

        return False
    
class DFSBinarySearch(ComputerAI):
    def __init__(self):
        super().__init__()

        # ===== DFS (kill mode) =====
        self.stack = []          # LIFO stack
        self.visited = set()

        # ===== Binary-style hunt =====
        self.start_col = random.choice([4, 5])     # E or F
        self.direction = random.choice([-1, 1])    # left or right

        self.row = 0
        self.col = self.start_col
        self.phase = 'primary'    # primary → secondary

    def makeAttack(self, gamelogic):
        self.steps += 1
        # ================= DFS KILL MODE =================
        if self.stack:
            x, y, dx, dy = self.stack.pop()

            if (x, y) in self.visited:
                return True

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':   # HIT
                self._hit(x, y, gamelogic)

                # Continue deeper in SAME direction
                nx, ny = x + dx, y + dy
                if 0 <= nx < 10 and 0 <= ny < 10:
                    self.stack.append((nx, ny, dx, dy))

            else:  # MISS
                self._miss(x, y, gamelogic)

            self.turn = False
            return False

        # ================= BINARY SWEEP MODE =================
        while self.row < 10:

            if 0 <= self.col < 10:
                x, y = self.row, self.col
                self.col += self.direction
            else:
                # Switch side or move to next row
                if self.phase == 'primary':
                    self.phase = 'secondary'
                    self.col = 5 if self.start_col == 4 else 4
                    self.direction *= -1
                else:
                    self.phase = 'primary'
                    self.col = self.start_col
                    self.direction *= -1
                    self.row += 1
                continue

            if (x, y) in self.visited:
                continue

            self.visited.add((x, y))

            if gamelogic[x][y] == 'O':   # HIT
                self._hit(x, y, gamelogic)

                # Seed DFS stack with all directions
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < 10 and 0 <= ny < 10:
                        self.stack.append((nx, ny, dx, dy))

            else:
                self._miss(x, y, gamelogic)

            self.turn = False
            return False

        return False

    # ---------------- Token helpers ----------------

    def _hit(self, x, y, gamelogic):
        gamelogic[x][y] = 'T'
        TOKENS.append(Tokens(
            REDTOKEN, pGameGrid[x][y], 'Hit',
            FIRETOKENIMAGELIST, EXPLOSIONIMAGELIST, None
        ))

    def _miss(self, x, y, gamelogic):
        gamelogic[x][y] = 'X'
        TOKENS.append(Tokens(
            BLUETOKEN, pGameGrid[x][y], 'Miss',
            None, None, None
        ))
    

class Tokens:
    def __init__(self, image, pos, action, imageList=None, explosionList=None, soundFile=None):
        self.image = image
        self.rect = self.image.get_rect()
        self.pos = pos
        self.rect.topleft = self.pos
        self.imageList = imageList
        self.explosionList = explosionList
        self.action = action
        self.soundFile = soundFile
        self.timer = pygame.time.get_ticks()
        self.imageIndex = 0
        self.explosionIndex = 0
        self.explosion = False


    def animate_Explosion(self):
        """Animating the Explosion sequence"""
        self.explosionIndex += 1
        if self.explosionIndex < len(self.explosionList):
            return self.explosionList[self.explosionIndex]
        else:
            return self.animate_fire()


    def animate_fire(self):
        """Animate the Fire sequence"""
        if pygame.time.get_ticks() - self.timer >= 100:
            self.timer = pygame.time.get_ticks()
            self.imageIndex += 1
        if self.imageIndex < len(self.imageList):
            return self.imageList[self.imageIndex]
        else:
            self.imageIndex = 0
            return self.imageList[self.imageIndex]


    def draw(self, window):
        """Draws the tokens to the screen"""
        if not self.imageList:
            window.blit(self.image, self.rect)
        else:
            self.image = self.animate_Explosion()
            self.rect = self.image.get_rect(topleft=self.pos)
            self.rect[1] = self.pos[1] - 10
            window.blit(self.image, self.rect)


#  Game Utility Functions
def createGameGrid(rows, cols, cellsize, pos):
    """Creates a game grid with coordinates for each cell"""
    startX = pos[0]
    startY = pos[1]
    coordGrid = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append((startX, startY))
            startX += cellsize
        coordGrid.append(rowX)
        startX = pos[0]
        startY += cellsize
    return coordGrid


def createGameLogic(rows, cols):
    """Updates the game grid with logic, ie - spaces and X for ships"""
    gamelogic = []
    for row in range(rows):
        rowX = []
        for col in range(cols):
            rowX.append(' ')
        gamelogic.append(rowX)
    return gamelogic


def updateGameLogic(coordGrid, shiplist, gamelogic):
    """Updates the game grid with the position of the ships"""
    for i, rowX in enumerate(coordGrid):
        for j, colX in enumerate(rowX):
            if gamelogic[i][j] == 'T' or gamelogic[i][j] == 'X':
                continue
            else:
                gamelogic[i][j] = ' '
                for ship in shiplist:
                    if pygame.rect.Rect(colX[0], colX[1], CELLSIZE, CELLSIZE).colliderect(ship.rect):
                        gamelogic[i][j] = 'O'


def showGridOnScreen(window, cellsize, playerGrid, computerGrid):
    """Draws the player and computer grids to the screen"""
    gamegrids = [playerGrid, computerGrid]
    for grid in gamegrids:
        for row in grid:
            for col in row:
                pygame.draw.rect(window, (255, 255, 255), (col[0], col[1], cellsize, cellsize), 1)


def loadImage(path, size, rotate=False):
    """A function to import the images into memory"""
    img = pygame.image.load(path).convert_alpha()
    img = pygame.transform.scale(img, size)
    if rotate == True:
        img = pygame.transform.rotate(img, -90)
    return img


def loadAnimationImages(path, aniNum,  size):
    """Load in stipulated number of images to memory"""
    imageList = []
    for num in range(aniNum):
        if num < 10:
            imageList.append(loadImage(f'{path}00{num}.png', size))
        elif num < 100:
            imageList.append(loadImage(f'{path}0{num}.png', size))
        else:
            imageList.append(loadImage(f'{path}{num}.png', size))
    return imageList


def loadSpriteSheetImages(spriteSheet, rows, cols, newSize, size):
    image = pygame.Surface((128, 128))
    image.blit(spriteSheet, (0, 0), (rows * size[0], cols * size[1], size[0], size[1]))
    image = pygame.transform.scale(image, (newSize[0], newSize[1]))
    image.set_colorkey((0, 0, 0))
    return image


def increaseAnimationImage(imageList, ind):
    return imageList[ind]


def createFleet():
    """Creates the fleet of ships"""
    fleet = []
    for name in FLEET.keys():
        fleet.append(
            Ship(name,
                 FLEET[name][1],
                 FLEET[name][2],
                 FLEET[name][3],
                 FLEET[name][4],
                 FLEET[name][5],
                 FLEET[name][6],
                 FLEET[name][7])
        )
    return fleet


def sortFleet(ship, shiplist):
    """Rearranges the list of ships"""
    shiplist.remove(ship)
    shiplist.append(ship)


def randomizeShipPositions(shiplist, gamegrid):
    """Select random locations on the game grid for the battleships"""
    placedShips = []
    for i, ship in enumerate(shiplist):
        validPosition = False
        while validPosition == False:
            ship.returnToDefaultPosition()
            rotateShip = random.choice([True, False])
            if rotateShip == True:
                yAxis = random.randint(0, 9)
                xAxis = random.randint(0, 9 - (ship.hImage.get_width()//50))
                ship.rotateShip(True)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            else:
                yAxis = random.randint(0, 9 - (ship.vImage.get_height()//50))
                xAxis = random.randint(0, 9)
                ship.rect.topleft = gamegrid[yAxis][xAxis]
            if len(placedShips) > 0:
                for item in placedShips:
                    if ship.rect.colliderect(item.rect):
                        validPosition = False
                        break
                    else:
                        validPosition = True
            else:
                validPosition = True
        placedShips.append(ship)


def deploymentPhase(deployment):
    global AUTOPLAY, TURN_PHASE

    AUTOPLAY = False           # disable autoplay
    TURN_PHASE = 'PLAYER'      # reset turn order

    return not deployment


def pick_random_ship_location(gameLogic):
    validChoice = False
    while not validChoice:
        posX = random.randint(0, 9)
        posY = random.randint(0, 9)
        if gameLogic[posX][posY] == 'O':
            validChoice = True

    return (posX, posY)


def displayRadarScanner(imagelist, indnum, SCANNER):
    if SCANNER == True and indnum <= 359:
        image = increaseAnimationImage(imagelist, indnum)
        return image
    else:
        return False


def displayRadarBlip(num, position):
    if SCANNER:
        image = None
        if position[0] >= 5 and position[1] >= 5:
            if num >= 0 and num <= 90:
                image = increaseAnimationImage(RADARBLIPIMAGES, num // 10)
        elif position[0] < 5 and position[1] >= 5:
            if num > 270 and num <= 360:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 4) // 10)
        elif position[0] < 5 and position[1] < 5:
            if num > 180 and num <= 270:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 3) // 10)
        elif position[0] >= 5 and position[1] < 5:
            if num > 90 and num <= 180:
                image = increaseAnimationImage(RADARBLIPIMAGES, (num // 2) // 10)
        return image


def takeTurns(p1, p2):
    global TURNTIMER, TURN_PHASE

    if not AUTOPLAY:
        # ===== NORMAL MANUAL MODE =====
        if not p1.turn:
            if not p2.makeAttack(pGameLogic):
                p1.turn = True
        return

    # ===== AUTOPLAY MODE =====
    current_time = pygame.time.get_ticks()

    # Enforce delay between turns
    if current_time - TURNTIMER < AI_DELAY:
        return

    # ---------- PLAYER AI TURN ----------
    if TURN_PHASE == 'PLAYER':
        autoplay_player_attack()

        p1.turn = False
        p2.turn = True

        TURN_PHASE = 'ENEMY'
        TURNTIMER = current_time
        return

    # ---------- ENEMY AI TURN ----------
    if TURN_PHASE == 'ENEMY':
        p2.makeAttack(pGameLogic)

        p2.turn = False
        p1.turn = True

        TURN_PHASE = 'PLAYER'
        TURNTIMER = current_time
        return


def checkForWinners(grid):
    validGame = True
    for row in grid:
        if 'O' in row:
            validGame = False
    return validGame


def shipLabelMaker(msg):
    """Makes the ship labels to display on the screen"""
    textMessage = pygame.font.SysFont('Stencil', 22)
    textMessage = textMessage.render(msg, 1, (0, 17, 167))
    textMessage = pygame.transform.rotate(textMessage, 90)
    return textMessage


def displayShipNames(window):
    """Posting the ship labels to the screen in the correct positions"""
    shipLabels = []
    for ship in ['carrier', 'battleship', 'cruiser', 'destroyer', 'submarine', 'patrol boat', 'rescue boat']:
        shipLabels.append(shipLabelMaker(ship))
    startPos = 25
    for item in shipLabels:
        window.blit(item, (startPos, 600))
        startPos += 75


def mainMenuScreen(window):
    window.fill((0, 0, 0))
    window.blit(MAINMENUIMAGE, (0, 0))

    for button in BUTTONS:
        button.active = (button.name == "Start")
        button.draw(window)



def deploymentScreen(window):
    window.fill((0, 0, 0))

    window.blit(BACKGROUND, (0, 0))
    window.blit(PGAMEGRIDIMG, (0, 0))
    window.blit(CGAMEGRIDIMG, (cGameGrid[0][0][0] - 50, cGameGrid[0][0][1] - 50))

    #  Draw ships to screen
    for ship in pFleet:
        ship.draw(window)
        ship.snapToGridEdge(pGameGrid)
        ship.snapToGrid(pGameGrid)

    displayShipNames(window)

    for ship in cFleet:
        ship.snapToGridEdge(cGameGrid)
        ship.snapToGrid(cGameGrid)

    for button in BUTTONS:
        if button.name in ['Randomize', 'Reset', 'Deploy', 'Quit', 'Radar Scan', 'Redeploy']:
            button.active = True
            button.draw(window)
        else:
            button.active = False


    radarScan = displayRadarScanner(RADARGRIDIMAGES, INDNUM, SCANNER)
    if not radarScan:
        pass
    else:
        window.blit(radarScan, (cGameGrid[0][0][0], cGameGrid[0][-1][1]))
        window.blit(RADARGRID, (cGameGrid[0][0][0], cGameGrid[0][-1][1]))

    RBlip = displayRadarBlip(INDNUM, BLIPPOSITION)
    if RBlip:
        window.blit(RBlip, (cGameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][0],
                            cGameGrid[BLIPPOSITION[0]][BLIPPOSITION[1]][1]))

    for token in TOKENS:
        token.draw(window)

    updateGameLogic(pGameGrid, pFleet, pGameLogic)
    updateGameLogic(cGameGrid, cFleet, cGameLogic)
    drawStepCounter(window, computer)

    AUTOPLAY_BUTTON.active = (DEPLOYMENT == False)
    AUTOPLAY_BUTTON.draw(window)

    if AUTOPLAY and AUTOPLAY_BUTTON.active:
        AUTOPLAY_BUTTON.drawOutline(window, (0, 200, 0))

    if AUTOPLAY:
        AUTOPLAY_BUTTON.drawOutline(window, (0, 200, 0))

def endScreen(window):
    window.fill((0, 0, 0))

    window.blit(ENDSCREENIMAGE, (0, 0))

    for button in BUTTONS:
        if button.name in ['Start', 'Quit']:
            button.active = True
            button.draw(window)
        else:
            button.active = False


def updateGameScreen(window, GAMESTATE):
    window.fill((0, 0, 0))

    if GAMESTATE == 'Main Menu':
        mainMenuScreen(window)
    elif GAMESTATE == 'Deployment':
        deploymentScreen(window)
    elif GAMESTATE == 'Game Over':
        endScreen(window)
    elif GAMESTATE == 'AI Config':
        aiConfigScreen(window)

    # Scale logical screen to window
    scaled = pygame.transform.smoothscale(
        window,
        WINDOW.get_size()
    )
    WINDOW.blit(scaled, (0, 0))
    pygame.display.update()

#get mouse pos
def get_logical_mouse_pos():
    mx, my = pygame.mouse.get_pos()   # <-- THIS was the mistake
    wx, wy = WINDOW.get_size()

    scale_x = LOGICAL_WIDTH / wx
    scale_y = LOGICAL_HEIGHT / wy

    return int(mx * scale_x), int(my * scale_y)

def aiConfigScreen(window):
    window.fill((0, 150, 170))  # teal background

    title = pygame.font.SysFont('Stencil', 36).render(
        'Choose AI Algorithm:', True, (0, 0, 0)
    )
    window.blit(title, (450, 80))

    for btn in AI_BUTTONS:
        btn.active = True
        btn.draw(window)
        if SELECTED_AI == btn.name:
            btn.drawOutline(window)

    subtitle = pygame.font.SysFont('Stencil', 36).render(
        'Choose Starting Position:', True, (0, 0, 0)
    )
    window.blit(subtitle, (420, 240))

    for btn in BEHAVIOUR_BUTTONS:
        btn.active = True
        btn.draw(window)
        if SELECTED_BEHAVIOUR == btn.name:
            btn.drawOutline(window)

    # Start button only active if both selected
    START_BUTTON.active = (SELECTED_AI is not None and SELECTED_BEHAVIOUR is not None)
    START_BUTTON.draw(window)

    if START_BUTTON.active:
        START_BUTTON.drawOutline(window, (0, 0, 0))

    # Bottom image
    bottom_img = loadImage(
        'assets/images/background/Battleship bottom image.webp',
        (LOGICAL_WIDTH, 300)
    )
    window.blit(bottom_img, (0, LOGICAL_HEIGHT - 300))

def drawStepCounter(window, computer):
    font = pygame.font.SysFont('Stencil', 24)
    text = font.render(f'AI Steps: {computer.steps}', True, (0, 0, 0))
    rect = text.get_rect()

    LEFT_GRID_RIGHT = (ROWS * CELLSIZE)
    RIGHT_GRID_LEFT = LOGICAL_WIDTH - (ROWS * CELLSIZE)
    MID_X = (LEFT_GRID_RIGHT + RIGHT_GRID_LEFT) // 2

    rect.center = (MID_X, 80)   # vertical position tweakable
    window.blit(text, rect)
    

def autoplay_player_attack():
    while True:
        x = random.randint(0, 9)
        y = random.randint(0, 9)
        if cGameLogic[x][y] in (' ', 'O'):
            break

    if cGameLogic[x][y] == 'O':
        cGameLogic[x][y] = 'T'
        TOKENS.append(Tokens(REDTOKEN, cGameGrid[x][y], 'Hit'))
    else:
        cGameLogic[x][y] = 'X'
        TOKENS.append(Tokens(GREENTOKEN, cGameGrid[x][y], 'Miss'))

#  Game Settings and Variables
LOGICAL_WIDTH = 1260
LOGICAL_HEIGHT = 960
ROWS = 10
COLS = 10
CELLSIZE = 50
DEPLOYMENT = True
SCANNER = False
INDNUM = 0
BLIPPOSITION = None
TURNTIMER = pygame.time.get_ticks()
GAMESTATE = 'Main Menu'
AUTOPLAY = False
AI_DELAY = 400  # milliseconds between moves
TURN_PHASE = 'PLAYER'   # PLAYER always starts

#for initial testing
SELECTED_AI = None          # 'BFS', 'DFS', 'LINEAR', 'BINARY'
SELECTED_BEHAVIOUR = None  # '(0,0)', 'RANDOM', 'MIDDLE'


# Variable size for laptop and desktop
info = pygame.display.Info()
WINDOW_WIDTH = int(info.current_w * 0.85)
WINDOW_HEIGHT = int(info.current_h * 0.85)

WINDOW = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT),
    pygame.RESIZABLE
)

# Virtual surface (game logic size)
GAMESCREEN = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

#  Colors


#  Pygame Display Initialization
pygame.display.set_caption('Battle Ship')


#  Game Lists/Dictionaries
FLEET = {
    'battleship': ['battleship', 'assets/images/ships/battleship/battleship.png', (125, 600), (40, 195),
                   4, 'assets/images/ships/battleship/battleshipgun.png', (0.4, 0.125), [-0.525, -0.34, 0.67, 0.49]],
    'cruiser': ['cruiser', 'assets/images/ships/cruiser/cruiser.png', (200, 600), (40, 195),
                2, 'assets/images/ships/cruiser/cruisergun.png', (0.4, 0.125), [-0.36, 0.64]],
    'destroyer': ['destroyer', 'assets/images/ships/destroyer/destroyer.png', (275, 600), (30, 145),
                  2, 'assets/images/ships/destroyer/destroyergun.png', (0.5, 0.15), [-0.52, 0.71]],
    'patrol boat': ['patrol boat', 'assets/images/ships/patrol boat/patrol boat.png', (425, 600), (20, 95),
                    0, '', None, None],
    'submarine': ['submarine', 'assets/images/ships/submarine/submarine.png', (350, 600), (30, 145),
                  1, 'assets/images/ships/submarine/submarinegun.png', (0.25, 0.125), [-0.45]],
    'carrier': ['carrier', 'assets/images/ships/carrier/carrier.png', (50, 600), (45, 245),
                0, '', None, None],
    'rescue ship': ['rescue ship', 'assets/images/ships/rescue ship/rescue ship.png', (500, 600), (20, 95),
                    0, '', None, None]
}
STAGE = ['Main Menu', 'Deployment', 'Game Over']

# Loading Game Variables
pGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (50, 50))
pGameLogic = createGameLogic(ROWS, COLS)
pFleet = createFleet()

cGameGrid = createGameGrid(ROWS, COLS, CELLSIZE, (LOGICAL_WIDTH - (ROWS * CELLSIZE), 50))
cGameLogic = createGameLogic(ROWS, COLS)
cFleet = createFleet()
randomizeShipPositions(cFleet, cGameGrid)


# Loading Game Images
MAINMENUIMAGE = loadImage('assets/images/background/Battleship.jpg', (LOGICAL_WIDTH // 3 * 2, LOGICAL_HEIGHT))
ENDSCREENIMAGE = loadImage('assets/images/background/Carrier.jpg', (LOGICAL_WIDTH, LOGICAL_HEIGHT))
BACKGROUND = loadImage('assets/images/background/gamebg.png', (LOGICAL_WIDTH, LOGICAL_HEIGHT))
PGAMEGRIDIMG = loadImage('assets/images/grids/player_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
CGAMEGRIDIMG = loadImage('assets/images/grids/comp_grid.png', ((ROWS + 1) * CELLSIZE, (COLS + 1) * CELLSIZE))
BUTTONIMAGE = loadImage('assets/images/buttons/button.png', (150, 50))
BUTTONIMAGE1 = loadImage('assets/images/buttons/button.png', (250, 100))
BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (25, 900), 'Randomize'),
    Button(BUTTONIMAGE, (150, 50), (200, 900), 'Reset'),
    Button(BUTTONIMAGE, (150, 50), (375, 900), 'Deploy'),
    Button(BUTTONIMAGE1, (250, 100), (900, LOGICAL_HEIGHT // 2 + 150), 'Start')
]

# --- AI Algorithm Buttons ---
AI_BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (200, 150), 'BFS'),
    Button(BUTTONIMAGE, (150, 50), (380, 150), 'DFS'),
]

# --- AI Behaviour Buttons ---
BEHAVIOUR_BUTTONS = [
    Button(BUTTONIMAGE, (150, 50), (260, 300), 'Random'),
    Button(BUTTONIMAGE, (150, 50), (440, 300), 'Linear Search'),
    Button(BUTTONIMAGE, (150, 50), (620, 300), 'Binary Search')
]

START_BUTTON = Button(BUTTONIMAGE1, (250, 100), (505, 450), 'Start')

LEFT_GRID_RIGHT = (ROWS * CELLSIZE)
RIGHT_GRID_LEFT = LOGICAL_WIDTH - (ROWS * CELLSIZE)
MID_X = (LEFT_GRID_RIGHT + RIGHT_GRID_LEFT) // 2

AUTOPLAY_BUTTON = Button(
    BUTTONIMAGE,
    (150, 50),
    (MID_X - 75, 140),   # center horizontally, below step counter
    'Autoplay'
)


REDTOKEN = loadImage('assets/images/tokens/redtoken.png', (CELLSIZE, CELLSIZE))
GREENTOKEN = loadImage('assets/images/tokens/greentoken.png', (CELLSIZE, CELLSIZE))
BLUETOKEN = loadImage('assets/images/tokens/bluetoken.png', (CELLSIZE, CELLSIZE))
FIRETOKENIMAGELIST = loadAnimationImages('assets/images/tokens/fireloop/fire1_ ', 13, (CELLSIZE, CELLSIZE))
EXPLOSIONSPRITESHEET = pygame.image.load('assets/images/tokens/explosion/explosion.png').convert_alpha()
EXPLOSIONIMAGELIST = []
for row in range(8):
    for col in range(8):
        EXPLOSIONIMAGELIST.append(loadSpriteSheetImages(EXPLOSIONSPRITESHEET, col, row, (CELLSIZE, CELLSIZE), (128, 128)))
TOKENS = []
RADARGRIDIMAGES = loadAnimationImages('assets/images/radar_base/radar_anim', 360, (ROWS * CELLSIZE, COLS * CELLSIZE))
RADARBLIPIMAGES = loadAnimationImages('assets/images/radar_blip/Blip_', 11, (50, 50))
RADARGRID = loadImage('assets/images/grids/grid_faint.png', ((ROWS) * CELLSIZE, (COLS) * CELLSIZE))

# Loading Game Sounds
# HITSOUND = pygame.mixer.Sound('assets/sounds/explosion.wav')
# HITSOUND.set_volume(0.05)
# SHOTSOUND = pygame.mixer.Sound('assets/sounds/gunshot.wav')
# SHOTSOUND.set_volume(0.05)
# MISSSOUND = pygame.mixer.Sound('assets/sounds/splash.wav')
# MISSSOUND.set_volume(0.05)



#  Initialise Players
player1 = Player()
computer = BFSRandom()

#  Main Game Loop
RUNGAME = True
while RUNGAME:


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNGAME = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # AUTOPLAY TOGGLE
                if (AUTOPLAY_BUTTON.active and
                    AUTOPLAY_BUTTON.rect.collidepoint(get_logical_mouse_pos())):

                    AUTOPLAY = not AUTOPLAY
                    TURNTIMER = pygame.time.get_ticks()
                # ================= AI CONFIG SCREEN =================
                if GAMESTATE == 'AI Config':

                    # Select AI algorithm
                    for btn in AI_BUTTONS:
                        if btn.rect.collidepoint(get_logical_mouse_pos()):
                            SELECTED_AI = btn.name

                    # Select AI Behaviour 
                    for btn in BEHAVIOUR_BUTTONS:
                        if btn.rect.collidepoint(get_logical_mouse_pos()):
                            SELECTED_BEHAVIOUR = btn.name

                    # Start game (only if both selected)
                    if START_BUTTON.active and START_BUTTON.rect.collidepoint(get_logical_mouse_pos()):

                        # BFS + Random Selected
                        if SELECTED_AI == 'BFS' and SELECTED_BEHAVIOUR == 'Random':
                            computer = BFSRandom()
                        if SELECTED_AI == 'BFS' and SELECTED_BEHAVIOUR == 'Linear Search':
                            computer = BFSLinearSearch()
                        if SELECTED_AI == 'BFS' and SELECTED_BEHAVIOUR == 'Binary Search':
                            computer = BFSBinarySearch()
                        if SELECTED_AI == 'DFS' and SELECTED_BEHAVIOUR == 'Random':
                            computer = DFSRandom()
                        if SELECTED_AI == 'DFS' and SELECTED_BEHAVIOUR == 'Linear Search':
                            computer = DFSLinearSearch()
                        if SELECTED_AI == 'DFS' and SELECTED_BEHAVIOUR == 'Binary Search':
                            computer = DFSBinarySearch()

                        # Reset game state
                        TOKENS.clear()
                        pGameLogic = createGameLogic(ROWS, COLS)
                        cGameLogic = createGameLogic(ROWS, COLS)
                        updateGameLogic(pGameGrid, pFleet, pGameLogic)
                        updateGameLogic(cGameGrid, cFleet, cGameLogic)

                        DEPLOYMENT = True
                        GAMESTATE = 'Deployment'

                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(get_logical_mouse_pos()):
                            ship.active = True
                            sortFleet(ship, pFleet)
                            ship.selectShipAndMove()

                else:
                    if player1.turn == True:
                        player1.makeAttack(cGameGrid, cGameLogic)
                        if player1.turn == False:
                            TURNTIMER = pygame.time.get_ticks()

                for button in BUTTONS:
                    if button.rect.collidepoint(get_logical_mouse_pos()):
                        if button.name == 'Deploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Redeploy' and button.active == True:
                            status = deploymentPhase(DEPLOYMENT)
                            DEPLOYMENT = status
                        elif button.name == 'Quit' and button.active == True:
                            RUNGAME = False
                        elif button.name == 'Radar Scan' and button.active == True:
                            SCANNER = True
                            INDNUM = 0
                            BLIPPOSITION = pick_random_ship_location(cGameLogic)
                        elif button.name == 'Start' and button.active:
                            GAMESTATE = 'AI Config'
                            if GAMESTATE == 'Game Over':
                                TOKENS.clear()
                                for ship in pFleet:
                                    ship.returnToDefaultPosition()
                                randomizeShipPositions(cFleet, cGameGrid)
                                pGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(pGameGrid, pFleet, pGameLogic)
                                cGameLogic = createGameLogic(ROWS, COLS)
                                updateGameLogic(cGameGrid, cFleet, cGameLogic)
                                status = deploymentPhase(DEPLOYMENT)
                                DEPLOYMENT = status
                            #GAMESTATE = STAGE[1]
                        button.actionOnPress()


            elif event.button == 3:
                if DEPLOYMENT == True:
                    for ship in pFleet:
                        if ship.rect.collidepoint(get_logical_mouse_pos()) and not ship.checkForRotateCollisions(pFleet):
                            ship.rotateShip(True)

    updateGameScreen(GAMESCREEN, GAMESTATE)
    if SCANNER == True:
        INDNUM += 1

    if GAMESTATE == 'Deployment' and DEPLOYMENT != True:
        player1Wins = checkForWinners(cGameLogic)
        computerWins = checkForWinners(pGameLogic)
        if player1Wins == True or computerWins == True:
            GAMESTATE = STAGE[2]



    takeTurns(player1, computer)

pygame.quit()
