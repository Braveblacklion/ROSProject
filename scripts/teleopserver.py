#!/usr/bin/env python

import rospy
from geometry_msgs.msg import Twist


def callback_receive_radio_data(msg):
    rospy.loginfo("Message recieved: ")
    rospy.loginfo(msg)


def callback_reset_counter(req):
    if req.data:
        global counter
        counter = 0
        return True, "Counter has been successfully reset"
    return False, "Counter has not been reset"


if __name__ == '__main__':

    rospy.init_node("teleopserver")

    sub = rospy.Subscriber("/groot/diffDrv/cmd_vel", Twist, callback_receive_radio_data)
    rospy.loginfo("Service server has been started")

    rospy.spin()




