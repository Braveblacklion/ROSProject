#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64

if __name__ == '__main__':
    rospy.init_node('openclosegripper')

    pub = rospy.Publisher("/groot/OutPortA/command", Float64, queue_size=10)

    rate = rospy.Rate(10)

    msg = Float64()
    # 1.0 to close
    # -1.0 to open
    msg.data = -1.0
    duration = rospy.Duration(0.5)
    while (rospy.get_rostime() <= rospy.get_rostime() + duration):
        pub.publish(msg)
    msg.data = 0.0
    while (rospy.get_rostime() <= rospy.get_rostime() + duration):
        pub.publish(msg)
    msg.data = 1.0
    while (rospy.get_rostime() <= rospy.get_rostime() + duration):
        pub.publish(msg)
    msg.data = 0.0
    while (rospy.get_rostime() <= rospy.get_rostime() + duration):
        pub.publish(msg)
    rate.sleep()