---
title: 'Chapter 12 - Voice-to-Action Pipelines (Whisper + LLMs)'
description: 'Building voice-controlled robot systems using Whisper and Large Language Models'
---

# Chapter 12: Voice-to-Action Pipelines (Whisper + LLMs)

## Learning Objectives

After reading this chapter, you will be able to:
- Understand the architecture of voice-to-action systems for robotics
- Integrate speech recognition (Whisper) with robotic control
- Connect Large Language Models (LLMs) for natural language understanding
- Design multimodal interaction systems combining voice and vision
- Implement context-aware voice command interpretation
- Evaluate and optimize voice-based robot control systems
- Handle edge cases and error recovery in voice interfaces

## Introduction

Voice-to-action systems enable robots to understand and respond to natural human language, creating intuitive interfaces between humans and robots. By combining automatic speech recognition (ASR) with Large Language Models (LLMs), robots can interpret complex verbal commands and translate them into executable actions. This chapter explores how to build systems that can listen to user commands, understand their intent, and execute appropriate robotic behaviors.

## Architecture of Voice-to-Action Systems

### System Components

A complete voice-to-action system typically comprises:

1. **Audio Input Processing**: Capturing and preprocessing audio signals
2. **Speech Recognition**: Converting speech to text (Whisper)
3. **Natural Language Understanding**: Interpreting text commands (LLM)
4. **Action Planning**: Translating intent into robot actions
5. **Execution and Feedback**: Performing actions and providing feedback

### Interaction Flow

The typical flow in a voice-to-action system:

```
User speaks -> Audio capture -> ASR -> Text -> NLU -> Intent -> Action -> Execution
                ↓                                     ↓
            Preprocessing                        Planning
```

## Speech Recognition with Whisper

### Whisper Fundamentals

Whisper is OpenAI's robust speech recognition model that can handle multiple languages and various acoustic conditions. It's particularly useful for robotics applications because:

- **Multilingual Support**: Understands multiple languages
- **Robustness**: Handles background noise and accents
- **Timestamps**: Provides temporal alignment of speech
- **Punctuation**: Adds punctuation to transcribed text

### Whisper Integration

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from audio_common_msgs.msg import AudioData
from sensor_msgs.msg import Image
import whisper
import torch
import pyaudio
import wave
import numpy as np
from queue import Queue
import threading
import time


class WhisperASRNode(Node):
    def __init__(self):
        super().__init__('whisper_asr')
        
        # Initialize Whisper model
        # Choose model size based on hardware constraints
        model_size = "medium"  # Options: tiny, base, small, medium, large
        self.get_logger().info(f"Loading Whisper model: {model_size}")
        
        try:
            if torch.cuda.is_available():
                self.model = whisper.load_model(model_size).cuda()
                self.get_logger().info("Whisper loaded on GPU")
            else:
                self.model = whisper.load_model(model_size)
                self.get_logger().info("Whisper loaded on CPU")
        except Exception as e:
            self.get_logger().error(f"Failed to load Whisper model: {e}")
            self.model = None
            return
        
        # Audio parameters
        self.rate = 16000  # Sample rate
        self.chunk_size = 1024  # Frames per buffer
        self.channels = 1  # Mono
        self.format = pyaudio.paInt16
        self.audio_queue = Queue()
        
        # Voice activity detection parameters
        self.energy_threshold = 0.01
        self.silence_duration = 1.0  # Seconds of silence to stop recording
        
        # Publishers and subscribers
        self.transcript_pub = self.create_publisher(String, '/voice_transcript', 10)
        self.command_pub = self.create_publisher(String, '/voice_command', 10)
        
        # Audio stream
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Start audio recording thread
        self.recording = False
        self.record_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.record_thread.start()
        
        # Timer for processing audio chunks
        self.process_timer = self.create_timer(0.1, self.process_audio_queue)
        
        self.get_logger().info("Whisper ASR node initialized")
    
    def start_listening(self):
        """Start listening for audio input"""
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size
        )
        
        self.recording = True
        self.get_logger().info("Started listening for voice commands")
    
    def stop_listening(self):
        """Stop listening for audio input"""
        self.recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.get_logger().info("Stopped listening for voice commands")
    
    def detect_voice_activity(self, audio_data):
        """Simple energy-based voice activity detection"""
        # Convert bytes to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Calculate energy
        energy = np.mean(audio_array ** 2)
        
        return energy > self.energy_threshold
    
    def record_audio(self):
        """Record audio in a separate thread"""
        if self.stream is None:
            self.start_listening()
        
        silence_counter = 0
        recording_chunks = []
        recording = False
        
        while rclpy.ok():
            if self.recording and self.stream and not self.stream.is_stopped():
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Check for voice activity
                if self.detect_voice_activity(data):
                    # Voice detected, start/end recording
                    if not recording:
                        self.get_logger().info("Voice activity detected, starting recording...")
                        recording = True
                        recording_chunks = [data]
                        silence_counter = 0
                    else:
                        # Continue recording
                        recording_chunks.append(data)
                        silence_counter = 0
                else:
                    # No voice activity
                    if recording:
                        silence_counter += self.chunk_size / self.rate  # Increment by chunk duration
                        
                        if silence_counter >= self.silence_duration:
                            # Silence duration reached, stop recording
                            self.get_logger().info(f"Silence detected, stopping recording after {silence_counter:.2f}s")
                            
                            # Save recorded audio to WAV for processing
                            if recording_chunks:
                                self.save_audio_chunk(recording_chunks)
                            
                            recording = False
            else:
                time.sleep(0.1)  # Polling interval when not recording
    
    def save_audio_chunk(self, audio_chunks):
        """Save audio chunks to a temporary WAV file for Whisper processing"""
        if not audio_chunks:
            return
        
        # Concatenate all audio chunks
        full_audio = b''.join(audio_chunks)
        
        # Save to temporary WAV file
        filename = f"/tmp/recording_{int(time.time())}.wav"
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(full_audio)
        wf.close()
        
        # Add to processing queue
        self.audio_queue.put(filename)
    
    def process_audio_queue(self):
        """Process audio files from the queue"""
        try:
            if not self.audio_queue.empty():
                audio_file = self.audio_queue.get_nowait()
                
                # Process audio with Whisper
                transcription = self.transcribe_audio(audio_file)
                
                if transcription:
                    # Publish transcription
                    transcript_msg = String()
                    transcript_msg.data = transcription
                    self.transcript_pub.publish(transcript_msg)
                    
                    self.get_logger().info(f"Transcribed: '{transcription}'")
                    
                    # Remove temp file
                    import os
                    os.remove(audio_file)
                
        except Exception as e:
            self.get_logger().error(f"Error processing audio: {e}")
    
    def transcribe_audio(self, audio_file):
        """Transcribe audio using Whisper model"""
        if self.model is None:
            return None
        
        try:
            # Load audio file
            audio = whisper.load_audio(audio_file)
            audio = whisper.pad_or_trim(audio)
            
            # Convert to log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Decode audio
            options = whisper.DecodingOptions(fp16=torch.cuda.is_available())
            result = whisper.decode(self.model, mel, options)
            
            return result.text
        
        except Exception as e:
            self.get_logger().error(f"Error during transcription: {e}")
            return None


