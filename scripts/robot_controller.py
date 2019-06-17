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
savedDirection = 0 # 1 For right -1 for left
savedSpeed = 0 # Saved speed
isPickingUp = False
blueCounter = 0


def handle_left_color_sensor(msg):
    global leftTouched
    global leftTouchedBlue
    if msg.data == 0:
        rospy.loginfo("Left Color Sensor untiefe detected")
        return
    elif msg.data == 1:
        # Drive left
        leftTouched = 1
        #Black detected
        rospy.loginfo("Left Color Sensor Black detected")
    elif msg.data == 6 or msg.data == 4:
        # Drive left
        leftTouched = 0
        leftTouchedBlue = 0
        rospy.loginfo("Left Color Sensor White detected")
    elif msg.data == 2:
        leftTouchedBlue = 1
        # Blue detected
        rospy.loginfo("Left Color Sensor Blue detected")
    else:
        leftTouched = 1
        rospy.loginfo("Left Color Sensor different color detected: " + str(msg.data))
    drive()


def handle_right_color_sensor(msg):
    global rightTouched
    global rightTouchedBlue
    if msg.data == 0:
        rospy.loginfo("Right Color Sensor untiefe detected")
        return
    elif msg.data == 1:
        rightTouched = 1
        # Black detected
        rospy.loginfo("Right Color Sensor Black detected")
    elif msg.data == 6 or msg.data == 4:
        # Drive forward
        rightTouched = 0
        rightTouchedBlue = 0
        rospy.loginfo("Right Color Sensor White detected")
    elif msg.data == 2:
        rightTouchedBlue = 1
        # Blue detected
        rospy.loginfo("Right Color Sensor Blue detected")
    else:
        rightTouched = 1
        rospy.loginfo("Right Color Sensor different color detected" + str(msg))
    drive()


def drive():
    global rightTouched, leftTouched
    global savedDirection
    global savedSpeed
    vel_msg = Twist()
    if rightTouchedBlue and leftTouchedBlue:
        pickUp()
    elif isPickingUp:
        return
    elif rightTouched == 1 and leftTouched == 1:
        #Abgrund? --> STOP
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

    #Publish the message
    pub.publish(vel_msg)


def pickUp():
    global blueCounter
    global isPickingUp
    global rightTouched
    global leftTouched
    global rightTouchedBlue
    global leftTouchedBlue
    vel_msg = Twist()
    blueCounter += 1
    if blueCounter >= 3:
        isPickingUp = True
        finished = False
        duration = rospy.Duration(1)

        vel_msg.linear.x = -1
        vel_msg.angular.z = 0.5
        while (rospy.get_rostime() <= rospy.get_rostime() + rospy.Duration(1)):
            pub.publish(vel_msg)

        #Try right
        if (leftTouchedBlue and rightTouchedBlue):
            #Turn left
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.5

            while(rospy.get_rostime() < rospy.get_rostime() + duration):
                pub.publish(vel_msg)
            # Drive a bit forward to test if ther is a black line
            while (rospy.get_rostime() < rospy.get_rostime() + duration):
                lalala = True
                #Wait for a second to come to full stop
            vel_msg.linear.x = 0.5
            vel_msg.angular.z = 0.0
            while(rospy.get_rostime() < duration + rospy.get_rostime()):
                pub.publish(vel_msg)





if __name__ == "__main__":
    global queue_size_int
    rospy.init_node("robot_controller")
    rospy.loginfo("Robot Controller Server node created")

    pub = rospy.Publisher("/groot/diffDrv/cmd_vel", Twist, queue_size=10)

    leftColorSensor = rospy.Subscriber("/groot/color_left", UInt8, handle_left_color_sensor, queue_size=10)
    rightColorSensor = rospy.Subscriber("/groot/color_right", UInt8, handle_right_color_sensor, queue_size=10)

    #touchSensor = rospy.Service("/groot/touch", ColorRGBA, handle_right_color_sensor)

    #Edit
    #infraRedSensor = rospy.Service("/ir...", ColorRGBA, handle_right_color_sensor)

    rospy.loginfo("Subscribers has been started")

    rospy.spin()
