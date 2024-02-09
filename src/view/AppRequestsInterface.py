from typing import Protocol

'''An interface for passing requests to the App'''
class AppRequestsInterface(Protocol):
    def quit_application(self) -> bool:
        '''quits the application'''
        raise NotImplementedError
    
    def start_active_measurement(self, source_file_name: str):
        '''starts the active measurement for given cFile'''
        raise NotImplementedError

    def quit_measurement(self):
        '''quits any measurement, passive or active'''
        raise NotImplementedError
    
    def load_from_directory(self, path: str):
        '''loads files from given path as a new project in model'''
        raise NotImplementedError
    
    def restart_measurement(self):
        raise NotImplementedError
    
    def run(self):
        raise NotImplementedError
    