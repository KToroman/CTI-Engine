from typing import Protocol

'''An interface for passing requests to the App'''
class AppRequestsInterface(Protocol):
    '''quits the application'''
    def quit_application(self) -> bool:
        raise NotImplementedError
    
    '''starts the active measurement for given cFile'''
    def start_active_measurement(self, source_file_name: str):
        raise NotImplementedError

    '''quits any measurement, passive or active'''
    def quit_measurement(self) -> bool:
        raise NotImplementedError
    
    '''loads files from given path as a new project in model'''
    def load_from_directory(self, path: str):
        raise NotImplementedError
    
    def restart_measurement(self) -> bool:
        raise NotImplementedError
    