def main(args=None):
    rclpy.init(args=args)
    asr_node = WhisperASRNode()
    
    try:
        asr_node.start_listening()
        rclpy.spin(asr_node)
    except KeyboardInterrupt:
        pass
    finally:
        asr_node.stop_listening()
        asr_node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

### Optimizing Whisper for Robotics

For real-time robotics applications, Whisper can be optimized in several ways:

```python
# whisper_optimizer.py
import whisper
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


class OptimizedWhisper:
    def __init__(self, model_size="medium"):
        # Load model with optimizations
        self.model = whisper.load_model(model_size)
        
        # Use mixed precision for faster inference on supported hardware
        if torch.cuda.is_available():
            self.model = self.model.half()  # FP16 precision
            self.device = "cuda"
        else:
            self.device = "cpu"
        
        self.model.to(self.device)
        
        # Warm up the model
        self.warmup()
    
    def warmup(self):
        """Warm up the model to improve first inference speed"""
        dummy_audio = torch.zeros(16000 * 2).to(self.device)  # 2 seconds of silence
        mel = whisper.log_mel_spectrogram(dummy_audio).to(self.device)
        
        options = whisper.DecodingOptions(fp16=torch.cuda.is_available())
        whisper.decode(self.model, mel, options)
    
    def transcribe_with_options(self, audio_path, language="en", task="transcribe"):
        """Transcribe with specific options for better accuracy"""
        # Load and preprocess audio
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        
        # Convert to Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(self.device)
        
        # Create decoding options with specific settings
        options = whisper.DecodingOptions(
            language=language,
            task=task,
            fp16=torch.cuda.is_available(),
            without_timestamps=True  # For faster processing
        )
        
        result = whisper.decode(self.model, mel, options)
        return result.text
    
    def batch_transcribe(self, audio_files):
        """Transcribe multiple audio files efficiently"""
        results = []
        for file_path in audio_files:
            result = self.transcribe_with_options(file_path)
            results.append(result)
        return results


# Usage
optimized_whisper = OptimizedWhisper(model_size="small")  # Small model for faster robotics response
```

## Natural Language Understanding with LLMs

### LLM Integration for Intent Recognition

