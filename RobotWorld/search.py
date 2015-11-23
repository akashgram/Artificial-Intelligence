#Akash Ram Gopal
#agopal@indiana.edu

#tested this on silo without the visualization part as it was throwing me an error with it.
import time
from heapq import *
import functools
import copy
import math
import random
import matplotlib.pyplot as plt
import os.path
import subprocess
import numpy as np
from matplotlib import colors
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import distance

infinity = float("inf")
#global variables required for my tweak
taken = False
completed = False
counter = 0
bestAstar = False

class RobotWorld:
    "The idea is that a RobotWorld is the datatype that goes in the queue."
    def __init__(self,width,length,height,initial,goal,name):
        self.hand = {'location' : (0,0,0), 'held' : None, 'closed?' : False}
        self.width, self.length, self.height = width, length, height
        self.blocks, self.goal = initial, goal
        self.n = name
        #tweaked my code a little since dfs and bfs are similar, whereas bestfirst and A* are similar
        if self.n == 'easy':
            self.go = initial
        else:
            self.go = {}
        self.cost, self.title = 0, ''
        assert(initial.keys() == goal.keys()) #there can't be blocks without a goal state, or goal states with a block that is not initialized.
        self.colormap, possible_colors = {}, set(colors.cnames.keys()) #for the sake of the visualization, not important to the function of RobotWorlds.
        for blockname in self.blocks:
            self.colormap[blockname] = possible_colors.pop()

    def __lt__(self,other):
        "Not meaningful, but necessary for RobotWorld to interact with a heapq"
        return True

    # The actions return the change in cost
    def moveUp(self):
        (x,y,z) = self.hand['location']
        if z < (self.height - 1):
            self.hand['location'] = (x,y,z+1)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y,z+1)
            self.cost += 1.0
            return 1.0

        else:
            print("Why is the 'moveUp' action occuring? The hand is as far up as it can go.")
            return 0

    def moveDown(self):
        (x,y,z) = self.hand['location']
        if z > 0:
            self.hand['location'] = (x,y,z-1)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y,z-1)
            self.cost += 1.0
            return 1.0

        else:
            print("Why is the 'moveDown' action occuring? The hand is on the floor.")
            return 0

    def moveLeft(self):
        (x,y,z) = self.hand['location']
        if y > 0:
            self.hand['location'] = (x,y-1,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y-1,z)
            self.cost += 1.0
            return 1.0

        else:
            print("Why is the 'moveLeft' action occuring? The hand is on the left edge.")
            return 0

    def moveRight(self):
        (x,y,z) = self.hand['location']
        if y < (self.length - 1):
            self.hand['location'] = (x,y+1,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x,y+1,z)
            self.cost += 1.0
            return 1.0

        else:
            print("Why is the 'moveRight' action occuring? The hand is on the right edge.")
            return 0

    def moveForward(self):
        (x,y,z) = self.hand['location']
        if x < (self.width - 1):
            self.hand['location'] = (x+1,y,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x+1,y,z)
            self.cost += 1
            return 1.0

        else:
            print("Why is the 'moveForward' action occuring? The hand is on the front edge.")
            return 0

    def moveBackward(self):
        (x,y,z) = self.hand['location']
        if x > 0:
            self.hand['location'] = (x-1,y,z)
            if self.hand['held']: self.blocks[self.hand['held']] = (x-1,y,z)
            self.cost += 1
            return 1.0
        else:
            print("Why is the 'moveBackward' action occuring? The hand is on the back edge.")
            return 0

    # the reason for the handOpen and handClose actions to have non-zero costs is to prevent the search from considering the "I'll close my hand on this block" and "I'll open and close my hand on this block 20 million times" as equivalent.
    def handOpen(self):
        if not self.hand['closed?']:
            print("Why is the 'handOpen' action occuring? The hand is already open.")
            return 0
        self.hand['closed?'] = False
        if self.hand['held']:
            self.hand['held'] = None
            self.cost += 0.1
            return 0.1

    def handClose(self):
        if self.hand['closed?']:
            print("Why is the 'handClose' action occuring? The hand is already closed.")
            return 0
        else:
            for (name,location) in self.blocks.iteritems():
                if location == self.hand['location']:
                    self.hand['held'] = name
                    self.hand['closed?'] = True
                    self.cost += 0.1
                    return 0.1
            print("Why did the 'handClose' action occur? There is no block here at {}".format(str(self.hand['location'])))
            return 0

    def isGoal(self):
        global bestAstar
        if bestAstar:
            return self.go == self.goal
        else:
            return self.blocks == self.goal

    def allowedActions(self):
        def alreadyThere(coord):
            for (block_name, block_coord) in self.blocks.iteritems():
                if (block_coord == coord) and (block_coord == self.goal[block_name]):
                    return True
            return False
        possibilities = ['close','forward','backward','left','right','up','down']

        if self.hand['closed?'] and alreadyThere(self.hand['location']): #try to open first if its a good idea
            possibilities = ['open'] + possibilities
        # Removing the close action if 'alreadyThere' is True could lead to problems in a 3D world, or even rare scenarios in a 2D world.
        # This is not relevant to the worlds here, but this should be removed if we re-use this for planning.
        if self.hand['closed?'] or (self.hand['location'] not in self.blocks.values()) or (alreadyThere(self.hand['location'])):
            possibilities.remove('close')
        (x,y,z) = self.hand['location']
        if x == 0: possibilities.remove('backward')
        if x == (self.length - 1): possibilities.remove('forward')
        if y == 0: possibilities.remove('left')
        if y == (self.width - 1): possibilities.remove('right')
        if z == 0: possibilities.remove('down')
        if z == (self.height - 1): possibilities.remove('up')
        if self.hand['closed?'] and ('open' not in possibilities): #try to put 'open' at the end, so moving around happens before
            possibilities = possibilities + ['open']               #pointless opening and closing.
        return possibilities

    def do(self,action):
        '''action is a string indicating an action for the RobotWorld to do. These strings come from the 'allowedActions' method, and are part of the process of
           iterating over neighboring nodes in the graph.'''
        if (action == 'up'): return self.moveUp()
        elif (action == 'down'): return self.moveDown()
        elif (action == 'left'): return self.moveLeft()
        elif (action == 'right'): return self.moveRight()
        elif (action == 'forward'): return self.moveForward()
        elif (action == 'backward'): return self.moveBackward()
        elif (action == 'open'): return self.handOpen()
        elif (action == 'close'): return self.handClose()
        else: print("Unexpected action {}".format(action))

    def visualize(self,serial_number):
        '''The blocks are colored according to their identity (exactly one color per block). These are persistent over time, so a block with a certain name in one frame of the animation will have the same color in all other frames.
           The triangles of the same color as a block indicate where the block's goal location is.
           The title 'cost=<number>' at the top indicates the cumulative cost of actions so far to bring the RobotWorld into its current state.
           The cross indicates the location of the robot hand.
        '''
        fig = plt.figure()
        axis = fig.add_subplot(111,projection='3d')
        axis.set_xlim(0, self.width)
        axis.set_ylim(0, self.length)
        axis.set_zlim(0, self.height)
        axis.set_xlabel('X Axis')
        axis.set_ylabel('Y Axis')
        axis.set_zlabel('Z Axis')
        n = len(self.blocks)

        for block in self.blocks.iteritems():
            blockname, coord = block
            axis.scatter(coord[0], coord[1], coord[2], s=500, marker=(4,0), c=self.colormap[blockname])
            target = self.goal[blockname]
            axis.scatter(target[0], target[1], target[2], s=300, marker=(3,0), c=self.colormap[blockname])

        robo_x, robo_y, robo_z = self.hand['location']
        axis.scatter(robo_x,robo_y,robo_z,s=500,marker='+', c='black')
        axis.set_title("cost={}".format(str(self.cost)))
        plt.savefig("snapshots/{}_{}.png".format(self.title,str(serial_number)))
        plt.close()

