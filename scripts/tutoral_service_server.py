#!/usr/bin/env python

import rospy
from std_srvs.srv import SetBool


def handle_tutorial_service():
    result = True
    rospy.loginfo("Cancel requested")
    return result


if __name__ == "__main__":
    rospy.init_node("tutorial_service_server")
    rospy.loginfo("Tutorial Service Server node created")

    service = rospy.Service("/reset_number_count", SetBool, handle_tutorial_service)
    rospy.loginfo("Service server has been started")

    rospy.spin()



