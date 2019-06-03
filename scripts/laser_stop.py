#!/usr/bin/env python

import rospy
from sensor_msgs.msg import LaserScan
from std_srvs.srv import SetBool

stopped = False


def callback_receive_laser_data(msg):
    global stopped
    # Now calculate if the robot is too close to an obstacle
    if min(msg.ranges) < 1:
        # Collision might occur stop the robot
        try:
            stopped = True
            stop_robot = rospy.ServiceProxy("/stop_robot", SetBool)
            response = stop_robot(True)
            rospy.loginfo("Robot should stop!")
            return response
        except rospy.ServiceException as e:
            rospy.logwarn("Service failed: " + str(e))
    elif stopped:
        # Collision might occur stop the robot
        try:
            stopped = False
            stop_robot = rospy.ServiceProxy("/stop_robot", SetBool)
            response = stop_robot(False)
            rospy.loginfo("Robot should roll again!")
            return response
        except rospy.ServiceException as e:
            rospy.logwarn("Service failed: " + str(e))


if __name__ == '__main__':
    rospy.init_node('husky_laser_stopper')

    topic_name = rospy.get_param("/laser_topic_name")

    sub = rospy.Subscriber(topic_name, LaserScan, callback_receive_laser_data, queue_size=10)

    rospy.wait_for_service("/stop_robot")

    rospy.spin()
