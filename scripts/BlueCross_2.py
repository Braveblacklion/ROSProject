#!/usr/bin/env python

import rospy
# To determine with message the motors node / sensors Nodes want
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8

############################# Colors
untiefe = 0  # 0 none
black = 1    # 1   black
blue = 2     # 2   blue
green = 3    # 3   green
yellow = 4   # 4   yellow
red = 5      # 5   red
white = 6    # 6   white
brown = 7    # 7   brown
#####################################

########################## Directions
left = -1
straight = 0
right = 1
#####################################

# Save the data of the sensors to
leftColor = 1
rightColor = 1

# Direction -1 = Left, 0 = Forward, 1 = right
temporaryDirection = 1
savedDirection = Left
kurva = False

# Saved speed
savedSpeed = 0

#Picking up Mode
isPickingUp = False
blueCounter = 0
isFinished = False
ausgerichtet = False
blackCounter = 0


def handle_left_color_sensor(msg):
    global leftColor
    leftColor = msg.data
    rospy.loginfo("Left Color Sensor color: " + str(leftColor))


def handle_right_color_sensor(msg):
    global rightColor
    rightColor = msg.data
    drive()
    rospy.loginfo("Right Color Sensor color: " + str(rightColor))


def drive():
    global temporaryDirection
    global savedSpeed
    global blueCounter
    global isFinished
    global isLeftTurnFalse
    global kurva

    vel_msg = Twist()
    if rightColor == 0 or leftColor == 0:
        return
    if rightColor == blue and leftColor == blue:
        pickUp()
        return
    elif isPickingUp:
        pickUp()
        return
    elif rightColor == black and kurva == False:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = -0.5
        rospy.loginfo("Drive: RIGHT!")
    elif leftColor == black:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = 0.5
        kurva = True
        rospy.loginfo("Drive: LEFT!")
    else:
        vel_msg.linear.x = 0.5
        vel_msg.angular.z = 0
        kurva = False

    # Reset counter
    blueCounter = 0
    isFinished = False
    isLeftTurnFalse = False
    # Publish the message
    pub.publish(vel_msg)


def pickUp():
    global savedDirection
    global blueCounter
    global isFinished
    global leftColor
    global rightColor
    global ausgerichtet
    global isPickingUp
    global left
    global right
    global straight
    global blackCounter
    vel_msg = Twist()
    blueCounter += 1

    if blueCounter >= 2 or isPickingUp == True:
        isPickingUp = True
        blueCounter = 0
    else:
        isPickingUp = False
        return

    # if rightTouchedBlue and leftTouchedBlue:
    if not ausgerichtet:
        if rightColor == untiefe and leftColor == untiefe:
            isPickingUp = False
            ausgerichtet = False
            return

        if rightColor == blue and leftColor == blue:
            # Dive a bit backward
            vel_msg.linear.x = -0.1
            vel_msg.angular.z = 0.0
        elif (rightColor == white or rightColor == yellow) and (leftColor == white or leftColor == yellow):
            # Drive right/left
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.5
            for x in xrange(30):
                pub.publish(vel_msg)
            savedDirection = left
            ausgerichtet = True
            rospy.sleep(2)
            return
        #1. richtung anerkannt, wie geht es weiter? gas gradeaus! mit black check
        elif rightColor == blue and (leftColor == white or leftColor == yellow) :
            # Turn right
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = -0.2 # anpassen, nach richtung robot, derzeitig laut pol
        elif leftColor == blue and (rightColor == white or rightColor == yellow):
            # Turn left
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.2
        elif rightColor == black or leftColor == black:
            # Seems to entered this mode wrongly
            ausgerichtet = False
            isPickingUp = False
            drive()
        else:
            rospy.loginfo("Right color: " + str(rightColor) + "and Left Color: " + str(leftColor))
            return
        pub.publish(vel_msg)
        return

    #ausgerichtet ist ok, -|- robot unter blaues kreuz nun gas, wenn error, dann spass


    if savedDirection == left and not (leftColor == black or rightColor == black):
        # Search left
        vel_msg.linear.x = 0.4
        vel_msg.angular.z = 0.0
        blackCounter +=1
        if blackCounter > 80:
            savedDirection = right  # Save direction = left
                             # spaeter: reboot robot to start (rückwärts fahren)
    elif savedDirection == right and not (leftColor == black or rightColor == black):
        # Turn right
        if blackCounter > 0:
            vel_msg.linear.x = -0.4
            vel_msg.angular.z = 0.0
            blackCounter -=1
        elif blackCounter == 0:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = -0.5 #dreh in die andere richtung
            for x in xrange(60):
                pub.publish(vel_msg)
        elif blackCounter == 0:
            vel_msg.linear.x = 0.4
            vel_msg.angular.z = 0.0
    elif rightColor == black or leftColor == black:
        rospy.loginfo("Saved direction = " + str(savedDirection))
        ausgerichtet = False
        isPickingUp = False
        isFinished = True
        # Reset counter
        blueCounter = 0
        return
    else:
        rospy.loginfo("Oooooops In else: " + "Right color: " + str(rightColor) + "and Left Color: " + str(leftColor))
        # Wrong direction go back and try again

    # Publish the message
    pub.publish(vel_msg)


if __name__ == "__main__":
    global queue_size_int
    rospy.init_node("robot_controller")
    rospy.loginfo("Robot Controller Server node created")

    pub = rospy.Publisher("/groot/diffDrv/cmd_vel", Twist, queue_size=10)

    leftColorSensor = rospy.Subscriber("/groot/color_left", UInt8, handle_left_color_sensor, queue_size=10)
    rightColorSensor = rospy.Subscriber("/groot/color_right", UInt8, handle_right_color_sensor, queue_size=10)

    # touchSensor = rospy.Service("/groot/touch", ColorRGBA, handle_right_color_sensor)

    # Edit
    # infraRedSensor = rospy.Service("/ir...", ColorRGBA, handle_right_color_sensor)

    rospy.loginfo("Subscribers has been started")

    rospy.spin()
