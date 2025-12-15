import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


class SystemComponent(Enum):
    """Enumeration of system components"""
    PERCEPTION = "perception"
    PLANNING = "planning"
    CONTROL = "control"
    COMMUNICATION = "communication"
    SENSORS = "sensors"
    ACTUATORS = "actuators"


class ErrorSeverity(Enum):
    """Enumeration of error severities"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class HumanoidError:
    """Representation of an error in the humanoid system"""
    component: SystemComponent
    severity: ErrorSeverity
    error_type: str
    description: str
    timestamp: float
    resolved: bool = False
    resolution_time: Optional[float] = None


class ErrorRecoverySystem:
    """
    System for error detection, reporting, and recovery in humanoid robotics
    """
    
    def __init__(self, node):
        self.node = node
        self.logger = logging.getLogger(__name__)
        
        # Active and historical errors
        self.active_errors = []
        self.error_history = []
        
        # Recovery strategies
        self.recovery_strategies = {
            'navigation_timeout': self.handle_navigation_timeout,
            'manipulation_failure': self.handle_manipulation_failure,
            'sensor_unavailable': self.handle_sensor_unavailable,
            'balance_loss': self.handle_balance_loss,
            'comms_failure': self.handle_comms_failure,
            'low_battery': self.handle_low_battery
        }
    
    def report_error(self, component: SystemComponent, severity: ErrorSeverity,
                     error_type: str, description: str) -> HumanoidError:
        """Report an error in the system"""
        import time
        error = HumanoidError(
            component=component,
            severity=severity,
            error_type=error_type,
            description=description,
            timestamp=time.time()
        )
        
        self.active_errors.append(error)
        self.error_history.append(error)
        
        # Log error with appropriate level
        if severity == ErrorSeverity.LOW:
            self.logger.info(f"[{component.value}] {error_type}: {description}")
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"[{component.value}] {error_type}: {description}")
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(f"[{component.value}] {error_type}: {description}")
        elif severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"[{component.value}] {error_type}: {description}")
        
        return error
    
    def handle_navigation_timeout(self, error: HumanoidError) -> bool:
        """Handle navigation timeout error"""
        self.logger.warning("Handling navigation timeout error")
        
        # Stop current navigation
        self.node.motion_controller.stop_navigation()
        
        # Return to safe position if possible
        return self.node.motion_controller.return_to_safe_position()
    
    def handle_manipulation_failure(self, error: HumanoidError) -> bool:
        """Handle manipulation failure error"""
        self.logger.warning("Handling manipulation failure error")
        
        # Release gripper if holding
        self.node.motion_controller.release_gripper()
        
        # Attempt alternative grasp approach
        return self.node.cognitive_planner.attempt_alternative_manipulation()
    
    def handle_sensor_unavailable(self, error: HumanoidError) -> bool:
        """Handle sensor unavailability error"""
        self.logger.warning(f"Handling sensor unavailability error for: {error.description}")
        
        # Switch to alternative sensors or fallback behaviors
        # This would depend on which sensor is affected
        return True  # Simplified for now
    
    def handle_balance_loss(self, error: HumanoidError) -> bool:
        """Handle robot balance loss error (CRITICAL)"""
        self.logger.critical("Handling balance loss error - IMMEDIATE EMERGENCY STOP!")
        
        # Emergency stop all motion
        self.node.motion_controller.emergency_stop()
        
        # Enter safe posture
        success = self.node.motion_controller.enter_safe_posture()
        
        if success:
            # Report to higher level system
            feedback_msg = String()
            feedback_msg.data = "EMERGENCY: Balance lost, entered safe posture. Awaiting operator instruction."
            self.node.feedback_publisher.publish(feedback_msg)
        else:
            self.logger.critical("FAILED to enter safe posture after balance loss - MANUAL INTERVENTION REQUIRED!")
        
        return success
    
    def handle_comms_failure(self, error: HumanoidError) -> bool:
        """Handle communication failure error"""
        self.logger.warning("Handling communication failure error")
        
        # Switch to offline/local mode if possible
        self.node.set_offline_mode(True)
        
        # Retry connection after delay
        import time
        time.sleep(5)
        
        # Attempt reconnection
        return self.node.attempt_reconnection()
    
    def handle_low_battery(self, error: HumanoidError) -> bool:
        """Handle low battery error"""
        self.logger.warning("Handling low battery error")
        
        # Navigate back to charging station
        charging_station_pos = self.node.get_charging_station_position()
        if charging_station_pos:
            return self.node.motion_controller.navigate_to_pose(charging_station_pos)
        else:
            self.logger.warning("No charging station available, stopping operations")
            return self.node.motion_controller.emergency_stop()
    
    def attempt_recovery(self, error_type: str, error_data: Dict[str, Any]) -> bool:
        """Attempt to recover from an error automatically"""
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error_data)
            except Exception as e:
                self.logger.error(f"Error recovery failed for {error_type}: {e}")
                return False
        else:
            self.logger.warning(f"No recovery strategy defined for error type: {error_type}")
            return False
    
    def resolve_error(self, error: HumanoidError) -> bool:
        """Mark an error as resolved"""
        if error in self.active_errors:
            error.resolved = True
            error.resolution_time = __import__('time').time()
            self.active_errors.remove(error)
            
            self.logger.info(f"Resolved error: {error.error_type}")
            return True
        else:
            self.logger.warning(f"Error not in active errors list: {error.error_type}")
            return False
    
    def get_active_errors(self) -> List[HumanoidError]:
        """Get list of currently active errors"""
        return [err for err in self.active_errors if not err.resolved]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        active_errors = self.get_active_errors()
        
        critical_errors = sum(1 for err in active_errors if err.severity == ErrorSeverity.CRITICAL)
        high_errors = sum(1 for err in active_errors if err.severity == ErrorSeverity.HIGH)
        medium_errors = sum(1 for err in active_errors if err.severity == ErrorSeverity.MEDIUM)
        low_errors = sum(1 for err in active_errors if err.severity == ErrorSeverity.LOW)
        
        # Determine overall health
        if critical_errors > 0:
            health_status = "CRITICAL"
        elif high_errors > 0:
            health_status = "UNSTABLE"
        elif high_errors + medium_errors > 0:
            health_status = "CAUTION"
        else:
            health_status = "HEALTHY"
        
        return {
            "status": health_status,
            "active_errors": len(active_errors),
            "critical_errors": critical_errors,
            "high_errors": high_errors,
            "medium_errors": medium_errors,
            "low_errors": low_errors,
            "total_errors": len(self.error_history),
            "timestamp": __import__('time').time()
        }
    
    def get_component_health(self, component: SystemComponent) -> Dict[str, Any]:
        """Get health status for a specific component"""
        active_errors = [err for err in self.active_errors if err.component == component]
        
        severity_counts = {
            ErrorSeverity.CRITICAL: 0,
            ErrorSeverity.HIGH: 0,
            ErrorSeverity.MEDIUM: 0,
            ErrorSeverity.LOW: 0
        }
        
        for error in active_errors:
            severity_counts[error.severity] += 1
        
        # Determine component health
        if severity_counts[ErrorSeverity.CRITICAL] > 0:
            comp_health = "CRITICAL"
        elif severity_counts[ErrorSeverity.HIGH] > 0:
            comp_health = "UNSTABLE" 
        elif severity_counts[ErrorSeverity.HIGH] + severity_counts[ErrorSeverity.MEDIUM] > 0:
            comp_health = "CAUTION"
        else:
            comp_health = "HEALTHY"
        
        return {
            "component": component.value,
            "health_status": comp_health,
            "active_errors": severity_counts,
            "last_error_time": max([err.timestamp for err in active_errors], default=0),
            "total_errors": sum(1 for err in self.error_history if err.component == component)
        }