```python
import openai
import json
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class RobotIntent:
    action: str
    parameters: Dict[str, any]
    confidence: float
    raw_command: str


class LLMNLU:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        openai.api_key = api_key
        self.model = model
        
        # Define robot actions schema
        self.actions_schema = {
            "move_forward": {
                "description": "Move robot forward",
                "parameters": {
                    "distance": {"type": "number", "description": "Distance to move in meters"},
                    "speed": {"type": "number", "description": "Speed (0.1 to 1.0)"}
                }
            },
            "move_backward": {
                "description": "Move robot backward",
                "parameters": {
                    "distance": {"type": "number", "description": "Distance to move in meters"},
                    "speed": {"type": "number", "description": "Speed (0.1 to 1.0)"}
                }
            },
            "turn_left": {
                "description": "Turn robot left",
                "parameters": {
                    "angle": {"type": "number", "description": "Angle to turn in degrees"},
                    "speed": {"type": "number", "description": "Turning speed (0.1 to 1.0)"}
                }
            },
            "turn_right": {
                "description": "Turn robot right",
                "parameters": {
                    "angle": {"type": "number", "description": "Angle to turn in degrees"},
                    "speed": {"type": "number", "description": "Turning speed (0.1 to 1.0)"}
                }
            },
            "pick_up": {
                "description": "Pick up an object",
                "parameters": {
                    "object_id": {"type": "string", "description": "Identifier of object to pick up"},
                    "position": {"type": "object", "description": "Position where object is located", 
                                 "properties": {"x": {"type": "number"}, "y": {"type": "number"}}}
                }
            },
            "place_down": {
                "description": "Place an object down",
                "parameters": {
                    "position": {"type": "object", "description": "Position to place object", 
                                 "properties": {"x": {"type": "number"}, "y": {"type": "number"}}}
                }
            },
            "go_to_location": {
                "description": "Navigate robot to a specific location",
                "parameters": {
                    "location": {"type": "string", "description": "Named location or coordinates"},
                    "speed": {"type": "number", "description": "Navigation speed (0.1 to 1.0)"}
                }
            },
            "find_object": {
                "description": "Look for a specific object",
                "parameters": {
                    "object_type": {"type": "string", "description": "Type of object to find"}
                }
            }
        }
    
    def recognize_intent(self, text: str, robot_context: Dict = None) -> Optional[RobotIntent]:
        """Recognize intent from text using LLM"""
        if robot_context is None:
            robot_context = {}
        
        # Format the prompt with the available actions and context
        actions_list = ", ".join(list(self.actions_schema.keys()))
        
        prompt = f"""
        You are a natural language understanding system for a robot.
        Based on the user's command, identify the appropriate action and extract relevant parameters.
        
        Available actions: {actions_list}
        
        Robot context: {json.dumps(robot_context)}
        
        User command: "{text}"
        
        Respond with a JSON object containing:
        {{
            "action": "the identified action",
            "parameters": {{"param1": "value1", "param2": "value2"}},
            "confidence": likelihood that this interpretation is correct (0.0 to 1.0)
        }}
        
        If the command cannot be interpreted as a robot action, set action to "unknown".
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that translates natural language commands into structured robot actions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent outputs
                max_tokens=200
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse the JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_response = json.loads(json_str)
                
                return RobotIntent(
                    action=parsed_response.get('action', 'unknown'),
                    parameters=parsed_response.get('parameters', {}),
                    confidence=min(1.0, float(parsed_response.get('confidence', 0.0))),
                    raw_command=text
                )
            else:
                # If parsing fails, try to extract action from plain text
                return self.parse_action_from_text(text)
        
        except Exception as e:
            self.logger.error(f"Error in NLU: {e}")
            return None
    
    def parse_action_from_text(self, text: str) -> Optional[RobotIntent]:
        """Fallback method to extract simple actions from text"""
        text_lower = text.lower()
        
        # Simple keyword matching as fallback
        if 'forward' in text_lower or 'ahead' in text_lower or 'go' in text_lower:
            return RobotIntent('move_forward', {'distance': 1.0}, 0.8, text)
        elif 'backward' in text_lower or 'back' in text_lower:
            return RobotIntent('move_backward', {'distance': 1.0}, 0.8, text)
        elif 'left' in text_lower and ('turn' in text_lower or 'rotate' in text_lower):
            return RobotIntent('turn_left', {'angle': 90}, 0.8, text)
        elif 'right' in text_lower and ('turn' in text_lower or 'rotate' in text_lower):
            return RobotIntent('turn_right', {'angle': 90}, 0.8, text)
        elif 'pick' in text_lower or 'grasp' in text_lower or 'grab' in text_lower:
            return RobotIntent('pick_up', {'object_id': 'target'}, 0.8, text)
        elif 'place' in text_lower or 'put' in text_lower:
            return RobotIntent('place_down', {}, 0.8, text)
        elif 'go to' in text_lower or 'navigate to' in text_lower:
            return RobotIntent('go_to_location', {'location': 'target'}, 0.8, text)
        elif 'find' in text_lower or 'look for' in text_lower:
            return RobotIntent('find_object', {'object_type': 'target'}, 0.8, text)
        
        return RobotIntent('unknown', {}, 0.0, text)


# Example usage
def main():
    # Initialize LLM NLU
    nlu = LLMNLU(api_key="your-openai-api-key")
    
    # Example commands
    commands = [
        "Move forward 2 meters",
        "Turn left by 45 degrees",
        "Find the red ball",
        "Go to the kitchen",
        "Pick up the coffee cup"
    ]
    
    robot_context = {
        "current_location": "living_room",
        "battery_level": 0.85,
        "objects_detected": ["ball", "cup", "chair"]
    }
    
    for cmd in commands:
        intent = nlu.recognize_intent(cmd, robot_context)
        if intent:
            print(f"Command: '{cmd}' -> Action: '{intent.action}', Params: {intent.parameters}, Confidence: {intent.confidence}")
        else:
            print(f"Could not parse command: '{cmd}'")


if __name__ == "__main__":
    main()
```

## Multimodal Integration

### Combining Voice and Vision

For more sophisticated robot control, voice commands can be combined with visual information:

