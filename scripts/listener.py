#!/usr/bin/env python

import math
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from visualization_msgs.msg import Marker
from std_srvs.srv import SetBool

stopped = False


def callback_receive_laser_data(msg):
    global stopped
    if not stopped:
        angle = msg.angle_min + msg.ranges.index(min(msg.ranges)) * msg.angle_increment
        rospy.loginfo("Minimum Distance: {} AND angle is {}".format(min(msg.ranges), angle*(180/math.pi)))

        # Now calculate xy distance between robot and pillar
        x = min(msg.ranges) * math.cos(angle)
        y = min(msg.ranges) * math.sin(angle)
        rospy.loginfo("Pillar is at: ({},{})".format(x, y))
        move_husky(x, y)
    else:
        rospy.loginfo("Robot stopped!")


def move_husky(x, y):
    gain = rospy.get_param("/movement_gain")
    if y < 0:
        co = abs(gain * y)
    elif y > 0:
        co = -abs(gain * y)
    else:
        co = 0
    vel_msg = Twist()
    vel_msg.angular.z = co
    vel_msg.linear.x = 1
    pub = rospy.Publisher("/cmd_vel", Twist, queue_size=10)
    pub.publish(vel_msg)
    rospy.loginfo("Velocity is at: ({},{})".format(vel_msg.linear.x, vel_msg.angular.z))
    place_visualization_marker(x, y)


def place_visualization_marker(x, y):
    pub_marker = rospy.Publisher("visualization_marker", Marker, queue_size=10)
    marker_msg = Marker()
    marker_msg.header.frame_id = "base_laser"
    marker_msg.header.stamp = rospy.Time()
    marker_msg.id = 123
    marker_msg.type = Marker.CYLINDER
    marker_msg.action = Marker.ADD
    marker_msg.pose.position.x = x
    marker_msg.pose.position.y = y
    marker_msg.pose.position.z = 0
    marker_msg.pose.orientation.x = 0.0
    marker_msg.pose.orientation.y = 0.0
    marker_msg.pose.orientation.z = 0.0
    marker_msg.pose.orientation.w = 1.0
    marker_msg.scale.x = 0.1
    marker_msg.scale.y = 0.1
    marker_msg.scale.z = 1
    # Alpha color of the marker
    marker_msg.color.a = 1.0
    marker_msg.color.r = 1.0
    marker_msg.color.g = 0.0
    marker_msg.color.b = 0.0
    pub_marker.publish(marker_msg)


def callback_stop_robot(req):
    global stopped
    if req.data:
        stopped = True
        return True, "Robot has been successfully stopped"
    else:
        stopped = False
        return False, "Robot running again"


if __name__ == '__main__':
    rospy.init_node('husky_highlevel_controller')

    topic_name = rospy.get_param("/laser_topic_name")
    param_queue_size = rospy.get_param("/laser_queue_size")

    rospy.loginfo("Topic name: {}".format(topic_name))
    rospy.loginfo("Queue_size: {}".format(param_queue_size))

    sub = rospy.Subscriber(topic_name, LaserScan, callback_receive_laser_data, queue_size=param_queue_size)

    service = rospy.Service("/stop_robot", SetBool, callback_stop_robot)
    rospy.loginfo("Service server has been started")

    rospy.spin()
