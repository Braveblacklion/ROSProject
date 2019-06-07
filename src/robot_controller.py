#!/usr/bin/env python

import rospy
# To determine with message the motors node / sensors Nodes want
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from std_msgs.msg import ColorRGBA

queue_size_int = 10
# Direction -1 = Left, 0 = Forward, 1 = right
leftTouched = 0
leftTouchedBlue = 0
rightTouched = 0
rightTouchedBlue = 0


def handle_left_color_sensor(msg):
    global leftTouched
    global leftTouchedBlue
    if msg.r < 0.1 & msg.g < 0.1 & msg.b < 0.1:
        # Drive left
        leftTouched = 1
        #Black detected
        rospy.loginfo("Left Color Sensor Black detected")
    elif msg.r < 0.1 & msg.g < 0.1 & msg.b < 0.7:
        leftTouchedBlue = 1
        # Blue detected
        rospy.loginfo("Left Color Sensor Blue detected")
    else:
        #Drive left
        leftTouched = 0
        leftTouchedBlue = 0

def handle_right_color_sensor(msg):
    global rightTouched
    global rightTouchedBlue
    if msg.r < 0.1 & msg.g < 0.1 & msg.b < 0.1:
        rightTouched = 1
        # Black detected
        rospy.loginfo("Right Color Sensor Black detected")
    elif msg.r < 0.1 & msg.g < 0.1 & msg.b < 0.7:
        rightTouchedBlue = 1
        # Blue detected
        rospy.loginfo("Right Color Sensor Blue detected")
    else:
        #Drive right
        rightTouched = 0
        rightTouchedBlue = 0

def drive():
    global rightTouched, leftTouched

    vel_msg = Twist()
    if rightTouched & leftTouched:
        #Abgrund? --> STOP
        vel_msg.angular.x = 0
        vel_msg.linear.x = 0
    elif rightTouched:
        vel_msg.angular.x = 0.1
        vel_msg.linear.x = 1.0
    elif leftTouched:
        vel_msg.angular.x = -0.1
        vel_msg.linear.x = 1

    #Publish the message
    rospy.Publisher("/groot/diffDrv/cmd_vel", vel_msg)


if __name__ == "__main__":
    global queue_size_int
    rospy.init_node("robot_controller")
    rospy.loginfo("Robot Controller Server node created")

    rospy.wait_for_service("/touch")
    rospy.wait_for_service("/ir...") #Edit

    leftColorSensor = rospy.Subscriber("/color_left", ColorRGBA, handle_left_color_sensor, queue_size=queue_size_int)
    rightColorSensor = rospy.Subscriber("/color_right", ColorRGBA, handle_right_color_sensor, queue_size=queue_size_int)

    rightColorSensor = rospy.Service("/touch", ColorRGBA, handle_right_color_sensor)

    #Edit
    rightColorSensor = rospy.Service("/ir...", ColorRGBA, handle_right_color_sensor)

    rospy.loginfo("Service server has been started")

    rospy.spin()
