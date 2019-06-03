#!/usr/bin/env python

import rospy
import  random
from std_msgs.msg import Int64

if __name__ == '__main__':
    rospy.init_node('number_publisher')

    pub = rospy.Publisher("/number", Int64, queue_size=10)

    rate = rospy.Rate(2)

    while not rospy.is_shutdown():
        msg = Int64()
        msg.data = random.randint(1, 1000)
        pub.publish(msg)
        rate.sleep()

    rospy.loginfo("Node stopped")
