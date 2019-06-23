#!/usr/bin/env python

import rospy
# To determine with message the motors node / sensors Nodes want
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8
from std_msgs.msg import Float64
from std_msgs.msg import Bool

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

##################### Claw Params
clawclose = 4
clawopen = -4
isclawopened = True
#################################

# Direction -1 = Left, 0 = Forward, 1 = right
# changed som variables
temporaryDirection = 1
savedDirection = left
saveDriveback = True

# Saved speed
savedSpeed = 0
openCloseCounter = 0

isTouching = False
turningCounter = 0



def handle_left_color_sensor(msg):
    global leftColor
    leftColor = msg.data
    rospy.loginfo("Left Color Sensor color: " + str(leftColor))


def handle_right_color_sensor(msg):
    global rightColor
    rightColor = msg.data
    rospy.loginfo("Right Color Sensor color: " + str(rightColor))
    open()
    close()
    #drive()

def handle_touch(msg):
    global isTouching
    if msg.data:
        isTouching = msg.data
        rospy.loginfo("Touched!!!!")
        #drive()
    rospy.loginfo("isTouching: " + str(isTouching))


def drive():
    global temporaryDirection
    global savedSpeed
    global blueCounter
    global isFinished
    global isLeftTurnFalse
    global savedDirection
    global isTouching

    vel_msg = Twist()
    if isTouching:
        closeAndTurn()
        return
    if rightColor == 0 or leftColor == 0:
        return
    if rightColor == blue and leftColor == blue:
        #open()
        return
    elif rightColor == black and leftColor == black:
        # Abgrund? --> STOP
        vel_msg.linear.x = savedSpeed
        vel_msg.angular.z = temporaryDirection
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
    # Publish the message
    pub.publish(vel_msg)


def open():
    global openCloseCounter
    global isclawopened
    global clawopen

    if not isclawopened:
        openCloseCounter += 1
        if openCloseCounter <= 12:
            msg = Float64()
            msg.data = clawopen
            servoPublisher.publish(msg)
            rospy.loginfo("Counter: " + str(openCloseCounter))
        else:
            openCloseCounter = 0
            msg = Float64()
            msg.data = 0.0
            servoPublisher.publish(msg)
            isclawopened = True


def close():
    global isclawopened
    global openCloseCounter
    global clawclose


    if isclawopened:
        openCloseCounter += 1
        if openCloseCounter <= 12:
            msg = Float64()
            msg.data = clawclose
            servoPublisher.publish(msg)
            rospy.loginfo("Counter: " + str(openCloseCounter))
        else:
            openCloseCounter = 0
            msg = Float64()
            msg.data = 0.0
            servoPublisher.publish(msg)
            isclawopened = False


def closeAndTurn():
    global isTouching
    global turningCounter
    global rightColor
    global leftColor
    global black

    # Close Arm here
    # Drive a bit backwards???
    rospy.loginfo("In close and Turn")
    turningCounter += 1
    vel_msg = Twist()
    vel_msg.linear.x = 0.0
    vel_msg.angular.z = -0.5
    if turningCounter <= 10:
        # 180Degree right around turn
        vel_msg.linear.x = -1
        vel_msg.angular.z = 0.0
        pub.publish(vel_msg)
    elif turningCounter <= 25:
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = -0.5
        pub.publish(vel_msg)
    else:
        if not rightColor == black and not leftColor == black:
            pub.publish(vel_msg)
        else:
            turningCounter = 0
            isTouching = False


if __name__ == "__main__":
    global queue_size_int
    rospy.init_node("robot_controller")
    rospy.loginfo("Robot Controller Server node created")

    pub = rospy.Publisher("/groot/diffDrv/cmd_vel", Twist, queue_size=10)
    servoPublisher = rospy.Publisher("/groot/OutPortA/command", Float64, queue_size=10)

    leftColorSensor = rospy.Subscriber("/groot/color_left", UInt8, handle_left_color_sensor, queue_size=10)
    rightColorSensor = rospy.Subscriber("/groot/color_right", UInt8, handle_right_color_sensor, queue_size=10)

    #touchSensor = rospy.Subscriber("/groot/touch", Bool, handle_touch, queue_size=10)

    rospy.loginfo("Subscribers has been started")

    rospy.spin()
