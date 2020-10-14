#!/usr/bin/env python
import rospy

from robot_localizer.msg import ParticleArray
from visualization_msgs.msg import Marker, MarkerArray

class ParticleVisualizer(object):
    """ This class subscribes to a source of ParticleArray messages which
    include a weight with each pose message and publishes MarkerArray
    messages with colors denoting weight
    """
    def __init__(self):
        rospy.init_node("particle_viz")
        rate = rospy.get_param("~update_rate", 10)
        self.r = rospy.Rate(rate)

        # Used to scale colors
        # TODO: Make this max weight dynamic
        self.max_weight = rospy.get_param("~max_weight", 0.0075)

        self.particlearray_sub = rospy.Subscriber("weighted_particlecloud",
            ParticleArray, self.particlearrayCB)
        self.particlearray_msg = ParticleArray()

        self.particle_viz_pub = rospy.Publisher("weighted_particlecloud_markers",
            MarkerArray, queue_size=10)

    def particlearrayCB(self, msg):
        """ Particle array callback """
        self.particlearray_msg = msg

    def createMarkerArray(self):
        """ Create MarkerArray ROS message from ParticleArray message and
        assign marker color based on weight """
        marker_array = MarkerArray()

        for idx, particle in enumerate(self.particlearray_msg.particles):
            # Initialize new marker
            new_marker = Marker()
            new_marker.header = self.particlearray_msg.header
            new_marker.id = idx
            new_marker.type = new_marker.ARROW
            new_marker.action = new_marker.ADD

            # Set marker scale
            new_marker.scale.x = 0.2
            new_marker.scale.y = 0.02
            new_marker.scale.z = 0.02

            # Fill in marker position & orientation info
            new_marker.pose = particle.pose
            # Color marker based on weight (green = high weight, red = low)
            new_marker.color.r = 1 - particle.weight/self.max_weight
            new_marker.color.g = particle.weight/self.max_weight
            new_marker.color.b = 0
            new_marker.color.a = 1.0

            # Add new marker to MarkerArray
            marker_array.markers.append(new_marker)

        return marker_array


    def run(self):
        while not rospy.is_shutdown():
            marker_array = self.createMarkerArray()
            self.particle_viz_pub.publish(marker_array)

            self.r.sleep()

if __name__ == "__main__":
    pv = ParticleVisualizer()
    pv.run()
