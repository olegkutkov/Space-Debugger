#
#   Copyright 2023  Oleg Kutkov <contact@olegkutkov.me>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.  
#
#vim:
#set expandtab
#set tabstop=4


import json
import gettext
import datetime
from entity import *
from dishy_data import *
from obstruction_img_gen import generate_img_from_list

_ = gettext.gettext

###

''' Starlink Dishy info parser and formatter '''
class Dishy(Entity):
    def __init__(self, json_object):
        print("Loading Dish")

        dish_object = json_object

        if STATUS_KEY in json_object:
          dish_object = json_object[STATUS_KEY]

        super().__init__('Dish', dish_object.get(DISH_REACHABLE_KEY, False), \
                                dish_object.get(DISH_CLOUD_ACCESS_KEY, False))

        if self.reachable and not self.parse_device_info(dish_object):
            raise Exception(_('Failed to load Dish Device Info'))

        self.plugins = []

        ''' Load additional data plugins '''
        if self.reachable:
            self.plugins.append(DishyNetwork(dish_object))
            self.plugins.append(DishyGPS(dish_object))
            self.plugins.append(DishyAntenna(dish_object))
            self.plugins.append(DishyAlignmentStats(dish_object))
            self.plugins.append(ModuleAlerts(dish_object))
            self.plugins.append(ModuleConfig(dish_object))
            self.plugins.append(Features(dish_object))
            self.plugins.append(DishyReadyStates(dish_object))
            self.plugins.append(DishyOutage(dish_object))
            self.plugins.append(DishyObstructions(dish_object))

    '''  This is SpaceX device '''
    def is_sx_device(self):
        return True

    def get_module_readable_name(self):
        return _('Dish')

    ''' Get device image '''
    def get_device_image_file(self):
        ''' Special handle for the HP without actuators '''
        if self.hw_version == 'hp1_proto0' or self.hw_version == 'hp1_proto1':
            if self.has_actuators == ActuatorStatus.UNKNOWN or self.has_actuators == ActuatorStatus.NO_ACTUATORS:
                return dev_images['hp_flat']

        if self.hw_version not in dev_images:
            return dev_images['unknown']

        return dev_images[self.hw_version]

    ''' Return readable and formatted data '''
    def get_readable_params(self, result):
            result[_('Hardware revision')] = self.hw_version
            result[_('Software version')] = self.sw_version
            result[_('Software update state')] = software_update_state_str[self.software_upd_state]
            result[_('User terminal ID')] = self.device_id
            result[_('Development hardware')] = self.yes_or_no(self.is_developer)
            result[_('Starlink cohoused')] = self.yes_or_no(self.dishy_cohoused)
            result[_('Actuators')] = actuator_status_str[self.has_actuators]
            result[_('Stow requested')] = self.yes_or_no(self.stow_requested)

            if self.mf_version != '':
                result[_('Manufactured version')] = self.mf_version

            result[_('Boot count')] = self.boot_count
            result[_('Software parts equal')] = self.yes_or_no(self.sw_parts_eq)

            if self.anti_rollback_version != 0:
                result[_('Anti-Rollback version')] = self.anti_rollback_version

            ''' Hacky way to introduce spacer, better way? '''
            result[' '] = ''

            result[_('Country code')] = self.country_code
            result[_('Device date/time')] = datetime.datetime.fromtimestamp(self.timestamp)
            result[_('Device timezone')] = 'GMT' + str(int(self.utc_off_hours / 60 / 60))
            result[_('Uptime')] = str(self.uptime) + ' ' +  _('seconds')

            result['  '] = ''

            result[_('Class of service')] = service_class_str[self.class_of_serivce]
            result[_('Mobility class')] = mobility_class_str[self.mobility_class]
            result[_('Service state')] = disablement_code_str[self.disablement_code]

    ''' Parse JSON data '''
    def parse_device_info(self, json_object):
            dish_object = json_object

            if STATUS_KEY in json_object:
                dish_object = json_object[STATUS_KEY]

            if DEVICE_INFO_KEY not in dish_object:
                return False

            device_info = dish_object[DEVICE_INFO_KEY]
            device_state = dish_object[DEVICE_STATE_KEY]

            self.device_id = device_info.get(DEVICE_INFO_ID_KEY, _('Unknown'))
            self.sw_version = device_info.get(DEVICE_INFO_SW_VER_KEY, _('Unknown'))
            self.hw_version = device_info.get(DEVICE_INFO_HW_VER_KEY, _('Unknown'))
            self.mf_version = device_info.get(DEVICE_INFO_MF_VER_KEY, _('Unknown'))
            self.country_code = device_info.get(DEVICE_INFO_CC_KEY, _('Unknown'))
            self.utc_off_hours = device_info.get(DEVICE_INFO_UTC_OFF_KEY, 0)
            self.sw_parts_eq = device_info.get(DEVICE_INFO_SW_PARTS_EQ_KEY, False)
            self.is_developer = device_info.get(DEVICE_INFO_IS_DEV_KEY, False)
            self.boot_count = device_info.get(DEVICE_INFO_BOOT_COUNT_KEY, 0)
            self.anti_rollback_version = device_info.get(DEVICE_INFO_ANTI_ROLLBACK_KEY, 0)
            self.dishy_cohoused = device_info.get(DEVICE_DISH_COHOUSED_KEY, False)

            self.timestamp = dish_object.get(DEVICE_TIMESTAMP_KEY, 0)
            self.uptime = device_state.get(DEVICE_UPTIME_KEY, 0)

            self.has_actuators = ActuatorStatus(dish_object.get(DEVICE_HAS_ACTUATORS_KEY, 0))
            self.stow_requested = dish_object.get(DEVICE_STOW_REQUESTED_KEY, False)
            self.mobility_class = MobylityClass(dish_object.get(DEVICE_MOBILITY_CLASS_KEY, 0))
            self.class_of_serivce = ServiceClass(dish_object.get(DEVICE_CLASS_OF_SERVICE_KEY, 0))
            self.disablement_code = DisablementCode(dish_object.get(DEVICE_DISABLEMENT_CODE_KEY, 0))

            self.software_upd_state = SoftwareUpdateState(dish_object.get(DEVICE_SOFTWARE_UPDATE_ST_KEY, 0))

            return True

    ''' Return additional data '''
    def get_additional_data(self, result):
        for plugin in self.plugins:
            if plugin.is_data_ready():
                result[plugin.get_name()] = plugin.get_data()


