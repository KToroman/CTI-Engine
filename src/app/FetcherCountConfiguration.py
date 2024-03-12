from attr import define


@define(frozen=True)
class FetcherCountConfiguration: 
    process_finder_count: int
    process_collector_count: int
    fetcher_count: int
    fetcher_process_count: int
    hierarchy_fetcher_worker_count: int

    STANDARD_PROCESS_FINDER_COUNT: int = 1
    STANDARD_PROCESS_COLLECTOR_COUNT: int = 1
    STANDARD_FETCHER_COUNT: int = 1
    STANDARD_FETCHER_PROCESS_COUNT: int = 15
    STANDARD_HIERARCHY_FETCHER_WORKER_COUNT: int = 16