def graphsearch(queue,queue_modification,timeout,visualize=False):
    "The things that I can think to say about graphsearch are mentioned in the directions on the website. If you have questions, email me at aseewald@indiana.edu"
    t0 = time.time()
    visited, history = [], []
    solution_info = {'cost' : infinity, 'num_expanded' : infinity, 'walltime' : infinity}
    while len(queue) > 0:
        if timeout == 0:
            print("Ran out of time for thinking")
            print("The queue is of size: {}".format(len(queue)))
            return solution_info
        queue, expanded = queue_modification(queue,visited)
        visited.append(expanded)
        if expanded.isGoal():
            tf = time.time()
            history.append(expanded)
            solution_info['cost'] = expanded.cost
            solution_info['num_expanded'] = len(history)
            solution_info['walltime'] = tf - t0
            print("The solution's cost is: {}, and involved expanding {} verticies".format(str(expanded.cost), str(len(history))))
            print("Finding the solution involved {} seconds of walltime".format(str(tf - t0)))
            print("----------------------------------------------------------------------------------")
            if visualize:
                for (i, world) in enumerate(history):
                    world.visualize(i)
            return solution_info
        else:
            timeout -= 1
            history.append(expanded)
    print("No possible actions left. And you may ask yourself, well, how did I get here? You may tell yourself, this is not my beautiful search algorithm.")
    return solution_info

