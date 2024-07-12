def check_emsstat(incidents, current_index):
    current_incident = incidents[current_index]
    # Check the current incident's ORI directly
    if current_incident['Incident ORI'].startswith('EMSSTAT'):
        return True
    
    # Check the next one or two incidents for the same time, location, and EMSSTAT ORI
    for next_index in range(current_index + 1, min(current_index + 3, len(incidents))):
        next_incident = incidents[next_index]
        if (current_incident['Incident_time'] == next_incident['Incident_time'] and
            current_incident['Location'] == next_incident['Location'] and
            next_incident['Incident ORI'].startswith('EMSSTAT')):
            return True
    for previous_index in range(current_index - 1, max(current_index -3, -1),-1):
        previous_incident = incidents[previous_index]
        if (current_incident['Incident_time'] == previous_incident['Incident_time'] and
            current_incident['Location'] == previous_incident['Location'] and
            previous_incident['Incident ORI'].startswith('EMSSTAT')):
            return True
    
    return False