```python
# multimodal_integration.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from vision_msgs.msg import Detection2DArray
from geometry_msgs.msg import Point
from cv_bridge import CvBridge
import json


class MultimodalVoiceControlNode(Node):
    def __init__(self):
        super().__init__('multimodal_voice_control')
        
        # Initialize components
        self.bridge = CvBridge()
        self.llm_nlu = LLMNLU(api_key=self.get_parameter('openai_api_key').value)  # Requires parameter
        
        # Robot state
        self.current_objects = {}
        self.robot_pose = None
        self.last_image = None
        
        # Subscribers
        self.voice_sub = self.create_subscription(
            String, '/voice_transcript', self.voice_callback, 10
        )
        
        self.image_sub = self.create_subscription(
            Image, '/camera/rgb/image_raw', self.image_callback, 10
        )
        
        self.detection_sub = self.create_subscription(
            Detection2DArray, '/object_detections', self.detection_callback, 10
        )
        
        # Publishers
        self.command_pub = self.create_publisher(String, '/robot_command', 10)
        self.action_request_pub = self.create_publisher(String, '/action_requests', 10)
        
        self.get_logger().info("Multimodal Voice Control Node initialized")
    
    def image_callback(self, msg):
        """Process incoming images"""
        try:
            self.last_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as e:
            self.get_logger().error(f"Error processing image: {e}")
    
    def detection_callback(self, msg):
        """Process object detections"""
        for detection in msg.detections:
            # Update current objects with detection info
            object_id = detection.results[0].id if detection.results else "unknown"
            confidence = detection.results[0].score if detection.results else 0
            
            if confidence > 0.5:  # Only store confident detections
                self.current_objects[object_id] = {
                    'bbox': detection.bbox,
                    'center': Point(
                        x=detection.bbox.center.x,
                        y=detection.bbox.center.y,
                        z=0.0  # Will be set from depth
                    ),
                    'confidence': confidence
                }
    
    def voice_callback(self, msg):
        """Process voice command"""
        command_text = msg.data
        
        self.get_logger().info(f"Processing voice command: '{command_text}'")
        
        # Get current robot context
        robot_context = self.build_robot_context()
        
        # Recognize intent using LLM
        intent = self.llm_nlu.recognize_intent(command_text, robot_context)
        
        if intent and intent.confidence > 0.7:
            # Process the intent with multimodal context
            self.process_intent_multimodal(intent)
        else:
            self.get_logger().warn(f"Low confidence intent recognition for: '{command_text}' (confidence: {intent.confidence if intent else 0})")
    
    def build_robot_context(self):
        """Build context including visual information"""
        context = {
            'current_objects': {},
            'robot_pose': self.robot_pose,
            'current_location': self.get_current_location(),
        }
        
        # Add object information from detections
        for obj_id, obj_info in self.current_objects.items():
            context['current_objects'][obj_id] = {
                'bbox_center_x': obj_info['center'].x,
                'bbox_center_y': obj_info['center'].y,
                'confidence': obj_info['confidence']
            }
        
        # Add more context as needed
        return context
    
    def process_intent_multimodal(self, intent):
        """Process intent using multimodal context"""
        if intent.action == 'pick_up':
            # Handle pick up command with visual context
            self.handle_pick_up_command(intent)
        elif intent.action == 'find_object':
            # Handle find object command with visual context
            self.handle_find_object_command(intent)
        elif intent.action == 'go_to_location':
            # Handle navigation command
            self.handle_go_to_location_command(intent)
        else:
            # Handle other commands
            self.publish_action_request(intent)
    
    def handle_pick_up_command(self, intent):
        """Handle pick up command with visual context"""
        # Determine which object to pick up based on command and visual context
        object_desc = intent.parameters.get('object_id', '').lower()
        
        # Find matching object in current view
        best_match = self.find_matching_object(object_desc)
        
        if best_match:
            # Convert image coordinates to world coordinates if possible
            world_coords = self.convert_image_to_world(best_match['center'])
            
            # Create pick-up action with precise coordinates
            pick_action = {
                'action': 'pick_up',
                'object_id': best_match['object_id'],
                'position': {
                    'x': float(world_coords[0]),
                    'y': float(world_coords[1]), 
                    'z': float(world_coords[2])
                },
                'raw_command': intent.raw_command
            }
            
            action_msg = String()
            action_msg.data = json.dumps(pick_action)
            self.action_request_pub.publish(action_msg)
            
            self.get_logger().info(f"Sending pick-up request for {best_match['object_id']} at {world_coords}")
        else:
            # Object not found in view, request to look around
            search_action = {
                'action': 'search_for_object',
                'object_type': object_desc,
                'raw_command': intent.raw_command
            }
            
            action_msg = String()
            action_msg.data = json.dumps(search_action)
            self.action_request_pub.publish(action_msg)
            
            self.get_logger().info(f"Object '{object_desc}' not found in view, initiating search")
    
    def handle_find_object_command(self, intent):
        """Handle find object command"""
        object_type = intent.parameters.get('object_type', '').lower()
        
        # Check if object is already in view
        if object_type in self.current_objects:
            object_info = self.current_objects[object_type]
            self.get_logger().info(f"Found {object_type} in current view at position {object_info['center']}")
            
            # Provide feedback to user
            feedback = f"I can see the {object_type} in front of me."
            self.provide_voice_feedback(feedback)
        else:
            # Object not in view, initiate search
            self.initiate_object_search(object_type)
    
    def handle_go_to_location_command(self, intent):
        """Handle navigation command"""
        location = intent.parameters.get('location', '').lower()
        
        # Convert location to coordinates (this would use a map)
        coords = self.location_to_coordinates(location)
        
        if coords:
            # Create navigation action
            nav_action = {
                'action': 'go_to_location',
                'coordinates': coords,
                'location_name': location,
                'raw_command': intent.raw_command
            }
            
            action_msg = String()
            action_msg.data = json.dumps(nav_action)
            self.action_request_pub.publish(action_msg)
            
            self.get_logger().info(f"Navigating to {location} at coordinates {coords}")
        else:
            self.get_logger().warn(f"Unknown location: {location}")
            self.provide_voice_feedback(f"I don't know where {location} is.")
    
    def find_matching_object(self, description):
        """Find object in current view matching the description"""
        # This could use more sophisticated matching
        for obj_id, obj_info in self.current_objects.items():
            if description in obj_id.lower() or obj_id.lower() in description:
                return {
                    'object_id': obj_id,
                    'center': obj_info['center'],
                    'confidence': obj_info['confidence']
                }
        
        # If no exact match, use LLM to find semantic match
        return self.semantic_object_matching(description)
    
    def semantic_object_matching(self, description):
        """Use LLM to match object description semantically"""
        # In practice, this would use an LLM to understand semantic similarity
        # between the description and detected objects
        if self.current_objects:
            # Just return the first detected object as a fallback
            obj_id = list(self.current_objects.keys())[0]
            obj_info = self.current_objects[obj_id]
            return {
                'object_id': obj_id,
                'center': obj_info['center'],
                'confidence': obj_info['confidence']
            }
        return None
    
    def convert_image_to_world(self, image_point):
        """Convert image coordinates to world coordinates"""
        # This would require depth information and camera calibration
        # For now, return placeholder coordinates
        # Implementation would use depth image and camera matrix
        return [image_point.x * 0.001, image_point.y * 0.001, 1.0]  # Placeholder
    
    def location_to_coordinates(self, location_name):
        """Convert location name to coordinates"""
        # This would use a map of known locations
        # For now, return some predefined coordinates
        location_coords = {
            'kitchen': [3.0, 1.0, 0.0],
            'bedroom': [-2.0, 2.0, 0.0],
            'living room': [0.0, 0.0, 0.0],
            'office': [-1.0, -1.5, 0.0]
        }
        
        return location_coords.get(location_name.lower())
    
    def initiate_object_search(self, object_type):
        """Initiate search for object"""
        search_action = {
            'action': 'search_for_object',
            'object_type': object_type
        }
        
        action_msg = String()
        action_msg.data = json.dumps(search_action)
        self.action_request_pub.publish(action_msg)
    
    def provide_voice_feedback(self, text):
        """Provide voice feedback to user (would interface with TTS)"""
        # In a real system, this would connect to a text-to-speech system
        self.get_logger().info(f"Voice feedback: {text}")


def main(args=None):
    rclpy.init(args=args)
    node = MultimodalVoiceControlNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Action Planning and Execution

### Converting LLM Output to Robot Actions

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav_msgs.msg import Path
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from std_msgs.msg import String, Bool
from builtin_interfaces.msg import Duration
import json


class ActionPlannerNode(Node):
    def __init__(self):
        super().__init__('action_planner')
        
        # Robot capabilities
        self.robot_capabilities = {
            'navigation': True,
            'manipulation': True,
            'grasping': True,
            'speech': True
        }
        
        # Current robot state
        self.current_pose = None
        self.is_moving = False
        self.is_manipulating = False
        
        # Subscribers
        self.action_sub = self.create_subscription(
            String, '/action_requests', self.action_request_callback, 10
        )
        
        self.pose_sub = self.create_subscription(
            PoseStamped, '/robot_pose', self.pose_callback, 10
        )
        
        # Publishers
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.nav_goal_pub = self.create_publisher(PoseStamped, '/move_base_simple/goal', 10)
        self.joint_traj_pub = self.create_publisher(JointTrajectory, '/joint_trajectory', 10)
        self.speech_pub = self.create_publisher(String, '/speech_commands', 10)
        
        # Service clients for complex actions
        self.grasp_client = None  # Would be initialized as a service client
        
        self.get_logger().info("Action Planner Node initialized")
    
    def action_request_callback(self, msg):
        """Process action requests from voice understanding"""
        try:
            action_data = json.loads(msg.data)
            action_type = action_data.get('action')
            
            self.get_logger().info(f"Received action: {action_type}")
            
            if action_type == 'move_forward':
                self.execute_move_forward(action_data)
            elif action_type == 'move_backward':
                self.execute_move_backward(action_data)
            elif action_type == 'turn_left':
                self.execute_turn_left(action_data)
            elif action_type == 'turn_right':
                self.execute_turn_right(action_data)
            elif action_type == 'go_to_location':
                self.execute_go_to_location(action_data)
            elif action_type == 'pick_up':
                self.execute_pick_up(action_data)
            elif action_type == 'place_down':
                self.execute_place_down(action_data)
            elif action_type == 'search_for_object':
                self.execute_search_for_object(action_data)
            else:
                self.get_logger().warn(f"Unknown action type: {action_type}")
                self.provide_feedback(f"Sorry, I don't know how to {action_type}")
                
        except json.JSONDecodeError:
            self.get_logger().error(f"Invalid JSON in action request: {msg.data}")
        except Exception as e:
            self.get_logger().error(f"Error processing action request: {e}")
    
    def pose_callback(self, msg):
        """Update current robot pose"""
        self.current_pose = msg.pose
    
    def execute_move_forward(self, action_data):
        """Execute forward movement"""
        distance = action_data.get('parameters', {}).get('distance', 1.0)
        speed = action_data.get('parameters', {}).get('speed', 0.3)
        
        # Simple implementation - in practice, this would use navigation stack
        twist = Twist()
        twist.linear.x = speed  # Move forward at specified speed
        twist.angular.z = 0.0
        
        # Calculate how long to maintain this velocity to travel the distance
        duration = distance / speed
        
        # Execute movement for calculated duration
        self.is_moving = True
        self.move_robot(twist, duration)
        self.is_moving = False
    
    def execute_move_backward(self, action_data):
        """Execute backward movement"""
        distance = action_data.get('parameters', {}).get('distance', 1.0)
        speed = action_data.get('parameters', {}).get('speed', 0.3)
        
        twist = Twist()
        twist.linear.x = -speed  # Move backward
        twist.angular.z = 0.0
        
        duration = distance / speed
        
        self.is_moving = True
        self.move_robot(twist, duration)
        self.is_moving = False
    
    def execute_turn_left(self, action_data):
        """Execute left turn"""
        angle_deg = action_data.get('parameters', {}).get('angle', 90)
        speed = action_data.get('parameters', {}).get('speed', 0.2)
        
        # Convert angle to radians
        angle_rad = angle_deg * 3.14159 / 180.0
        
        # Simple turn implementation (would use proper rotation in practice)
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = speed  # Turn left (positive angular velocity)
        
        # Estimate duration based on turn speed
        duration = angle_rad / speed
        
        self.is_moving = True
        self.move_robot(twist, duration)
        self.is_moving = False
    
    def execute_turn_right(self, action_data):
        """Execute right turn"""
        angle_deg = action_data.get('parameters', {}).get('angle', 90)
        speed = action_data.get('parameters', {}).get('speed', 0.2)
        
        angle_rad = angle_deg * 3.14159 / 180.0
        
        twist = Twist()
        twist.linear.x = 0.0
        twist.angular.z = -speed  # Turn right (negative angular velocity)
        
        duration = angle_rad / speed
        
        self.is_moving = True
        self.move_robot(twist, duration)
        self.is_moving = False
    
    def execute_go_to_location(self, action_data):
        """Execute navigation to location"""
        coordinates = action_data.get('coordinates')
        location_name = action_data.get('location_name', 'target')
        
        if coordinates:
            # Create navigation goal
            goal = PoseStamped()
            goal.header.frame_id = 'map'
            goal.header.stamp = self.get_clock().now().to_msg()
            goal.pose.position.x = coordinates[0]
            goal.pose.position.y = coordinates[1]
            goal.pose.position.z = coordinates[2] if len(coordinates) > 2 else 0.0
            
            # Set orientation to face forward (optional)
            goal.pose.orientation.w = 1.0
            
            self.nav_goal_pub.publish(goal)
            self.provide_feedback(f"Going to {location_name}")
        else:
            self.provide_feedback(f"Sorry, I don't know where {location_name} is")
    
    def execute_pick_up(self, action_data):
        """Execute pick-up action"""
        obj_id = action_data.get('object_id')
        position = action_data.get('position', {})
        
        if position:
            # This would involve complex manipulation planning
            # 1. Navigate to object position
            # 2. Plan grasp trajectory
            # 3. Execute grasp
            
            self.get_logger().info(f"Attempting to pick up object {obj_id} at {position}")
            
            # For now, just acknowledge the command
            self.provide_feedback(f"Picking up the {obj_id}")
        else:
            self.provide_feedback(f"Position not specified for {obj_id}")
    
    def execute_place_down(self, action_data):
        """Execute place-down action"""
        position = action_data.get('position', {})
        
        if position:
            # Would execute place-down maneuver
            self.get_logger().info(f"Placing object down at {position}")
            self.provide_feedback("Putting object down")
        else:
            # Use current position
            if self.current_pose:
                pos = self.current_pose.position
                self.get_logger().info(f"Placing object down at current position ({pos.x}, {pos.y}, {pos.z})")
                self.provide_feedback("Putting object down")
            else:
                self.provide_feedback("I don't know where to put it down")
    
    def execute_search_for_object(self, action_data):
        """Execute search for object action"""
        obj_type = action_data.get('object_type', 'object')
        
        self.get_logger().info(f"Searching for {obj_type}")
        
        # This would implement search pattern (turn and look around, move to different viewpoints)
        # For now, just acknowledge
        search_pattern = [
            {'action': 'turn', 'angle': 45},
            {'action': 'turn', 'angle': -90},
            {'action': 'turn', 'angle': 45}
        ]
        
        self.provide_feedback(f"Looking for the {obj_type}")
        
        # Execute search pattern
        for cmd in search_pattern:
            if cmd['action'] == 'turn':
                twist = Twist()
                twist.linear.x = 0.0
                twist.angular.z = cmd['angle'] * 3.14159 / 180.0 / 2.0  # Convert to angular velocity
                
                self.move_robot(twist, 2.0)  # Turn for 2 seconds
    
    def move_robot(self, twist_cmd, duration):
        """Execute movement command for specified duration"""
        timer = self.create_timer(0.1, lambda: self.publish_twist(twist_cmd))
        
        # Wait for the duration
        start_time = self.get_clock().now()
        while (self.get_clock().now() - start_time).nanoseconds < duration * 1e9:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        # Stop the robot
        stop_cmd = Twist()
        self.publish_twist(stop_cmd)
        timer.cancel()
    
    def publish_twist(self, twist_cmd):
        """Publish twist command to robot"""
        self.cmd_vel_pub.publish(twist_cmd)
    
    def provide_feedback(self, text):
        """Provide feedback through speech"""
        speech_msg = String()
        speech_msg.data = text
        self.speech_pub.publish(speech_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ActionPlannerNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
```

