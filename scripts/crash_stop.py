#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Imu
from std_srvs.srv import SetBool
from geometry_msgs.msg import Vector3


stopped = False


def callback_receive_laser_data(msg):
    # Now calculate if the robot is too close to an obstacle
    if abs(msg.angular_velocity.x) > 0.03 or abs(msg.angular_velocity.y) > 0.03:
        # Collision might occur stop the robot
        try:
            stop_robot = rospy.ServiceProxy("/stop_robot", SetBool)
            response = stop_robot(True)
            rospy.loginfo("Robot emergency stop!")
            return response
        except rospy.ServiceException as e:
            rospy.logwarn("Service failed: " + str(e))


if __name__ == '__main__':
    rospy.init_node('husky_laser_stopper')

    sub = rospy.Subscriber("/imu/data/", Imu, callback_receive_laser_data, queue_size=10)

    rospy.wait_for_service("/stop_robot")

    rospy.spin()
