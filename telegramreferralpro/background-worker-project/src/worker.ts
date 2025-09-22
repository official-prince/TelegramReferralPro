import { Task, WorkerOptions } from './types';

class BackgroundWorker {
    private tasks: Task[] = [];
    private isRunning: boolean = false;
    private options: WorkerOptions;

    constructor(options: WorkerOptions) {
        this.options = options;
    }

    public start(): void {
        this.isRunning = true;
        this.processTasks();
    }

    public stop(): void {
        this.isRunning = false;
    }

    public addTask(task: Task): void {
        this.tasks.push(task);
        if (this.isRunning) {
            this.processTasks();
        }
    }

    private async processTasks(): Promise<void> {
        while (this.isRunning && this.tasks.length > 0) {
            const task = this.tasks.shift();
            if (task) {
                await this.executeTask(task);
            }
        }
    }

    private async executeTask(task: Task): Promise<void> {
        try {
            await task.run();
        } catch (error) {
            console.error(`Error executing task: ${error}`);
        }
    }
}

export default BackgroundWorker;