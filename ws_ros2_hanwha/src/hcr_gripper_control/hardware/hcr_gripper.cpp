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

#include "hcr_gripper/hcr_gripper.hpp"
#include <string>
#include <vector>

namespace hcr_gripper
{

CallbackReturn Gripper::on_init(const hardware_interface::HardwareComponentInterfaceParams & params)
{
  if (hardware_interface::SystemInterface::on_init(params) != CallbackReturn::SUCCESS)
  {
    return CallbackReturn::ERROR;
  }

  // Get Weak Pointer to Executor from HardwareComponentInterfaceParams
  executor_ = params.executor;

  // Ensure that the executor is available before creating the custom status node
  if (auto locked_executor = executor_.lock())
  {
    std::string name_lower = get_hardware_info().name;
    std::transform(
      name_lower.begin(), name_lower.end(), name_lower.begin(),
      [](unsigned char c) { return std::tolower(c); });

    std::string node_name = name_lower + "_custom_node";
    custom_status_node_ = std::make_shared<rclcpp::Node>(node_name);

    locked_executor->add_node(custom_status_node_->get_node_base_interface());
  }

  gripper_position_ = 0;
  gripper_velocity_ = 0;
  gripper_position_command_ = 0;
  check_status = false;
  check_command = false;

  const hardware_interface::ComponentInfo &joint = info_.joints[0];

  // One command interface: position
  if (joint.command_interfaces.size() != 1)
  {
    RCLCPP_FATAL(
        get_logger(), "Joint '%s' has %zu command interfaces found. 1 expected.", joint.name.c_str(),
        joint.command_interfaces.size());
        
    return CallbackReturn::ERROR;
  }

  if (joint.command_interfaces[0].name != hardware_interface::HW_IF_POSITION)
  {
    RCLCPP_FATAL(
        get_logger(), "Joint '%s' has %s command interfaces found. '%s' expected.", joint.name.c_str(),
        joint.command_interfaces[0].name.c_str(), hardware_interface::HW_IF_POSITION);

    return CallbackReturn::ERROR;
  }

  // Two state interfaces: position and velocity
  if (joint.state_interfaces.size() != 2)
  {
    RCLCPP_FATAL(
        get_logger(), "Joint '%s' has %zu state interface. 2 expected.", joint.name.c_str(),
        joint.state_interfaces.size());

    return CallbackReturn::ERROR;
  }

  for (int i = 0; i < 2; ++i)
  {
    if (!(joint.state_interfaces[i].name == hardware_interface::HW_IF_POSITION ||
          joint.state_interfaces[i].name == hardware_interface::HW_IF_VELOCITY))
    {
      RCLCPP_FATAL(
          get_logger(), "Joint '%s' has %s state interface. Expected %s or %s.", joint.name.c_str(),
          joint.state_interfaces[i].name.c_str(), hardware_interface::HW_IF_POSITION,
          hardware_interface::HW_IF_VELOCITY);

      return CallbackReturn::ERROR;
    }
  }


  return CallbackReturn::SUCCESS;
}

CallbackReturn Gripper::on_configure(const rclcpp_lifecycle::State & /*previous_state*/)
{
  if (custom_status_node_)
  {
    RCLCPP_INFO(get_logger(), "Creating custom status publisher");

    printf("Executor is valid, creating custom status publisher\n");

    custom_status_publisher_ =
      custom_status_node_->create_publisher<control_msgs::msg::DynamicInterfaceGroupValues>("/gpio_controller/commands", 1);

    auto custom_timer_callback = [this]() -> void
    {
      if (/* custom_status_publisher_ && */ check_command == true)
      {
        control_msgs::msg::DynamicInterfaceGroupValues msg; 
        control_msgs::msg::InterfaceValue interface_value;

        msg.interface_groups.push_back("IOs");

        interface_value.interface_names.push_back("D0");
        if( command == true ) 
          interface_value.values.push_back(0.0);
        else
          interface_value.values.push_back(1.0);

        interface_value.interface_names.push_back("D1");
        if( command == true ) 
          interface_value.values.push_back(1.0);
        else
          interface_value.values.push_back(0.0);

        msg.interface_values.push_back(interface_value);
        
        custom_status_publisher_->publish(std::move(msg));

        check_command = false;
      }

    };

    using namespace std::chrono_literals;
    custom_status_timer_ = custom_status_node_->create_wall_timer(0.1s, custom_timer_callback); 

    RCLCPP_INFO(get_logger(), "Custom status publisher created");
    printf("Custom status publisher created\n");
  }
  else
  {
    RCLCPP_ERROR(get_logger(), "Executor expired, cannot create custom status publisher");
    printf("Executor expired, cannot create custom status publisher\n");
    return CallbackReturn::ERROR;
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

std::vector<hardware_interface::StateInterface> Gripper::export_state_interfaces()
{
  std::vector<hardware_interface::StateInterface> state_interfaces;

  state_interfaces.emplace_back(hardware_interface::StateInterface(
    info_.joints[0].name, hardware_interface::HW_IF_POSITION, &gripper_position_));
  state_interfaces.emplace_back(hardware_interface::StateInterface(
    info_.joints[0].name, hardware_interface::HW_IF_VELOCITY, &gripper_velocity_));

  return state_interfaces;
}

std::vector<hardware_interface::CommandInterface> Gripper::export_command_interfaces()
{
  std::vector<hardware_interface::CommandInterface> command_interfaces;

  command_interfaces.emplace_back(hardware_interface::CommandInterface(
      info_.joints[0].name, hardware_interface::HW_IF_POSITION, &gripper_position_command_));

  return command_interfaces;
}

return_type Gripper::read(const rclcpp::Time & /*time*/, const rclcpp::Duration &/* period*/)
{
  if (check_status)
  {
    RCLCPP_DEBUG(get_logger(), "Request gripper state ");

    check_status = false;
  }

  return return_type::OK;
}

return_type Gripper::write(const rclcpp::Time &, const rclcpp::Duration &)
{
  if( gripper_position_ == gripper_position_command_ )
    return return_type::OK;

  check_status = false;

  if(gripper_position_command_ < 0.001 )
  {
      check_command = true;
      command = true;
  }
  else if(gripper_position_command_ > 0.01 )
  {
      check_command = true;
      command = false;
  }

  gripper_position_ = gripper_position_command_;

  return return_type::OK;
}

} // namespace hcr_gripper

#include "pluginlib/class_list_macros.hpp"

PLUGINLIB_EXPORT_CLASS(
  hcr_gripper::Gripper, hardware_interface::SystemInterface)
