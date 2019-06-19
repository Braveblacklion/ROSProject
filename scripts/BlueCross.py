#!/usr/bin/env python

import rospy
# To determine with message the motors node / sensors Nodes want
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8

# Direction -1 = Left, 0 = Forward, 1 = right
leftTouched = 0
leftTouchedBlue = 0
rightTouched = 0
rightTouchedBlue = 0
savedDirection = -1 # 1 For right -1 for left
savedSpeed = 0 # Saved speed
isPickingUp = False
blueCounter = 0
isFinished = False
ausgerichtet = False
isSearching = False


def handle_left_color_sensor(msg):
    global leftTouched
    global leftTouchedBlue
    if msg.data == 0:
        rospy.loginfo("Left Color Sensor untiefe detected")
        leftTouchedBlue = 0
        leftTouched = 0
        return
    elif msg.data == 1:
        # Drive left
        leftTouched = 1
        leftTouchedBlue = 0
        #Black detected
        rospy.loginfo("Left Color Sensor Black detected")
    elif msg.data == 6 or msg.data == 4:
        # Drive left
        leftTouched = 0
        leftTouchedBlue = 0
        rospy.loginfo("Left Color Sensor White detected")
    elif msg.data == 2:
        leftTouchedBlue = 1
        leftTouched = 0
        # Blue detected
        rospy.loginfo("Left Color Sensor Blue detected")
    else:
        leftTouched = 1
        leftTouchedBlue = 0
        rospy.loginfo("Left Color Sensor different color detected: " + str(msg.data))


def handle_right_color_sensor(msg):
    global rightTouched
    global rightTouchedBlue
    if msg.data == 0:
        rospy.loginfo("Right Color Sensor untiefe detected")
        rightTouchedBlue = 0
        rightTouched = 0
        return
    elif msg.data == 1:
        rightTouched = 1
        rightTouchedBlue = 0
        # Black detected
        rospy.loginfo("Right Color Sensor Black detected")
    elif msg.data == 6 or msg.data == 4:
        # Drive forward
        rightTouched = 0
        rightTouchedBlue = 0
        rospy.loginfo("Right Color Sensor White detected")
    elif msg.data == 2:
        rightTouchedBlue = 1
        rightTouched = 0
        # Blue detected
        rospy.loginfo("Right Color Sensor Blue detected")
    else:
        rightTouched = 1
        rightTouchedBlue = 0
        rospy.loginfo("Right Color Sensor different color detected" + str(msg))
    drive()


def drive():
    global savedDirection
    global savedSpeed
    global blueCounter
    global isFinished
    global isLeftTurnFalse

    vel_msg = Twist()
    if rightTouchedBlue and leftTouchedBlue:
        pickUp()
        return
    elif isPickingUp:
        pickUp()
        return
    elif rightTouched == 1 and leftTouched == 1:
        # Abgrund? --> STOP
        vel_msg.linear.x = savedSpeed
        vel_msg.angular.z = savedDirection
        rospy.loginfo("Drive: STOP!")
    elif rightTouched == 1:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = -0.5
        savedSpeed = 0
        savedDirection = -0.5
        rospy.loginfo("Drive: RIGHT!")
    elif leftTouched == 1:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = 0.5
        savedSpeed = 0
        savedDirection = 0.5
        rospy.loginfo("Drive: LEFT!")
    else:
        vel_msg.linear.x = 0.5
        vel_msg.angular.z = 0
        savedSpeed = 0.5
        savedDirection = 0

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
    global rightTouchedBlue
    global leftTouchedBlue
    global leftTouched
    global rightTouched
    global ausgerichtet
    global isPickingUp
    global isSearching

    isPickingUp = True

    vel_msg = Twist()
    if isFinished:
        rospy.loginfo("Finished!!!")
        isPickingUp = False
        savedDirection
        return
    # if rightTouchedBlue and leftTouchedBlue:
    if not ausgerichtet:
        if rightTouchedBlue and leftTouchedBlue:
            # Dive a bit forward
            vel_msg.linear.x = 0.1
            vel_msg.angular.z = 0.0
        elif not rightTouchedBlue or not leftTouchedBlue:
            vel_msg.linear.x = -0.5
            vel_msg.angular.z = 0.0
            for x in xrange(3):
                pub.publish(vel_msg)
            ausgerichtet = True
            return
        elif not rightTouchedBlue and leftTouchedBlue:
            # Drive a bit right
            test = 123
        elif rightTouched or leftTouched:
            # Seems to entered this mode wrongly
            ausgerichtet = False
            isPickingUp = False
            isLeftTurnFalse = False
        else:
            return
        pub.publish(vel_msg)
        return

    if savedDirection == -1 and not rightTouched and not leftTouched and rightTouchedBlue:
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = 0.5
        isSearching = True
        savedDirection = -1  # Save direction = left
    elif savedDirection == 1 and not rightTouched and not leftTouched and leftTouchedBlue:
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = -0.5
        isSearching = True# Save direction = right
    elif rightTouched or leftTouched:
        rospy.loginfo("Saved direction = " + str(savedDirection))
        ausgerichtet = False
        isPickingUp = False
        isFinished = True
        isSearching = False
    elif not rightTouched and not leftTouched and not isSearching:
        vel_msg.linear.x = -0.1
        vel_msg.angular.z = 0.0
    else:
        vel_msg.linear.x = -0.0
        vel_msg.angular.z = -0.5
        savedDirection = 1
        rospy.loginfo("In else")
        isLeftTurnFalse = True
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