def duplicateWorld(world,worlds):
    "You may want to test if a world is in some visited set. This function is needed to define a more loose idea of equality, so that worlds with different accumulated costs are considered equivalent."
    for w in worlds:
        if (w.hand == world.hand) and (w.blocks == world.blocks):
            return True
    return False

def dummyExample():
    "Shows the mechanics of a RobotWorld's 'do', and 'allowedActions' methods, as well as how to use a queue."
    easy = RobotWorld(5,5,1,{'A' : (1,0,0), 'B' : (3,1,0)}, {'A' : (1,1,0), 'B' : (3,1,0)})
    if easy.isGoal():
        print("You've found the solution")
    queue = []
    heappush(queue, (0, easy)) #this is a minqueue where '0' is the key.

    for action in easy.allowedActions():
        neighbor = copy.deepcopy(easy)
        deltaCost = neighbor.do(action)

def breadthFirst(queue,visited):
    curr = heappop(queue)
    #to check if the node to be expanded is already visited or not!
    loop = True
    while loop:
        loop = False
        for i in range(0,len(visited)):
            if(curr[1].hand == visited[i].hand) and len(queue) > 0:
                curr = heappop(queue)
                loop = True
                break
    for action in curr[1].allowedActions():
        neighbor = copy.deepcopy(curr[1])
        deltaCost = neighbor.do(action)
        #Since BFS should not backtrack, therefore I am eliminating the actions to backtrack
        if(action != "backward" and action !="left"):
            if duplicateWorld(neighbor,visited) == False:
                heappush(queue,(len(queue),neighbor)) #using length of queue as key to queue 
    return queue,curr[1]

def depthFirst(queue,visited):
    curr = heappop(queue)
    loop = True
    #to check if the node to be expanded is already visited or not!
    while loop:
        loop = False
        for i in range(0,len(visited)):
            if(curr[1].hand == visited[i].hand) and len(queue) > 0:
                curr = heappop(queue)
                loop = True
                break
    level = 0
    for action in curr[1].allowedActions():
        neighbor = copy.deepcopy(curr[1])
        deltaCost = neighbor.do(action)
        if duplicateWorld(neighbor,visited) == False:
            heappush(queue,(level + 1,neighbor)) #using level as to key to queue
    return queue,curr[1]    

