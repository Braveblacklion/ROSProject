#!/usr/bin/env python

import rospy
from std_msgs.msg import Float64

if __name__ == '__main__':
    rospy.init_node('openclosegripper')

    pub = rospy.Publisher("/groot/OutPortA/command", Float64, queue_size=10)

    msg = Float64()
    # 1.0 to close
    # -1.0 to open
    msg.data = 5.0
    pub.publish(msg)
    rospy.sleep(1)
    msg.data = 0.0
    pub.publish(msg)