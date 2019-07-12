#!/usr/bin/env python

import rospy
# To determine with message the motors node / sensors Nodes want
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from std_msgs.msg import UInt8
from std_msgs.msg import Bool
from std_msgs.msg import Float64

############################# Colors
untiefe = 0  # 0 none
black = 1    # 1   black
blue = 2     # 2   blue
green = 3    # 3   green
yellow = 4   # 4   yellow
red = 5      # 5   red
white = 6    # 6   white
brown = 7    # 7   brown
#####################################

########################## Directions
left = -1
straight = 0
right = 1
#####################################

##################### Claw Params
clawclose = 4
clawopen = -4
isclawopened = False
openCloseCounter = 0

isTouching = False
turningCounter = 0
isOpening = False

wasOpenedOnce = False
#################################

# Save the data of the sensors to
leftColor = 1
rightColor = 1

# Direction -1 = Left, 0 = Forward, 1 = right
# changed som variables
temporaryDirection = 1
savedDirection = left
saveDriveback = True
# Saved speed
savedSpeed = 0



#Picking up Mode
isPickingUp = False
blueCounter = 0
isFinished = False
ausgerichtet = False
blackCounter = 0



def handle_touch_sensor(msg):
    global isTouching
    if msg.data:
        isTouching = msg.data
        rospy.loginfo("Touched!!!!")
        #drive()
    rospy.loginfo("isTouching: " + str(isTouching))

def handle_left_color_sensor(msg):
    global leftColor
    leftColor = msg.data
    rospy.loginfo("Left Color Sensor color: " + str(leftColor))


def handle_right_color_sensor(msg):
    global rightColor
    rightColor = msg.data
    drive()
    rospy.loginfo("Right Color Sensor color: " + str(rightColor))


def drive():
    global temporaryDirection
    global savedSpeed
    global blueCounter
    global isFinished
    global isLeftTurnFalse
    global isTouching
    global isOpening
    vel_msg = Twist()
    if isTouching:
        closeAndTurn()
        return
    if isOpening:
        open()
        return
    if rightColor == 0 or leftColor == 0:
        return
    if rightColor == blue and leftColor == blue:
        pickUp()
        return
    elif isPickingUp:
        pickUp()
        return
    elif rightColor == black and leftColor == black:
        # Abgrund? --> STOP
        vel_msg.linear.x = savedSpeed
        vel_msg.angular.z = temporaryDirection
        #rospy.loginfo("Drive: STOP!")
    elif rightColor == black and leftColor == black:
        # Abgrund? --> STOP
        vel_msg.linear.x = savedSpeed
        vel_msg.angular.z = temporaryDirection
        #rospy.loginfo("Drive: STOP!")
    elif rightColor == black:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = -0.5

        savedSpeed = 0.1
        savedDirection = -0.5
        #rospy.loginfo("Drive: RIGHT!")
    elif leftColor == black:
        vel_msg.linear.x = 0.1
        vel_msg.angular.z = 0.5

        savedSpeed = 0.1
        savedDirection = 0.5
        #rospy.loginfo("Drive: LEFT!")
    else:
        vel_msg.linear.x = 0.5
        vel_msg.angular.z = 0

        savedSpeed = 0.5
        savedDirection = 0

    # Reset counter
    blueCounter = 0
    isFinished = False
    isLeftTurnFalse = False
    # Publish the message
    pub.publish(vel_msg)


