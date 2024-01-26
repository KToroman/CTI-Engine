from typing_extensions import Protocol

'''An interface for passing requests to the App'''
class AppRequestsInterface(Protocol):
    '''quits the application'''
    def quit_application() -> bool:
        raise NotImplementedError
    
    '''starts the active measurement for given cFile'''
    def start_active_measurement(source_file_name: str):
        raise NotImplementedError

    '''quits any measurement, passive or active'''
    def quit_measurement() -> bool:
        raise NotImplementedError
    
    '''loads files from given path as a new project in model'''
    def load_from_directory(path: str):
        raise NotImplementedError
    
    '''pauses active measurement'''
    def pause_active_measurement():
        raise NotImplementedError
    
    '''resumes previously paused active measurement'''
    def resume_active_measurement():
        raise NotImplementedError