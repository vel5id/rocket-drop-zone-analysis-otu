/**
 * API client for rocket simulation backend.
 * Connects to FastAPI backend at localhost:8000
 */

import {
    SimulationConfig,
    SimulationStatus,
    SimulationResult
} from './types';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Check if the backend is available.
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.ok;
    } catch (error) {
        console.error("Health check failed:", error);
        return false;
    }
}

/**
 * Start a new simulation.
 * Returns job_id for status polling.
 */
export async function runSimulation(config: Partial<SimulationConfig> = {}): Promise<SimulationStatus> {
    const response = await fetch(`${API_BASE_URL}/simulation/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            iterations: config.iterations ?? 1000,
            use_gpu: config.use_gpu ?? true,
            launch_lat: config.launch_lat ?? 45.72341,
            launch_lon: config.launch_lon ?? 63.32275,
            azimuth: config.azimuth ?? 45.0,
        }),
    });

    if (!response.ok) {
        throw new Error(`Simulation failed: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Poll simulation status.
 */
export async function getSimulationStatus(jobId: string): Promise<SimulationStatus> {
    const response = await fetch(`${API_BASE_URL}/simulation/status/${jobId}`);

    if (!response.ok) {
        throw new Error(`Failed to get status: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Get full simulation results.
 */
export async function getSimulationResults(jobId: string): Promise<SimulationResult> {
    const response = await fetch(`${API_BASE_URL}/results/${jobId}`);

    if (!response.ok) {
        throw new Error(`Failed to get results: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Poll simulation until complete, calling onProgress with updates.
 */
export async function pollSimulation(
    jobId: string,
    onProgress: (status: SimulationStatus) => void,
    intervalMs: number = 500
): Promise<SimulationResult> {
    return new Promise((resolve, reject) => {
        const poll = async () => {
            try {
                const status = await getSimulationStatus(jobId);
                onProgress(status);

                if (status.status === 'completed') {
                    const results = await getSimulationResults(jobId);
                    resolve(results);
                } else if (status.status === 'failed') {
                    // Use the error message from the backend status if available
                    const errorMessage = (status as any).error || 'Simulation failed';
                    reject(new Error(errorMessage));
                } else {
                    setTimeout(poll, 2000);
                }
            } catch (error) {
                reject(error);
            }
        };

        poll();
    });
}

/**
 * Run simulation and poll until complete.
 * Convenience function that combines runSimulation and pollSimulation.
 */
export async function runAndWaitSimulation(
    config: Partial<SimulationConfig>,
    onProgress: (status: SimulationStatus) => void
): Promise<SimulationResult> {
    const { job_id } = await runSimulation(config);
    return pollSimulation(job_id, onProgress);
}