## Voice Interaction Design Patterns

### Context Management

Effective voice-to-action systems maintain context across interactions:

```python
# context_manager.py
import time
from typing import Dict, Any, Optional


class InteractionContext:
    def __init__(self):
        self.conversation_history = []
        self.current_intent = None
        self.pending_actions = []
        self.user_preferences = {}
        self.robot_state = {}
        self.last_interaction_time = time.time()
        self.context_timeout = 300  # 5 minutes timeout
    
    def add_interaction(self, user_input: str, robot_response: str, intent: Dict[str, Any]):
        """Add interaction to conversation history"""
        interaction = {
            'timestamp': time.time(),
            'user_input': user_input,
            'robot_response': robot_response,
            'intent': intent,
            'context_snapshot': self.get_context_snapshot()
        }
        
        self.conversation_history.append(interaction)
        
        # Trim history if it gets too long
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-20:]  # Keep last 20 interactions
        
        self.last_interaction_time = time.time()
    
    def get_context_snapshot(self) -> Dict[str, Any]:
        """Get current state snapshot for LLM context"""
        return {
            'current_intent': self.current_intent,
            'pending_actions': self.pending_actions,
            'user_preferences': self.user_preferences,
            'robot_state': self.robot_state,
            'recent_interactions': self.get_recent_interactions(3)  # Last 3 interactions
        }
    
    def get_recent_interactions(self, count: int) -> list:
        """Get recent interactions for context"""
        # Return last 'count' interactions
        return self.conversation_history[-count:] if len(self.conversation_history) >= count else self.conversation_history[:]
    
    def update_robot_state(self, new_state: Dict[str, Any]):
        """Update robot state in context"""
        self.robot_state.update(new_state)
    
    def set_pending_action(self, action: Dict[str, Any]):
        """Set pending action in context"""
        self.pending_actions.append(action)
    
    def clear_pending_actions(self):
        """Clear all pending actions"""
        self.pending_actions.clear()
    
    def is_context_valid(self) -> bool:
        """Check if context is still valid (not timed out)"""
        return (time.time() - self.last_interaction_time) < self.context_timeout


class ContextAwareNLU:
    def __init__(self, api_key: str):
        self.llm_nlu = LLMNLU(api_key)
        self.interaction_context = InteractionContext()
    
    def process_command_with_context(self, command: str, robot_state: Dict[str, Any] = None) -> Optional[RobotIntent]:
        """Process command considering conversation context"""
        # Update robot state in context
        if robot_state:
            self.interaction_context.update_robot_state(robot_state)
        
        # Build enhanced context with history
        enhanced_context = self.interaction_context.get_context_snapshot()
        
        # Add recent interactions to context
        recent_interactions = self.interaction_context.get_recent_interactions(5)
        enhanced_context['recent_dialogue'] = [f"User: {i['user_input']}, Robot: {i['robot_response']}" 
                                               for i in recent_interactions]
        
        # Process command with context
        intent = self.llm_nlu.recognize_intent(command, enhanced_context)
        
        # Update context with new interaction
        if intent:
            response_text = self.generate_response(intent)
            self.interaction_context.add_interaction(command, response_text, intent.__dict__ if intent else {})
        
        return intent
    
    def generate_response(self, intent: RobotIntent) -> str:
        """Generate appropriate response based on intent"""
        responses = {
            'move_forward': "Moving forward",
            'move_backward': "Moving backward",
            'turn_left': "Turning left",
            'turn_right': "Turning right",
            'pick_up': f"Picking up the {intent.parameters.get('object_id', 'object')}",
            'place_down': "Placing the object down",
            'go_to_location': f"Going to {intent.parameters.get('location', 'the location')}",
            'find_object': f"Looking for {intent.parameters.get('object_type', 'an object')}",
            'unknown': "I didn't understand that command"
        }
        
        return responses.get(intent.action, f"Performing {intent.action}")
    
    def resolve_anaphora(self, text: str) -> str:
        """Resolve pronouns and references in the current context"""
        # This would implement pronoun resolution
        # For example: "it" -> refers to last mentioned object
        # "there" -> refers to location mentioned previously
        # Implementation would use the conversation history
        return text


# Example usage
def main():
    # Initialize system
    context_nlu = ContextAwareNLU("your-openai-api-key")
    
    # Simulate conversation
    conversations = [
        ("Go to the kitchen", {"current_location": "living_room"}),
        ("Find the red ball", {"current_location": "kitchen", "objects_detected": ["ball", "cup"]}),
        ("Pick it up", {"current_location": "kitchen", "objects_detected": ["red ball", "cup"], "holding_object": False})
    ]
    
    for command, robot_state in conversations:
        intent = context_nlu.process_command_with_context(command, robot_state)
        print(f"Command: '{command}' -> Action: '{intent.action if intent else 'None'}'")


if __name__ == "__main__":
    main()
```