def bestFirst(queue,visited,heuristic):
    global taken, completed, counter, bestAstar
    name = []
    bestAstar = True
    curr = heappop(queue)
    name.append(curr[1].goal.keys())
    # my own implementaton where I am inserting all the nodes to be expanded into an array
    # and then finding the minimum key in the array.
    # After finding the minimum, I insert this node into the queue so that it can be expanded next
    # Counter is a variable which keeps changing the goal state as we start from initial of A and 
    # then change to goal state of A, then change it to initial of B block and so on
    if curr[1].hand['location'] == curr[1].goal[name[0][counter]] and curr[1].hand['closed?'] == False:
        a = name[0][counter]
        curr[1].go[a] = curr[1].blocks[name[0][counter]]
        curr[1].blocks[name[0][counter]] = []
        counter = counter + 1
        del visited[:]

    if len(name[0]) > counter:
        arr =[]
        for action in curr[1].allowedActions():
            neighbor = copy.deepcopy(curr[1])
            deltaCost = neighbor.do(action)
            arr.append(neighbor)

            if taken == False:
                if neighbor.hand['closed?'] == True:
                    while len(queue):
                        heappop(queue)
                    del arr[:]
                    for action_goal in neighbor.allowedActions():
                        neighbor_goal = copy.deepcopy(neighbor)
                        deltaCost = neighbor_goal.do(action_goal)
                        if neighbor_goal.hand['held'] != None:
                            arr.append(neighbor_goal)
                    taken = True
                    break
        min = 1000
        arr_len = len(arr)
        for i in range (arr_len):
            if curr[1].hand['held'] == None and arr[i].hand['held'] != None:
                min = 0
                node = arr[i]
            if curr[1].hand['held'] != None and arr[i].hand['held'] == None and curr[1].goal[name[0][counter]] != arr[i].hand['location']:
                pass
            else:
                if duplicateWorld(arr[i],visited) == False:
                    if arr[i].hand['held'] != None:
                        #
                        temp = heuristic(arr[i].hand['location'],arr[i].goal[name[0][counter]])
                    else:
                        temp = heuristic(arr[i].hand['location'],arr[i].blocks[name[0][counter]])
                    if temp <= min:
                        min = temp
                        node = arr[i]
                else:
                    pass
        heappush(queue,(min,node))

    return queue,curr[1]

def aStar(queue,visited,heuristic):
    global taken, completed, counter,bestAstar
    completed = False
    name = []
    bestAstar = True
    curr = heappop(queue)
    if curr[1].n == 'easy':
        taken = False
    name.append(curr[1].goal.keys())

    if curr[1].hand['location'] == curr[1].goal[name[0][counter]] and curr[1].hand['closed?'] == False:
        a = name[0][counter]
        curr[1].go[a] = curr[1].blocks[name[0][counter]]
        curr[1].blocks[name[0][counter]] = []
        counter = counter + 1
        del visited[:]

    if len(name[0]) > counter:
        arr =[]
        for action in curr[1].allowedActions():
            neighbor = copy.deepcopy(curr[1])
            deltaCost = neighbor.do(action)
            arr.append(neighbor)

            if taken == False:
                if neighbor.hand['closed?'] == True:
                    while len(queue):
                        heappop(queue)
                    del arr[:]
                    for action_goal in neighbor.allowedActions():
                        neighbor_goal = copy.deepcopy(neighbor)
                        deltaCost = neighbor_goal.do(action_goal)
                        if neighbor_goal.hand['held'] != None:
                            arr.append(neighbor_goal)
                    taken = True
                    break
        min = 1000
        arr_len = len(arr)
        for i in range (arr_len):
            if curr[1].hand['held'] == None and arr[i].hand['held'] != None:
                min = 0
                node = arr[i]
            if curr[1].hand['held'] != None and arr[i].hand['held'] == None and curr[1].goal[name[0][counter]] != arr[i].hand['location']:
                pass
            else:
                if duplicateWorld(arr[i],visited) == False:
                    if arr[i].hand['held'] != None:
                        #same as best first, except that for finding the minimum key, we add the cost for A*
                        temp = deltaCost + heuristic(arr[i].hand['location'],arr[i].goal[name[0][counter]])
                    else:
                        temp = deltaCost + heuristic(arr[i].hand['location'],arr[i].blocks[name[0][counter]])
                    if temp <= min:
                        min = temp
                        node = arr[i]
                else:
                    pass
        heappush(queue,(min,node))

    return queue,curr[1]

