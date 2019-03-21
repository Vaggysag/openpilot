from selfdrive.controls.lib.pid import PIController
from common.numpy_fast import interp
from common.realtime import sec_since_boot
from cereal import car
import math
import numpy as np
from selfdrive.kegman_conf import kegman_conf

_DT = 0.01    # 100Hz


def get_steer_max(CP, v_ego):
  return interp(v_ego, CP.steerMaxBP, CP.steerMaxV)


class LatControl(object):
  def __init__(self, CP):

    kegman = kegman_conf()
    self.write_conf = False

    if kegman.conf['react'] == "-1":
      kegman.conf['react'] = str(round(CP.steerReactance,3))
      self.write_conf = True
    if kegman.conf['damp'] == "-1":
      kegman.conf['damp'] = str(round(CP.steerInductance,3))
      self.write_conf = True
    if kegman.conf['Kp'] == "-1":
      kegman.conf['Kp'] = str(round(CP.steerKpV[0],3))
      self.write_conf = True
    if kegman.conf['Ki'] == "-1":
      kegman.conf['Ki'] = str(round(CP.steerKiV[0],3))
      self.write_conf = True

    if self.write_conf:
      kegman.write_config(kegman.conf)

    self.mpc_frame = 0
    self.actual_projection = CP.steerInductance
    self.desired_projection = CP.steerReactance
    self.actual_smoothing = self.actual_projection / _DT
    self.desired_smoothing = self.desired_projection / _DT
    self.dampened_angle_steers = 0.0
    self.dampened_desired_angle = 0.0
    # Eliminate break-points, since they aren't needed (and would cause problems for resonance)
    KpV = [np.interp(25.0, CP.steerKpBP, CP.steerKpV)]
    KiV = [np.interp(25.0, CP.steerKiBP, CP.steerKiV)]
    self.pid = PIController(([0.], KpV),
                            ([0.], KiV),
                            k_f=CP.steerKf, pos_limit=1.0)
    self.steer_counter = 1.0
    self.steer_counter_prev = 0.0
    self.rough_steers_rate = 0.0
    self.prev_angle_steers = 0.0
    self.calculate_rate = True

  def reset(self):
    self.pid.reset()

  def live_tune(self, CP):
    self.mpc_frame += 1
    if self.mpc_frame % 300 == 0:
      # live tuning through /data/openpilot/tune.py overrides interface.py settings
      kegman = kegman_conf()
      if kegman.conf['tuneGernby'] == "1":
        self.steerKpV = np.array([float(kegman.conf['Kp'])])
        self.steerKiV = np.array([float(kegman.conf['Ki'])])
        self.actual_projection = float(kegman.conf['damp'])
        self.desired_projection = float(kegman.conf['react']) * 10.
        self.actual_smoothing = self.actual_projection / _DT
        self.desired_smoothing = self.desired_projection / _DT

        # Eliminate break-points, since they aren't needed (and would cause problems for resonance)
        KpV = [np.interp(25.0, CP.steerKpBP, self.steerKpV)]
        KiV = [np.interp(25.0, CP.steerKiBP, self.steerKiV)]
        self.pid._k_i = ([0.], KiV)
        self.pid._k_p = ([0.], KpV)
        print(self.desired_projection, self.actual_projection)
      self.mpc_frame = 0


  def update(self, active, v_ego, angle_steers, angle_rate, angle_offset, steer_override, CP, VM, path_plan):

    self.live_tune(CP)

    if angle_rate == 0.0 and self.calculate_rate:
      if angle_steers != self.prev_angle_steers:
        self.steer_counter_prev = self.steer_counter
        self.rough_steers_rate = (self.rough_steers_rate + 100.0 * (angle_steers - self.prev_angle_steers) / self.steer_counter_prev) / 2.0
        self.steer_counter = 0.0
      elif self.steer_counter >= self.steer_counter_prev:
        self.rough_steers_rate = (self.steer_counter * self.rough_steers_rate) / (self.steer_counter + 1.0)
      self.steer_counter += 1.0
      angle_rate = self.rough_steers_rate
      self.prev_angle_steers = angle_steers
    else:
      # If non-zero angle_rate is provided, stop calculating rate
      self.calculate_rate = False

    if v_ego < 0.3 or not active:
      output_steer = 0.0
      self.pid.reset()
      self.dampened_angle_steers = angle_steers
      self.dampened_desired_angle = angle_steers
    else:
      projected_desired_angle = np.interp(sec_since_boot() + self.desired_projection, path_plan.mpcTimes, path_plan.mpcAngles)
      self.dampened_desired_angle = ((self.desired_smoothing * self.dampened_desired_angle) + projected_desired_angle) / (1. + self.desired_smoothing)

      if CP.steerControlType == car.CarParams.SteerControlType.torque:
        projected_angle_steers = float(angle_steers) + self.actual_projection * float(angle_rate)
        self.dampened_angle_steers = ((self.actual_smoothing * self.dampened_angle_steers) + projected_angle_steers) / (1. + self.actual_smoothing)

        steers_max = get_steer_max(CP, v_ego)
        self.pid.pos_limit = steers_max
        self.pid.neg_limit = -steers_max
        deadzone = 0.0

        feed_forward = v_ego**2 * self.dampened_desired_angle
        output_steer = self.pid.update(self.dampened_desired_angle, self.dampened_angle_steers, check_saturation=(v_ego > 10),
                                        override=steer_override, feedforward=feed_forward, speed=v_ego, deadzone=deadzone)

    self.sat_flag = self.pid.saturated

    # return MPC angle in the unused output (for ALCA)
    if CP.steerControlType == car.CarParams.SteerControlType.torque:
      return output_steer, path_plan.angleSteers
    else:
      return self.dampened_desired_angle, path_plan.angleSteers
