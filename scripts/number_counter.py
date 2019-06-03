#!/usr/bin/env python

import rospy
from std_msgs.msg import Int64
from std_srvs.srv import SetBool

counter = 0


def callback_receive_radio_data(msg):
    global counter
    rospy.loginfo("Message recieved: ")
    rospy.loginfo(msg)

    counter += 1

    msg = Int64()
    msg.data = counter
    pub.publish(msg)


def callback_reset_counter(req):
    if req.data:
        global counter
        counter = 0
        return True, "Counter has been successfully reset"
    return False, "Counter has not been reset"


if __name__ == '__main__':

    rospy.init_node('number_counter')

    sub = rospy.Subscriber("/number", Int64, callback_receive_radio_data)

    pub = rospy.Publisher("/number_count", Int64, queue_size=10)

    # rosservice call /reset_counter "data: true" ## Will reset the counter
    service = rospy.Service("/reset_counter", SetBool, callback_reset_counter)
    rospy.loginfo("Service server has been started")

    rospy.spin()




