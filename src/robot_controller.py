#!/usr/bin/env python

import rospy
# To determine with message the motors node / sensors Nodes want
from std_srvs.srv import SetBool

def handle_tutorial_service():
    result = True
    rospy.loginfo("Cancel requested")
    return result

if __name__ == '__main__':
    rospy.init_node("ev3_controller")
    rospy.wait_for_service("/cmd_vel")

    try:
        ev3_controller = rospy.ServiceProxy("/ev3_controller", SetBool)
        response = add_two_ints(2, 6)
        rospy.loginfo("Sum is: " + str(response.sum))
    except rospy.ServiceException as e:
        rospy.logwarn("Service failed: " + str(e))



if __name__ == "__main__":
    rospy.init_node("tutorial_service_server")
    rospy.loginfo("Tutorial Service Server node created")

    service = rospy.Service("/reset_number_count", SetBool, handle_tutorial_service)
    rospy.loginfo("Service server has been started")

    rospy.spin()
