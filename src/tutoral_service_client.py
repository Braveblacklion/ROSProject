#!/usr/bin/env python

import rospy
from std_srvs.srv import SetBool

if __name__ == '__main__':
    rospy.init_node("add_two_ints_client")

    rospy.wait_for_service("/add_two_ints")

    try:
        add_two_ints = rospy.ServiceProxy("/add_two_ints", SetBool)
        response = add_two_ints(2, 6)
        rospy.loginfo("Sum is: " + str(response.sum))
    except rospy.ServiceException as e:
        rospy.logwarn("Service failed: " + str(e))
