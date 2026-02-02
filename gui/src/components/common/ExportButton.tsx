import { AlertCircle, Download, Loader2 } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { generateExport, getExportDownloadUrl, getExportStatus } from '../../api';
import { GeoJSONFeatureCollection, GeoJSONPolygon, OTUCellProperties } from '../../types';

interface ExportButtonProps {
    jobId?: string;
    otuGrid?: GeoJSONFeatureCollection<GeoJSONPolygon, OTUCellProperties>;
    date?: string;
    label?: string;
}

const ExportButton: React.FC<ExportButtonProps> = ({ jobId, otuGrid, date, label = "Export Table" }) => {
    const [status, setStatus] = useState<'idle' | 'generating' | 'ready' | 'error'>('idle');
    const [taskId, setTaskId] = useState<string | null>(null);
    const [progress, setProgress] = useState(0);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    // Poll for status when generating
    useEffect(() => {
        let interval: NodeJS.Timeout;

        if (status === 'generating' && taskId) {
            interval = setInterval(async () => {
                try {
                    const res = await getExportStatus(taskId);
                    if (res.status === 'completed') {
                        setStatus('ready');
                        setProgress(100);
                        clearInterval(interval);
                        // Auto trigger download? Only if user wants? 
                        // Let's require a click to download to avoid popup blockers, or just handle it.
                    } else if (res.status === 'failed') {
                        setStatus('error');
                        setErrorMsg(res.error || 'Export failed');
                        clearInterval(interval);
                    } else {
                        setProgress(res.progress || 20); // Fake progress if 0
                    }
                } catch (e) {
                    console.error("Poll failed", e);
                }
            }, 1000);
        }

        return () => clearInterval(interval);
    }, [status, taskId]);

    const handleMainClick = async () => {
        if (status === 'ready' && taskId) {
            // Download
            window.location.href = getExportDownloadUrl(taskId);
            // Reset after download
            setTimeout(() => setStatus('idle'), 2000);
            return;
        }

        if (status === 'generating') return; // Ignore

        // START EXPORT
        if (jobId && !jobId.startsWith('mock-')) {
            // Backend Export
            try {
                setStatus('generating');
                setProgress(0);
                const res = await generateExport({ job_id: jobId, include_time_series: false });
                setTaskId(res.task_id);
            } catch (e) {
                console.error(e);
                setStatus('error');
                setErrorMsg('Failed to start export');
            }
        } else {
            // Legacy Client-Side Export (Fallback for Mock/Demo)
            handleLegacyExport();
        }
    };

    const handleLegacyExport = () => {
        if (!otuGrid || !otuGrid.features || otuGrid.features.length === 0) {
            alert('No OTU data to export');
            return;
        }

        // Generate CSV content
        const headers = [
            'ID', 'Latitude', 'Longitude',
            'NDVI (Q_Vi)', 'Soil Strength (Q_Si)', 'Soil Quality (Q_Bi)',
            'Relief Factor (Q_Relief)', 'OTU Index (Q_OTU)', 'Missing Data'
        ];

        const rows = otuGrid.features.map(feature => {
            const props = feature.properties;
            const coords = feature.geometry.coordinates[0];
            const lons = coords.map(c => c[0]);
            const lats = coords.map(c => c[1]);
            const centerLon = lons.reduce((a, b) => a + b, 0) / lons.length;
            const centerLat = lats.reduce((a, b) => a + b, 0) / lats.length;
            const missing = props.missing_data && props.missing_data.length > 0
                ? props.missing_data.join(', ') : 'None';

            return [
                props.id || '',
                centerLat.toFixed(6),
                centerLon.toFixed(6),
                (props.q_vi ?? 0).toFixed(4),
                (props.q_si ?? 0).toFixed(4),
                (props.q_bi ?? 0).toFixed(4),
                (props.q_relief ?? 0).toFixed(4),
                (props.q_otu ?? 0).toFixed(4),
                missing
            ];
        });

        const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        const filename = date ? `otu_table_BASIC_${date}.csv` : `otu_table_BASIC.csv`;

        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const isDisabled = (!jobId && (!otuGrid || !otuGrid.features)) || status === 'generating';

    // Button Styling
    let btnClass = "bg-emerald-600 hover:bg-emerald-700 text-white shadow-lg hover:shadow-xl";
    let icon = <Download className="w-5 h-5" />;
    let text = label;

    if (status === 'generating') {
        btnClass = "bg-blue-600 cursor-wait";
        icon = <Loader2 className="w-5 h-5 animate-spin" />;
        text = `Generating ${progress}%`;
    } else if (status === 'ready') {
        btnClass = "bg-green-600 hover:bg-green-700 animate-pulse";
        icon = <Download className="w-5 h-5" />;
        text = "Download Report";
    } else if (status === 'error') {
        btnClass = "bg-red-600 hover:bg-red-700";
        icon = <AlertCircle className="w-5 h-5" />;
        text = "Retry Export";
    }

    if (isDisabled && status !== 'generating') {
        btnClass = "bg-gray-700 text-gray-500 cursor-not-allowed";
    }

    return (
        <div className="flex flex-col gap-1 w-full">
            <button
                onClick={handleMainClick}
                disabled={isDisabled && status !== 'error'}
                className={`
                    px-4 py-2 rounded-lg font-medium transition-all
                    flex items-center justify-center gap-2
                    ${btnClass}
                `}
                title={status === 'error' ? errorMsg || 'Error' : 'Export Full Compliance Report'}
            >
                {icon}
                <span>{text}</span>
            </button>
            {status === 'error' && (
                <span className="text-[10px] text-red-400 text-center">{errorMsg}</span>
            )}
            {jobId && !jobId.startsWith('mock-') && status === 'idle' && (
                <span className="text-[10px] text-gray-400 text-center">Includes Sentinel-2 Metadata & Economics</span>
            )}
        </div>
    );
};

export default ExportButton;