def pickUp():
    global savedDirection
    global blueCounter
    global isFinished
    global leftColor
    global rightColor
    global ausgerichtet
    global isPickingUp
    global left
    global right
    global straight
    global blackCounter
    global saveDriveback
    global bluecrossed
    global first
    global isOpening
    global turningRadius

    vel_msg = Twist()
    blueCounter += 1

    if blueCounter >= 2 or isPickingUp:
        isPickingUp = True
        blueCounter = 0
    else:
        isPickingUp = False
        return

    # if rightTouchedBlue and leftTouchedBlue:
    if not ausgerichtet:
        if rightColor == untiefe and leftColor == untiefe:
            isPickingUp = False
            ausgerichtet = False
            return

        if rightColor == blue and leftColor == blue:
            # Dive a bit backward
            vel_msg.linear.x = -0.1
            vel_msg.angular.z = 0.0
        elif (rightColor == white or rightColor == yellow) and (leftColor == white or leftColor == yellow):
            # Drive right/left
            if saveDriveback == False:
                ausgerichtet = True

            if saveDriveback == True: # driven over blue
                saveDriveback = False
                vel_msg.linear.x = -0.1
                vel_msg.angular.z = 0.0
                for x in xrange(45):
                    pub.publish(vel_msg)
                rospy.sleep(2)
            return
        # 1. richtung anerkannt, wie geht es weiter? gas gradeaus! mit black check
        elif rightColor == blue and (leftColor == white or leftColor == yellow) :
            # Turn right
            vel_msg.linear.x = -0.1
            vel_msg.angular.z = -0.2 # anpassen, nach richtung robot, changed for on white instead of blue
            saveDriveback = True
        elif leftColor == blue and (rightColor == white or rightColor == yellow):
            # Turn left
            vel_msg.linear.x = -0.1
            vel_msg.angular.z = 0.2
            saveDriveback = True
        elif rightColor == black or leftColor == black:
            # Seems to entered this mode wrongly
            ausgerichtet = False
            isPickingUp = False
            drive()
        else:
            #rospy.loginfo("Right color: " + str(rightColor) + "and Left Color: " + str(leftColor))
            return
        pub.publish(vel_msg)
        return

    if savedDirection == left and not (leftColor == black or rightColor == black):
        # Search left

        if blackCounter > 25:
            savedDirection = right  # Save direction = left
            blackCounter -= 15
        elif blackCounter < -1:
            vel_msg.linear.x = -0.4
            vel_msg.angular.z = 0.0
        elif blackCounter == -1:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.5  # dreh zurueck
            for x in xrange(350):
                pub.publish(vel_msg)
        elif blackCounter == 0:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = 0.5
            for x in xrange(350):
                pub.publish(vel_msg)
        elif blackCounter > 0:
            vel_msg.linear.x = 0.4
            vel_msg.angular.z = 0.0

        blackCounter += 1
                             # spaeter: reboot robot to start (rueckwaerts fahren)
    elif savedDirection == right and not (leftColor == black or rightColor == black):
        # Turn right
        if blackCounter > 0:
            vel_msg.linear.x = -0.4
            vel_msg.angular.z = 0.0
        elif blackCounter == 0:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = -0.5  # dreh zurueck
            for x in xrange(250):
                pub.publish(vel_msg)
        elif blackCounter == -1:
            vel_msg.linear.x = 0.0
            vel_msg.angular.z = -0.5  # dreh in die andere richtung
            for x in xrange(250):
                pub.publish(vel_msg)
        elif blackCounter < -25:
            savedDirection = left
            blackCounter +=15
        elif blackCounter < -1:
            vel_msg.linear.x = 0.4
            vel_msg.angular.z = 0.0

        blackCounter -=1

    elif rightColor == black or leftColor == black:
        #rospy.loginfo("Saved direction = " + str(savedDirection))
        ausgerichtet = False
        isPickingUp = False
        isFinished = True
        rospy.loginfo("MuuuuuuuP!!!")
        # Reset counter
        blueCounter = 0
        if savedDirection == left:
            blackCounter = 0
        else:
            blackCounter = -1
        saveDriveback = True
        isOpening = True
        return
    else:
        rospy.loginfo("Oooooops In else: " + "Right color: " + str(rightColor) + "and Left Color: " + str(leftColor))
        # Wrong direction go back and try again

    # Publish the message
    pub.publish(vel_msg)


def open():
    global openCloseCounter
    global isclawopened
    global clawopen
    global isOpening
    global wasOpenedOnce

    if wasOpenedOnce:
        isOpening = False
        return

    if not isclawopened:
        isOpening = True
        openCloseCounter += 1
        if openCloseCounter <= 10:
            msg = Float64()
            msg.data = clawopen
            servoPublisher.publish(msg)
            rospy.loginfo("Counter: " + str(openCloseCounter))
        else:
            openCloseCounter = 0
            msg = Float64()
            msg.data = 0.0
            servoPublisher.publish(msg)
            isclawopened = True
            isOpening = False
            wasOpenedOnce = True


def close():
    global isclawopened
    global openCloseCounter
    global clawclose

    if isclawopened:
        openCloseCounter += 1
        if openCloseCounter <= 12:
            msg = Float64()
            msg.data = clawclose
            servoPublisher.publish(msg)
            rospy.loginfo("Counter: " + str(openCloseCounter))
        else:
            openCloseCounter = 0
            msg = Float64()
            msg.data = 0.0
            servoPublisher.publish(msg)
            isclawopened = False


def closeAndTurn():
    global isTouching
    global turningCounter
    global rightColor
    global leftColor
    global black
    global isclawopened

    # Close Arm here
    if isclawopened:
        close()
        return
    # Drive a bit backwards???
    rospy.loginfo("In close and Turn")
    turningCounter += 1
    vel_msg = Twist()
    vel_msg.linear.x = 0.0
    vel_msg.angular.z = -0.5
    if turningCounter <= 8:
        # 180Degree right around turn
        vel_msg.linear.x = -1
        vel_msg.angular.z = 0.0
        pub.publish(vel_msg)
    elif turningCounter <= 25:
        vel_msg.linear.x = 0.0
        vel_msg.angular.z = -0.5
        pub.publish(vel_msg)
    else:
        if not rightColor == black and not leftColor == black:
            pub.publish(vel_msg)
        else:
            turningCounter = 0
            isTouching = False


if __name__ == "__main__":
    global queue_size_int
    rospy.init_node("robot_controller")
    rospy.loginfo("Robot Controller Server node created")

    pub = rospy.Publisher("/groot/diffDrv/cmd_vel", Twist, queue_size=10)

    leftColorSensor = rospy.Subscriber("/groot/color_left", UInt8, handle_left_color_sensor, queue_size=10)
    rightColorSensor = rospy.Subscriber("/groot/color_right", UInt8, handle_right_color_sensor, queue_size=10)
    touchSensor = rospy.Subscriber("/groot/touch", Bool, handle_touch_sensor, queue_size=10)
    servoPublisher = rospy.Publisher("/groot/OutPortA/command", Float64, queue_size=10)
    # touchSensor = rospy.Service("/groot/touch", ColorRGBA, handle_right_color_sensor)

    # Edit
    # infraRedSensor = rospy.Service("/ir...", ColorRGBA, handle_right_color_sensor)

    rospy.loginfo("Subscribers has been started")

    rospy.spin()
