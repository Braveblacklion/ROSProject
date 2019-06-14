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
    if msg.r < 9.0 and msg.g < 9.0 and msg.b < 9.0:
        rospy.loginfo("Left Color Sensor untiefe detected")
    elif msg.r < 25.0 and msg.g < 25.0 and msg.b < 25.0:
        # Drive left
        leftTouched = 1
        #Black detected
        rospy.loginfo("Left Color Sensor Black detected")
    elif msg.r > 100.0 and msg.g > 100.0 and msg.b > 100.0:
        # Drive left
        leftTouched = 0
        leftTouchedBlue = 0
        rospy.loginfo("Left Color Sensor White detected")
    elif msg.r > 40.0 and msg.g > 60.0 and msg.b > 75.0:
        leftTouchedBlue = 1
        # Blue detected
        rospy.loginfo("Left Color Sensor Blue detected")
    else:
        rospy.loginfo("Left Color Sensor different color detected")
    drive()


def handle_right_color_sensor(msg):
    global rightTouched
    global rightTouchedBlue
    if msg.r < 9.0 and msg.g < 9.0 and msg.b < 9.0:
        rospy.loginfo("Right Color Sensor untiefe detected")
    elif msg.r < 25.0 and msg.g < 25.0 and msg.b < 25.0:
        rightTouched = 1
        # Black detected
        rospy.loginfo("Right Color Sensor Black detected")
    elif msg.r > 100.0 and msg.g > 100.0 and msg.b > 100.0:
        # Drive forward
        rightTouched = 0
        rightTouchedBlue = 0
        rospy.loginfo("Right Color Sensor White detected")
    elif msg.r > 40.0 and msg.g > 60.0 and msg.b > 75.0:
        rightTouchedBlue = 1
        # Blue detected
        rospy.loginfo("Right Color Sensor Blue detected")
    else:
        rospy.loginfo("Right Color Sensor different color detected")
    drive()


def drive():
    global rightTouched, leftTouched

    vel_msg = Twist()
    if rightTouched & leftTouched:
        #Abgrund? --> STOP
        vel_msg.angular.x = 0
        vel_msg.linear.x = 0
    elif rightTouched:
        vel_msg.angular.x = 1
        vel_msg.linear.x = 10.0
    elif leftTouched:
        vel_msg.angular.x = -1
        vel_msg.linear.x = 10

    #Publish the message
    pub.publish(vel_msg)


if __name__ == "__main__":
    global queue_size_int
    rospy.init_node("robot_controller")
    rospy.loginfo("Robot Controller Server node created")

    pub = rospy.Publisher("/groot/diffDrv/cmd_vel", Twist, queue_size=10)

    leftColorSensor = rospy.Subscriber("/color_left", ColorRGBA, handle_left_color_sensor, queue_size=10)
    rightColorSensor = rospy.Subscriber("/color_right", ColorRGBA, handle_right_color_sensor, queue_size=10)

    #touchSensor = rospy.Service("/touch", ColorRGBA, handle_right_color_sensor)

    #Edit
    #infraRedSensor = rospy.Service("/ir...", ColorRGBA, handle_right_color_sensor)

    rospy.loginfo("Subscribers has been started")

    rospy.spin()
