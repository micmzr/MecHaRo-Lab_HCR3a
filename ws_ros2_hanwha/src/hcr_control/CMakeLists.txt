cmake_minimum_required(VERSION 3.30)
project(hcr_control LANGUAGES CXX)

if(NOT WIN32)

if(CMAKE_CXX_COMPILER_ID MATCHES "(GNU|Clang)")
  add_compile_options(-Wall -Wextra)
endif()

# find dependencies
set(HW_IF_INCLUDE_DEPENDS
  pluginlib
  rcpputils
  hardware_interface
)
set(REF_GEN_INCLUDE_DEPENDS
  kdl_parser
  rclcpp
  trajectory_msgs
)
set(CONTROLLER_INCLUDE_DEPENDS
  pluginlib
  rcpputils
  controller_interface
  realtime_tools
  trajectory_msgs
)

# find dependencies
find_package(ament_cmake REQUIRED)
foreach(Dependency IN ITEMS ${HW_IF_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()
foreach(Dependency IN ITEMS ${REF_GEN_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()
foreach(Dependency IN ITEMS ${CONTROLLER_INCLUDE_DEPENDS})
  find_package(${Dependency} REQUIRED)
endforeach()

add_library(
  hcr_control
  SHARED
  hardware/hcr_hardware.cpp
)

set(ALL_TARGET_DEPENDS
  pluginlib::pluginlib
  rcpputils::rcpputils
  hardware_interface::hardware_interface
  controller_interface::controller_interface
  realtime_tools::realtime_tools
  trajectory_msgs::trajectory_msgs
)

target_compile_features(hcr_control PUBLIC cxx_std_17)
target_include_directories(hcr_control PUBLIC
$<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}/hardware/include>
$<INSTALL_INTERFACE:include/hcr_control>
)
target_link_libraries(
  hcr_control PUBLIC
  ${ALL_TARGET_DEPENDS}
)

# Causes the visibility macros to use dllexport rather than dllimport,
# which is appropriate when building the dll but not consuming it.
target_compile_definitions(${PROJECT_NAME} PRIVATE "HCR_CONTROL_BUILDING_DLL")

# Export hardware plugins
pluginlib_export_plugin_description_file(hardware_interface hcr_control.xml)

# INSTALL
install(
  DIRECTORY hardware/include/
  DESTINATION include/hcr_control
)

install(TARGETS hcr_control
  EXPORT export_hcr_control
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
endif()

## EXPORTS
ament_export_targets(export_hcr_control HAS_LIBRARY_TARGET)
ament_export_dependencies(${HW_IF_INCLUDE_DEPENDS} ${REF_GEN_INCLUDE_DEPENDS} ${CONTROLLER_INCLUDE_DEPENDS})
ament_package()

else()
  message(STATUS "Skipping ${PROJECT_NAME} because compilation is disabled on Windows.")
endif()