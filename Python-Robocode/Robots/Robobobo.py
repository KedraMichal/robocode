# ! /usr/bin/python
# -*- coding: utf-8 -*-

from robot import Robot  # Import a base Robot
from collections import defaultdict
import numpy as np
import pickle
import os



class Robobobo(Robot):  # Create a Robot

    def init(self):  # NECESARY FOR THE GAME   To initialyse your robot

        # Set the bot color in RGB
        self.setColor(5, 5, 5)
        self.setGunColor(11, 11, 1)
        self.setRadarColor(23, 23, 23)
        self.setBulletsColor(0, 200, 100)

        # get the map size
        size = self.getMapSize()  # get the map size
        self.radarVisible(True)  # show the radarField
        self.epsilon = 0.8  # experiment rate
        self.alpha = 0.15  # learning rate
        self.gamma = 0.8  # discount factor
        self.q = defaultdict(lambda: 0)  # quality
        self.rewards = []
        self.possible_actions_id = [1, 2, 3, 4, 5, 6]
        # possible_actions = [self.move(40), self.turn(40), self.fire(3), self.radarTurn(40), self.gunTurn(40), self.move(-40)]

        self.bullet_hit = False
        self.hit_wall = False
        self.hit_by_robot =  False
        self.hit_robot = False
        self.hit_by_bullet = False
        self.bullet_miss = False
        self.target_spotted = 0
        self.observation = []

    def run(self):  # NECESARY FOR THE GAME  main loop to command the bot
        if os.path.exists('knowledge.txt'):
            with open(f'knowledge.txt', 'r', encoding='utf-8') as file:
                d_dict = defaultdict(lambda: 0)
                for item in file.readlines():
                    items = item.rstrip('\n').split(') ')
                    key = eval(items[0] + ')')
                    values = float(items[1])
                    d_dict[key] = values
                self.q = d_dict

        if not self.observation:
            angle_gun, angle_facing, angle_radar, position = self.sensors()
            x_pos, y_pos = self.buckets_position(position)
            angle_gun_b, angle_facing_b, angle_radar_b = self.buckets_angle(angle_gun), self.buckets_angle(
                angle_facing), self.buckets_angle(angle_radar)
            observation = (x_pos, y_pos, angle_gun_b, angle_facing_b, angle_radar_b, self.target_spotted)
            self.target_spotted = 0
        else:
            observation = self.observation

        action_id = self.pick_action_id(observation)

        if action_id == 1:
            self.move(40)
        elif action_id == 2:
            self.turn(40)
        elif action_id == 3:
            self.fire(3)
        elif action_id == 4:
            self.radarTurn(40)
        elif action_id == 5:
            self.gunTurn(40)
        elif action_id == 6:
            self.move(-40)

        reward = 0
        if self.bullet_hit:
            reward += 2
            self.bullet_hit = False
        if self.hit_wall:
            reward -= 2
            self.hit_wall = False
        if self.hit_by_robot:
            reward -= 2
            self.hit_by_robot = False
        if self.hit_robot:
            reward += 2
            self.hit_robot = False
        if self.hit_by_bullet:
            reward -= 2
            self.hit_by_bullet = False
        if self.bullet_miss:
            reward += 2
            self.bullet_miss = False

        angle_gun, angle_facing, angle_radar, position = self.sensors()
        x_pos, y_pos = self.buckets_position(position)
        angle_gun_b, angle_facing_b, angle_radar_b = self.buckets_angle(angle_gun), self.buckets_angle(
            angle_facing), self.buckets_angle(angle_radar)
        new_observation = (x_pos, y_pos, angle_gun_b, angle_facing_b, angle_radar_b, self.target_spotted)
        self.target_spotted = 0
        self.update_knowledge(action_id, observation, new_observation, reward)
        self.observation = new_observation

        with open('knowledge.txt', 'w', encoding='utf-8') as file:
            for k, v in self.q.items():
                file.write(f'{k} {v}\n')

    def sensors(self):  # NECESARY FOR THE GAME
        """Tick each frame to have datas about the game"""

        pos = self.getPosition()  # return the center of the bot
        x = pos.x()  # get the x coordinate
        y = pos.y()  # get the y coordinate

        angle_gun = self.getGunHeading()  # Returns the direction that the robot's gun is facing
        angle_facing = self.getHeading()  # Returns the direction that the robot is facing
        angle_radar = self.getRadarHeading()  # Returns the direction that the robot's radar is facing
        # list = self.getEnemiesLeft()  # return a list of the enemies alive in the battle
        # for robot in list:
        #     id = robot["id"]
        #     name = robot["name"]

        # each element of the list is a dictionnary with the bot's id and the bot's name
        return angle_gun, angle_facing, angle_radar, pos


    def onHitByRobot(self, robotId, robotName):
        self.rPrint("damn a bot collided me!")
        self.hit_by_robot = True

    def onHitWall(self):
        self.reset()  # To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        # self.pause(100)
        # self.move(-100)
        self.rPrint('ouch! a wall !')
        #self.setRadarField("large")  # Change the radar field form
        self.hit_wall = True

    def onRobotHit(self, robotId, robotName):  # when My bot hit another
        self.rPrint('collision with:' + str(
            robotName))  # Print information in the robotMenu (click on the righ panel to see it)
        self.hit_robot = True

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):  # NECESARY FOR THE GAME
        """ When i'm hit by a bullet"""
        self.reset()  # To reset the run fonction to the begining (auomatically called on hitWall, and robotHit event)
        self.rPrint("hit by " + str(bulletBotName) + "with power:" + str(bulletPower))
        self.hit_by_bullet = True

    def onBulletHit(self, botId, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a bot"""
        self.rPrint("fire done on " + str(botId))
        self.bullet_hit = True

    def onBulletMiss(self, bulletId):  # NECESARY FOR THE GAME
        """when my bullet hit a wall"""
        self.rPrint("the bullet " + str(bulletId) + " fail")
        self.pause(10)  # wait 10 frames
        self.bullet_miss = True

    def onRobotDeath(self):  # NECESARY FOR THE GAME
        """When my bot die"""
        self.rPrint("damn I'm Dead")
        print('xd')

    def onTargetSpotted(self, botId, botName, botPos):  # NECESARY FOR THE GAME
        "when the bot see another one"
        self.target_spotted = 1
        self.rPrint("I see the bot:" + str(botId) + "on position: x:" + str(botPos.x()) + " , y:" + str(botPos.y()))

    def buckets_angle(self, angel):
        bucket_number = 0
        for angle_value in range(60, 360, 60):
            if angel < angle_value:
                return bucket_number
            else:
                bucket_number += 1
        return bucket_number

    def buckets_position(self, position):
        map_x, map_y = self.getMapSize().width(), self.getMapSize().height()
        n_buckets = 3
        x_number, y_number = 0, 0
        for i in range(n_buckets):
            if position.x() > (map_x * ((i + 1) / n_buckets)):
                x_number += 1
            if position.y() > (map_y * ((i + 1) / n_buckets)):
                y_number += 1

        return x_number, y_number




    def pick_action_id(self, observation):
        if np.random.random() > self.epsilon:
            action_values = []
            for action in self.possible_actions_id:
                max_q = self.q[(observation, action)]
                action_values.append(max_q)
            id_best = np.argmax(action_values)
            picked_action = self.possible_actions_id[id_best]
        else:
            return np.random.choice(self.possible_actions_id)

        return picked_action

    def update_knowledge(self, action, observation, new_observation, reward):
        possible_actions_id = [1, 2, 3, 4, 5]
        q_values = []
        for action_id in possible_actions_id:
            q_values.append(self.q[(new_observation, action_id)])

        learned_value = reward + self.gamma * max(q_values)
        self.q[(observation, action)] = (1 - self.alpha) * self.q[(observation, action)] + self.alpha * learned_value