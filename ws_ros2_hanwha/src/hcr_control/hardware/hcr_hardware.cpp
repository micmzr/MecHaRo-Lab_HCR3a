// Copyright 2023 ros2_control Development Team
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "hcr_hardware/hcr_hardware.hpp"
#include <string>
#include <vector>

int HCR_fd = -1;
extern int get_HCR_fd(void)
{
  return HCR_fd;
}

namespace hcr_control
{

static const rclcpp::Logger LOGGER = rclcpp::get_logger("HCRSystemHardware");

CallbackReturn RobotSystem::on_init(const hardware_interface::HardwareInfo & info)
{
  if (hardware_interface::SystemInterface::on_init(info) != CallbackReturn::SUCCESS)
  {
    return CallbackReturn::ERROR;
  }

  // robot has 6 joints and 2 interfaces
  joint_position_.assign(6, 0);
  // joint_velocities_.assign(6, 0);
  joint_position_command_.assign(6, 0);
  // joint_velocities_command_.assign(6, 0);
  hw_gpio_in_.assign(8, 0);
  hw_gpio_out_.assign(8, 0);

  for (int i = 0; i < 6; i++)
    jnts_com[i] = (double) joint_position_command_[i];

  for (const auto & joint : info_.joints)
  {
    for (const auto & interface : joint.state_interfaces)
    {
      joint_interfaces[interface.name].push_back(joint.name);
    }
  }

  // We have only 1 GPIO component configured
  if (info_.gpios.size() != 1)
  {
    RCLCPP_FATAL(
      get_logger(), "HCR has '%ld' GPIO components, '%d' expected.",
      info_.gpios.size(), 1);
    return hardware_interface::CallbackReturn::ERROR;
  }

  // 8 command interface
  if (info_.gpios[0].command_interfaces.size() != 8)
  {
    RCLCPP_FATAL(
      get_logger(), "GPIO component %s has '%ld' command interfaces, '%d' expected.",
      info_.gpios[0].name.c_str(), info_.gpios[0].command_interfaces.size(), 8);
    return hardware_interface::CallbackReturn::ERROR;
  }
  
  // 8 state interfaces
  if (info_.gpios[0].state_interfaces.size() != 8)
  {
    RCLCPP_FATAL(
      get_logger(), "GPIO component %s has '%ld' state interfaces, '%d' expected.",
      info_.gpios[0].name.c_str(), info_.gpios[1].state_interfaces.size(), 8);
    return hardware_interface::CallbackReturn::ERROR;
  }

  const auto hcr_port = stoi(info_.hardware_parameters["hcr_port"]);
  const auto hcr_ip = info_.hardware_parameters["hcr_ip"];

  struct sockaddr_in server_addr;
  memset(&server_addr, 0, sizeof(server_addr));
  server_addr.sin_family = AF_INET;

  if (inet_pton( AF_INET, hcr_ip.c_str(),&server_addr.sin_addr) <= 0)
  {
    RCLCPP_FATAL(LOGGER, "Invalid HCR IP address %s",hcr_ip.c_str());

    return CallbackReturn::ERROR;
  }

  if (hcr_port <= 0)
  {
    RCLCPP_FATAL(LOGGER, "Invalid HCR port %d",hcr_port);

    return CallbackReturn::ERROR;
  }

  server_addr.sin_port = htons(hcr_port);

  if ((HCR = socket(AF_INET, SOCK_STREAM, 0)) < 0)
  {
    RCLCPP_FATAL(LOGGER, "Could not init socket");

    return CallbackReturn::ERROR;
  }

  if (connect(HCR, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0)
  {
    RCLCPP_FATAL(LOGGER, "Could not connect to HCR system");

    return CallbackReturn::ERROR;
  }

  struct timeval timeout;
  timeout.tv_sec = 1; //SOCKET_READ_TIMEOUT_SEC;
  timeout.tv_usec = 0;
  setsockopt(HCR, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

  int one = 1;
  if (setsockopt(HCR, IPPROTO_TCP, TCP_NODELAY, (void *)&one, sizeof(one)) < 0) 
  {
    RCLCPP_FATAL(LOGGER, "setsockopt(TCP_NODELAY) failed");
  }

  one = 1;
  if (setsockopt(HCR, IPPROTO_TCP, TCP_QUICKACK, &one, sizeof(one)) < 0) 
  {
    RCLCPP_FATAL(LOGGER, "setsockopt TCP_QUICKACK) failed");
  }

  HCR_fd = HCR;

  return CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> RobotSystem::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  int ind = 0;
  for (const auto & joint_name : joint_interfaces["position"])
  {
    state_interfaces.emplace_back(joint_name, "position", &joint_position_[ind++]);
  }

  hw_gpio_in_.resize(8);
  size_t ct = 0;
  for (size_t i = 0; i < info_.gpios.size(); i++)
  {
    for (auto state_if : info_.gpios.at(i).state_interfaces)
    {
      state_interfaces.emplace_back(info_.gpios.at(i).name, state_if.name, &hw_gpio_in_[ct++]);
    }
  }

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> RobotSystem::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  int ind = 0;
  for (const auto & joint_name : joint_interfaces["position"])
  {
    command_interfaces.emplace_back(joint_name, "position", &joint_position_command_[ind++]);
  }

  hw_gpio_out_.resize(8);
  size_t ct = 0;
  for (size_t i = 0; i < info_.gpios.size(); i++)
  {
    for (auto command_if : info_.gpios.at(i).command_interfaces)
    {
      command_interfaces.emplace_back(info_.gpios.at(i).name, command_if.name, &hw_gpio_out_[ct++]);
    }
  }

  return command_interfaces;
}

return_type RobotSystem::read(const rclcpp::Time & /*time*/, const rclcpp::Duration &/* period*/)
{
  rclcpp::Time time_start = rclcpp::Clock().now();
  RCLCPP_INFO(LOGGER, "Send JNT command to HCR");

  send(HCR, GET_JOINTS, strlen(GET_JOINTS), 0);
 
  memset(HCR_buf, '\0', sizeof(HCR_buf));

  rclcpp::Time time_now = rclcpp::Clock().now();
  RCLCPP_INFO(LOGGER, "Send to HCR, time taken: %f sec", (time_now - time_start).seconds());

  if (recv(HCR, HCR_buf, sizeof(HCR_buf), 0) > 0)
  {
    RCLCPP_DEBUG(LOGGER, "Get data from HCR: %s", HCR_buf);

    if (strncmp("JNT", HCR_buf, 3) == 0)
    {
      double jnts[6];

      sscanf(HCR_buf + 4, "%lg %lg %lg %lg %lg %lg",
             jnts, jnts + 1, jnts + 2, jnts + 3, jnts + 4, jnts + 5);

      for (int i = 0; i < 6; i++)
      {
        joint_position_[i] = jnts[i] * M_PI / 180.l;
      }
    }
    else
    {
      RCLCPP_WARN(LOGGER, "Unknown data from HCR: %s", HCR_buf);
    }
  }
  else
  {
    RCLCPP_WARN(LOGGER, "Cant get data from HCR");
  }
  
  time_now = rclcpp::Clock().now();
  RCLCPP_INFO(LOGGER, "Get from HCR, time taken: %f sec", (time_now - time_start).seconds());

  send(HCR, GET_GPI, strlen(GET_GPI), 0);
  memset(HCR_buf, '\0', sizeof(HCR_buf));

  time_now = rclcpp::Clock().now();
  RCLCPP_INFO(LOGGER, "Send GPI to HCR, time taken: %f sec", (time_now - time_start).seconds());

  if (recv(HCR, HCR_buf, sizeof(HCR_buf), 0) > 0)
  {
    RCLCPP_DEBUG(LOGGER, "Get data from HCR: %s", HCR_buf);

    if (strncmp("GPI", HCR_buf, 3) == 0)
    {
      int gpios[8];

      sscanf(HCR_buf + 4, "%d %d %d %d %d %d %d %d",
             gpios, gpios + 1, gpios + 2, gpios + 3,
             gpios + 4, gpios + 5, gpios + 6, gpios + 7);

      for (int i = 0; i < 8; i++)
      {
        hw_gpio_in_[i] = (double) gpios[i];
      }
    }
    else
    {
      RCLCPP_WARN(LOGGER, "Unknown data from HCR: %s", HCR_buf);
    }
  }
  else
  {
    RCLCPP_WARN(LOGGER, "Cant get data from HCR");
  }

  time_now = rclcpp::Clock().now();
  RCLCPP_INFO(LOGGER, "Get GPO from HCR, time taken: %f sec", (time_now - time_start).seconds());

  return return_type::OK;
}

return_type RobotSystem::write(const rclcpp::Time &, const rclcpp::Duration &)
{  
  bool diff = false; 

  for (int i = 0; i < 6; i++)
  {
    if (jnts_com[i] != joint_position_command_[i])
    {
      diff = true;
      break;
    }
  }

  if (diff)
  {
    for (int i = 0; i < 6; i++)
      jnts_com[i] = (double) joint_position_command_[i];

    memset(HCR_buf, '\0', sizeof(HCR_buf));

    sprintf(HCR_buf, "MOV %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f\n",
            (float)(jnts_com[0] * 180.l / M_PI),
            (float)(jnts_com[1] * 180.l / M_PI),
            (float)(jnts_com[2] * 180.l / M_PI),
            (float)(jnts_com[3] * 180.l / M_PI),
            (float)(jnts_com[4] * 180.l / M_PI),
            (float)(jnts_com[5] * 180.l / M_PI));

    send(HCR, HCR_buf, strlen(HCR_buf), 0);

    RCLCPP_INFO(LOGGER, "Send command to HCR: %s", HCR_buf);
  }

  diff = false;

  for (int i = 0; i < 8; i++)
  {
    if (gpo_com[i] != hw_gpio_out_[i])
    {
      diff = true;
      break;
    }
  }

  if (diff)
  {
    for (int i = 0; i < 8; i++)
      gpo_com[i] = (double) hw_gpio_out_[i];

    memset(HCR_buf, '\0', sizeof(HCR_buf));

    sprintf(HCR_buf, "GPO %d %d %d %d %d %d %d %d\n",
            (int)gpo_com[0], (int)gpo_com[1], (int)gpo_com[2], (int)gpo_com[3],
            (int)gpo_com[4], (int)gpo_com[5], (int)gpo_com[6], (int)gpo_com[7]);

    send(HCR, HCR_buf, strlen(HCR_buf), 0);

    RCLCPP_INFO(LOGGER, "Send command to HCR: %s", HCR_buf);
  }

  return return_type::OK;
}

}  // namespace hcr_control

#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
  hcr_control::RobotSystem, hardware_interface::SystemInterface)
