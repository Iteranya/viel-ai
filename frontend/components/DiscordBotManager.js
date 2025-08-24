// DiscordBotManager.js

// Import Preact and hooks from a CDN
import { h } from 'https://esm.sh/preact';
import { useState, useEffect, useCallback } from 'https://esm.sh/preact/hooks';

// --- Configuration ---
const API_BASE_URL = '/api';
const STATUS_POLL_INTERVAL = 5000; // Check status every 5 seconds

// --- Helper Components (Can be shared with other components) ---

const Alert = ({ message, type = 'error', onDismiss }) => {
    const baseClasses = 'p-4 my-4 text-sm rounded-lg flex justify-between items-center';
    const typeClasses = {
        error: 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200',
    };
    return html`
        <div class="p-4 my-4 text-sm rounded-lg flex justify-between items-center bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200" role="alert">
            <div><span class="font-medium">Error!</span> ${message}</div>
            ${onDismiss && html`
                <button onClick=${onDismiss} class="ml-4 -mr-1 p-1 rounded-md hover:bg-opacity-20 hover:bg-current">
                    <i class="fas fa-times"></i>
                </button>
            `}
        </div>
    `;
};

// --- Main Component ---

export function DiscordBotManager() {
    // --- State Management ---
    const [status, setStatus] = useState(null); // 'active', 'inactive', 'starting', 'error'
    const [isLoading, setIsLoading] = useState(false); // For activate/deactivate actions
    const [error, setError] = useState(null);

    // --- Status and Color Mapping ---
    const statusInfo = {
        active: { text: "Online", color: "bg-green-500", icon: "fa-robot" },
        inactive: { text: "Offline", color: "bg-gray-500", icon: "fa-power-off" },
        starting: { text: "Starting...", color: "bg-yellow-500 animate-pulse", icon: "fa-spinner fa-spin" },
        error: { text: "Error", color: "bg-red-500", icon: "fa-exclamation-triangle" },
        checking: { text: "Checking...", color: "bg-blue-500 animate-pulse", icon: "fa-question-circle" }
    };

    // --- API Call Functions ---

    const checkStatus = useCallback(async () => {
        // Don't poll if an action is in progress
        if (isLoading) return;
        try {
            const response = await fetch(`${API_BASE_URL}/discord/status`);
            if (!response.ok) throw new Error('Could not connect to the server to check status.');
            const data = await response.json();
            setStatus(data.status);
            if (data.status === 'error') {
                setError(data.detail || 'An unknown error occurred on the bot thread.');
            }
        } catch (err) {
            setStatus('error');
            setError(err.message);
        }
    }, [isLoading]);

    // --- Component Lifecycle: Polling for Status ---

    useEffect(() => {
        // Check status immediately on mount
        checkStatus();
        // Then set up an interval to poll for status
        const intervalId = setInterval(checkStatus, STATUS_POLL_INTERVAL);
        // Clean up the interval when the component unmounts
        return () => clearInterval(intervalId);
    }, [checkStatus]);

    // --- Event Handlers for Actions ---

    const handleAction = async (action) => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE_URL}/discord/${action}`, {
                method: 'POST'
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || `Failed to ${action} bot.`);
            }
            // Immediately check status after a successful action
            await checkStatus();
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    // --- Render Logic ---

    const currentStatus = statusInfo[status] || statusInfo.checking;

    return html`
        <div class="max-w-md mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md text-gray-900 dark:text-gray-100 font-sans">
            <h2 class="text-2xl font-bold mb-4 text-center">Discord Bot Control</h2>

            {/* Status Indicator */}
            <div class="flex items-center justify-center p-4 mb-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
                <div class="w-4 h-4 rounded-full mr-3 ${currentStatus.color}"></div>
                <span class="font-semibold text-lg">${currentStatus.text}</span>
                <i class="fas ${currentStatus.icon} ml-3 text-gray-500 dark:text-gray-400"></i>
            </div>

            ${error && html`<${Alert} message=${error} onDismiss=${() => setError(null)} />`}

            {/* Action Buttons */}
            <div class="grid grid-cols-2 gap-4 mt-6">
                <button
                    onClick=${() => handleAction('activate')}
                    disabled=${isLoading || status === 'active' || status === 'starting'}
                    class="btn btn-success disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    ${isLoading && status !== 'active' ? html`<span class="spinner-sm"></span>` : html`<i class="fas fa-play mr-2"></i>Activate`}
                </button>
                <button
                    onClick=${() => handleAction('deactivate')}
                    disabled=${isLoading || status === 'inactive' || status === 'error'}
                    class="btn btn-danger disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    ${isLoading && status === 'active' ? html`<span class="spinner-sm"></span>` : html`<i class="fas fa-stop mr-2"></i>Deactivate`}
                </button>
            </div>
        </div>
    `;
}
