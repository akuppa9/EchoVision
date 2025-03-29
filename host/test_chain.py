#!/usr/bin/env python3
"""
Test script for the reasoning and action chain functionality.
This script bypasses the multiprocessing and buffer to focus only on testing
the chain-of-thought reasoning and action execution.
"""

import os
import time
import re
from transcription import transcribe_with_elevenlabs
import json
from reasoning import reasoning
from dotenv import load_dotenv
from action import Action


def test_chain(images, query):
    # Load environment variables from .env file
    load_dotenv()

    # Initialize the Action class
    actions = Action()

    # Function to execute the API call based on the action
    def execute_action(action_info, restaurant_address=None):
        if action_info["action_type"] == "image_analysis":
            # No API call needed, just return the analysis
            return action_info["analysis"]
            
        function_name = action_info["function"]
        params = action_info["parameters"]
        
        # Debug the parameters being passed to the function
        print(f"DEBUG: Function: {function_name}, Parameters: {params}")
        
        if function_name == "get_current_location":
            try:
                location = actions.get_current_location()
                return f"{location['lat']},{location['lng']}"
            except Exception as e:
                print(f"Error calling get_current_location: {e}")
                # Use a default San Francisco location as fallback
                return "37.7749,-122.4194"
                
        elif function_name == "get_nearby_places":
            try:
                location_str = params.get("location", "37.7749,-122.4194")
                place_type = params.get("type", "restaurant")
                radius = int(params.get("radius", 5000))
                audio = False  # We don't want audio output in this test
                
                # Convert location string to tuple as required by action.py
                if isinstance(location_str, str) and ',' in location_str:
                    lat, lng = location_str.split(',')
                    location = (float(lat.strip()), float(lng.strip()))
                    print(f"Converted location string '{location_str}' to tuple {location}")
                else:
                    # Fallback to San Francisco coordinates
                    location = (37.7749, -122.4194)
                    print(f"Using default location tuple {location}")
                
                places_data = actions.get_nearby_places(location, place_type, radius)
                
                # Format the result as a string
                if places_data and "results" in places_data and len(places_data["results"]) > 0:
                    place = places_data["results"][0]
                    name = place.get("name", "Unknown name")
                    vicinity = place.get("vicinity", "Unknown address")
                    return f"{name}, {vicinity}"
                else:
                    return f"No {place_type} found nearby"
            except Exception as e:
                print(f"Error calling get_nearby_places: {e}")
                return f"Error finding nearby {place_type}: {str(e)}"
                
        elif function_name == "get_route_to_destination":
            try:
                origin = params.get("origin", "")
                destination = params.get("destination", "")
                
                # Debug the origin and destination values
                print(f"DEBUG: Origin: {origin}")
                print(f"DEBUG: Destination: {destination}")
                
                # Verify we have a destination before proceeding
                if not destination and restaurant_address:
                    # Use the restaurant_address passed as a parameter
                    destination = restaurant_address
                    print(f"WARNING: Empty destination parameter. Using passed restaurant address: {destination}")
                
                if not destination:
                    return "Error: No destination provided for route calculation."
                
                # If origin is coordinates, convert to the proper format
                if isinstance(origin, str) and ',' in origin:
                    try:
                        lat, lng = origin.split(',')
                        origin = f"{lat.strip()},{lng.strip()}"
                    except:
                        pass  # Keep origin as is if conversion fails
                        
                # The actual action.py function doesn't return anything directly
                # But for our test, we need a return value to continue the chain
                # So we'll mock a response
                actions.get_route_to_destination(origin, destination)
                return f"Route from {origin} to {destination} has been calculated. Directions are being provided."
            except Exception as e:
                print(f"Error calling get_route_to_destination: {e}")
                return f"Error getting directions: {str(e)}"
        else:
            return f"Unknown function: {function_name}"

    # Function to parse the reasoning response
    def parse_reasoning_response(response):
        try:
            lines = response.strip().split('\n')
            action_chain = ""
            next_action = ""
            parameter_to_save = ""
            parameters_line = ""  # Add a variable to capture a separate Parameters: line
            
            # Step 1: Extract high-level sections from the response
            in_parameters_section = False
            parameters_lines = []
            analysis_content = []
            
            # Check if this is an image analysis response
            if "image analysis is needed" in response.lower() or "analysis:" in response.lower():
                # This is an image analysis response - extract the full analysis content
                analysis_mode = False
                for line in lines:
                    if line.strip().startswith("Analysis:") or "##" in line and "Analysis" in line:
                        analysis_mode = True
                        continue
                    if analysis_mode:
                        analysis_content.append(line)
                        
                # If we found analysis content, return it as image analysis
                if analysis_content:
                    analysis_text = "\n".join(analysis_content).strip()
                    print(f"DEBUG: Detected image analysis response with content length: {len(analysis_text)}")
                    return {
                        "action_type": "image_analysis",
                        "action_chain": "image_analysis",
                        "analysis": analysis_text,
                        "parameter_to_save": "none"
                    }
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("Action Chain:"):
                    action_chain = line.replace("Action Chain:", "").strip()
                elif line.startswith("Next Action:"):
                    next_action = line.replace("Next Action:", "").strip()
                elif line.startswith("Parameter to Save:"):
                    parameter_to_save = line.replace("Parameter to Save:", "").strip()
                elif line.startswith("Parameters:"):
                    in_parameters_section = True
                    # Don't add the "Parameters:" line itself to parameters_lines
                    continue
                elif in_parameters_section and line.startswith("-"):
                    # This is a parameter in the list that started with "Parameters:"
                    parameters_lines.append(line)
            
            # Join all parameter lines for processing
            if parameters_lines:
                parameters_line = "\n".join(parameters_lines)
                print(f"DEBUG: Parameters lines found:\n{parameters_line}")
            
            # Print out the extracted parts for debugging
            print(f"DEBUG: Extracted action_chain: {action_chain}")
            print(f"DEBUG: Extracted next_action: {next_action}")
            print(f"DEBUG: Extracted parameter_to_save: {parameter_to_save}")
            print(f"DEBUG: Combined parameters_line: {parameters_line}")
            
            # Check for image analysis in the action chain or next action
            if action_chain and "image analysis" in action_chain.lower():
                # Extract analysis from the remaining text in the response
                analysis_text = next_action.strip()
                # If there's a detailed analysis section, use that
                if "Analysis:" in response or "###" in response:
                    # Find the analysis section
                    analysis_section = False
                    analysis_lines = []
                    for line in lines:
                        if "Analysis:" in line or "###" in line and "Analysis" in line:
                            analysis_section = True
                            continue
                        if analysis_section:
                            analysis_lines.append(line)
                    
                    if analysis_lines:
                        analysis_text = "\n".join(analysis_lines).strip()
                
                return {
                    "action_type": "image_analysis",
                    "action_chain": action_chain,
                    "analysis": analysis_text,
                    "parameter_to_save": parameter_to_save
                }
            
            # Check if the next action contains "analyze" or other image analysis keywords
            if "analyz" in next_action.lower() or "describ" in next_action.lower() or "explain" in next_action.lower():
                # This is likely an image analysis request
                return {
                    "action_type": "image_analysis",
                    "action_chain": action_chain,
                    "analysis": extract_analysis_from_response(response),
                    "parameter_to_save": parameter_to_save
                }
                
            # Extract function name and parameters from next_action
            # Simple parsing for function calls like: function_name(param1="value1", param2="value2")
            if "image analysis" in next_action.lower():
                return {
                    "action_type": "image_analysis",
                    "action_chain": action_chain,
                    "analysis": extract_analysis_from_response(response),
                    "parameter_to_save": parameter_to_save
                }
            
            # Check if we have a function name with parameters in parentheses
            function_match = re.search(r'(\w+)\s*\((.*?)\)', next_action)
            
            # If not found, try to extract just the function name without parameters
            if not function_match and parameters_line:
                # Extract just the function name
                function_name = next_action.strip()
                # Use the separate parameters line
                params_str = parameters_line
                print(f"DEBUG: Using split format - function: {function_name}, params: {params_str}")
            elif function_match:
                # Standard format with function(params)
                function_name = function_match.group(1)
                params_str = function_match.group(2)
                print(f"DEBUG: Using standard format - function: {function_name}, params: {params_str}")
            else:
                # Last resort: try to just extract a function name
                function_name_match = re.search(r'(\w+)', next_action)
                if function_name_match:
                    function_name = function_name_match.group(1)
                    params_str = ""
                    print(f"DEBUG: Extracted bare function name: {function_name}")
                else:
                    print(f"DEBUG: Could not match function pattern in: {next_action}")
                    return None
                
            # Parse parameters
            params = {}
            
            # Parse parameters from the parameters section if it exists
            if parameters_lines:
                for param_line in parameters_lines:
                    # Format is typically "- key: value" or "- key: "value""
                    param_match = re.match(r'-\s*(\w+):\s*[\'"]?([^\'"]+)[\'"]?', param_line)
                    if param_match:
                        key = param_match.group(1)
                        value = param_match.group(2).strip()
                        params[key] = value
            
            # Special handling for specific functions if parameters weren't found in separate lines
            if not params:
                if function_name == "get_current_location":
                    # No parameters needed
                    pass
                elif function_name == "get_nearby_places":
                    # Handle the case where parameters are in a tuple format like (lat,lng, 'type')
                    tuple_match = re.search(r'\((.*?)\)', params_str)
                    if tuple_match:
                        tuple_params = tuple_match.group(1).split(',')
                        if len(tuple_params) >= 2:
                            # First two parameters are likely lat,lng
                            lat_lng = ','.join([p.strip() for p in tuple_params[:2]])
                            params['location'] = lat_lng
                        
                        # Look for type in quotes
                        type_match = re.search(r"'([^']+)'", params_str)
                        if type_match:
                            params['type'] = type_match.group(1)
                        elif '"' in params_str:
                            type_match = re.search(r'"([^"]+)"', params_str)
                            if type_match:
                                params['type'] = type_match.group(1)
                    else:
                        # Try standard parameter extraction
                        # Try to extract location and type parameters even if not specified with key=value format
                        # First check for key=value format
                        location_match = re.search(r'location\s*[=:]\s*[\'"]?([\w\.\-\,]+)[\'"]?', params_str, re.IGNORECASE)
                        type_match = re.search(r'type\s*[=:]\s*[\'"]?([\w\.\-\,]+)[\'"]?', params_str, re.IGNORECASE)
                        radius_match = re.search(r'radius\s*[=:]\s*(\d+)', params_str, re.IGNORECASE)
                        
                        if location_match:
                            params['location'] = location_match.group(1)
                        else:
                            # Try to find first parameter as location
                            location_match = re.search(r'[\'"]([\w\.\-\,]+)[\'"]', params_str)
                            if location_match:
                                params['location'] = location_match.group(1)
                            else:
                                # Try to extract coordinates directly 
                                coords_match = re.search(r'([\d\.\-]+,[\d\.\-]+)', params_str)
                                if coords_match:
                                    params['location'] = coords_match.group(1)
                        
                        if type_match:
                            params['type'] = type_match.group(1)
                        else:
                            # Try to find restaurant or other types in quotes
                            type_match = re.search(r'[\'"](\w+)[\'"]', params_str)
                            if type_match:
                                params['type'] = type_match.group(1)
                            elif 'restaurant' in params_str:
                                params['type'] = 'restaurant'
                            elif 'gas_station' in params_str:
                                params['type'] = 'gas_station'
                            elif 'hospital' in params_str:
                                params['type'] = 'hospital'
                            elif 'park' in params_str:
                                params['type'] = 'park'
                        
                        if radius_match:
                            params['radius'] = radius_match.group(1)
                            
                elif function_name == "get_route_to_destination":
                    # Similar parsing for route function
                    origin_match = re.search(r'origin\s*[=:]\s*[\'"]?([\d\.\-\,]+)[\'"]?', params_str, re.IGNORECASE)
                    dest_match = re.search(r'destination\s*[=:]\s*[\'"]?([^\'"]+)[\'"]?', params_str, re.IGNORECASE)
                    mode_match = re.search(r'mode\s*[=:]\s*[\'"]?([\w\.\-\,]+)[\'"]?', params_str, re.IGNORECASE)
                    
                    if origin_match:
                        params['origin'] = origin_match.group(1)
                    else:
                        # Try to find first parameter as origin (coordinates)
                        coords_match = re.search(r'([\d\.\-]+,[\d\.\-]+)', params_str)
                        if coords_match:
                            params['origin'] = coords_match.group(1)
                    
                    if dest_match:
                        params['destination'] = dest_match.group(1)
                    else:
                        # Look for address-like text in quotes
                        address_match = re.search(r'[\'"]([^\'"]+)[\'"]', params_str)
                        if address_match:
                            params['destination'] = address_match.group(1)
                            
                    # If we still don't have a destination, check the full line for quoted text after the coordinates
                    if 'destination' not in params:
                        full_quote_match = re.search(r'[\d\.\-]+,[\d\.\-]+[^\'"]*[\'"]([^\'"]+)[\'"]', params_str)
                        if full_quote_match:
                            params['destination'] = full_quote_match.group(1)
                    
                    if mode_match:
                        params['mode'] = mode_match.group(1)
                        
            # If params is still empty but we have a coordinate in the params_str, try to extract location
            if not params and function_name == "get_nearby_places":
                coords_match = re.search(r'([\d\.\-]+,[\d\.\-]+)', params_str)
                if coords_match:
                    params['location'] = coords_match.group(1)
                    
                    # Look for place type clues in the text
                    for type_name in ["restaurant", "gas_station", "hospital", "park", "store", "pharmacy", "cafe", "bank", "lodging"]:
                        if type_name in params_str.lower():
                            params['type'] = type_name
                            break
                    
                    # Default to restaurant if nothing else found
                    if 'type' not in params:
                        params['type'] = 'restaurant'
                    
            print(f"DEBUG: Extracted parameters: {params}")
                    
            return {
                "action_type": "api_call",
                "function": function_name,
                "parameters": params,
                "action_chain": action_chain,
                "parameter_to_save": parameter_to_save.split('(')[0] if '(' in parameter_to_save else parameter_to_save
            }
        except Exception as e:
            print(f"Error parsing reasoning response: {e}")
            print(f"Response was: {response}")
            return None

    # Helper function to determine the next function based on the action chain
    def determine_next_action(action_chain, executed_functions, context_params):
        """
        Determine the next action to execute based on the action chain and context
        
        Args:
            action_chain: The action chain description from the model
            executed_functions: Set of already executed functions
            context_params: Dict of parameters already collected
            
        Returns:
            Next function to execute or None if chain is complete
        """
        # Parse the action chain to identify the sequence
        action_sequence = []
        
        # Check if action_chain contains a structured sequence
        if "->" in action_chain:
            # Split by arrow notation
            steps = action_chain.split("->")
            action_sequence = [step.strip().split("(")[0].strip() for step in steps]
        elif "," in action_chain:
            # Split by commas
            steps = action_chain.split(",")
            action_sequence = [step.strip().split("(")[0].strip() for step in steps]
        elif "\n" in action_chain:
            # Split by newlines
            steps = action_chain.split("\n")
            action_sequence = [step.strip().split("(")[0].strip() for step in steps if step.strip()]
        
        print(f"Parsed action sequence: {action_sequence}")
        
        # Find the first function in the sequence that hasn't been executed yet
        for func in action_sequence:
            if func not in executed_functions and func in ["get_current_location", "get_nearby_places", "get_route_to_destination"]:
                return func
        
        # If no specific sequence found or all executed, determine based on available context
        if "get_current_location" not in executed_functions:
            return "get_current_location"
        
        if "coordinates" in context_params and "get_nearby_places" not in executed_functions:
            return "get_nearby_places"
        
        if "coordinates" in context_params and "destination" in context_params and "get_route_to_destination" not in executed_functions:
            return "get_route_to_destination"
        
        # All known steps executed
        return None

    def process_query(images, query):
        print(f"\n\nPROCESSING QUERY: {query}")
        print("=" * 50)
        
        # Check if this is a pure image analysis query that doesn't need API calls
        query_lower = query.lower()
        is_image_analysis = any(keyword in query_lower for keyword in [
            "analyz", "describ", "explain", "tell me about", "what is", "what's in", 
            "show me", "identify", "recognize", "interpret", "read", "tell me what", 
            "scan", "look at", "examine", "codesignal, surrounding"
        ])
        
        if is_image_analysis:
            print("Identified as an image analysis query - skipping API calls")
            step_counter = 1
            
            # Just call reasoning once to get the image analysis
            print(f"\nSTEP {step_counter}: Performing image analysis")
            response = reasoning(images, query, "")
            print(f"Model response:\n{response}")
            
            # Extract the analysis content
            analysis = extract_analysis_from_response(response)
            
            action_info = {
                "action_type": "image_analysis",
                "action_chain": "image_analysis",
                "analysis": analysis,
                "parameter_to_save": "none"
            }
            
            return {
                "final_result": analysis,
                "action_history": [action_info],
                "context_params": {"query_type": "image_analysis"}
            }
        
        # For non-image analysis queries, proceed with the usual action chain
        param_for_next_action = ""
        action_history = []
        final_result = ""
        step_counter = 1
        
        # Track which functions have been executed and store context
        executed_functions = set()
        context_params = {}
        
        # Detect query type to help guide the chain
        place_type = ""  # Default empty, will be determined below
        
        # Try to extract place type from query
        if "restaurant" in query_lower or "food" in query_lower or "eat" in query_lower or "dining" in query_lower:
            place_type = "restaurant"
        elif "gas" in query_lower or "fuel" in query_lower:
            place_type = "gas_station"
        elif "hospital" in query_lower or "doctor" in query_lower or "medical" in query_lower or "emergency" in query_lower:
            place_type = "hospital"
        elif "store" in query_lower or "shop" in query_lower or "mall" in query_lower:
            place_type = "store"
        elif "park" in query_lower or "playground" in query_lower or "garden" in query_lower:
            place_type = "park"
        elif "hotel" in query_lower or "motel" in query_lower or "place to stay" in query_lower or "lodging" in query_lower:
            place_type = "lodging"
        elif "coffee" in query_lower or "cafe" in query_lower:
            place_type = "cafe"
        elif "school" in query_lower or "college" in query_lower or "university" in query_lower:
            place_type = "school"
        elif "bank" in query_lower or "atm" in query_lower:
            place_type = "bank"
        elif "pharmacy" in query_lower or "drugstore" in query_lower:
            place_type = "pharmacy"
        else:
            # Default to restaurant if no specific type is detected
            place_type = "restaurant"
        
        context_params["place_type"] = place_type
        print(f"Detected place type: {place_type}")
        
        # First call to reasoning to start the chain
        print(f"\nSTEP {step_counter}: Initial reasoning to determine action chain")
        response = reasoning(images, query, param_for_next_action)
        print(f"Reasoning response:\n{response}")
        step_counter += 1
        
        # Continue processing actions until we reach a final result
        max_steps = 10
        while step_counter < max_steps:
            print(f"\nSTEP {step_counter}: Parsing reasoning response")
            # Parse the reasoning response
            action_info = parse_reasoning_response(response)
            
            if not action_info:
                print("ERROR: Could not parse reasoning response")
                
                # Try direct extraction as fallback
                print("Attempting direct extraction as fallback...")
                function_match = re.search(r'Next Action:\s*([\w_]+)', response)
                if function_match:
                    function_name = function_match.group(1)
                    print(f"Extracted function name: {function_name}")
                    
                    # Create action info based on the function name
                    if function_name == "get_current_location":
                        action_info = {
                            "action_type": "api_call",
                            "function": function_name,
                            "parameters": {},
                            "action_chain": "",
                            "parameter_to_save": "coordinates"
                        }
                    elif function_name == "get_nearby_places":
                        # Extract type if available, otherwise use the detected type
                        type_match = re.search(r'type:\s*[\'"]([^\'"]+)[\'"]', response, re.IGNORECASE)
                        place_type_param = type_match.group(1) if type_match else context_params.get("place_type", "restaurant")
                        
                        action_info = {
                            "action_type": "api_call",
                            "function": function_name,
                            "parameters": {
                                "location": context_params.get("coordinates", ""),
                                "type": place_type_param
                            },
                            "action_chain": "",
                            "parameter_to_save": "destination"
                        }
                    elif function_name == "get_route_to_destination":
                        action_info = {
                            "action_type": "api_call",
                            "function": function_name,
                            "parameters": {
                                "origin": context_params.get("coordinates", ""),
                                "destination": context_params.get("destination", "")
                            },
                            "action_chain": "",
                            "parameter_to_save": "none"
                        }
                    else:
                        # Still can't parse, give up
                        break
                    
                    print(f"Created fallback action info: {action_info}")
                else:
                    # Give up if we can't extract even basic function name
                    break
                
            # Store action in history
            action_history.append(action_info)
            
            print(f"Action determined: {action_info}")
            step_counter += 1
            
            # If this is an image analysis, we're done
            if action_info["action_type"] == "image_analysis":
                print(f"\nSTEP {step_counter}: Performing image analysis (final step)")
                final_result = action_info["analysis"]
                print(f"Analysis result: {final_result}")
                break
                
            function_name = action_info["function"]
            
            # Check if we're repeating functions and should progress to the next function in the chain
            if function_name in executed_functions:
                print(f"Function {function_name} has already been executed. Determining next action...")
                
                # Determine the next appropriate function based on context
                next_function = determine_next_action(action_info["action_chain"], executed_functions, context_params)
                
                if next_function:
                    print(f"Progressing to next step in chain: {next_function}")
                    function_name = next_function
                    
                    # Create appropriate parameters for the next function
                    if function_name == "get_nearby_places":
                        action_info = {
                            "action_type": "api_call",
                            "function": function_name,
                            "parameters": {
                                "location": context_params.get("coordinates", ""),
                                "type": context_params.get("place_type", "restaurant")
                            },
                            "action_chain": action_info["action_chain"],
                            "parameter_to_save": "destination"
                        }
                    elif function_name == "get_route_to_destination":
                        action_info = {
                            "action_type": "api_call",
                            "function": function_name,
                            "parameters": {
                                "origin": context_params.get("coordinates", ""),
                                "destination": context_params.get("destination", "")
                            },
                            "action_chain": action_info["action_chain"],
                            "parameter_to_save": "none"
                        }
            
            # Execute the action
            print(f"\nSTEP {step_counter}: Executing action: {action_info['function']}")
            
            # Update parameters based on detected place type for get_nearby_places
            if function_name == "get_nearby_places" and "type" not in action_info["parameters"]:
                action_info["parameters"]["type"] = context_params.get("place_type", "restaurant")
                print(f"Adding detected place type to parameters: {action_info['parameters']}")
                
            # Special handling for route destination to ensure parameters are set correctly
            if function_name == "get_route_to_destination":
                # Force origin and destination parameters to be set
                if "origin" not in action_info["parameters"] or not action_info["parameters"]["origin"]:
                    action_info["parameters"]["origin"] = context_params.get("coordinates", "")
                    print(f"Setting missing origin parameter: {action_info['parameters']['origin']}")
                else:
                    # Clean up origin parameter - make sure it's just coordinates
                    origin = action_info["parameters"]["origin"]
                    coords_match = re.search(r'([\d\.\-]+,[\d\.\-]+)', origin)
                    if coords_match:
                        action_info["parameters"]["origin"] = coords_match.group(1)
                        print(f"Cleaned up origin parameter: {action_info['parameters']['origin']}")
                    
                if "destination" not in action_info["parameters"] or not action_info["parameters"]["destination"]:
                    action_info["parameters"]["destination"] = context_params.get("destination", "")
                    print(f"Setting missing destination parameter: {action_info['parameters']['destination']}")
                    
                action_result = execute_action(action_info, context_params.get("destination"))
            else:
                action_result = execute_action(action_info)
                
            print(f"Action result: {action_result}")
            step_counter += 1
            
            # Mark this function as executed
            executed_functions.add(function_name)
            
            # Store important results in context
            if function_name == "get_current_location":
                context_params["coordinates"] = action_result
            elif function_name == "get_nearby_places":
                context_params["destination"] = action_result
            
            # Check if we need another action in the chain
            if not action_info["parameter_to_save"] or action_info["parameter_to_save"].lower() == "none":
                # This is the last action in the chain
                print("\nThis was the final action in the chain")
                final_result = action_result
                break
                
            # Check if we have all the necessary parameters to complete the chain
            if "coordinates" in context_params and "destination" in context_params:
                next_function = determine_next_action(action_info["action_chain"], executed_functions, context_params)
                if next_function == "get_route_to_destination":
                    print(f"We have all necessary parameters. Using custom prompt to guide to get_route_to_destination...")
                    
                    # Get the coordinates and destination
                    coordinates = context_params.get("coordinates", "")
                    destination = context_params.get("destination", "")
                    
                    print(f"Using coordinates: {coordinates}")
                    print(f"Using destination: {destination}")
                    
                    # Create a modified prompt to guide the model
                    custom_prompt = f"""Based on the previous steps, we have:
    1. Coordinates: {coordinates}
    2. Destination: {destination}

    The next step should be to get directions from the coordinates to the destination.

    Format your response EXACTLY like this:
    Action Chain: get_route_to_destination
    Next Action: get_route_to_destination(origin="{coordinates}", destination="{destination}")
    Parameter to Save: None"""
                    response = reasoning(images, custom_prompt, param_for_next_action)
                    print(f"Custom reasoning response:\n{response}")
                    continue
                elif next_function is None:
                    # We've completed all actions in the chain
                    print("All actions in the chain have been completed")
                    final_result = action_result
                    break
            
            print(f"Parameter to save for next action: {action_info['parameter_to_save']}")    
            # Call reasoning again with the result as the parameter for the next action
            param_for_next_action = action_result
            print(f"\nSTEP {step_counter}: Calling reasoning again with parameter: {param_for_next_action}")
            response = reasoning(images, query, param_for_next_action)
            print(f"Next reasoning response:\n{response}")
            step_counter += 1
        
        # If we reached the maximum number of steps without completing
        if step_counter >= max_steps:
            print("WARNING: Maximum number of steps reached")
            
            # As a fallback, if we have both coordinates and destination but haven't completed routing yet
            if "coordinates" in context_params and "destination" in context_params and "get_route_to_destination" not in executed_functions:
                print("Executing final get_route_to_destination as fallback")
                
                origin = context_params["coordinates"]
                destination = context_params["destination"]
                
                print(f"Using coordinates: {origin}")
                print(f"Using destination: {destination}")
                
                route_action = {
                    "action_type": "api_call",
                    "function": "get_route_to_destination",
                    "parameters": {
                        "origin": origin,
                        "destination": destination
                    },
                    "parameter_to_save": "none"
                }
                final_result = execute_action(route_action, destination)
            else:
                final_result = "Chain stopped due to exceeding maximum steps"
        
        print("\n" + "=" * 50)
        print("FINAL RESULT:")
        print(final_result)
        print("=" * 50)
        
        print("\nACTION HISTORY:")
        for i, action in enumerate(action_history):
            print(f"  Step {i+1}: {action}")
        
        print("\nCONTEXT PARAMETERS:")
        for key, value in context_params.items():
            print(f"  {key}: {value}")
        
        return {
            "final_result": final_result,
            "action_history": action_history,
            "context_params": context_params
        }

    # Helper function to extract analysis content from a response
    def extract_analysis_from_response(response):
        """
        Extract the analysis section from a response text.
        """
        lines = response.strip().split('\n')
        
        # Check for a dedicated analysis section
        analysis_section = False
        analysis_lines = []
        
        for line in lines:
            # Check for common analysis section headers
            if "Analysis:" in line or "##" in line and "Analysis" in line:
                analysis_section = True
                continue
            
            if analysis_section:
                analysis_lines.append(line)
        
        # If we found a dedicated analysis section, return it
        if analysis_lines:
            return "\n".join(analysis_lines).strip()
        
        # Otherwise, extract the relevant part after the standard format
        # Find where the standard format ends
        param_save_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("Parameter to Save:"):
                param_save_idx = i
                break
        
        # If we found the end of the standard format, return everything after it
        if param_save_idx >= 0 and param_save_idx < len(lines) - 1:
            return "\n".join(lines[param_save_idx + 1:]).strip()
        
        # If all else fails, return the original Next Action content
        for line in lines:
            if line.startswith("Next Action:"):
                return line.replace("Next Action:", "").strip()
        
        # Last resort: return the entire response
        return response

    def main():
        # Check if the test image exists
        for image in images:
            if not os.path.exists(image):
                print(f"ERROR: Image {image} not found")
                return
        # Process each query
        for test_query in query:
            print("\n" + "="*70)
            print("="*70)
            
        
            result = process_query(images, test_query)
            
        
            if result:
                print("\n" + "="*70)
                print("FINAL RESULT SUMMARY:")
                print(f"Query: {test_query}")
                if "image_analysis" in result.get("action_history", [{}])[0].get("action_type", ""):
                    print(f"Action type: Image Analysis")
                else:
                    print(f"Detected place type: {result['context_params'].get('place_type', 'unknown')}")
                print(f"Final result: {result['final_result']}")
                print("="*70)
            
            time.sleep(1)  

    if __name__ == "__main__":
        main() 
test_chain(["../CodeSignal_Score.png"], ["tell me where to find the nearest park"])