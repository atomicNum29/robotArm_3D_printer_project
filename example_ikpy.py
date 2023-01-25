
import ikpy.utils.plot as plot_utils
import numpy as np
from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink

left_arm_chain = Chain(name='left_arm', links=[
    OriginLink(),
    URDFLink(
      name="shoulder",
      origin_translation=[-10, 0, 5],
      origin_orientation=[0, 1.57, 0],
      rotation=[0, 1, 0],
    ),
    URDFLink(
      name="elbow",
      origin_translation=[25, 0, 0],
      origin_orientation=[0, 0, 0],
      rotation=[0, 1, 0],
    ),
    URDFLink(
      name="wrist",
      origin_translation=[22, 0, 0],
      origin_orientation=[0, 0, 0],
      rotation=[0, 1, 0],
    )
])

target_position = [ 10, 0, 0]

print("The angles of each joints are : ", left_arm_chain.inverse_kinematics(target_position))

real_frame = left_arm_chain.forward_kinematics(left_arm_chain.inverse_kinematics(target_position))
print("Computed position vector : %s, original position vector : %s" % (real_frame[:3, 3], target_position))

# Optional: support for 3D plotting in the NB
# If there is a matplotlib error, uncomment the next line, and comment the line below it.
# %matplotlib inline
# %matplotlib widget
import matplotlib.pyplot as plt

fig, ax = plot_utils.init_3d_figure()
left_arm_chain.plot(left_arm_chain.inverse_kinematics(target_position), ax, target=target_position)
# plt.xlim(-0.1, 0.1)
# plt.ylim(-0.1, 0.1)
plt.show()