## Performance Optimization and Error Handling

### Handling Common Voice Interface Issues

```python
# error_handling.py
import asyncio
import numpy as np


class VoiceInterfaceErrorHandler:
    def __init__(self):
        self.error_recovery_strategies = {
            'unclear_command': self.ask_for_clarification,
            'unknown_action': self.suggest_alternatives,
            'execution_failure': self.retry_or_alternative,
            'context_confusion': self.reset_context
        }
    
    def handle_asr_error(self, error_type: str, context: Dict[str, Any] = None):
        """Handle automatic speech recognition errors"""
        if error_type == 'low_audio_quality':
            # Ask user to speak louder or clearer
            return "I'm having trouble hearing you. Could you speak louder or closer to the microphone?"
        elif error_type == 'background_noise':
            return "There's too much background noise. Could you speak again when it's quieter?"
        elif error_type == 'partial_recognition':
            # Try to infer from partial recognition
            partial_text = context.get('partial_text', '')
            return f"Did you mean something like: {partial_text}?"
        return "I didn't catch that. Could you repeat your command?"
    
    def handle_nlu_error(self, command: str, recognized_intent: RobotIntent = None):
        """Handle natural language understanding errors"""
        if recognized_intent and recognized_intent.confidence < 0.3:
            return f"I'm not sure what you mean by '{command}'. Could you rephrase that?"
        elif recognized_intent is None or recognized_intent.action == 'unknown':
            return f"I don't know how to '{command}'. Here are some things I can do: move, turn, pick up, go to, find."
        else:
            return f"I understood your command as '{recognized_intent.action}' but I'm not sure how to proceed."
    
    def handle_action_error(self, action: str, error_details: Dict[str, Any]):
        """Handle errors during action execution"""
        if action == 'navigation':
            return "I tried to navigate there but encountered an obstacle. I'll find an alternate route."
        elif action == 'manipulation':
            return "I couldn't complete that manipulation. Let me try a different approach."
        else:
            return f"I had trouble executing '{action}'. {error_details.get('message', '')}"
    
    def ask_for_clarification(self, original_command: str):
        """Ask user for clarification"""
        return f"I'm not sure what you mean by '{original_command}'. Could you be more specific or rephrase?"
    
    def suggest_alternatives(self, original_command: str):
        """Suggest alternative commands"""
        alternatives = [
            "move forward/backward",
            "turn left/right", 
            "go to kitchen/living room",
            "pick up the [object]",
            "find the [object]"
        ]
        return f"I didn't understand '{original_command}'. Try one of these: {', '.join(alternatives)}"
    
    def retry_or_alternative(self, failed_action: Dict[str, Any]):
        """Retry action or suggest alternative"""
        action_type = failed_action.get('action', 'unknown')
        error = failed_action.get('error', 'unknown')
        
        if action_type == 'navigation' and 'obstacle' in error:
            return "I found an obstacle. I'll try to navigate around it."
        elif action_type == 'grasping' and 'object_not_found' in error:
            return "I can't find that object anymore. Could you point it out or move closer?"
        else:
            return f"I couldn't complete that action. Would you like me to try something else?"
    
    def reset_context(self):
        """Reset interaction context"""
        return "I'm getting confused. Let's start fresh. What would you like me to do?"


class PerformanceOptimizer:
    def __init__(self):
        self.transcription_cache = {}
        self.intent_cache = {}
        self.response_cache = {}
        self.cache_size_limit = 100
    
    def cache_transcription(self, audio_hash: str, transcription: str):
        """Cache audio transcriptions to avoid repeated processing"""
        if len(self.transcription_cache) >= self.cache_size_limit:
            # Remove oldest entry
            oldest_key = next(iter(self.transcription_cache))
            del self.transcription_cache[oldest_key]
        
        self.transcription_cache[audio_hash] = transcription
    
    def get_cached_transcription(self, audio_hash: str) -> Optional[str]:
        """Retrieve cached transcription"""
        return self.transcription_cache.get(audio_hash)
    
    def cache_intent(self, command: str, intent: RobotIntent):
        """Cache intent interpretations"""
        if len(self.intent_cache) >= self.cache_size_limit:
            oldest_key = next(iter(self.intent_cache))
            del self.intent_cache[oldest_key]
        
        self.intent_cache[command] = intent
    
    def get_cached_intent(self, command: str) -> Optional[RobotIntent]:
        """Retrieve cached intent"""
        return self.intent_cache.get(command)
    
    def cache_response(self, command: str, response: str):
        """Cache robot responses"""
        if len(self.response_cache) >= self.cache_size_limit:
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        self.response_cache[command] = response
    
    def get_cached_response(self, command: str) -> Optional[str]:
        """Retrieve cached response"""
        return self.response_cache.get(command)


# Integration with main system
class OptimizedVoiceControlNode(MultimodalVoiceControlNode):
    def __init__(self):
        super().__init__()
        
        # Initialize performance optimizer and error handler
        self.optimizer = PerformanceOptimizer()
        self.error_handler = VoiceInterfaceErrorHandler()
    
    def voice_callback(self, msg):
        """Enhanced voice command processing with caching and error handling"""
        command_text = msg.data
        
        self.get_logger().info(f"Processing voice command: '{command_text}'")
        
        # Try to get cached result first
        cached_intent = self.optimizer.get_cached_intent(command_text)
        if cached_intent:
            self.get_logger().info("Using cached intent interpretation")
            self.process_intent_multimodal(cached_intent)
            return
        
        # Get current robot context
        robot_context = self.build_robot_context()
        
        try:
            # Recognize intent using LLM
            intent = self.llm_nlu.recognize_intent(command_text, robot_context)
            
            if intent:
                # Cache the intent for future use
                self.optimizer.cache_intent(command_text, intent)
                
                if intent.confidence > 0.7:
                    # Process the intent
                    self.process_intent_multimodal(intent)
                else:
                    # Handle low-confidence recognition
                    error_response = self.error_handler.handle_nlu_error(command_text, intent)
                    self.provide_feedback(error_response)
            else:
                # Handle failed recognition
                error_response = self.error_handler.handle_nlu_error(command_text, None)
                self.provide_feedback(error_response)
                
        except Exception as e:
            self.get_logger().error(f"Error processing voice command: {e}")
            self.provide_feedback(self.error_handler.handle_asr_error('processing_error'))
    
    def provide_feedback(self, text):
        """Enhanced feedback with caching"""
        # Check for cached response
        cached_response = self.optimizer.get_cached_response(text)
        if cached_response:
            text = cached_response
        else:
            # Cache this response for similar future requests
            self.optimizer.cache_response(text[:50], text)  # Cache using first 50 chars as key
        
        # In a real system, this would connect to a text-to-speech system
        self.get_logger().info(f"Voice feedback: {text}")
        
        # Publish feedback
        feedback_msg = String()
        feedback_msg.data = text
        self.speech_pub.publish(feedback_msg)
```

