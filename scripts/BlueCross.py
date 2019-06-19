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
savedDirection = 0

# Saved speed
savedSpeed = 0

#Picking up Mode
isPickingUp = False
blueCounter = 0
isFinished = False
ausgerichtet = False


def handle_left_color_sensor(msg):
    global leftColor
    leftColor = msg.data
    rospy.loginfo("Left Color Sensor color: " + leftColor)


def handle_right_color_sensor(msg):
    global rightColor
    rightColor = msg.data
    rospy.loginfo("Left Color Sensor color: " + rightColor)
    drive()


def drive():
    global savedDirection
    global savedSpeed
    global blueCounter
    global isFinished
    global isLeftTurnFalse

    vel_msg = Twist()
    if rightColor == blue and leftColor == blue:
        pickUp()
        return
    elif isPickingUp:
        pickUp()
        return
    elif rightColor == black and leftColor == black:
        # Abgrund? --> STOP
        vel_msg.linear.x = savedSpeed
        vel_msg.angular.z = savedDirection
        rospy.loginfo("Drive: STOP!")
    elif rightColor == black:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = -0.5

        savedSpeed = 0.1
        savedDirection = -0.5
        rospy.loginfo("Drive: RIGHT!")
    elif leftColor == black:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = 0.5

        savedSpeed = 0.1
        savedDirection = 0.5
        rospy.loginfo("Drive: LEFT!")
    else:
        vel_msg.linear.x = 0.5
        vel_msg.angular.z = 0

        savedSpeed = 0.5
        savedDirection = 0

    # Reset counter
    blueCounter = 0
    isFinished = False
    isLeftTurnFalse = False
    savedDirection = -1
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

    blueCounter += 1

    # To be sure that the robot realy is on blue not just an error
    if blueCounter >= 3:
        isPickingUp = True
    else:
        return

    vel_msg = Twist()
    if isFinished:
        rospy.loginfo("Finished!!!")
        isPickingUp = False
        return
    # if rightTouchedBlue and leftTouchedBlue:
    if not ausgerichtet:
        if rightColor == blue and leftColor == blue:
            # Dive a bit forward
            vel_msg.linear.x = 0.1
            vel_msg.angular.z = 0.0
        elif rightColor == white and leftColor == white:
            vel_msg.linear.x = -0.5
            vel_msg.angular.z = 0.0
            for x in xrange(3):
                pub.publish(vel_msg)
            savedDirection = left
            ausgerichtet = True
            return
        elif rightColor == blue and leftColor == white:
            # Turn right
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = -0.2
        elif leftColor == blue and rightColor == white:
            # Turn left
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.2
        elif rightColor == black or leftColor == black:
            # Seems to entered this mode wrongly
            ausgerichtet = False
            isPickingUp = False
        else:
            rospy.loginfo("Right color: " + str(rightColor) + "and Left Color: " + str(leftColor))
            return
        pub.publish(vel_msg)
        return

    if savedDirection == 0:
        # If savedDirection not set
        savedDirection = left

    if savedDirection == left and not leftColor == black and rightColor == blue:
        # Search left
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0.5
        savedDirection = -1  # Save direction = left
    elif savedDirection == right and not rightColor == black and leftColor == blue:
        # Turn right
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = -0.5
    elif rightColor == black or leftColor == black:
        rospy.loginfo("Saved direction = " + str(savedDirection))
        ausgerichtet = False
        isPickingUp = False
        isFinished = True
        # Reset counter
        blueCounter = 0
        return
    elif leftColor == white :
        # Nothing found so Turn right now
        savedDirection = right
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = -0.5
    else:
        # Search right
        rospy.loginfo("Oooooops In else")
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
