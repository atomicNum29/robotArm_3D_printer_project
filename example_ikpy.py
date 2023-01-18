import ikpy.chain
import ikpy.utils.plot as plot_utils
import numpy as np
from ikpy.link import OriginLink, URDFLink

my_chain = ikpy.chain.Chain(
  name='test_arm', links=[
    OriginLink(),
    URDFLink(
      name="first_link",
      origin_translation=[1, 1, 0],
      origin_orientation=[0, 0, 0],
      rotation=[0, 0, 1],
    ),
    URDFLink(
      name="second_link",
      origin_translation=[1, 0, 0],
      origin_orientation=[0, 0, 0],
      rotation=[0, 0, 1],
    )
])

target_position = [ 1, 0, 0]

print("The angles of each joints are : ", my_chain.inverse_kinematics(target_position))

real_frame = my_chain.forward_kinematics(my_chain.inverse_kinematics(target_position))
print("Computed position vector : %s, original position vector : %s" % (real_frame[:3, 3], target_position))

# Optional: support for 3D plotting in the NB
# If there is a matplotlib error, uncomment the next line, and comment the line below it.
# %matplotlib inline
# %matplotlib widget
import matplotlib.pyplot as plt

fig, ax = plot_utils.init_3d_figure()
my_chain.plot(my_chain.inverse_kinematics(target_position), ax, target=target_position)
# plt.xlim(-0.1, 0.1)
# plt.ylim(-0.1, 0.1)
plt.show()