## Chapter Summary

This chapter covered building voice-to-action systems for robotics using Whisper for speech recognition and LLMs for natural language understanding. We explored the architecture and components of such systems, implemented Whisper integration with optimization techniques, connected LLMs for intent recognition, integrated multimodal perception, and designed action planning systems. We also covered context management and error handling to create robust voice interfaces for robots.

## Checklist

- [ ] Integrate Whisper for speech recognition
- [ ] Connect LLM for natural language understanding
- [ ] Implement multimodal context awareness
- [ ] Design action planning system
- [ ] Add context management capabilities
- [ ] Implement error handling and recovery
- [ ] Optimize for real-time performance
- [ ] Validate on physical robot

## Exercises

### Exercise 1: Basic Voice Command System

Build a simple system that takes voice commands and converts them to basic robot movements.

#### Solution

1. Set up Whisper for speech recognition
2. Create simple command parser
3. Connect to basic robot movement commands
4. Test with common commands (move forward, turn left, etc.)

#### Hints

- Start with a simple keyword-based parser as backup
- Consider voice activity detection to trigger recognition
- Add error handling for unrecognized commands
- Use ROS 2 topics to connect components

### Exercise 2: Context-Aware Conversation

Create a system that maintains context during multi-turn conversations.

#### Solution

1. Implement conversation history tracking
2. Add pronoun resolution capability
3. Maintain object reference context
4. Handle follow-up questions appropriately

#### Hints

- Store recent interactions in memory
- Use entity linking to maintain object references
- Implement dialogue state tracking
- Consider timeout for context expiration

## References

- [OpenAI Whisper Documentation](https://github.com/openai/whisper)
- [ChatGPT Integration Guide](https://platform.openai.com/docs/guides/chat)
- [Robot Operating System 2 Documentation](https://docs.ros.org/en/humble/)
- [Spoken Language Systems by Jurafsky & Martin](https://web.stanford.edu/~jurafsky/slp3/)
- [Multimodal Machine Learning Survey](https://arxiv.org/abs/1905.12862)