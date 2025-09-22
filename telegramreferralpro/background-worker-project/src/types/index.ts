export interface Task {
    id: string;
    data: any;
    priority?: number;
}

export interface WorkerOptions {
    concurrency?: number;
    timeout?: number;
    retryAttempts?: number;
}