''' Additional data plugins '''

''' Network info '''
class DishyNetwork(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        self.ether_speed = json_object.get(DEVICE_ETHER_SPEED_KEY, 100)
        self.downlink_tput_bps = json_object.get(NET_DOWNLINK_TPUT_BPS_KEY, 0)
        self.uplink_tput_bps = json_object.get(NET_UPLINK_TPUT_BPS_KEY, 0)
        self.pop_ping_latency = json_object.get(NET_POP_PING_LATENCY_MS_KEY, 0)
        self.pop_ping_drop_rate = json_object.get(NET_POP_PING_DROP_RATE_KEY, 0)
        self.senconds_to_first_non_empty_slot = json_object.get(NET_SECONDS_TO_FIRST_NON_EMPTY_SLOT_KEY, 0)

        self.data_ready = True

    def get_name(self):
        return 'Network'

    def get_data(self):
        eht_text = str(self.ether_speed) + ' Mbps ' + ('(slow, check your cable or device)' \
                    if self.ether_speed < 1000 else '(nominal)')

        data = [
            [ _('Ethernet speed'), eht_text ],
            [ _('Downlink Throughput, Kbps'), round(self.downlink_tput_bps / 1024, 3) ],
            [ _('Uplink Throughput, Kbps'), round(self.uplink_tput_bps / 1024, 3) ],
            [ _('PoP ping latency, ms'), round(self.pop_ping_latency, 3) ],
            [ _('PoP ping drop rate'), self.pop_ping_drop_rate ],
            [ _('Seconds to first non-empty slot'), self.senconds_to_first_non_empty_slot ]
        ]

        return [ _('Network'), data ]

''' GPS info '''
class DishyGPS(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_GPS_STATS_KEY not in json_object:
            return None

        gps_stats = json_object[DEVICE_GPS_STATS_KEY]

        self.gps_valid = gps_stats.get(DEVICE_GPS_STATS_GPS_VALID_KEY, False)
        self.gps_sats = gps_stats.get(DEVICE_GPS_STATS_GPS_SATS_KEY, 0)
        self.gps_no_sats_after_fix = gps_stats.get(DEVICE_GPS_STATS_NO_SATS_AFTER_FFIX_KEY, False)
        self.gps_inhibit = gps_stats.get(DEVICE_GPS_INHIBIT_KEY, False)

        self.data_ready = True

    def get_name(self):
        return 'GPS'

    def get_data(self):
        data = [
            [ _('GPS valid'),  self.yes_or_no(self.gps_valid) ],
            [ _('GPS satellites'), self.gps_sats ],
            [ _('No GPS satellites after first fix'), self.yes_or_no(self.gps_no_sats_after_fix) ],
            [ _('Don\'t trust Dishy\'s GPS'), self.yes_or_no(self.gps_inhibit) ]
        ]

        return [ _('GPS'), data ]

''' Alignment stats '''
class DishyAlignmentStats(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_ALIGNMENT_STATS_KEY not in json_object:
            return None

        self.stats = json_object[DEVICE_ALIGNMENT_STATS_KEY]

        self.has_actuators = ActuatorStatus(self.stats.get(DEVICE_HAS_ACTUATORS_KEY, 0))
        self.actuator_state = ActuatorState(self.stats.get(DEVICE_ALIGNMENT_STATS_ACTUATOR_STATE_KEY, 0))
        self.tilt_angle = self.stats.get(DEVICE_ALIGNMENT_STATS_TILT_ANGLE_DEG_KEY, 0)
        self.boresight_az_deg = self.stats.get(DEVICE_BORESIGHT_AZIMUTH_DEG_KEY, 0)
        self.boresight_el_deg = self.stats.get(DEVICE_BORESIGHT_ELEVATION_DEG_KEY, 0)
        self.desired_boresight_azimuth_deg = self.stats.get(DEVICE_DESIRED_BORESIGHT_AZ_DEG_KEY, 0)
        self.desired_boresight_elevation_deg = self.stats.get(DEVICE_DESIRED_BORESIGHT_EL_DEG_KEY, 0)
        self.attitude_est_state = AttitudeEstimationState(self.stats.get(DEVICE_ALIGNMENT_STATS_ATTITUDE_ESTIMATION_STATE_KEY, 0))
        self.attitude_uncert = self.stats.get(DEVICE_ALIGNMENT_STATS_ATTITUDE_UNCERTANITY_DEG_KEY, 0)

        self.data_ready = True

    def get_name(self):
        return 'Alignment'

    def get_data(self):
        data = [
            [ _('Actuators'), actuator_status_str[self.has_actuators] ],
            [ _('Actuator state'), actuator_state_str[self.actuator_state] ],
            [ _('Tilt angle, deg'), self.tilt_angle ],
            [ _('Panel boresight Azimuth angle, deg'), self.boresight_az_deg ],
            [ _('Panel boresight Elevation agngle, deg'), self.boresight_el_deg ],
            [ _('Panel desired boresight Azimuth angle, deg'), self.desired_boresight_azimuth_deg],
            [ _('Panel desired boresight Elevation angle, deg'), self.desired_boresight_elevation_deg],
            [ _('Attitude Estimation State'), attitude_estimation_state_str[self.attitude_est_state]],
            [ _('Attitude Uncertainty, deg'), self.attitude_uncert ]
        ]

        return [ _('Alignment'), data ]

''' Basic antenna info '''
class DishyAntenna(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        self.snr_above_noise_floor = json_object.get(DEVICE_IS_SNR_ABOVE_NOISE_FLOOR_KEY, False)
        self.snr_persistently_low = json_object.get(DEVICE_IS_SNR_PERSISTENTLY_LOW_KEY, False)
        self.boresight_az_deg = json_object.get(DEVICE_BORESIGHT_AZIMUTH_DEG_KEY, 0)
        self.boresight_el_deg = json_object.get(DEVICE_BORESIGHT_ELEVATION_DEG_KEY, 0)

        self.data_ready = True

    def get_name(self):
        return 'Antenna'

    def get_data(self):
        data = [
            [ _('Signal level'), _('Good') if self.snr_above_noise_floor else _('Bad') ],
            [ _('SNR persistently low'), self.yes_or_no(self.snr_persistently_low) ],
            [ _('Panel boresight Azimuth angle, deg'), self.boresight_az_deg ],
            [ _('Panel boresight Elevation agngle, deg'), self.boresight_el_deg ]
        ]

        return [ _('Antenna'), data ]

''' Ready states '''
class DishyReadyStates(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_READY_STATES_KEY not in json_object:
            return None

        self.init_durations = None

        ready_states = json_object[DEVICE_READY_STATES_KEY]

        self.cady = ready_states.get(DEVICE_READY_STATES_CADY_KEY, False)
        self.scp = ready_states.get(DEVICE_READY_STATES_SCP_KEY, False)
        self.l1l2 = ready_states.get(DEVICE_READY_STATES_L1L2_KEY, False)
        self.xphy = ready_states.get(DEVICE_READY_STATES_XPHY_KEY, False)
        self.aap = ready_states.get(DEVICE_READY_STATES_AAP_KEY, False)
        self.rf = ready_states.get(DEVICE_READY_STATES_RF_KEY, False)

        if DEVICE_INIT_DURATION_SEC_KEY in json_object:
            init_dur = json_object[DEVICE_INIT_DURATION_SEC_KEY]

            self.init_durations = [
                [ _('RF front end ready'), str(init_dur.get(DEVICE_INIT_RF_READY_KEY, 0)) + ' sec' ],
                [ _('GPS fixed (valid)'), str(init_dur.get(DEVICE_INIT_GPS_VALID_KEY, 0)) + ' sec' ],
                [ _('Satellite signal detected'), str(init_dur.get(DEVICE_INIT_BURST_DETECTED_KEY, 0)) + ' sec' ],
                [ _('Initial network entry'), str(init_dur.get(DEVICE_INIT_INITIAL_NETWORK_ENTRY_KEY, 0)) + ' sec' ],
                [ _('First control plane'), str(init_dur.get(DEVICE_INIT_FIRST_CONTROL_PLANE_KEY, 0)) + ' sec' ],
                [ _('Network schedule'), str(init_dur.get(DEVICE_INIT_NETWORK_SCHEDULE_KEY, 0)) + ' sec' ],
                [ _('First PoP ping'), str(init_dur.get(DEVICE_INIT_FIRST_POP_PING_KEY, 0)) + ' sec' ],
                [ _('Attitude initialized'), str(init_dur.get(DEVICE_INIT_ATTITUDE_INITIALIZATION_KEY, 0)) + ' sec' ],
                [ _('Extended Kalman filter converged'), str(init_dur.get(DEVICE_INIT_EKF_CONVERGED_KEY, 0)) + ' sec' ],
                [ _('Stable connection'), str(init_dur.get(DEVICE_INIT_STABLE_CONNECTION_KEY, 0)) + ' sec' ]
            ]

        self.data_ready = True

    def get_name(self):
        return 'ReadyStates'

    def get_data(self):
        data = [
            [ _('Clock generator'),  self.yes_or_no(self.cady) ],
            [ _('RFFE bus interface'), self.yes_or_no(self.scp) ],
            [ _('Modem L1L2'), self.yes_or_no(self.l1l2) ],
            [ _('Xilinx XPHY interface'), self.yes_or_no(self.xphy) ],
            [ _('Digital beamformers'), self.yes_or_no(self.aap) ],
            [ _('RF front end'), self.yes_or_no(self.rf) ],
            [ 'init_durations', self.init_durations ]
        ]

        return [ _('Ready states'), data ]

''' Outages info '''
class DishyOutage(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_OUTAGE_KEY not in json_object:
            return None

        outage_data = json_object[DEVICE_OUTAGE_KEY]

        self.cause = OutageCause(outage_data.get(DEVICE_OUTAGE_CAUSE_KEY, 0))
        self.start_timestamp_ns = outage_data.get(DEVICE_OUTAGE_START_TIMESTAMP_NS_KEY, 0)
        self.outage_duration_ns = outage_data.get(DEVICE_OUTAGE_DURATION_NS_KEY, 0)
        self.did_switch = outage_data.get(DEVICE_OUTAGE_DID_SWITCH_KEY, False)

        self.data_ready = True

    def get_name(self):
        return 'Outage'

    def get_data(self):
        data = [
            [ _('Cause'), outage_cause_str[self.cause] ],
            [ _('Start timestamp, ns'), self.start_timestamp_ns ],
            [ _('Duration, ns'), self.outage_duration_ns ],
            [ _('Did switch'), self.yes_or_no(self.did_switch) ]
        ]

        return [ _('Outage'), data ]

''' Obstructions info '''
class DishyObstructions(EntityModule):
    def __init__(self, json_object):
        super().__init__()

        if DEVICE_OBSTRUCTION_STATS_KEY not in json_object:
            return None

        obstr_data = json_object[DEVICE_OBSTRUCTION_STATS_KEY]

        self.currently_obstructed = obstr_data.get(DEVICE_OBSTRUCTION_STATS_CURRENTLY_OBSTRUCTED_KEY, False)
        self.fraction_obstructed = obstr_data.get(DEVICE_OBSTRUCTION_STATS_FRACTION_OBSTRUCTED_KEY, 0)
        self.time_obstructed = obstr_data.get(DEVICE_OBSTRUCTION_STATS_TIME_OBSTRUCTED_KEY, 0)
        self.valid_sec = obstr_data.get(DEVICE_OBSTRUCTION_STATS_VALID_SEC_KEY, 0)
        self.patches_valid = obstr_data.get(DEVICE_OBSTRUCTION_STATS_PATCHES_VALID_KEY, 0)
        self.frac_obstr_list = obstr_data.get(DEVICE_OBSTRUCTION_STATS_WEDGE_FRAC_OBSTRUCTED_LIST_KEY, [])
        self.abs_obstr_list = obstr_data.get(DEVICE_OBSTRUCTION_STATS_WEDGE_ABS_OBSTRUCTED_LIST_KEY, [])
        self.avg_pr_dur_sec = obstr_data.get(DEVICE_OBSTRUCTION_STATS_AVG_PROLONGED_OBSTR_DURATION_SEC_KEY, 0)
        self.avg_pr_int_sec = obstr_data.get(DEVICE_OBSTRUCTION_STATS_AVG_PROLONGED_OBSTR_INTERVAL_SEC_KEY, 0)
        self.avg_pr_valid = obstr_data.get(DEVICE_OBSTRUCTION_STATS_AVG_PROLONGED_OBSTR_VALID, False)

        self.image = None

        if len(self.frac_obstr_list):
            self.image = generate_img_from_list(self.frac_obstr_list)

        self.data_ready = True

    def get_name(self):
        return 'Obstructions'

    def get_data(self):
        data = [
            [ _('Currently obstructed'), self.yes_or_no(self.currently_obstructed) ],
            [ _('Fraction obstructed'), self.fraction_obstructed ],
            [ _('Time obstructed'), self.time_obstructed ],
            [ _('Time valid, sec'), self.valid_sec ],
            [ _('Patches valid'), self.patches_valid],
            [ _('Average prolonged obstruction duration, sec'), self.avg_pr_dur_sec ],
            [ _('Average prolonged obstruction interval, sec'), self.avg_pr_int_sec],
            [ _('Average prolonged obstruction valid'), self.yes_or_no(self.avg_pr_valid) ],
            [ 'image_blob', self.image ]
        ]

        return [ _('Obstructions'), data ]