def run(world,title,heuristics,timeout=5000):
    global counter
    solutions = []
    queue = []
    world0 = copy.deepcopy(world)
    world0.title=(title + '_DFS')
    heappush(queue,(0,world0))
    print("Doing Depth First Search  on {}:".format(title))
    solutions.append(graphsearch(queue, depthFirst, timeout))

    queue = []
    world1 = copy.deepcopy(world)
    world1.title=(title + '_bestAstar')
    heappush(queue,(0,world1))
    print("Doing Breadth First Search on {}:".format(title))
    solutions.append(graphsearch(queue, breadthFirst, timeout))

    for h in heuristics:
        queue, hname = [], str(h).split(' ')[1]
        world4 = copy.deepcopy(world)
        world4.title=(title + hname + '_Astar')
        heappush(queue,(0,world4))
        aStar_h = functools.partial(aStar,heuristic=h)
        print("Doing A* with heuristic {} on {}:".format(hname,title))
        counter = 0
        solutions.append(graphsearch(queue, aStar_h, timeout))
        taken = False

        
        queue = []
        world2 = copy.deepcopy(world)
        world2.title=(title + hname + '_BestFirst')
        heappush(queue,(0,world2))
        bestFirst_h = functools.partial(bestFirst,heuristic=h)
        print("Doing Best First with heuristic {} on {}:".format(hname,title))
        counter = 0
        solutions.append(graphsearch(queue, bestFirst_h, timeout))
        taken = False
        
    return solutions

def experiment(heuristics,described_worlds):
    data =[]
    for (world,title) in described_worlds:
        global taken, counter
        data.append(run(world,title,heuristics,timeout=10000))
        taken = False
        counter = 0
    fig, axes = plt.subplots(nrows=len(described_worlds))
    fig.set_size_inches(20,30)

    if len(described_worlds) == 1: # a hack to get consistent indexing behavoir from matplotlib.
        axes = [axes]
    color_codes = random.sample(colors.cnames.keys(), len(described_worlds) * (2 + 2 * len(heuristics)))
    labels = ['DFS','bestAstar']

    for heuristic in heuristics:
        hname = str(heuristic).split(' ')[1]
        labels.append('Best_' + hname)
        labels.append('A*_' + hname)
    # set the legend of the figure to correspond to colors.
    for (i, solutions) in enumerate(data): #2 because discard breadthFirst and depthFirst b/c no heuristic.
        axes[i].set_title(described_worlds[i][1])
        axes[i].set_xlabel("verticies expanded")
        axes[i].set_ylabel("cost of solution")
        for (j, solution) in enumerate(solutions):
           print("{} is {}".format(labels[j], color_codes[j]))
           if solution['cost'] == infinity:
               pass
           else:
               axes[i].scatter(solution['num_expanded'],solution['cost'], color=color_codes[j], label=labels[j])
    plt.savefig("experiment.png")
    plt.close()

if not os.path.exists("snapshots"):
    if subprocess.call(["mkdir","snapshots"]) != 0:
        print("Failed to make a directory to store images in.")

def heuristics1(initial,final): #Euclidean Distance
    return distance.euclidean(initial,final)

def heuristics2(initial,final): #Manhattan Distance
    yaxis = abs((initial[0] - final[0]))
    xaxis = abs((initial[1] - final[1]))
    diff =  yaxis + xaxis
    return diff

hs = {heuristics1,heuristics2} #this is a set, put your heuristic functions in here.
#presolved = RobotWorld(4,4,1,{'A' : (3,3,0), 'B' : (3,1,0)}, {'A' : (3,3,0), 'B' : (3,1,0)},'easy')
easy = RobotWorld(5,5,1,{'A' : (1,0,0), 'B' : (3,1,0)}, {'A' : (1,1,0), 'B' : (3,1,0)},'easy')

medium = RobotWorld(6,6,1,{'A' : (1,1,0), 'B' : (3,1,0)}, {'A' : (4,4,0), 'B' : (4,5,0)},'medium')

hard = RobotWorld(10,10,1,{'A' : (1,0,0), 'B' : (9,9,0), 'C' : (4,4,0)}, {'A' : (4,4,0), 'B' : (1,0,0), 'C' : (9,9,0)},'hard')
#experiment(hs, [(easy, 'easy')])
#experiment(hs, [(presolved, 'ps')])
experiment(hs,[(easy, 'easy'), (medium,'medium'), (hard, 'hard')])
#experiment(hs, [(medium,'medium')])