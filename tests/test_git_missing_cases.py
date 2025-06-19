def prioritize_elements(elements):
    """Prioritize elements for blame processing"""
    public_apis = []
    implementation = []
    tests = []
    
    for element in elements:
        if element.is_public_api():
            public_apis.append(element)
        elif element.file_path.startswith('tests/'):
            tests.append(element)
        else:
            implementation.append(element)
            
    # Process in priority order
    return public_apis + implementation + tests