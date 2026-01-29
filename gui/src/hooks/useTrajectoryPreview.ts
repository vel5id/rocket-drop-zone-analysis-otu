/**
 * Custom hook for automatic trajectory preview when trajectory parameters change.
 * Implements FUNC-3 and alg_1 from spec: automatic preview with debouncing and error handling.
 * 
 * @param simConfig - Current simulation configuration
 * @param backendAvailable - Whether backend is available
 * @param previewEnabled - Whether preview layer is active
 * @param onPreviewUpdate - Callback when preview data is received
 * @param onError - Callback for error handling
 * @param debounceMs - Debounce delay in milliseconds (default 400ms)
 * 
 * @returns Object containing loading state and error message
 */
import { useEffect, useState, useRef, useCallback } from 'react';
import { SimulationConfig, TrajectoryPoint } from '../types';
import { getTrajectoryPreview } from '../api';

export interface UseTrajectoryPreviewResult {
    isLoading: boolean;
    error: string | null;
    clearError: () => void;
}

/**
 * Extracts a unique key from trajectory‑relevant parameters.
 * This key is used to detect changes that should trigger a new preview.
 * 
 * Parameters influencing trajectory (based on spec FUNC‑3):
 * - azimuth (Launch Azimuth) – primary direction
 * - sep_altitude, sep_velocity, sep_fp_angle, sep_azimuth – separation state
 * - launch_lat, launch_lon – launch location
 * - rocket_dry_mass, rocket_ref_area – rocket characteristics
 * - target_date – atmospheric conditions
 * 
 * Note: iterations and use_gpu do NOT affect a single trajectory preview.
 */
const getTrajectoryParamsKey = (config: SimulationConfig): string => {
    return [
        config.azimuth,
        config.sep_altitude,
        config.sep_velocity,
        config.sep_fp_angle,
        config.sep_azimuth,
        config.launch_lat,
        config.launch_lon,
        config.rocket_dry_mass ?? 0,
        config.rocket_ref_area ?? 0,
        config.target_date,
    ].join(':');
};

export function useTrajectoryPreview(
    simConfig: SimulationConfig,
    backendAvailable: boolean | null,
    previewEnabled: boolean,
    onPreviewUpdate: (trajectory: TrajectoryPoint[]) => void,
    onError?: (error: string) => void,
    debounceMs: number = 400
): UseTrajectoryPreviewResult {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);
    const previousParamsRef = useRef<string>('');

    // Clear error helper
    const clearError = useCallback(() => setError(null), []);

    // Main effect for debounced preview
    useEffect(() => {
        // Conditions for preview activation
        if (!backendAvailable || !previewEnabled) {
            // Clear any pending timeout
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
                timeoutRef.current = null;
            }
            // Do NOT clear preview here to avoid infinite loops
            return;
        }

        const currentParams = getTrajectoryParamsKey(simConfig);
        const previousParams = previousParamsRef.current;

        // Only trigger if trajectory parameters changed
        if (currentParams === previousParams) {
            return;
        }

        // Update previous params
        previousParamsRef.current = currentParams;

        // Clear existing timeout
        if (timeoutRef.current) {
            clearTimeout(timeoutRef.current);
            timeoutRef.current = null;
        }

        // Set loading state after a short delay to avoid flickering
        const loadingTimeout = setTimeout(() => {
            setIsLoading(true);
        }, 100);

        // Debounced API call
        timeoutRef.current = setTimeout(async () => {
            try {
                clearTimeout(loadingTimeout);
                setIsLoading(true);
                setError(null);

                const response = await getTrajectoryPreview(simConfig);
                onPreviewUpdate(response.path);
                setIsLoading(false);
            } catch (err) {
                console.error('Preview fetch failed:', err);
                const errorMessage = err instanceof Error ? err.message : 'Unknown error';
                setError(errorMessage);
                if (onError) onError(errorMessage);
                setIsLoading(false);
            }
        }, debounceMs);

        // Cleanup
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }
            clearTimeout(loadingTimeout);
        };
    }, [
        simConfig,
        backendAvailable,
        previewEnabled,
        onPreviewUpdate,
        onError,
        debounceMs,
    ]);

    return { isLoading, error, clearError };
}